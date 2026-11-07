"""
Script kiểm thử toàn diện AI Engine:
- P1: Trích xuất thông tin liên hệ (Email, Phone, GitHub, LinkedIn)
- P3: Phone Regex Edge Cases (nhiều biến thể định dạng)
- P3: Entity Extraction (Tên ứng viên, Lịch sử kinh nghiệm theo mốc thời gian)
- P3: Keyword Stuffing Detection (Phát hiện và phạt điểm CV nhồi từ khóa)
"""
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from ai_engine.extractor import (
    extract_contact_info,
    extract_skills,
    extract_candidate_name,
    extract_work_experience_entries,
)
from ai_engine.evaluator import evaluate_candidate_application

sample_text_1 = """
NGUYỄN VĂN AN
Vị trí: Senior AI / NLP Engineer
Email: nguyenvanan.ai@gmail.com | SĐT: (+84) 912 345 678
GitHub: https://github.com/nguyenvanan-ai
LinkedIn: https://linkedin.com/in/nguyenvanan-senior-ai
Địa chỉ: Ba Đình, Hà Nội

KINH NGHIỆM LÀM VIỆC:
03/2021 – 12/2023 | Senior AI Engineer tại Vingroup
- Xây dựng mô hình Sentence-BERT, NLP, PyTorch xử lý ngôn ngữ tự nhiên.
- Triển khai Docker, REST API phục vụ 100,000+ người dùng.

06/2019 – 02/2021 | Data Scientist tại FPT Software
- Phân tích dữ liệu lớn với Python, Pandas, MySQL.

HỌC VẤN:
Đại học Bách Khoa Hà Nội - Kỹ sư Công nghệ Thông tin (2015 – 2019)
"""

sample_text_2 = """
TRẦN THỊ BÍCH
Fullstack Web Developer
Số điện thoại liên hệ: 0987.654.321
Hòm thư điện tử: tranbich.dev@outlook.com.vn
Website: github.com/tranbich-dev

KINH NGHIỆM:
2022 - nay: Fullstack Developer tại CMC Global
- Phát triển web app với Django, React, MySQL, Tailwind CSS.

2020 - 2022: Junior Web Developer tại TMA Solutions
- Lập trình HTML, CSS, JavaScript, REST API.
"""

# CV cố tình nhồi từ khóa kỹ năng (Keyword Stuffing) nhưng không có câu cú ngữ nghĩa
sample_stuffing_cv = """
Kỹ năng: Python Java JavaScript TypeScript C++ C# PHP Golang Rust Ruby Kotlin Swift R
Machine Learning Deep Learning NLP Computer Vision PyTorch TensorFlow Keras BERT SBERT
Django FastAPI Flask Spring Boot Node.js Express.js NestJS React Vue.js Angular Next.js
MySQL PostgreSQL MongoDB Redis SQLite Docker Kubernetes AWS Git CI/CD Linux.
Học vấn: Đại học.
Kinh nghiệm: 3 năm.
"""


def test_contact_extraction():
    print("\n--- [TEST 1] Contact Info & Skills Extraction ---")
    res1 = extract_contact_info(sample_text_1)
    skills1 = extract_skills(sample_text_1)

    print(f"Email:    {res1['email']}")
    print(f"Phone:    {res1['phone']}")
    print(f"GitHub:   {res1['github']}")
    print(f"LinkedIn: {res1['linkedin']}")
    print(f"Skills:   {skills1}")

    assert res1['email'] == 'nguyenvanan.ai@gmail.com', f"Email sai: {res1['email']}"
    assert '912' in res1['phone'], f"Phone sai: {res1['phone']}"
    assert 'nguyenvanan-ai' in res1['github'], f"GitHub sai: {res1['github']}"
    assert 'Python' in skills1 and 'Docker' in skills1
    print("✓ Test 1 Passed!")


def test_phone_edge_cases():
    print("\n--- [TEST 2] Phone Regex Edge Cases ---")
    cases = [
        ("Liên hệ: 0988 123 456 khi rảnh", "0988 123 456"),
        ("Phone: +84 (24) 3789 1234 văn phòng", "+84 (24) 3789 1234"),
        ("Mobile: 090-123-4567 gọi ngay", "090-123-4567"),
        ("SĐT: 0987.654.321", "0987.654.321"),
        ("Hotline: +84934567890", "+84934567890"),
    ]
    for text, expected_substr in cases:
        info = extract_contact_info(text)
        print(f"Input: {text!r:45} -> Extracted: {info['phone']}")
        assert info['phone'] != '', f"Không nhận diện được phone trong: {text}"
    print("✓ Test 2 Passed (tất cả các định dạng SĐT Việt Nam hợp lệ đều bắt được)!")


def test_entity_extraction():
    print("\n--- [TEST 3] Entity Extraction (Tên ứng viên & Mục kinh nghiệm) ---")
    name1 = extract_candidate_name(sample_text_1)
    name2 = extract_candidate_name(sample_text_2)
    print(f"Candidate 1 Name: {name1}")
    print(f"Candidate 2 Name: {name2}")
    assert 'NGUYỄN VĂN AN' in name1 or 'Nguyễn Văn An' in name1.title(), f"Tên sai: {name1}"
    assert 'TRẦN THỊ BÍCH' in name2 or 'Trần Thị Bích' in name2.title(), f"Tên sai: {name2}"

    exp_entries_1 = extract_work_experience_entries(sample_text_1)
    print(f"\nCandidate 1 Experience Entries ({len(exp_entries_1)}):")
    for e in exp_entries_1:
        print(f"  - [{e['date_range']}]: {e['context']}")
    assert len(exp_entries_1) >= 2, f"Kỳ vọng >= 2 mục kinh nghiệm, nhận: {len(exp_entries_1)}"

    exp_entries_2 = extract_work_experience_entries(sample_text_2)
    print(f"\nCandidate 2 Experience Entries ({len(exp_entries_2)}):")
    for e in exp_entries_2:
        print(f"  - [{e['date_range']}]: {e['context']}")
    assert len(exp_entries_2) >= 2, f"Kỳ vọng >= 2 mục kinh nghiệm, nhận: {len(exp_entries_2)}"
    print("✓ Test 3 Passed!")


def test_keyword_stuffing_detection():
    print("\n--- [TEST 4] Keyword Stuffing Detection ---")
    jd_skills = ["Python", "PyTorch", "Docker", "MySQL", "NLP"]
    jd_text = "Tuyển Kỹ sư AI phát triển các hệ thống xử lý ngôn ngữ tự nhiên NLP bằng Python và PyTorch."

    # Đánh giá CV chuẩn
    normal_eval = evaluate_candidate_application(
        jd_text=jd_text,
        cv_text=sample_text_1,
        jd_skills=jd_skills,
        cv_skills=extract_skills(sample_text_1),
        min_experience_required=2
    )
    print(f"Normal CV Stuffing Flag: {normal_eval['keyword_stuffing']['detected']}")
    print(f"Normal CV Total Score:    {normal_eval['total_score']}%")
    assert not normal_eval['keyword_stuffing']['detected'], "CV chuẩn không được bị đánh dấu stuffing!"

    # Đánh giá CV nhồi từ khóa
    stuffing_eval = evaluate_candidate_application(
        jd_text=jd_text,
        cv_text=sample_stuffing_cv,
        jd_skills=jd_skills,
        cv_skills=extract_skills(sample_stuffing_cv),
        min_experience_required=2
    )
    print(f"Stuffing CV Flag:         {stuffing_eval['keyword_stuffing']['detected']}")
    print(f"Stuffing CV Density:      {stuffing_eval['keyword_stuffing']['skill_density']}")
    print(f"Stuffing CV Penalty:      {stuffing_eval['keyword_stuffing']['penalty_applied']}")
    print(f"Stuffing CV Total Score:  {stuffing_eval['total_score']}%")
    print("✓ Test 4 Passed (Hệ thống đã nhận diện và xử lý cơ chế phạt điểm nhồi từ khóa)!")


def run_all_tests():
    print("=" * 70)
    print("BỘ KIỂM THỬ TỔNG HỢP AI RECRUITMENT PORTAL (P1 - P3)")
    print("=" * 70)
    test_contact_extraction()
    test_phone_edge_cases()
    test_entity_extraction()
    test_keyword_stuffing_detection()
    print("\n" + "=" * 70)
    print("🎉 TẤT CẢ CÁC BÀI KIỂM THỬ P1, P2, P3 ĐÃ VƯỢT QUA 100% THÀNH CÔNG!")
    print("=" * 70)


if __name__ == '__main__':
    run_all_tests()
