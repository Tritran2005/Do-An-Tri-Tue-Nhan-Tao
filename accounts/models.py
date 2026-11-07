from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CANDIDATE = 'candidate'
    ROLE_HR = 'hr'
    ROLE_ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Quản trị viên Hệ thống (System Admin)'),
        (ROLE_HR, 'Nhà tuyển dụng (HR/Recruiter)'),
        (ROLE_CANDIDATE, 'Ứng viên (Candidate)'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CANDIDATE,
        verbose_name='Vai trò',
        help_text='Phân định quyền hạn: Admin, HR hoặc Ứng viên'
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Số điện thoại'
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Tên công ty (Dành cho HR)'
    )

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_candidate(self):
        return self.role == self.ROLE_CANDIDATE

    @property
    def is_hr(self):
        return self.role == self.ROLE_HR

    def __str__(self):
        full_name = self.get_full_name()
        display_name = full_name if full_name else self.username
        return f"{display_name} ({self.get_role_display()})"
