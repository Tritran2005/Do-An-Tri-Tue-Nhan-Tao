import os
import logging
from celery import shared_task
from django.apps import apps

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_cv_application_async_task(self, application_id: int):
    """
    Celery Background Worker Task:
    Xử lý trích xuất văn bản (kèm OCR Fallback), bóc tách kỹ năng, SĐT, Email
    và chấm điểm AI 4 trụ cột bất đồng bộ qua Redis Queue.
    """
    Application = apps.get_model('jobs', 'Application')
    
    try:
        application = Application.objects.select_related('job', 'candidate').get(id=application_id)
    except Application.DoesNotExist:
        logger.error(f"[Celery] Không tìm thấy Application id={application_id}")
        return {"status": "error", "message": "Application not found"}

    try:
        from ai_engine.parser import extract_text_from_file
        from ai_engine.extractor import extract_skills, extract_contact_info
        from ai_engine.evaluator import evaluate_candidate_application

        logger.info(f"[Celery Task] Bắt đầu xử lý Application #{application.id} ({application.candidate.username})")

        cv_path = application.cv_file.path
        if not os.path.exists(cv_path):
            raise FileNotFoundError(f"File CV không tồn tại trên đĩa: {cv_path}")

        # 1. Trích xuất văn bản (tự động kích hoạt OCR nếu PDF dạng scan ảnh)
        raw_text = extract_text_from_file(cv_path)
        application.parsed_text = raw_text

        # 2. Bóc tách Kỹ năng IT (80+ Canonical Taxonomy)
        extracted_skills = extract_skills(raw_text)
        application.extracted_skills = extracted_skills

        # 3. Bóc tách thông tin liên hệ (Email & Số điện thoại)
        contact_info = extract_contact_info(raw_text)
        if contact_info.get('email'):
            application.extracted_email = contact_info['email']
        if contact_info.get('phone'):
            application.extracted_phone = contact_info['phone']

        # 4. Đánh giá đa chiều 4 trụ cột qua S-BERT & Rule-based engine
        job = application.job
        jd_skills = job.get_skills_list()
        eval_result = evaluate_candidate_application(
            jd_text=job.description,
            cv_text=raw_text,
            jd_skills=jd_skills,
            cv_skills=extracted_skills,
            min_experience_required=job.min_experience
        )

        # 5. Cập nhật điểm số và dữ liệu XAI
        application.match_score = eval_result["total_score"]
        application.total_score = eval_result["total_score"]
        application.skill_score = eval_result["scores"]["skill_score"]
        application.semantic_score = eval_result["scores"]["semantic_score"]
        application.experience_score = eval_result["scores"]["experience_score"]
        application.education_score = eval_result["scores"]["education_score"]
        application.matched_skills = eval_result["skills_breakdown"]["matched_skills"]
        application.missing_skills = eval_result["skills_breakdown"]["missing_skills"]
        # P3 – Cập nhật cờ cảnh báo nhồi từ khóa
        ks_info = eval_result.get("keyword_stuffing", {})
        application.keyword_stuffing_flag = ks_info.get("detected", False)

        application.save()
        logger.info(
            f"[Celery Task] Hoàn tất xử lý Application #{application.id}! "
            f"Điểm tổng hợp: {application.match_score}%"
        )
        return {
            "status": "success",
            "application_id": application.id,
            "match_score": application.match_score,
            "ranking_tier": eval_result.get("ranking_tier", "")
        }

    except Exception as exc:
        logger.error(f"[Celery Task] Lỗi khi xử lý Application #{application_id}: {exc}", exc_info=True)
        # Thử lại task nếu lỗi ngẫu nhiên/tạm thời
        raise self.retry(exc=exc)


# ==============================================================================
# EMAIL NOTIFICATION TASK (P2 - Gửi email thông báo trạng thái ứng tuyển)
# ==============================================================================

# Bản đồ trạng thái -> biểu tượng, nhãn, thông điệp, lời khuyên AI Coach
STATUS_EMAIL_MAP = {
    'pending': {
        'icon': '⏳',
        'label': 'Đang chờ xem xét (Pending)',
        'message': 'Hồ sơ của bạn đã được nhận. Nhà tuyển dụng sẽ sớm xem xét và phản hồi.',
        'coach_tip': 'Trong lúc chờ đợi, hãy chuẩn bị sẵn cho buổi phỏng vấn bằng cách nghiên cứu thêm về công ty và ôn lại các kỹ năng chuyên môn.',
    },
    'reviewed': {
        'icon': '👀',
        'label': 'Đã được xem xét (Reviewed)',
        'message': 'Nhà tuyển dụng đã xem hồ sơ của bạn và đang trong quá trình đánh giá.',
        'coach_tip': 'Đây là dấu hiệu tích cực! Hãy cập nhật LinkedIn và chuẩn bị danh sách câu hỏi để hỏi nhà tuyển dụng trong buổi phỏng vấn.',
    },
    'accepted': {
        'icon': '🎉',
        'label': 'Được chấp thuận (Accepted)',
        'message': 'Chúc mừng! Hồ sơ của bạn đã được chấp thuận. Nhà tuyển dụng sẽ liên hệ để sắp xếp bước tiếp theo.',
        'coach_tip': 'Bạn đã vượt qua vòng sàng lọc! Hãy chuẩn bị kỹ cho buổi phỏng vấn kỹ thuật: ôn tập data structures, giải bài trên LeetCode và chuẩn bị câu trả lời cho các câu hỏi behavioral.',
    },
    'rejected': {
        'icon': '💙',
        'label': 'Chưa phù hợp lần này (Not Selected)',
        'message': 'Rất tiếc, hồ sơ của bạn không phù hợp với yêu cầu vị trí này. Đừng nản lòng, hãy tiếp tục cố gắng!',
        'coach_tip': 'Mỗi lần từ chối là một cơ hội học hỏi. Hãy xem lại các kỹ năng còn thiếu trong báo cáo AI và tập trung cải thiện chúng. Thị trường việc làm rất rộng mở!',
    },
}


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_status_notification_email_task(self, application_id: int, new_status: str):
    """
    Celery Background Worker Task:
    Gửi email HTML thông báo cho ứng viên khi HR thay đổi trạng thái hồ sơ.
    Bao gồm: điểm AI, kỹ năng matched/missing, và lời khuyên từ AI Career Coach.
    """
    Application = apps.get_model('jobs', 'Application')

    try:
        application = Application.objects.select_related('job', 'job__hr', 'candidate').get(id=application_id)
    except Application.DoesNotExist:
        logger.error(f"[Email Task] Không tìm thấy Application id={application_id}")
        return {"status": "error", "message": "Application not found"}

    candidate = application.candidate
    candidate_email = application.contact_email  # Dùng property ưu tiên email từ CV

    if not candidate_email:
        logger.warning(f"[Email Task] Ứng viên #{candidate.id} ({candidate.username}) không có email — bỏ qua gửi thông báo.")
        return {"status": "skipped", "reason": "no_email"}

    try:
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.conf import settings as django_settings

        status_meta = STATUS_EMAIL_MAP.get(new_status, STATUS_EMAIL_MAP['pending'])

        # Bóc tách kỹ năng theo định dạng phù hợp template
        matched = application.matched_skills or []
        missing = application.missing_skills or []

        # Lời khuyên nâng cao: nếu từ chối & có kỹ năng còn thiếu, liệt kê cụ thể
        coach_tip = status_meta['coach_tip']
        if new_status == 'rejected' and missing:
            top_missing = ', '.join(missing[:5])
            coach_tip = (
                f"Hồ sơ của bạn còn thiếu một số kỹ năng quan trọng: {top_missing}. "
                f"Hãy ưu tiên học thêm các kỹ năng này để tăng tỷ lệ phù hợp ở các vị trí tương tự. "
                f"Mỗi lần từ chối là cơ hội để hoàn thiện bản thân!"
            )

        site_url = getattr(django_settings, 'SITE_URL', 'http://127.0.0.1:8000')

        # Render HTML template
        html_content = render_to_string('email/status_notification.html', {
            'candidate_name': candidate.get_full_name() or candidate.username,
            'job_title': application.job.title,
            'company_name': getattr(application.job.hr, 'company_name', '') or application.job.hr.username,
            'status_code': new_status,
            'status_icon': status_meta['icon'],
            'status_label': status_meta['label'],
            'status_message': status_meta['message'],
            'ai_score': round(application.total_score or 0, 1),
            'skill_score': round(application.skill_score or 0, 1),
            'semantic_score': round(application.semantic_score or 0, 1),
            'matched_skills': matched,
            'missing_skills': missing,
            'coach_tip': coach_tip,
            'application_id': application.id,
            'site_url': site_url,
        })

        # Nội dung text thuần (fallback cho email client không hỗ trợ HTML)
        text_content = (
            f"Xin chào {candidate.get_full_name() or candidate.username},\n\n"
            f"Hồ sơ ứng tuyển vị trí '{application.job.title}' của bạn vừa được cập nhật:\n"
            f"Trạng thái mới: {status_meta['label']}\n"
            f"Điểm AI: {round(application.total_score or 0, 1)}%\n\n"
            f"Lời khuyên: {coach_tip}\n\n"
            f"Xem chi tiết tại: {site_url}/jobs/applications/{application.id}/\n\n"
            f"Trân trọng,\nAI Recruitment Portal"
        )

        subject = f"[AI Recruitment] {status_meta['icon']} Cập nhật hồ sơ: {application.job.title}"

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            to=[candidate_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(
            f"[Email Task] Đã gửi email thông báo trạng thái '{new_status}' "
            f"cho ứng viên {candidate.username} ({candidate_email})"
        )
        return {"status": "sent", "to": candidate_email, "application_id": application_id}

    except Exception as exc:
        logger.error(
            f"[Email Task] Lỗi gửi email Application #{application_id}: {exc}",
            exc_info=True
        )
        raise self.retry(exc=exc)

