import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from jobs.models import JobPosting

def seed_accounts():
    print("Setting up Admin and HR demo accounts...")
    
    # 1. Create or update superuser 'admin'
    admin_user, admin_created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@airecruitment.vn',
            'first_name': 'Hệ Thống',
            'last_name': 'Quản Trị',
            'role': User.ROLE_ADMIN,
            'is_staff': True,
            'is_superuser': True,
        }
    )
    admin_user.role = User.ROLE_ADMIN
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.set_password('admin123')
    admin_user.save()
    admin_status = "Created" if admin_created else "Updated"
    print(f"{admin_status} Admin superuser 'admin' (password: admin123, role: admin).")

    # Update any other superusers to role='admin'
    admins = User.objects.filter(is_superuser=True)
    for adm in admins:
        if adm.role != User.ROLE_ADMIN:
            adm.role = User.ROLE_ADMIN
            adm.save()
            print(f"Updated superuser '{adm.username}' to role='admin'.")

    # 2. Create or update hr_demo account
    hr_user, created = User.objects.get_or_create(
        username='hr_demo',
        defaults={
            'email': 'hr_demo@techcorp.vn',
            'first_name': 'Thu Hà',
            'last_name': 'Trần Thị',
            'company_name': 'TechCorp Vietnam',
            'role': User.ROLE_HR,
            'is_staff': True,
        }
    )
    hr_user.set_password('hr123')
    hr_user.role = User.ROLE_HR
    hr_user.first_name = 'Thu Hà'
    hr_user.last_name = 'Trần Thị'
    hr_user.company_name = 'TechCorp Vietnam'
    hr_user.is_staff = True
    hr_user.save()
    
    status_str = "Created" if created else "Updated"
    print(f"{status_str} HR account 'hr_demo' (password: hr123, Company: TechCorp Vietnam).")

    # 3. Create or update candidate_demo account
    candidate_user, c_created = User.objects.get_or_create(
        username='candidate_demo',
        defaults={
            'email': 'an.nguyen@example.com',
            'first_name': 'Văn An',
            'last_name': 'Nguyễn',
            'phone_number': '0988123456',
            'role': User.ROLE_CANDIDATE,
        }
    )
    candidate_user.set_password('candidate123')
    candidate_user.role = User.ROLE_CANDIDATE
    candidate_user.first_name = 'Văn An'
    candidate_user.last_name = 'Nguyễn'
    candidate_user.phone_number = '0988123456'
    candidate_user.save()
    c_status = "Created" if c_created else "Updated"
    print(f"{c_status} Candidate account 'candidate_demo' (password: candidate123).")

    # 4. Assign existing jobs to hr_demo
    updated_jobs = JobPosting.objects.all().update(hr=hr_user)
    print(f"Assigned {updated_jobs} existing job postings to 'hr_demo'.")

if __name__ == '__main__':
    seed_accounts()
