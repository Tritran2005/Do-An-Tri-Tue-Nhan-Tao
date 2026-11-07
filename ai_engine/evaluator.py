import re
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
from .matcher import calculate_semantic_similarity, match_skills

logger = logging.getLogger(__name__)

# ==============================================================================
# HỆ THỐNG TRỌNG SỐ ĐA TIÊU CHÍ (MULTI-CRITERIA SCORING WEIGHTS)
# ==============================================================================
# S_total = (0.35 * skill_score) + (0.25 * semantic_score) + (0.25 * experience_score) + (0.15 * education_score)
DEFAULT_WEIGHTS = {
    'skill': 0.35,        # 35% Điểm kỹ năng khớp thực tế (Skill Matching)
    'semantic': 0.25,     # 25% Điểm tương đồng ngữ nghĩa toàn diện (Sentence-BERT)
    'experience': 0.25,   # 25% Điểm kinh nghiệm làm việc (Experience)
    'education': 0.15,    # 15% Điểm trình độ học vấn (Education)
}


# ==============================================================================
# BÓC TÁCH & ĐÁNH GIÁ KINH NGHIỆM (EXPERIENCE SCORER)
# ==============================================================================
def extract_years_of_experience(cv_text: str) -> int:
    """
    Sử dụng Regex bóc tách số năm kinh nghiệm làm việc từ văn bản CV.
    Ví dụ: '3+ năm kinh nghiệm', '5 years of experience', '2 năm làm việc'.
    """
    if not cv_text:
        return 0

    patterns = [
        r'(?:hơn|trên|tổng|over)?\s*(\d+)\+?\s*(?:năm|years?)\s*(?:kinh nghiệm|làm việc|experience|kn)',
        r'(?:kinh nghiệm|experience)\s*[:\-\s]*(?:hơn|trên|over)?\s*(\d+)\+?\s*(?:năm|years?)',
        r'(\d+)\+?\s*(?:năm|years?)\s*(?:ở vị trí|làm tại)',
    ]

    found_years = []
    for pat in patterns:
        matches = re.findall(pat, cv_text, re.IGNORECASE)
        for m in matches:
            # Lấy nhóm chữ số trong tuple kết quả
            for item in m:
                if item.isdigit():
                    val = int(item)
                    if 0 < val <= 35:  # Giới hạn số năm thực tế hợp lý
                        found_years.append(val)

    if found_years:
        return max(found_years)
    return 1  # Giá trị ngầm định 1 năm nếu CV có đề cập dự án


def calculate_experience_score(
    min_experience_required: int,
    candidate_experience: Optional[int] = None,
    cv_text: str = ""
) -> Tuple[float, int]:
    """
    Tính điểm kinh nghiệm (0 - 100%).
    - Nếu JD không yêu cầu kinh nghiệm (Fresher / 0 năm): Đạt 100%.
    - Nếu ứng viên >= kinh nghiệm yêu cầu: Đạt 100%.
    - Nếu ứng viên < kinh nghiệm yêu cầu: Tính theo tỷ lệ phần trăm (sàn 35%).
    """
    if candidate_experience is None:
        candidate_experience = extract_years_of_experience(cv_text)

    if min_experience_required <= 0:
        return 100.0, candidate_experience

    if candidate_experience >= min_experience_required:
        return 100.0, candidate_experience
    else:
        # Tỷ lệ so với yêu cầu, có điểm sàn động
        ratio = candidate_experience / min_experience_required
        score = max(35.0, min(95.0, ratio * 100.0))
        return round(score, 2), candidate_experience


# ==============================================================================
# BÓC TÁCH & ĐÁNH GIÁ HỌC VẤN (EDUCATION SCORER)
# ==============================================================================
def calculate_education_score(cv_text: str) -> Tuple[float, str]:
    """
    Nhận diện trình độ học vấn trong CV và cho điểm chuẩn hóa (0 - 100%):
    - Tiến sĩ (PhD / Doctorate): 100%
    - Thạc sĩ (Master): 90%
    - Đại học / Kỹ sư / Cử nhân (Bachelor / Engineer): 85%
    - Cao đẳng (College / Associate): 70%
    - Khác / Baseline: 75%
    """
    if not cv_text:
        return 75.0, "Không xác định"

    cv_lower = cv_text.lower()

    if re.search(r'\b(tiến sĩ|phd|doctorate)\b', cv_lower):
        return 100.0, "Tiến sĩ (PhD)"
    elif re.search(r'\b(thạc sĩ|master|cao học|msc|mba)\b', cv_lower):
        return 90.0, "Thạc sĩ (Master)"
    elif re.search(r'\b(đại học|cử nhân|kỹ sư|bachelor|b\.s|b\.a|university)\b', cv_lower):
        return 85.0, "Đại học / Kỹ sư (Bachelor)"
    elif re.search(r'\b(cao đẳng|college|associate)\b', cv_lower):
        return 70.0, "Cao đẳng (College)"
    else:
        return 80.0, "Đạt yêu cầu cơ bản"


# ==============================================================================
# 3. HÀM TÍNH ĐIỂM TỔNG HỢP ĐA TIÊU CHÍ (MULTI-CRITERIA EVALUATION PIPELINE)
# ==============================================================================
def calculate_total_score(
    skill_score: float,
    semantic_score: float,
    experience_score: float,
    education_score: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Tính điểm tổng hợp S_total theo công thức trọng số chuẩn hóa:
    S_total = (w1 * skill) + (w2 * semantic) + (w3 * exp) + (w4 * edu)
    """
    w = weights or DEFAULT_WEIGHTS
    total = (
        (w['skill'] * skill_score) +
        (w['semantic'] * semantic_score) +
        (w['experience'] * experience_score) +
        (w['education'] * education_score)
    )
    return round(total, 2)


def evaluate_candidate_application(
    jd_text: str,
    cv_text: str,
    jd_skills: Union[List[str], str],
    cv_skills: Union[List[str], str],
    min_experience_required: int = 0,
    candidate_experience: Optional[int] = None,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Hàm Orchestrator trung tâm thực thi trọn vẹn quy trình AI Matching & XAI Scoring.

    Quy trình:
    1. So khớp kỹ năng & bóc tách Matched/Missing Skills qua toán tử tập hợp.
    2. Đo lường độ tương đồng ngữ nghĩa bằng Sentence-BERT Cosine Similarity.
    3. Chấm điểm kinh nghiệm làm việc.
    4. Chấm điểm trình độ học vấn.
    5. Tính điểm tổng hợp đa tiêu chí S_total.

    Returns:
        Dict: Toàn bộ báo cáo XAI gồm điểm thành phần, điểm tổng và các danh sách kỹ năng.
    """
    w = weights or DEFAULT_WEIGHTS

    # 1. Skill Matching
    skill_result = match_skills(jd_skills=jd_skills, cv_skills=cv_skills)
    skill_score = skill_result["skill_score"]

    # 2. Semantic Similarity (Sentence-BERT)
    semantic_score = calculate_semantic_similarity(jd_text=jd_text, cv_text=cv_text)

    # 3. Experience Score
    exp_score, detected_years = calculate_experience_score(
        min_experience_required=min_experience_required,
        candidate_experience=candidate_experience,
        cv_text=cv_text
    )

    # 4. Education Score
    edu_score, detected_degree = calculate_education_score(cv_text=cv_text)

    # 5. Total Multi-Criteria Score
    total_score = calculate_total_score(
        skill_score=skill_score,
        semantic_score=semantic_score,
        experience_score=exp_score,
        education_score=edu_score,
        weights=w
    )

    # Đánh giá xếp loại hồ sơ
    if total_score >= 80.0:
        ranking_tier = "Xuất sắc (Highly Recommended)"
        badge_color = "emerald"
    elif total_score >= 65.0:
        ranking_tier = "Tiềm năng (Recommended)"
        badge_color = "blue"
    elif total_score >= 50.0:
        ranking_tier = "Trung bình (Consider)"
        badge_color = "amber"
    else:
        ranking_tier = "Chưa phù hợp (Low Match)"
        badge_color = "rose"

    # ==================================================================
    # P3 – KEYWORD STUFFING DETECTION
    # Phát hiện CV nhồi từ khóa (kỹ năng liệt kê dày đặc, thiếu ngữ cảnh)
    # ==================================================================
    stuffing_detected = False
    stuffing_penalty_applied = False
    adjusted_skill_score = skill_score

    matched_skills_list = skill_result["matched_skills"]
    word_count = len(cv_text.split()) if cv_text else 1
    skill_density = len(matched_skills_list) / max(1, word_count)

    # Ngưỡng: >15% từ trong CV là kỹ năng VÀ điểm ngữ nghĩa thấp (<40%)
    # → CV rất có thể chỉ là "danh sách kỹ năng", không có nội dung thực chất
    STUFFING_DENSITY_THRESHOLD = 0.15
    STUFFING_SEMANTIC_THRESHOLD = 40.0
    STUFFING_PENALTY_FACTOR = 0.70  # Giảm 30% điểm kỹ năng

    if skill_density > STUFFING_DENSITY_THRESHOLD and semantic_score < STUFFING_SEMANTIC_THRESHOLD:
        stuffing_detected = True
        adjusted_skill_score = round(skill_score * STUFFING_PENALTY_FACTOR, 2)
        stuffing_penalty_applied = True
        logger.warning(
            f"[Keyword Stuffing] Phát hiện CV nhồi từ khóa! "
            f"Mật độ kỹ năng={skill_density:.3f} (>{STUFFING_DENSITY_THRESHOLD}), "
            f"Semantic={semantic_score:.1f}% (<{STUFFING_SEMANTIC_THRESHOLD}%). "
            f"Điểm kỹ năng bị phạt: {skill_score} → {adjusted_skill_score}"
        )

    # Tính lại tổng điểm nếu có phạt
    if stuffing_penalty_applied:
        total_score = calculate_total_score(
            skill_score=adjusted_skill_score,
            semantic_score=semantic_score,
            experience_score=exp_score,
            education_score=edu_score,
            weights=w
        )
        # Cập nhật ranking tier sau khi phạt
        if total_score >= 80.0:
            ranking_tier = "Xuất sắc (Highly Recommended)"
            badge_color = "emerald"
        elif total_score >= 65.0:
            ranking_tier = "Tiềm năng (Recommended)"
            badge_color = "blue"
        elif total_score >= 50.0:
            ranking_tier = "Trung bình (Consider)"
            badge_color = "amber"
        else:
            ranking_tier = "Chưa phù hợp (Low Match)"
            badge_color = "rose"

    return {
        "total_score": total_score,
        "ranking_tier": ranking_tier,
        "badge_color": badge_color,
        "scores": {
            "skill_score": adjusted_skill_score,
            "raw_skill_score": skill_score,         # Điểm kỹ năng gốc trước khi áp phạt
            "semantic_score": semantic_score,
            "experience_score": exp_score,
            "education_score": edu_score,
        },
        "weights": w,
        "skills_breakdown": {
            "matched_skills": skill_result["matched_skills"],
            "missing_skills": skill_result["missing_skills"],
            "additional_skills": skill_result["additional_skills"],
            "match_ratio": skill_result["match_ratio"],
            "total_required": skill_result["total_required"],
            "total_matched": skill_result["total_matched"],
        },
        "keyword_stuffing": {
            "detected": stuffing_detected,
            "skill_density": round(skill_density, 4),
            "penalty_applied": stuffing_penalty_applied,
            "penalty_factor": STUFFING_PENALTY_FACTOR if stuffing_penalty_applied else 1.0,
        },
        "meta": {
            "candidate_experience_years": detected_years,
            "min_experience_required": min_experience_required,
            "candidate_education_degree": detected_degree,
        }
    }
