from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsAuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.candidate_user = User.objects.create_user(
            username='candidate_user',
            email='candidate@example.com',
            password='Password123!',
            role=User.ROLE_CANDIDATE,
            first_name='Nguyen',
            last_name='An'
        )
        self.hr_user = User.objects.create_user(
            username='hr_user',
            email='hr@example.com',
            password='Password123!',
            role=User.ROLE_HR,
            first_name='Tran',
            last_name='Binh',
            company_name='TechCorp Vietnam'
        )

    def test_custom_user_roles(self):
        """Kiểm tra thuộc tính role và helper methods của Custom User Model."""
        self.assertEqual(self.candidate_user.role, 'candidate')
        self.assertTrue(self.candidate_user.is_candidate)
        self.assertFalse(self.candidate_user.is_hr)

        self.assertEqual(self.hr_user.role, 'hr')
        self.assertTrue(self.hr_user.is_hr)
        self.assertFalse(self.hr_user.is_candidate)

    def test_password_is_hashed_securely(self):
        """Đảm bảo mật khẩu không lưu plaintext mà được hash an toàn."""
        self.assertNotEqual(self.candidate_user.password, 'Password123!')
        self.assertTrue(self.candidate_user.check_password('Password123!'))

    def test_candidate_login_redirect(self):
        """Ứng viên đăng nhập phải được chuyển hướng về trang Job Board."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'candidate_user',
            'password': 'Password123!'
        }, follow=True)
        self.assertRedirects(response, reverse('jobs:job_list'))
        self.assertContains(response, 'Sàn Tuyển Dụng AI')

    def test_hr_login_redirect(self):
        """Nhà tuyển dụng đăng nhập phải được chuyển hướng về trang HR Dashboard."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'hr_user',
            'password': 'Password123!'
        }, follow=True)
        self.assertRedirects(response, reverse('jobs:hr_dashboard'))
        self.assertContains(response, 'Quản Lý Tin Tuyển Dụng')
        self.assertContains(response, 'TechCorp Vietnam')

    def test_register_candidate(self):
        """Kiểm tra luồng đăng ký ứng viên mới."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'new_candidate',
            'first_name': 'Le',
            'last_name': 'Hoa',
            'email': 'hoa.le@example.com',
            'role': 'candidate',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }, follow=True)
        self.assertRedirects(response, reverse('jobs:job_list'))
        new_user = User.objects.get(username='new_candidate')
        self.assertEqual(new_user.role, 'candidate')
        self.assertTrue(new_user.check_password('StrongPass123!'))

    def test_register_hr_requires_company_name(self):
        """HR đăng ký mà thiếu tên công ty thì form phải báo lỗi."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'new_hr',
            'first_name': 'Pham',
            'last_name': 'Cuong',
            'email': 'cuong.pham@example.com',
            'role': 'hr',
            'company_name': '',  # Bỏ trống
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertFormError(response.context['form'], 'company_name', 'Nhà tuyển dụng vui lòng nhập Tên công ty / tổ chức.')

    def test_role_access_control(self):
        """Kiểm tra quyền truy cập chéo giữa Candidate và HR."""
        # Đăng nhập bằng tài khoản Candidate
        self.client.login(username='candidate_user', password='Password123!')
        
        # Candidate cố truy cập HR Dashboard -> Bị từ chối và đẩy về trang Job Board
        response = self.client.get(reverse('jobs:hr_dashboard'), follow=True)
        self.assertRedirects(response, reverse('jobs:job_list'))
        self.assertContains(response, 'Truy cập bị từ chối')

        # Đăng xuất
        self.client.logout()

        # Đăng nhập bằng tài khoản HR
        self.client.login(username='hr_user', password='Password123!')
        
        # HR cố truy cập trang dành riêng cho Candidate (nếu có) -> bảo vệ decorator
        response = self.client.get(reverse('accounts:job_board'), follow=True)
        self.assertRedirects(response, reverse('jobs:hr_dashboard'))
        self.assertContains(response, 'Truy cập bị từ chối')
