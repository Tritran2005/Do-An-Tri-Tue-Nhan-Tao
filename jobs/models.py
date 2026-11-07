from django.db import models
from django.conf import settings

class JobPosting(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Toàn thời gian (Full-time)'),
        ('Part-time', 'Bán thời gian (Part-time)'),
        ('Remote', 'Làm việc từ xa (Remote)'),
        ('Hybrid', 'Linh hoạt (Hybrid)'),
    ]

    hr = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_postings',
        limit_choices_to={'role': 'hr'},
        verbose_name="Nhà tuyển dụng phụ trách"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Tiêu đề công việc"
    )
    description = models.TextField(
        verbose_name="Mô tả chi tiết công việc (Job Description - JD)",
        help_text="Nội dung JD chi tiết phục vụ bóc tách từ khóa và chấm điểm Semantic Matching qua Sentence-BERT"
    )
    required_skills = models.TextField(
        verbose_name="Kỹ năng trọng tâm yêu cầu",
        help_text="Nhập các kỹ năng phân tách bằng dấu phẩy. Ví dụ: Python, Django, MySQL, NLP, Docker"
    )
    min_experience = models.PositiveIntegerField(
        default=0,
        verbose_name="Số năm kinh nghiệm tối thiểu (năm)",
        help_text="0 nếu chấp nhận Fresher/Mới tốt nghiệp"
    )
    location = models.CharField(
        max_length=100,
        default="Hà Nội",
        verbose_name="Địa điểm làm việc"
    )
    salary_range = models.CharField(
        max_length=100,
        default="Thỏa thuận",
        verbose_name="Mức lương dự kiến"
    )
    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPE_CHOICES,
        default='Full-time',
        verbose_name="Hình thức làm việc"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang tuyển dụng"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày đăng tin"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Cập nhật lần cuối"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bài tuyển dụng"
        verbose_name_plural = "Danh sách bài tuyển dụng"

    def get_skills_list(self):
        """Phân tách chuỗi kỹ năng thành danh sách Python chuẩn hóa, phục vụ AI Skill Matching."""
        if not self.required_skills:
            return []
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]

    def __str__(self):
        company = getattr(self.hr, 'company_name', '') or self.hr.username
        return f"{self.title} ({company})"


class Application(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Chờ duyệt (Pending)'),
        (STATUS_REVIEWED, 'Đã xem hồ sơ (Reviewed)'),
        (STATUS_ACCEPTED, 'Chấp thuận (Accepted)'),
        (STATUS_REJECTED, 'Từ chối (Rejected)'),
    ]

    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name="Vị trí tuyển dụng"
    )
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        limit_choices_to={'role': 'candidate'},
        verbose_name="Ứng viên"
    )
    cv_file = models.FileField(
        upload_to='cv_uploads/%Y/%m/',
        verbose_name="File CV đính kèm"
    )
    parsed_text = models.TextField(
        blank=True,
        default='',
        verbose_name="Văn bản trích xuất từ CV"
    )
    extracted_skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Kỹ năng bóc tách từ CV (AI Extractor)"
    )
    extracted_email = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Email bóc tách từ CV (AI Extractor)"
    )
    extracted_phone = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name="Số điện thoại bóc tách từ CV (AI Extractor)"
    )

    # AI Scoring & XAI Breakdown
    match_score = models.FloatField(
        default=0.0,
        verbose_name="Điểm phù hợp tổng thể match_score (%)",
        help_text="Điểm số tương thích chuẩn hóa từ 0 - 100% phục vụ tự động sắp xếp ứng viên"
    )
    total_score = models.FloatField(
        default=0.0,
        verbose_name="Điểm tổng hợp S_total (%)"
    )
    skill_score = models.FloatField(
        default=0.0,
        verbose_name="Điểm kỹ năng S_skill (%)"
    )
    semantic_score = models.FloatField(
        default=0.0,
        verbose_name="Điểm ngữ nghĩa Sentence-BERT (%)"
    )
    experience_score = models.FloatField(
        default=0.0,
        verbose_name="Điểm kinh nghiệm (%)"
    )
    education_score = models.FloatField(
        default=0.0,
        verbose_name="Điểm học vấn (%)"
    )
    matched_skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Kỹ năng đã khớp (Matched)"
    )
    missing_skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Kỹ năng còn thiếu (Missing)"
    )
    # P3 – Cờ phát hiện nhồi từ khóa (Keyword Stuffing Detection)
    keyword_stuffing_flag = models.BooleanField(
        default=False,
        verbose_name="Cảnh báo nhồi từ khóa (Keyword Stuffing)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Trạng thái ứng tuyển"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời gian nộp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Cập nhật lần cuối"
    )

    class Meta:
        ordering = ['-match_score', '-created_at']
        unique_together = ('job', 'candidate')
        verbose_name = "Hồ sơ ứng tuyển"
        verbose_name_plural = "Danh sách hồ sơ ứng tuyển"

    def save(self, *args, **kwargs):
        # Tự động đồng bộ giữa match_score và total_score
        if self.match_score and not self.total_score:
            self.total_score = self.match_score
        elif self.total_score and not self.match_score:
            self.match_score = self.total_score
        super().save(*args, **kwargs)

    @property
    def cv_file_path(self):
        """Đường dẫn tuyệt đối tới file CV trên ổ đĩa."""
        return self.cv_file.path if self.cv_file else ""

    @property
    def contact_email(self):
        """Ưu tiên email trích xuất trực tiếp từ CV; nếu trống thì lấy email tài khoản người dùng."""
        return self.extracted_email or getattr(self.candidate, 'email', '') or ""

    @property
    def contact_phone(self):
        """Ưu tiên số điện thoại trích xuất trực tiếp từ CV; nếu trống thì lấy SĐT tài khoản."""
        return self.extracted_phone or getattr(self.candidate, 'phone_number', '') or ""

    def __str__(self):
        candidate_name = self.candidate.get_full_name() or self.candidate.username
        return f"Hồ sơ: {candidate_name} -> {self.job.title}"

