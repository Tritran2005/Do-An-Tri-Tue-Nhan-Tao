import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ai_engine.parser import extract_text_from_file
from ai_engine.extractor import extract_skills, extract_contact_info
from ai_engine.evaluator import evaluate_candidate_application
from jobs.models import JobPosting

def test_all_sample_cvs():
    job1 = JobPosting.objects.get(id=1) # Senior AI
    job2 = JobPosting.objects.get(id=2) # Fullstack
    
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_cvs')
    files = sorted([f for f in os.listdir(sample_dir) if f.endswith(('.pdf', '.docx'))])

    print("\n" + "="*80)
    print(f"TESTING {len(files)} SAMPLE CVS AGAINST JOB 1: '{job1.title}'")
    print(f"Required Skills: {job1.required_skills} | Min Exp: {job1.min_experience} years")
    print("="*80)

    for f in files:
        path = os.path.join(sample_dir, f)
        text = extract_text_from_file(path)
        skills = extract_skills(text)
        contact = extract_contact_info(text)
        res = evaluate_candidate_application(
            jd_text=job1.description,
            cv_text=text,
            jd_skills=job1.required_skills,
            cv_skills=skills,
            min_experience_required=job1.min_experience
        )
        print(f"\n[FILE]: {f}")
        print(f" -> Contact: Email={contact.get('email') or 'N/A'} | Phone={contact.get('phone') or 'N/A'}")
        print(f" -> Total Match Score: {res['total_score']}% ({res['ranking_tier']})")
        print(f" -> Breakdown: Skill={res['scores']['skill_score']}%, S-BERT={res['scores']['semantic_score']}%, Exp={res['scores']['experience_score']}%, Edu={res['scores']['education_score']}%")
        print(f" -> Matched Skills ({len(res['skills_breakdown']['matched_skills'])}): {res['skills_breakdown']['matched_skills']}")
        print(f" -> Missing Skills ({len(res['skills_breakdown']['missing_skills'])}): {res['skills_breakdown']['missing_skills']}")

    print("\n" + "="*80)
    print(f"TESTING {len(files)} SAMPLE CVS AGAINST JOB 2: '{job2.title}'")
    print(f"Required Skills: {job2.required_skills} | Min Exp: {job2.min_experience} years")
    print("="*80)

    for f in files:
        path = os.path.join(sample_dir, f)
        text = extract_text_from_file(path)
        skills = extract_skills(text)
        res = evaluate_candidate_application(
            jd_text=job2.description,
            cv_text=text,
            jd_skills=job2.required_skills,
            cv_skills=skills,
            min_experience_required=job2.min_experience
        )
        print(f"\n[FILE]: {f}")
        print(f" -> Total Match Score: {res['total_score']}% ({res['ranking_tier']})")
        print(f" -> Breakdown: Skill={res['scores']['skill_score']}%, S-BERT={res['scores']['semantic_score']}%, Exp={res['scores']['experience_score']}%, Edu={res['scores']['education_score']}%")
        print(f" -> Matched Skills ({len(res['skills_breakdown']['matched_skills'])}): {res['skills_breakdown']['matched_skills']}")
        print(f" -> Missing Skills ({len(res['skills_breakdown']['missing_skills'])}): {res['skills_breakdown']['missing_skills']}")

if __name__ == '__main__':
    test_all_sample_cvs()
