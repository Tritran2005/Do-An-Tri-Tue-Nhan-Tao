import os
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from jobs.models import JobPosting, Application

User = get_user_model()

class MultiJobScreeningTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Admin User
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@example.com',
            password='Password123!',
            role=User.ROLE_ADMIN
        )

        # HR User
        self.hr_user = User.objects.create_user(
            username='hr_demo_test',
            email='hr_demo@techcorp.vn',
            password='Password123!',
            role=User.ROLE_HR,
            first_name='Thu Hà',
            last_name='Trần Thị',
            company_name='TechCorp Vietnam'
        )

        # Candidate User
        self.candidate_user = User.objects.create_user(
            username='candidate_test',
            email='candidate@example.com',
            password='Password123!',
            role=User.ROLE_CANDIDATE
        )

        # Job 1: AI / Python Focus
        self.job_ai = JobPosting.objects.create(
            hr=self.hr_user,
            title='Senior AI / Python Engineer',
            required_skills='Python, PyTorch, Sentence-BERT, Machine Learning, Scikit-Learn',
            description='Tuyển dụng Kỹ sư AI phát triển các mô hình xử lý ngôn ngữ tự nhiên NLP và Sentence-BERT.',
            min_experience=3,
            location='Hà Nội'
        )

        # Job 2: Web / Frontend Focus
        self.job_web = JobPosting.objects.create(
            hr=self.hr_user,
            title='Frontend React / Tailwind Developer',
            required_skills='React.js, Vue.js, TailwindCSS, JavaScript, HTML, CSS',
            description='Tuyển dụng Lập trình viên Frontend phát triển giao diện Web React và TailwindCSS.',
            min_experience=1,
            location='TP. Hồ Chí Minh'
        )

    def test_user_role_properties(self):
        """Kiểm tra helper properties của 3-Tier RBAC (is_admin, is_hr, is_candidate)."""
        self.assertTrue(self.admin_user.is_admin)
        self.assertFalse(self.admin_user.is_candidate)

        self.assertTrue(self.hr_user.is_hr)
        self.assertFalse(self.hr_user.is_candidate)
        self.assertFalse(self.hr_user.is_admin)

        self.assertTrue(self.candidate_user.is_candidate)
        self.assertFalse(self.candidate_user.is_hr)
        self.assertFalse(self.candidate_user.is_admin)

    def test_hr_multi_job_screening_access_control(self):
        """Đảm bảo Candidate không thể vào trang Multi-Job Screening (Decorator check)."""
        self.client.login(username='candidate_test', password='Password123!')
        response = self.client.get(reverse('jobs:hr_multi_job_screening'), follow=True)
        self.assertRedirects(response, reverse('jobs:job_list'))
        self.assertContains(response, 'Truy cập bị từ chối')

        # HR login ok
        self.client.logout()
        self.client.login(username='hr_demo_test', password='Password123!')
        response = self.client.get(reverse('jobs:hr_multi_job_screening'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sàng Lọc CV Đa Vị Trí')

    def test_cross_job_screening_evaluation(self):
        """Kiểm tra AI Cross-Job Evaluation chọn Job điểm cao nhất cho CV AI/Python."""
        self.client.login(username='hr_demo_test', password='Password123!')

        sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sample_cvs', 'CV_01_Nguyen_Van_An_Senior_AI_NLP.pdf')
        with open(sample_path, 'rb') as f:
            cv_file = SimpleUploadedFile("CV_Nguyen_Van_An_AI.pdf", f.read(), content_type="application/pdf")

        response = self.client.post(reverse('jobs:hr_multi_job_screening'), {
            'job_ids': [self.job_ai.id, self.job_web.id],
            'cv_files': [cv_file]
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ma Trận So Khớp Đa Vị Trí')
        self.assertContains(response, 'Nguyen Van An')
        self.assertContains(response, 'PHÙ HỢP NHẤT')

        # Verify application created for best fit job (job_ai)
        app = Application.objects.filter(job=self.job_ai).first()
        self.assertIsNotNone(app)
        self.assertGreaterEqual(app.match_score, 50.0)
