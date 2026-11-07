import os, sys, django

sys.path.insert(0, r'd:\DDTTNT')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from jobs.models import JobPosting, Application

print("=== USERS ===")
for u in User.objects.all():
    print(f"User: id={u.id}, username='{u.username}', role='{u.role}', is_staff={u.is_staff}")

print("\n=== JOBS ===")
for j in JobPosting.objects.all():
    print(f"Job: id={j.id}, title='{j.title}', creator='{j.created_by.username}'")

print("\n=== APPLICATIONS ===")
for a in Application.objects.all()[:5]:
    print(f"App: id={a.id}, job_id={a.job_id}, candidate='{a.candidate.username}', total_score={a.total_score}")
