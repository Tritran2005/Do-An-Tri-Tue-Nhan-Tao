from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import JobPosting

User = get_user_model()

class JobPostingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.hr_user_1 = User.objects.create_user(
            username='hr_john',
            email='john@techcorp.com',
            password='Password123!',
            role='hr',
            company_name='TechCorp Vietnam'
        )
        self.hr_user_2 = User.objects.create_user(
            username='hr_sarah',
            email='sarah@innovate.com',
            password='Password123!',
            role='hr',
            company_name='Innovate Labs'
        )
        self.candidate_user = User.objects.create_user(
            username='candidate_bob',
            email='bob@dev.com',
            password='Password123!',
            role='candidate'
        )

        self.job_1 = JobPosting.objects.create(
            hr=self.hr_user_1,
            title='AI Engineer',
            description='Build NLP models using Sentence-BERT.',
            required_skills='Python, PyTorch, Sentence-BERT, MySQL',
            min_experience=2,
            location='Hà Nội',
            salary_range='30 - 45 triệu',
            job_type='Full-time',
            is_active=True
        )

    def test_job_skills_list_extraction(self):
        """Kiểm tra phương thức get_skills_list bóc tách chuỗi kỹ năng thành list chuẩn hóa."""
        skills = self.job_1.get_skills_list()
        self.assertEqual(skills, ['Python', 'PyTorch', 'Sentence-BERT', 'MySQL'])

    def test_public_job_board_accessible_by_guest(self):
        """Khách vãng lai và ứng viên có thể xem danh sách bài tuyển dụng công khai."""
        response = self.client.get(reverse('jobs:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Engineer')
        self.assertContains(response, 'TechCorp Vietnam')

    def test_job_detail_public(self):
        """Trang chi tiết JD có thể xem công khai."""
        response = self.client.get(reverse('jobs:job_detail', kwargs={'pk': self.job_1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Build NLP models using Sentence-BERT.')
        self.assertContains(response, 'Python')

    def test_candidate_cannot_access_hr_dashboard(self):
        """Ứng viên cố truy cập HR Dashboard phải bị chặn và chuyển hướng."""
        self.client.login(username='candidate_bob', password='Password123!')
        response = self.client.get(reverse('jobs:hr_dashboard'), follow=True)
        self.assertRedirects(response, reverse('jobs:job_list'))
        self.assertContains(response, 'Truy cập bị từ chối')

    def test_hr_can_create_job(self):
        """Nhà tuyển dụng có thể tạo mới tin tuyển dụng."""
        self.client.login(username='hr_john', password='Password123!')
        response = self.client.post(reverse('jobs:job_create'), {
            'title': 'Django Backend Lead',
            'required_skills': 'Django, Python, PostgreSQL, Redis',
            'min_experience': 4,
            'salary_range': '40 - 60 triệu',
            'location': 'TP. Hồ Chí Minh',
            'job_type': 'Full-time',
            'description': 'Lead backend development team for SaaS platform.',
            'is_active': True,
        }, follow=True)
        self.assertRedirects(response, reverse('jobs:hr_dashboard'))
        self.assertTrue(JobPosting.objects.filter(title='Django Backend Lead').exists())

    def test_hr_cannot_edit_other_hr_job(self):
        """HR này không được phép chỉnh sửa bài đăng của HR khác."""
        self.client.login(username='hr_sarah', password='Password123!')
        response = self.client.get(reverse('jobs:job_update', kwargs={'pk': self.job_1.pk}), follow=True)
        self.assertRedirects(response, reverse('jobs:hr_dashboard'))
        self.assertContains(response, 'Bạn không có quyền chỉnh sửa bài tuyển dụng của nhà tuyển dụng khác.')

    def test_ai_skill_extractor(self):
        """Kiểm tra AI Extractor bóc tách đúng danh sách kỹ năng chuẩn hóa từ văn bản thô."""
        from ai_engine.extractor import extract_skills
        text = "Lập trình viên thành thạo Python, Django, MySQL, Docker và mô hình Sentence-BERT. Biết thêm React."
        skills = extract_skills(text)
        self.assertIn('Python', skills)
        self.assertIn('Django', skills)
        self.assertIn('MySQL', skills)
        self.assertIn('Docker', skills)
        self.assertIn('Sentence-BERT', skills)
        self.assertIn('React', skills)
        self.assertNotIn('Java', skills)

    def test_candidate_apply_cv_workflow(self):
        """Ứng viên nộp CV (.docx): hệ thống tự động bóc tách text và trích xuất kỹ năng."""
        import io
        import docx
        from django.core.files.uploadedfile import SimpleUploadedFile
        from .models import Application

        # Tạo file DOCX trong bộ nhớ RAM
        doc = docx.Document()
        doc.add_heading('Le Van C - AI Engineer Resume', 0)
        doc.add_paragraph('Experienced in Python, PyTorch, and Sentence-BERT for text matching and NLP.')
        doc.add_paragraph('Database: MySQL, Redis. Tools: Docker, Git.')
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        uploaded_file = SimpleUploadedFile(
            name='candidate_resume.docx',
            content=buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

        self.client.login(username='candidate_bob', password='Password123!')
        response = self.client.post(
            reverse('jobs:job_apply', kwargs={'pk': self.job_1.pk}),
            {'cv_file': uploaded_file},
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        app = Application.objects.get(job=self.job_1, candidate=self.candidate_user)
        self.assertTrue(len(app.parsed_text) > 0)
        self.assertIn('Python', app.parsed_text)
        self.assertIn('Sentence-BERT', app.parsed_text)

        # Kiểm tra kỹ năng được trích xuất tự động vào JSONField
        self.assertIn('Python', app.extracted_skills)
        self.assertIn('PyTorch', app.extracted_skills)
        self.assertIn('Sentence-BERT', app.extracted_skills)
        self.assertIn('MySQL', app.extracted_skills)
        self.assertIn('Docker', app.extracted_skills)

        # Kiểm tra điểm số đa tiêu chí đã được tính toán tự động
        self.assertGreater(app.total_score, 0.0)
        self.assertGreater(app.skill_score, 0.0)
        self.assertGreater(app.semantic_score, 0.0)

    def test_skill_matcher_and_xai_sets(self):
        """Kiểm tra toán tử tập hợp matched_skills và missing_skills."""
        from ai_engine.matcher import match_skills
        jd_skills = ['Python', 'Django', 'MySQL', 'Docker', 'Kubernetes']
        cv_skills = ['Python', 'MySQL', 'React', 'Git']

        result = match_skills(jd_skills, cv_skills)
        self.assertEqual(result['matched_skills'], ['MySQL', 'Python'])
        self.assertEqual(result['missing_skills'], ['Django', 'Docker', 'Kubernetes'])
        self.assertEqual(result['additional_skills'], ['Git', 'React'])
        # 2 / 5 = 40.0%
        self.assertEqual(result['skill_score'], 40.0)

    def test_multi_criteria_scoring_formula(self):
        """Kiểm tra công thức trọng số chuẩn S_total = (0.35*skill) + (0.25*semantic) + (0.25*exp) + (0.15*edu)."""
        from ai_engine.evaluator import calculate_total_score
        # Giả sử: skill=80, semantic=70, exp=90, edu=85
        # S_total = (0.35 * 80) + (0.25 * 70) + (0.25 * 90) + (0.15 * 85)
        # S_total = 28 + 17.5 + 22.5 + 12.75 = 80.75
        total = calculate_total_score(
            skill_score=80.0,
            semantic_score=70.0,
            experience_score=90.0,
            education_score=85.0
        )
        self.assertEqual(total, 80.75)

    def test_hr_job_candidates_sorting_by_match_score_descending(self):
        """Kiểm tra danh sách ứng viên trong HR Dashboard tự động sắp xếp giảm dần theo match_score."""
        from .models import Application
        cand_1 = User.objects.create_user(username='cand_low', password='Password123!', role='candidate')
        cand_2 = User.objects.create_user(username='cand_high', password='Password123!', role='candidate')
        cand_3 = User.objects.create_user(username='cand_mid', password='Password123!', role='candidate')

        app_low = Application.objects.create(
            job=self.job_1,
            candidate=cand_1,
            match_score=52.0,
            total_score=52.0,
            skill_score=40.0,
            semantic_score=50.0,
            matched_skills=['Python'],
            missing_skills=['PyTorch', 'Sentence-BERT', 'MySQL']
        )
        app_high = Application.objects.create(
            job=self.job_1,
            candidate=cand_2,
            match_score=94.5,
            total_score=94.5,
            skill_score=100.0,
            semantic_score=90.0,
            matched_skills=['Python', 'PyTorch', 'Sentence-BERT', 'MySQL'],
            missing_skills=[]
        )
        app_mid = Application.objects.create(
            job=self.job_1,
            candidate=cand_3,
            match_score=76.0,
            total_score=76.0,
            skill_score=75.0,
            semantic_score=70.0,
            matched_skills=['Python', 'MySQL'],
            missing_skills=['PyTorch', 'Sentence-BERT']
        )

        self.client.login(username='hr_john', password='Password123!')
        response = self.client.get(reverse('jobs:hr_job_candidates', kwargs={'pk': self.job_1.pk}))
        self.assertEqual(response.status_code, 200)

        # Kiểm tra danh sách được trả về theo thứ tự giảm dần chính xác
        applications = list(response.context['applications'])
        self.assertEqual(applications[0].pk, app_high.pk)
        self.assertEqual(applications[0].match_score, 94.5)
        self.assertEqual(applications[1].pk, app_mid.pk)
        self.assertEqual(applications[1].match_score, 76.0)
        self.assertEqual(applications[2].pk, app_low.pk)
        self.assertEqual(applications[2].match_score, 52.0)

        # Kiểm tra hiển thị tag XAI trên HTML
        self.assertContains(response, 'TOP 1 KHUYẾN NGHỊ')
        self.assertContains(response, '94.5%')
        self.assertContains(response, 'Kỹ năng đã khớp')
        self.assertContains(response, 'Kỹ năng còn thiếu')

    def test_hr_cannot_view_other_hr_job_candidates(self):
        """HR không được phép xem bảng xếp hạng ứng viên của HR khác."""
        self.client.login(username='hr_sarah', password='Password123!')
        response = self.client.get(reverse('jobs:hr_job_candidates', kwargs={'pk': self.job_1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('jobs:hr_dashboard'))

    def test_application_status_update_by_hr(self):
        """HR có thể cập nhật trạng thái ứng viên (pending -> accepted)."""
        from .models import Application
        cand = User.objects.create_user(username='cand_alex', password='Password123!', role='candidate')
        app = Application.objects.create(
            job=self.job_1,
            candidate=cand,
            match_score=85.0,
            status=Application.STATUS_PENDING
        )

        self.client.login(username='hr_john', password='Password123!')
        url = reverse('jobs:application_update_status', kwargs={'pk': app.pk})
        response = self.client.post(url, {'status': 'accepted'})
        self.assertEqual(response.status_code, 302)

        app.refresh_from_db()
        self.assertEqual(app.status, Application.STATUS_ACCEPTED)

    def test_candidate_my_applications_view(self):
        """Ứng viên có thể xem trang my-applications với điểm số và missing_skills."""
        from .models import Application
        app = Application.objects.create(
            job=self.job_1,
            candidate=self.candidate_user,
            match_score=78.5,
            total_score=78.5,
            matched_skills=['Python', 'MySQL'],
            missing_skills=['Sentence-BERT']
        )

        self.client.login(username='candidate_bob', password='Password123!')
        response = self.client.get(reverse('jobs:my_applications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '78.5%')
        self.assertContains(response, 'Sentence-BERT')
        self.assertContains(response, 'Gợi ý từ AI Career Coach')

    def test_hr_batch_update_status_success(self):
        """HR có thể cập nhật trạng thái hàng loạt cho nhiều ứng viên cùng lúc."""
        from .models import Application
        cand1 = User.objects.create_user(username='batch_cand1', password='Password123!', role='candidate')
        cand2 = User.objects.create_user(username='batch_cand2', password='Password123!', role='candidate')
        app1 = Application.objects.create(job=self.job_1, candidate=cand1, match_score=80.0, status='pending')
        app2 = Application.objects.create(job=self.job_1, candidate=cand2, match_score=75.0, status='pending')

        self.client.login(username='hr_john', password='Password123!')
        url = reverse('jobs:hr_batch_update_status', kwargs={'pk': self.job_1.pk})
        response = self.client.post(url, {
            'application_ids': [app1.id, app2.id],
            'new_status': 'accepted'
        })
        self.assertEqual(response.status_code, 302)

        app1.refresh_from_db()
        app2.refresh_from_db()
        self.assertEqual(app1.status, 'accepted')
        self.assertEqual(app2.status, 'accepted')

    def test_hr_batch_update_status_unauthorized(self):
        """HR không sở hữu job không thể cập nhật trạng thái hàng loạt."""
        from .models import Application
        cand = User.objects.create_user(username='batch_cand_unauth', password='Password123!', role='candidate')
        app = Application.objects.create(job=self.job_1, candidate=cand, match_score=80.0, status='pending')

        self.client.login(username='hr_sarah', password='Password123!')  # Sarah does not own job_1
        url = reverse('jobs:hr_batch_update_status', kwargs={'pk': self.job_1.pk})
        response = self.client.post(url, {
            'application_ids': [app.id],
            'new_status': 'accepted'
        })
        self.assertEqual(response.status_code, 302)
        app.refresh_from_db()
        self.assertEqual(app.status, 'pending')  # Status must remain unchanged

    def test_hr_batch_upload_cvs(self):
        """HR có thể tải lên tệp CV để AI tự động trích xuất và tính điểm."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from .models import Application
        import docx

        # Tạo file docx test trong memory
        doc = docx.Document()
        doc.add_paragraph("Kỹ sư Python có 3 năm kinh nghiệm làm việc với Django, MySQL và REST API.")
        doc.add_paragraph("Tốt nghiệp Đại học Bách Khoa Hà Nội.")
        import io
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)

        uploaded = SimpleUploadedFile("CV_Test_Candidate.docx", bio.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        self.client.login(username='hr_john', password='Password123!')
        url = reverse('jobs:hr_batch_upload_cvs', kwargs={'pk': self.job_1.pk})
        response = self.client.post(url, {'cv_files': [uploaded]})
        self.assertEqual(response.status_code, 302)

        # Kiểm tra application đã được tạo thành công
        app = Application.objects.filter(job=self.job_1, cv_file__icontains='CV_Test_Candidate').first()
        self.assertIsNotNone(app)
        self.assertGreater(app.match_score, 0.0)
        self.assertIn('Python', app.extracted_skills)




