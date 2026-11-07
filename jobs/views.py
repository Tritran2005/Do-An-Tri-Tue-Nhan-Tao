import os
import re
import csv
import uuid
import secrets
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from accounts.views import hr_required, candidate_required
from .models import JobPosting, Application
from .forms import JobPostingForm, ApplicationForm
from ai_engine.parser import extract_text_from_file
from ai_engine.extractor import extract_skills, extract_contact_info
from ai_engine.evaluator import evaluate_candidate_application

logger = logging.getLogger(__name__)


# ==========================================
# PUBLIC VIEWS (Ứng viên & Khách xem tự do)
# ==========================================
def job_list_view(request):
    """
    Trang Sàn Tuyển Dụng Công Khai (Job Board).
    Hỗ trợ tìm kiếm theo từ khóa (tiêu đề, kỹ năng, mô tả) và lọc theo kinh nghiệm/địa điểm.
    """
    query = request.GET.get('q', '').strip()
    exp_filter = request.GET.get('exp', '').strip()
    type_filter = request.GET.get('type', '').strip()

    jobs = JobPosting.objects.filter(is_active=True).select_related('hr')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(required_skills__icontains=query) |
            Q(description__icontains=query) |
            Q(hr__company_name__icontains=query) |
            Q(location__icontains=query)
        )

    if exp_filter:
        try:
            exp_val = int(exp_filter)
            jobs = jobs.filter(min_experience__lte=exp_val)
        except ValueError:
            pass

    if type_filter:
        jobs = jobs.filter(job_type=type_filter)

    # Phân trang: 9 tin tuyển dụng mỗi trang
    paginator = Paginator(jobs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'query': query,
        'exp_filter': exp_filter,
        'type_filter': type_filter,
        'total_jobs_count': jobs.count(),
    })


def job_detail_view(request, pk):
    """
    Trang chi tiết bài tuyển dụng (JD Detail).
    Hiển thị thông tin công ty, yêu cầu kỹ năng, mô tả và nút ứng tuyển.
    """
    job = get_object_or_404(JobPosting.objects.select_related('hr'), pk=pk)
    skills_list = job.get_skills_list()

    # Kiểm tra xem người dùng hiện tại có phải là chủ bài đăng (HR sở hữu) hay không
    is_owner = request.user.is_authenticated and (job.hr == request.user or request.user.is_superuser)

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'skills_list': skills_list,
        'is_owner': is_owner,
    })


# ==========================================
# HR MANAGEMENT VIEWS (Chỉ dành cho HR)
# ==========================================
@hr_required
def hr_dashboard_view(request):
    """
    Bảng điều khiển quản lý của Nhà tuyển dụng (HR Dashboard).
    Hiển thị danh sách các bài tuyển dụng do chính HR này đăng tải và các số liệu tổng quan.
    """
    my_jobs = JobPosting.objects.filter(hr=request.user).annotate(
        applicant_count=Count('applications')
    )
    active_count = my_jobs.filter(is_active=True).count()
    inactive_count = my_jobs.filter(is_active=False).count()

    return render(request, 'jobs/hr_dashboard.html', {
        'jobs': my_jobs,
        'total_count': my_jobs.count(),
        'active_count': active_count,
        'inactive_count': inactive_count,
    })


@hr_required
def hr_job_candidates_view(request, pk):
    """
    Trang Báo Cáo Xếp Hạng Ứng Viên & XAI (HR Candidate Ranking & Screener Dashboard) cho một Job cụ thể.
    - Tự động sắp xếp (sorting) giảm dần theo match_score (ORDER BY match_score DESC, created_at DESC).
    - Tích hợp XAI trực quan: matched_skills (xanh lá), missing_skills (đỏ).
    - Phân rã điểm thành phần: Kỹ năng, Ngữ nghĩa, Kinh nghiệm, Học vấn.
    - Bộ lọc theo từ khóa, mức độ phù hợp (Tier) và trạng thái ứng tuyển.
    """
    job = get_object_or_404(JobPosting, pk=pk)

    if job.hr != request.user and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền quản lý hồ sơ ứng viên của bài tuyển dụng này.")
        return redirect('jobs:hr_dashboard')

    # Query gốc: Tự động sắp xếp giảm dần theo match_score trong MySQL
    base_qs = Application.objects.filter(job=job).select_related('candidate', 'job')
    
    # KPI Metrics trên toàn bộ ứng viên của Job
    total_candidates = base_qs.count()
    high_match_count = base_qs.filter(match_score__gte=70.0).count()
    top_score = base_qs.order_by('-match_score').first().match_score if total_candidates > 0 else 0.0
    avg_score = round(sum(a.match_score for a in base_qs) / total_candidates, 1) if total_candidates > 0 else 0.0

    # Lọc & Tìm kiếm
    applications = base_qs.order_by('-match_score', '-created_at')
    
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    tier_filter = request.GET.get('tier', '').strip()

    if query:
        applications = applications.filter(
            Q(candidate__username__icontains=query) |
            Q(candidate__first_name__icontains=query) |
            Q(candidate__last_name__icontains=query) |
            Q(candidate__email__icontains=query)
        )

    if status_filter:
        applications = applications.filter(status=status_filter)

    if tier_filter == 'excellent':
        applications = applications.filter(match_score__gte=80.0)
    elif tier_filter == 'good':
        applications = applications.filter(match_score__gte=65.0, match_score__lt=80.0)
    elif tier_filter == 'potential':
        applications = applications.filter(match_score__gte=50.0, match_score__lt=65.0)
    elif tier_filter == 'low':
        applications = applications.filter(match_score__lt=50.0)

    return render(request, 'jobs/hr_job_candidates.html', {
        'job': job,
        'applications': applications,
        'filtered_count': applications.count(),
        'total_candidates': total_candidates,
        'top_score': top_score,
        'avg_score': avg_score,
        'high_match_count': high_match_count,
        'query': query,
        'status_filter': status_filter,
        'tier_filter': tier_filter,
    })


@hr_required
def hr_export_candidates_csv_view(request, pk):
    """
    Xuất báo cáo xếp hạng ứng viên AI ra định dạng CSV (tương thích 100% Microsoft Excel với UTF-8 BOM).
    Bao gồm thông tin liên hệ (Email, SĐT), điểm tổng hợp, điểm 4 trụ cột và kỹ năng khớp/thiếu.
    """
    job = get_object_or_404(JobPosting, pk=pk)
    if job.hr != request.user and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền xuất dữ liệu của bài tuyển dụng này.")
        return redirect('jobs:hr_dashboard')

    applications = Application.objects.filter(job=job).select_related('candidate').order_by('-match_score', '-created_at')

    # Định dạng tên file an toàn: Bao_cao_ung_vien_[JobSlug]_[NgayThang].csv
    job_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', job.title.strip())[:30]
    filename = f"Bao_cao_ung_vien_{job_slug}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # utf-8-sig giúp Microsoft Excel trên Windows tự nhận diện Unicode tiếng Việt không bị lỗi font
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    # 1. Tiêu đề báo cáo
    writer.writerow(['BÁO CÁO XẾP HẠNG ỨNG VIÊN AI - NỀN TẢNG TUYỂN DỤNG THÔNG MINH'])
    writer.writerow(['Vị trí tuyển dụng:', job.title])
    writer.writerow(['Công ty / Nhà tuyển dụng:', getattr(job.hr, 'company_name', '') or job.hr.username])
    writer.writerow(['Yêu cầu kinh nghiệm tối thiểu:', f"{job.min_experience} năm"])
    writer.writerow(['Kỹ năng trọng tâm trong JD:', job.required_skills])
    writer.writerow(['Thời điểm xuất báo cáo:', timezone.now().strftime('%d/%m/%Y %H:%M:%S')])
    writer.writerow([])  # Dòng phân cách

    # 2. Tiêu đề các cột dữ liệu
    headers = [
        'Xếp hạng',
        'Họ và tên ứng viên',
        'Email liên hệ',
        'Số điện thoại',
        'Điểm phù hợp tổng thể (%)',
        'Phân tầng đánh giá',
        'Điểm Kỹ năng (%)',
        'Điểm Ngữ nghĩa S-BERT (%)',
        'Điểm Kinh nghiệm (%)',
        'Điểm Học vấn (%)',
        'Kỹ năng đã đáp ứng (Matched)',
        'Kỹ năng còn thiếu (Missing)',
        'Trạng thái hồ sơ',
        'Thời gian nộp hồ sơ'
    ]
    writer.writerow(headers)

    # 3. Ghi dữ liệu từng ứng viên
    valid_statuses = dict(Application.STATUS_CHOICES)
    for rank, app in enumerate(applications, start=1):
        score = app.match_score
        if score >= 80.0:
            tier = 'Xuất sắc (Top Match)'
        elif score >= 65.0:
            tier = 'Tiềm năng (Good Match)'
        elif score >= 50.0:
            tier = 'Trung bình (Average)'
        else:
            tier = 'Chưa phù hợp (Low Match)'

        matched_str = ', '.join(app.matched_skills) if app.matched_skills else 'Không có'
        missing_str = ', '.join(app.missing_skills) if app.missing_skills else 'Không có'
        status_label = valid_statuses.get(app.status, app.status)
        created_time = app.created_at.strftime('%d/%m/%Y %H:%M') if app.created_at else ''
        candidate_name = app.candidate.get_full_name() or app.candidate.username

        writer.writerow([
            f"#{rank}",
            candidate_name,
            app.contact_email,
            app.contact_phone,
            f"{app.match_score:.1f}",
            tier,
            f"{app.skill_score:.1f}",
            f"{app.semantic_score:.1f}",
            f"{app.experience_score:.1f}",
            f"{app.education_score:.1f}",
            matched_str,
            missing_str,
            status_label,
            created_time
        ])

    return response


# ==============================================================================
# P2 – XUẤT BÁO CÁO EXCEL (.xlsx) VỚI ĐỊNH DẠNG CHUYÊN NGHIỆP
# ==============================================================================
@hr_required
def hr_export_candidates_xlsx_view(request, pk):
    """
    Xuất báo cáo xếp hạng ứng viên AI ra file Excel (.xlsx) với định dạng chuyên nghiệp:
    - Header màu xanh đậm, chữ trắng đậm
    - Freeze pane dòng tiêu đề
    - Auto-fit chiều rộng cột
    - Tô màu cột điểm theo thang màu (xanh lá = cao, vàng = trung bình, đỏ = thấp)
    """
    try:
        from openpyxl import Workbook
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        import io
    except ImportError:
        messages.error(request, "Thư viện openpyxl chưa được cài đặt. Vui lòng chạy: pip install openpyxl")
        return redirect('jobs:hr_job_candidates', pk=pk)

    job = get_object_or_404(JobPosting, pk=pk)
    if job.hr != request.user and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền xuất dữ liệu của bài tuyển dụng này.")
        return redirect('jobs:hr_dashboard')

    applications = Application.objects.filter(job=job).select_related('candidate').order_by('-match_score', '-created_at')

    # ------ Tạo Workbook ------
    wb = Workbook()
    ws = wb.active
    ws.title = "Xếp hạng ứng viên AI"

    # Màu sắc chủ đề
    COLOR_HEADER_BG  = "4F46E5"  # Indigo đậm
    COLOR_SUBHEADER  = "E0E7FF"  # Indigo nhạt
    COLOR_WHITE      = "FFFFFF"
    COLOR_GREEN      = "D1FAE5"  # Xanh lá nhạt - điểm cao
    COLOR_YELLOW     = "FEF9C3"  # Vàng nhạt   - điểm trung bình
    COLOR_RED        = "FFE4E6"  # Đỏ nhạt     - điểm thấp

    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0'),
    )

    # ------ Dòng 1: Tiêu đề báo cáo ------
    ws.merge_cells('A1:N1')
    ws['A1'] = "BÁO CÁO XẾP HẠNG ỨNG VIÊN AI — NỀN TẢNG TUYỂN DỤNG THÔNG MINH"
    ws['A1'].font = Font(name='Segoe UI', bold=True, size=14, color=COLOR_WHITE)
    ws['A1'].fill = PatternFill("solid", fgColor=COLOR_HEADER_BG)
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 32

    # Dòng 2-6: Thông tin báo cáo
    meta_rows = [
        ("Vị trí tuyển dụng:", job.title),
        ("Công ty / HR:", getattr(job.hr, 'company_name', '') or job.hr.username),
        ("Kinh nghiệm tối thiểu:", f"{job.min_experience} năm"),
        ("Kỹ năng yêu cầu:", job.required_skills),
        ("Thời điểm xuất:", timezone.now().strftime('%d/%m/%Y %H:%M:%S')),
    ]
    for i, (label, value) in enumerate(meta_rows, start=2):
        ws.cell(row=i, column=1).value = label
        ws.cell(row=i, column=1).font = Font(bold=True, color="374151")
        ws.cell(row=i, column=1).fill = PatternFill("solid", fgColor=COLOR_SUBHEADER)
        ws.merge_cells(f'B{i}:N{i}')
        ws.cell(row=i, column=2).value = value
        ws.cell(row=i, column=2).alignment = Alignment(wrap_text=True)
        ws.row_dimensions[i].height = 16

    header_row = len(meta_rows) + 2  # Dòng tiêu đề cột thực sự

    # ------ Tiêu đề cột dữ liệu ------
    headers = [
        'Xếp hạng', 'Họ và tên', 'Email liên hệ', 'Số điện thoại',
        'Điểm tổng (%)', 'Phân tầng AI',
        'Điểm KN (%)', 'Điểm BERT (%)', 'Điểm Kinh nghiệm (%)', 'Điểm Học vấn (%)',
        'Kỹ năng Matched', 'Kỹ năng Missing',
        'Trạng thái', 'Ngày nộp hồ sơ'
    ]
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col_idx)
        cell.value = header
        cell.font = Font(bold=True, color=COLOR_WHITE, name='Segoe UI', size=10)
        cell.fill = PatternFill("solid", fgColor=COLOR_HEADER_BG)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[header_row].height = 24

    # Freeze dòng tiêu đề cột
    ws.freeze_panes = ws.cell(row=header_row + 1, column=1)

    # ------ Dữ liệu ứng viên ------
    valid_statuses = dict(Application.STATUS_CHOICES)
    for rank, app in enumerate(applications, start=1):
        row_idx = header_row + rank
        score = app.match_score

        if score >= 80.0:
            tier = 'Xuất sắc ⭐'
            score_fill = PatternFill("solid", fgColor=COLOR_GREEN)
        elif score >= 65.0:
            tier = 'Tiềm năng 👍'
            score_fill = PatternFill("solid", fgColor="D1FAE5")
        elif score >= 50.0:
            tier = 'Trung bình ⚠'
            score_fill = PatternFill("solid", fgColor=COLOR_YELLOW)
        else:
            tier = 'Chưa phù hợp ❌'
            score_fill = PatternFill("solid", fgColor=COLOR_RED)

        matched_str = ', '.join(app.matched_skills) if app.matched_skills else '—'
        missing_str = ', '.join(app.missing_skills) if app.missing_skills else '—'
        status_label = valid_statuses.get(app.status, app.status)
        created_time = app.created_at.strftime('%d/%m/%Y %H:%M') if app.created_at else ''
        candidate_name = app.candidate.get_full_name() or app.candidate.username

        row_data = [
            f"#{rank}", candidate_name, app.contact_email, app.contact_phone,
            round(score, 1), tier,
            round(app.skill_score, 1), round(app.semantic_score, 1),
            round(app.experience_score, 1), round(app.education_score, 1),
            matched_str, missing_str,
            status_label, created_time
        ]

        # Màu nền xen kẽ giữa các dòng
        row_bg = "F8FAFC" if rank % 2 == 0 else COLOR_WHITE

        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.value = value
            cell.border = thin_border
            cell.alignment = Alignment(wrap_text=True, vertical='center')

            # Cột điểm tổng (cột 5): tô màu theo thang điểm
            if col_idx == 5:
                cell.fill = score_fill
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center', vertical='center')
            elif col_idx in (7, 8, 9, 10):  # Điểm thành phần
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.fill = PatternFill("solid", fgColor=row_bg)
            elif col_idx == 1:  # Cột xếp hạng
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.font = Font(bold=True)
                cell.fill = PatternFill("solid", fgColor=row_bg)
            else:
                cell.fill = PatternFill("solid", fgColor=row_bg)

        ws.row_dimensions[row_idx].height = 20

    # ------ Tự động căn chỉnh độ rộng cột ------
    col_min_widths = [8, 24, 28, 16, 14, 22, 12, 12, 18, 12, 40, 40, 22, 18]
    for col_idx, min_w in enumerate(col_min_widths, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = min_w

    # ------ Xuất file ra HTTP Response ------
    job_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', job.title.strip())[:30]
    filename = f"Bao_cao_ung_vien_{job_slug}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



@hr_required
def application_update_status_view(request, pk):
    """
    Xử lý cập nhật nhanh trạng thái hồ sơ ứng viên (Pending -> Reviewed -> Accepted -> Rejected).
    """
    application = get_object_or_404(Application.objects.select_related('job', 'candidate'), pk=pk)
    
    if application.job.hr != request.user and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền cập nhật trạng thái hồ sơ này.")
        return redirect('jobs:hr_dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = dict(Application.STATUS_CHOICES)
        if new_status in valid_statuses:
            application.status = new_status
            application.save()
            candidate_name = application.candidate.get_full_name() or application.candidate.username
            messages.success(request, f"Đã cập nhật trạng thái ứng viên {candidate_name} thành '{valid_statuses[new_status]}'.")

            # --- P2: Gửi email thông báo trạng thái cho ứng viên ---
            try:
                from jobs.tasks import send_status_notification_email_task
                from django.conf import settings as dj_settings
                if getattr(dj_settings, 'ENABLE_ASYNC_CELERY', False):
                    # Chạy bất đồng bộ qua Celery worker
                    send_status_notification_email_task.delay(application.id, new_status)
                else:
                    # Chạy đồng bộ (fallback khi không có Celery/Redis)
                    send_status_notification_email_task(application.id, new_status)
            except Exception as email_err:
                logger.warning(f"[Email] Không gửi được email thông báo: {email_err}")
            # ---------------------------------------------------------
        else:
            messages.error(request, "Trạng thái cập nhật không hợp lệ.")

    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('jobs:hr_job_candidates', pk=application.job.pk)


@hr_required
def hr_batch_update_status_view(request, pk):
    """
    Xử lý cập nhật trạng thái hàng loạt (Bulk Status Update) cho nhiều ứng viên trong 1 Job.
    """
    job = get_object_or_404(JobPosting, pk=pk)
    if job.hr != request.user and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền quản lý bài tuyển dụng này.")
        return redirect('jobs:hr_dashboard')

    if request.method == 'POST':
        app_ids = request.POST.getlist('application_ids')
        new_status = request.POST.get('new_status')
        valid_statuses = dict(Application.STATUS_CHOICES)

        if not app_ids:
            messages.warning(request, "Vui lòng chọn ít nhất một hồ sơ ứng viên để thực hiện thao tác duyệt hàng loạt.")
            return redirect('jobs:hr_job_candidates', pk=job.pk)

        if new_status not in valid_statuses:
            messages.error(request, "Trạng thái cập nhật không hợp lệ.")
            return redirect('jobs:hr_job_candidates', pk=job.pk)

        updated_count = Application.objects.filter(
            id__in=app_ids,
            job=job
        ).update(status=new_status)

        # --- P2: Gửi email thông báo trạng thái hàng loạt cho các ứng viên ---
        try:
            from jobs.tasks import send_status_notification_email_task
            from django.conf import settings as dj_settings
            for app_id in app_ids:
                try:
                    if getattr(dj_settings, 'ENABLE_ASYNC_CELERY', False):
                        send_status_notification_email_task.delay(int(app_id), new_status)
                    else:
                        send_status_notification_email_task(int(app_id), new_status)
                except Exception as item_err:
                    logger.warning(f"[Batch Email] Không gửi được email cho Application #{app_id}: {item_err}")
        except Exception as email_err:
            logger.warning(f"[Batch Email] Lỗi gửi email hàng loạt: {email_err}")
        # --------------------------------------------------------------------

        status_display = valid_statuses[new_status]
        messages.success(request, f"Đã cập nhật thành công trạng thái '{status_display}' cho {updated_count} hồ sơ ứng viên đã chọn!")

    return redirect('jobs:hr_job_candidates', pk=job.pk)


@hr_required
def hr_batch_upload_cvs_view(request, pk):
    """
    Xử lý tải lên và đánh giá AI hàng loạt nhiều tệp CV (PDF/DOCX) cho một bài tuyển dụng.
    """
    job = get_object_or_404(JobPosting, pk=pk)
    if job.hr != request.user and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền quản lý bài tuyển dụng này.")
        return redirect('jobs:hr_dashboard')

    if request.method == 'POST':
        cv_files = request.FILES.getlist('cv_files')
        if not cv_files:
            messages.warning(request, "Vui lòng chọn ít nhất một tệp CV (.pdf hoặc .docx) để tải lên hàng loạt.")
            return redirect('jobs:hr_job_candidates', pk=job.pk)

        success_count = 0
        error_count = 0

        for file_obj in cv_files:
            try:
                # 1. Kiểm tra phần mở rộng
                ext = os.path.splitext(file_obj.name)[1].lower()
                if ext not in ['.pdf', '.docx']:
                    error_count += 1
                    continue

                # 2. Xử lý tên ứng viên từ tên tệp (ví dụ: CV_01_Nguyen_Van_An_Senior.pdf -> Nguyen Van An)
                base_name = os.path.splitext(file_obj.name)[0]
                clean_name = re.sub(r'^CV[_-]?\d*[_-]?', '', base_name, flags=re.IGNORECASE)
                parts = clean_name.replace('_', ' ').split()
                if len(parts) >= 2:
                    full_name = ' '.join(parts[:3])
                else:
                    full_name = clean_name.replace('_', ' ')

                slug_name = re.sub(r'[^a-zA-Z0-9]', '', full_name.lower())[:15] or 'candidate'
                candidate_email = f"{slug_name}@candidate.local"

                User = get_user_model()
                candidate_user = User.objects.filter(email=candidate_email).first()
                if not candidate_user:
                    username_candidate = f"{slug_name}_{uuid.uuid4().hex[:4]}"
                    candidate_user = User.objects.create_user(
                        username=username_candidate,
                        email=candidate_email,
                        password=secrets.token_urlsafe(16),
                        role=User.ROLE_CANDIDATE,
                        first_name=parts[-1] if parts else full_name,
                        last_name=' '.join(parts[:-1]) if len(parts) > 1 else ''
                    )

                # 3. Tạo hoặc lấy Application
                application, created = Application.objects.get_or_create(
                    job=job,
                    candidate=candidate_user,
                    defaults={'status': Application.STATUS_PENDING}
                )
                application.cv_file = file_obj
                application.save()

                # 4. Trích xuất text từ CV
                raw_text = extract_text_from_file(application.cv_file.path)
                application.parsed_text = raw_text

                # 5. Bóc tách kỹ năng & thông tin liên hệ từ CV
                extracted_skills = extract_skills(raw_text)
                application.extracted_skills = extracted_skills

                contact_info = extract_contact_info(raw_text)
                if contact_info.get('email'):
                    application.extracted_email = contact_info['email']
                if contact_info.get('phone'):
                    application.extracted_phone = contact_info['phone']


                # 6. Đánh giá đa tiêu chí & Sentence-BERT
                jd_skills = job.get_skills_list()
                evaluation_result = evaluate_candidate_application(
                    jd_text=job.description,
                    cv_text=raw_text,
                    jd_skills=jd_skills,
                    cv_skills=extracted_skills,
                    min_experience_required=job.min_experience
                )

                # 7. Lưu điểm số và dữ liệu XAI
                application.match_score = evaluation_result["total_score"]
                application.total_score = evaluation_result["total_score"]
                application.skill_score = evaluation_result["scores"]["skill_score"]
                application.semantic_score = evaluation_result["scores"]["semantic_score"]
                application.experience_score = evaluation_result["scores"]["experience_score"]
                application.education_score = evaluation_result["scores"]["education_score"]
                application.matched_skills = evaluation_result["skills_breakdown"]["matched_skills"]
                application.missing_skills = evaluation_result["skills_breakdown"]["missing_skills"]
                # P3 – Cập nhật cờ keyword stuffing từ kết quả AI evaluator
                ks_info = evaluation_result.get("keyword_stuffing", {})
                application.keyword_stuffing_flag = ks_info.get("detected", False)
                application.save()

                success_count += 1
            except Exception as e:
                logger.error(f"Lỗi khi xử lý tải lên hàng loạt {file_obj.name}: {e}")
                error_count += 1

        if success_count > 0:
            messages.success(request, f"🎉 Đã tải lên và hoàn thành đánh giá AI tự động cho {success_count} hồ sơ CV!")
        if error_count > 0:
            messages.warning(request, f"⚠️ Có {error_count} tệp không thể xử lý (định dạng không hỗ trợ hoặc lỗi nội dung).")

    return redirect('jobs:hr_job_candidates', pk=job.pk)


@hr_required
def job_create_view(request):
    """View đăng bài tuyển dụng mới dành cho HR."""
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.hr = request.user  # Gán bài đăng cho HR hiện tại
            job.save()
            messages.success(request, f"Đã tạo thành công bài tuyển dụng: '{job.title}'!")
            return redirect('jobs:hr_dashboard')
        else:
            messages.error(request, "Vui lòng kiểm tra lại các trường thông tin JD.")
    else:
        form = JobPostingForm()

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'title': 'Đăng Tin Tuyển Dụng Mới (Tạo JD)',
        'action_label': 'Đăng tin ngay'
    })


@hr_required
def job_update_view(request, pk):
    """View chỉnh sửa bài tuyển dụng (Chỉ người đăng hoặc Superuser mới có quyền sửa)."""
    job = get_object_or_404(JobPosting, pk=pk)

    # Đảm bảo HR chỉ sửa được bài của chính mình
    if job.hr != request.user and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền chỉnh sửa bài tuyển dụng của nhà tuyển dụng khác.")
        return redirect('jobs:hr_dashboard')

    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cập nhật bài tuyển dụng '{job.title}' thành công!")
            return redirect('jobs:hr_dashboard')
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin chỉnh sửa.")
    else:
        form = JobPostingForm(instance=job)

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'job': job,
        'title': f'Chỉnh Sửa Tin Tuyển Dụng: {job.title}',
        'action_label': 'Lưu thay đổi'
    })


@hr_required
def job_delete_view(request, pk):
    """View xóa bài tuyển dụng (Chỉ người đăng hoặc Superuser mới có quyền xóa)."""
    job = get_object_or_404(JobPosting, pk=pk)

    if job.hr != request.user and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền xóa bài tuyển dụng này.")
        return redirect('jobs:hr_dashboard')

    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f"Đã xóa vĩnh viễn bài tuyển dụng '{title}'.")
        return redirect('jobs:hr_dashboard')

    return render(request, 'jobs/job_confirm_delete.html', {'job': job})


# ==========================================
# CANDIDATE APPLICATION & AI CV WORKFLOW
# ==========================================
@candidate_required
def apply_job_view(request, pk):
    """
    Quy trình Ứng tuyển & Kích hoạt AI Parser / Extractor:
    1. Ứng viên tải file CV (.pdf hoặc .docx).
    2. Hệ thống lưu tệp vào storage.
    3. Parser trích xuất raw text từ file.
    4. Extractor quét từ điển kỹ năng (Taxonomy) bóc tách các kỹ năng ứng viên có.
    5. Lưu kết quả vào CSDL MySQL.
    """
    job = get_object_or_404(JobPosting, pk=pk, is_active=True)
    existing_application = Application.objects.filter(job=job, candidate=request.user).first()

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES, instance=existing_application)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = request.user
            application.save()

            # KÍCH HOẠT PIPELINE AI XỬ LÝ CV & ĐÁNH GIÁ ĐA TIÊU CHÍ
            try:
                # Kiểm tra nếu cấu hình hàng đợi Celery bất đồng bộ đang kích hoạt
                if getattr(settings, 'ENABLE_ASYNC_CELERY', False):
                    try:
                        from .tasks import process_cv_application_async_task
                        process_cv_application_async_task.delay(application.id)
                        messages.success(
                            request,
                            "Nộp hồ sơ thành công! AI đang tiến hành phân tích CV trong hàng đợi nền (Celery Async Worker)..."
                        )
                        return redirect('jobs:application_detail', pk=application.pk)
                    except Exception as celery_err:
                        logger.warning(f"Không thể kết nối Celery/Redis ({celery_err}). Chuyển sang xử lý đồng bộ cục bộ.")

                # Bước 1: Trích xuất toàn bộ văn bản thô (kèm OCR Fallback)
                cv_abs_path = application.cv_file.path
                raw_text = extract_text_from_file(cv_abs_path)
                application.parsed_text = raw_text

                # Bước 2: Bóc tách thực thể kỹ năng qua Regex & Taxonomy
                extracted_skills = extract_skills(raw_text)
                application.extracted_skills = extracted_skills

                # Bóc tách thông tin liên hệ (Email & SĐT) trực tiếp từ văn bản CV
                contact_info = extract_contact_info(raw_text)
                if contact_info.get('email'):
                    application.extracted_email = contact_info['email']
                if contact_info.get('phone'):
                    application.extracted_phone = contact_info['phone']

                # Bước 3 & 4: Đánh giá đa tiêu chí và tính điểm tổng hợp S_total
                evaluation = evaluate_candidate_application(
                    jd_text=job.description,
                    cv_text=raw_text,
                    jd_skills=job.required_skills,
                    cv_skills=extracted_skills,
                    min_experience_required=job.min_experience
                )

                # Lưu điểm số vào CSDL MySQL
                application.match_score = evaluation['total_score']
                application.total_score = evaluation['total_score']
                application.skill_score = evaluation['scores']['skill_score']
                application.semantic_score = evaluation['scores']['semantic_score']
                application.experience_score = evaluation['scores']['experience_score']
                application.education_score = evaluation['scores']['education_score']
                application.matched_skills = evaluation['skills_breakdown']['matched_skills']
                application.missing_skills = evaluation['skills_breakdown']['missing_skills']
                # P3 – Keyword Stuffing flag
                ks_info = evaluation.get("keyword_stuffing", {})
                application.keyword_stuffing_flag = ks_info.get("detected", False)

                application.save()
                messages.success(
                    request,
                    f"Nộp hồ sơ thành công! AI Đánh giá: Độ phù hợp tổng thể đạt {application.total_score}% ({evaluation['ranking_tier']})."
                )
            except Exception as e:
                messages.warning(
                    request,
                    f"Hồ sơ đã được lưu, nhưng xảy ra cảnh báo trong tiến trình AI Parser: {str(e)}"
                )

            return redirect('jobs:application_detail', pk=application.pk)
        else:
            messages.error(request, "Tệp CV tải lên không hợp lệ. Vui lòng chọn tệp định dạng .PDF hoặc .DOCX dưới 10MB.")
    else:
        form = ApplicationForm(instance=existing_application)

    return render(request, 'jobs/apply_job.html', {
        'job': job,
        'form': form,
        'existing_application': existing_application,
    })


@login_required
def application_detail_view(request, pk):
    """
    Xem chi tiết hồ sơ ứng tuyển:
    Hiển thị thông tin file, danh sách kỹ năng đã trích xuất, và đoạn trích văn bản thô.
    Chỉ cho phép Ứng viên sở hữu hoặc HR phụ trách bài đăng xem.
    """
    application = get_object_or_404(
        Application.objects.select_related('job', 'job__hr', 'candidate'),
        pk=pk
    )

    is_owner_candidate = (application.candidate == request.user)
    is_job_hr = (application.job.hr == request.user)

    if not (is_owner_candidate or is_job_hr or request.user.is_superuser):
        messages.error(request, "Bạn không có quyền truy cập hồ sơ ứng tuyển này.")
        return redirect('jobs:job_list')

    # Tự động tính điểm nếu hồ sơ chưa được chấm điểm (auto-evaluate)
    if application.total_score == 0.0 and application.parsed_text:
        eval_result = evaluate_candidate_application(
            jd_text=application.job.description,
            cv_text=application.parsed_text,
            jd_skills=application.job.required_skills,
            cv_skills=application.extracted_skills,
            min_experience_required=application.job.min_experience
        )
        application.total_score = eval_result['total_score']
        application.skill_score = eval_result['scores']['skill_score']
        application.semantic_score = eval_result['scores']['semantic_score']
        application.experience_score = eval_result['scores']['experience_score']
        application.education_score = eval_result['scores']['education_score']
        application.matched_skills = eval_result['skills_breakdown']['matched_skills']
        application.missing_skills = eval_result['skills_breakdown']['missing_skills']
        application.save()

    matched_skills = application.matched_skills
    missing_skills = application.missing_skills

    return render(request, 'jobs/application_detail.html', {
        'application': application,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'is_hr_view': is_job_hr or request.user.is_superuser,
    })


@candidate_required
def my_applications_view(request):
    """
    Khu vực Ứng viên (Candidate Portal - My Applications):
    - Hiển thị danh sách hồ sơ ứng tuyển của bản thân, tự động sắp xếp giảm dần theo match_score.
    - Hiển thị điểm số tương thích của bản thân và danh sách kỹ năng còn thiếu (missing_skills).
    - Cung cấp gợi ý phát triển kỹ năng và bổ sung hồ sơ để ứng viên trau dồi, cải thiện.
    """
    applications = Application.objects.filter(
        candidate=request.user
    ).select_related('job', 'job__hr').order_by('-match_score', '-created_at')

    total_count = applications.count()
    accepted_count = applications.filter(status=Application.STATUS_ACCEPTED).count()
    pending_count = applications.filter(status=Application.STATUS_PENDING).count()
    avg_match_score = round(sum(a.match_score for a in applications) / total_count, 1) if total_count > 0 else 0.0

    return render(request, 'jobs/my_applications.html', {
        'applications': applications,
        'total_count': total_count,
        'accepted_count': accepted_count,
        'pending_count': pending_count,
        'avg_match_score': avg_match_score,
    })


@hr_required
def hr_multi_job_screening_view(request):
    """
    Tính Năng Sàng Lọc CV Đa Vị Trí (Multi-Job Batch CV Screening):
    - HR lựa chọn 1 hoặc nhiều bài tuyển dụng đang mở.
    - HR tải lên hàng loạt tệp CV (.pdf, .docx).
    - AI Pipeline tự động chạy phân tích chéo (Cross-Job Evaluation):
      + Bóc tách kỹ năng từng CV.
      + Chấm điểm độc lập từng CV với TẤT CẢ các Job được chọn (Sentence-BERT, Skill matching, Multi-criteria).
      + Xác định vị trí tối ưu nhất (Best Fit Recommendation) có điểm số cao nhất.
      + Ghi nhận hồ sơ ứng tuyển vào vị trí phù hợp nhất.
      + Trực quan hóa Ma trận So khớp Đa vị trí (Cross-Job Score Matrix) với badge 🌟 PHÙ HỢP NHẤT.
    """
    if request.user.is_admin:
        available_jobs = JobPosting.objects.filter(is_active=True).select_related('hr')
    else:
        available_jobs = JobPosting.objects.filter(hr=request.user, is_active=True).select_related('hr')

    matrix_data = []
    selected_jobs = []
    selected_job_ids = []

    if request.method == 'POST':
        job_ids = request.POST.getlist('job_ids')
        cv_files = request.FILES.getlist('cv_files')

        if not job_ids:
            messages.warning(request, "Vui lòng chọn ít nhất một Bài tuyển dụng (Job) để thực hiện sàng lọc đa vị trí.")
        elif not cv_files:
            messages.warning(request, "Vui lòng tải lên ít nhất một tệp CV (.pdf hoặc .docx) để tiến hành phân tích.")
        else:
            selected_jobs = list(available_jobs.filter(id__in=job_ids))
            selected_job_ids = [str(j.id) for j in selected_jobs]
            User = get_user_model()
            processed_count = 0

            for file_obj in cv_files:
                ext = os.path.splitext(file_obj.name)[1].lower()
                if ext not in ['.pdf', '.docx']:
                    continue

                # 1. Trích xuất tên ứng viên & email từ tên tệp
                base_name = os.path.splitext(file_obj.name)[0]
                clean_name = re.sub(r'^CV[_-]?\d*[_-]?', '', base_name, flags=re.IGNORECASE)
                parts = clean_name.replace('_', ' ').split()
                if len(parts) >= 2:
                    full_name = ' '.join(parts[:3])
                else:
                    full_name = clean_name.replace('_', ' ') or 'Ung vien'

                slug_name = re.sub(r'[^a-zA-Z0-9]', '', full_name.lower())[:15] or 'candidate'
                candidate_email = f"{slug_name}@candidate.local"

                candidate_user = User.objects.filter(email=candidate_email).first()
                if not candidate_user:
                    username_candidate = f"{slug_name}_{uuid.uuid4().hex[:4]}"
                    candidate_user = User.objects.create_user(
                        username=username_candidate,
                        email=candidate_email,
                        password=secrets.token_urlsafe(16),
                        role=User.ROLE_CANDIDATE,
                        first_name=parts[-1] if parts else full_name,
                        last_name=' '.join(parts[:-1]) if len(parts) > 1 else ''
                    )

                first_job = selected_jobs[0]
                temp_app, _ = Application.objects.get_or_create(
                    job=first_job,
                    candidate=candidate_user,
                    defaults={'status': Application.STATUS_PENDING}
                )
                temp_app.cv_file = file_obj
                temp_app.save()

                raw_text = extract_text_from_file(temp_app.cv_file.path)
                extracted_skills = extract_skills(raw_text)
                contact_info = extract_contact_info(raw_text)
                if contact_info.get('email'):
                    temp_app.extracted_email = contact_info['email']
                if contact_info.get('phone'):
                    temp_app.extracted_phone = contact_info['phone']
                temp_app.save()

                # 2. Đánh giá chéo với TẤT CẢ các Job đã chọn
                job_evaluations = []
                best_job = None
                best_score = -1.0
                best_eval = None

                for job in selected_jobs:
                    jd_skills = job.get_skills_list()
                    eval_result = evaluate_candidate_application(
                        jd_text=job.description,
                        cv_text=raw_text,
                        jd_skills=jd_skills,
                        cv_skills=extracted_skills,
                        min_experience_required=job.min_experience
                    )
                    score = eval_result['total_score']
                    job_evaluations.append((job, eval_result))

                    if score > best_score:
                        best_score = score
                        best_job = job
                        best_eval = eval_result

                # 3. Ghi nhận hồ sơ ứng tuyển vào vị trí Phù hợp nhất (Best Fit)
                if best_job and best_eval:
                    best_app, created = Application.objects.get_or_create(
                        job=best_job,
                        candidate=candidate_user,
                        defaults={'status': Application.STATUS_PENDING}
                    )
                    best_app.cv_file = file_obj
                    best_app.parsed_text = raw_text
                    best_app.extracted_skills = extracted_skills
                    if contact_info.get('email'):
                        best_app.extracted_email = contact_info['email']
                    if contact_info.get('phone'):
                        best_app.extracted_phone = contact_info['phone']
                    best_app.match_score = best_eval["total_score"]
                    best_app.total_score = best_eval["total_score"]
                    best_app.skill_score = best_eval["scores"]["skill_score"]
                    best_app.semantic_score = best_eval["scores"]["semantic_score"]
                    best_app.experience_score = best_eval["scores"]["experience_score"]
                    best_app.education_score = best_eval["scores"]["education_score"]
                    best_app.matched_skills = best_eval["skills_breakdown"]["matched_skills"]
                    best_app.missing_skills = best_eval["skills_breakdown"]["missing_skills"]
                    best_app.save()

                # 4. Xây dựng Dữ liệu Ma trận Chấm Điểm Chéo
                scores_by_job = {}
                for job, eval_res in job_evaluations:
                    scores_by_job[job.id] = {
                        'job_id': job.id,
                        'job_title': job.title,
                        'total_score': eval_res['total_score'],
                        'skill_score': eval_res['scores']['skill_score'],
                        'semantic_score': eval_res['scores']['semantic_score'],
                        'matched_skills': eval_res['skills_breakdown']['matched_skills'],
                        'missing_skills': eval_res['skills_breakdown']['missing_skills'],
                        'ranking_tier': eval_res['ranking_tier'],
                        'is_best_fit': (job.id == (best_job.id if best_job else None))
                    }

                job_scores_list = [scores_by_job.get(job.id) for job in selected_jobs]

                matrix_data.append({
                    'candidate_name': full_name,
                    'email': contact_info.get('email') or candidate_email,
                    'phone': contact_info.get('phone') or '',
                    'cv_filename': file_obj.name,
                    'job_scores_list': job_scores_list,
                    'best_job': best_job,
                    'best_score': best_score,
                    'extracted_skills': extracted_skills,
                })
                processed_count += 1

            if processed_count > 0:
                matrix_data.sort(key=lambda x: x['best_score'], reverse=True)
                messages.success(
                    request,
                    f"🎉 Phân tích AI thành công {processed_count} CV cho {len(selected_jobs)} vị trí công việc! Ma trận so khớp hiển thị bên dưới."
                )

    return render(request, 'jobs/hr_multi_job_screening.html', {
        'jobs': available_jobs,
        'selected_jobs': selected_jobs,
        'selected_job_ids': selected_job_ids,
        'matrix_data': matrix_data,
    })

