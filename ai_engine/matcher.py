import os
import logging
from typing import List, Dict, Set, Union, Tuple
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

# ==============================================================================
# SINGLETON MODEL CACHE FOR SENTENCE-BERT
# ==============================================================================
# Tránh nạp lại model nặng vào RAM ở mỗi request, duy trì 1 instance duy nhất
_SBERT_MODEL: SentenceTransformer = None

def get_sentence_bert_model(model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2') -> SentenceTransformer:
    """
    Khởi tạo hoặc trả về Singleton instance của mô hình Sentence-BERT.
    Ưu tiên tải trực tiếp từ cache cục bộ (local_files_only) để loại bỏ độ trễ mạng.
    """
    global _SBERT_MODEL
    if _SBERT_MODEL is None:
        try:
            # Thử nạp từ cache cục bộ trước
            _SBERT_MODEL = SentenceTransformer(model_name, local_files_only=True)
            logger.info(f"Loaded Sentence-BERT model '{model_name}' from local cache.")
        except Exception:
            try:
                # Fallback nếu local_files_only chưa có
                _SBERT_MODEL = SentenceTransformer(model_name)
                logger.info(f"Loaded Sentence-BERT model '{model_name}' online.")
            except Exception as e:
                # Fallback model tiếng Anh nhẹ nếu model multilingual lỗi
                logger.warning(f"Could not load {model_name}, falling back to all-MiniLM-L6-v2: {e}")
                _SBERT_MODEL = SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True)
    return _SBERT_MODEL


# ==============================================================================
# 1. SEMANTIC MATCHING (SENTENCE-BERT COSINE SIMILARITY)
# ==============================================================================
def calculate_semantic_similarity(jd_text: str, cv_text: str) -> float:
    """
    Tính độ tương đồng ngữ nghĩa (Semantic Matching Score) giữa Mô tả công việc (JD)
    và văn bản CV bằng Sentence-BERT và Cosine Similarity.

    Args:
        jd_text (str): Nội dung chi tiết bài tuyển dụng (Job Description).
        cv_text (str): Văn bản thô đã trích xuất từ CV ứng viên.

    Returns:
        float: Điểm số ngữ nghĩa từ 0.0 đến 100.0 (%).
    """
    if not jd_text or not cv_text:
        return 0.0

    try:
        model = get_sentence_bert_model()

        # Sentence-BERT hoạt động tốt nhất với các đoạn văn bản có độ dài vừa phải
        # Ta lấy tối đa 2000 ký tự đầu của JD và CV (tập trung vào mục tiêu & kinh nghiệm cốt lõi)
        jd_sample = jd_text[:2000].strip()
        cv_sample = cv_text[:2000].strip()

        # Nhúng vector (Embedding)
        emb_jd = model.encode(jd_sample, convert_to_tensor=True)
        emb_cv = model.encode(cv_sample, convert_to_tensor=True)

        # Tính Cosine Similarity
        cosine_sim = float(util.cos_sim(emb_jd, emb_cv)[0][0])

        # Chuẩn hóa về thang điểm 0 - 100% (nếu < 0 thì kẹp về 0)
        score_percentage = max(0.0, min(100.0, cosine_sim * 100.0))
        return round(score_percentage, 2)
    except Exception as e:
        logger.error(f"Lỗi khi tính Semantic Similarity qua Sentence-BERT: {e}")
        return 50.0  # Điểm an toàn dự phòng nếu mô hình gặp sự cố


# ==============================================================================
# 2. SKILL MATCHING & XAI SET OPERATIONS
# ==============================================================================
def match_skills(
    jd_skills: Union[List[str], str],
    cv_skills: Union[List[str], str]
) -> Dict[str, Union[float, List[str], str]]:
    """
    So sánh tập hợp kỹ năng giữa JD và CV, phục vụ tính điểm và giải thích XAI:
    - matched_skills: JD ∩ CV (Kỹ năng ứng viên sở hữu khớp với yêu cầu)
    - missing_skills: JD \ CV (Kỹ năng bắt buộc trong JD nhưng CV còn thiếu)
    - additional_skills: CV \ JD (Kỹ năng thêm ứng viên có nhưng JD không yêu cầu)

    Args:
        jd_skills: Danh sách kỹ năng yêu cầu của JD (List hoặc chuỗi phân tách bằng dấu phẩy)
        cv_skills: Danh sách kỹ năng bóc tách từ CV (List hoặc chuỗi phân tách bằng dấu phẩy)

    Returns:
        Dict: Chứa skill_score (0-100), matched_skills, missing_skills, additional_skills
    """
    # Chuẩn hóa jd_skills thành list
    if isinstance(jd_skills, str):
        jd_list = [s.strip() for s in jd_skills.split(',') if s.strip()]
    else:
        jd_list = [s.strip() for s in (jd_skills or []) if s.strip()]

    # Chuẩn hóa cv_skills thành list
    if isinstance(cv_skills, str):
        cv_list = [s.strip() for s in cv_skills.split(',') if s.strip()]
    else:
        cv_list = [s.strip() for s in (cv_skills or []) if s.strip()]

    # Tạo map tra cứu case-insensitive: lower_name -> canonical_name
    jd_map = {s.lower(): s for s in jd_list}
    cv_map = {s.lower(): s for s in cv_list}

    jd_set_lower = set(jd_map.keys())
    cv_set_lower = set(cv_map.keys())

    # Thực hiện toán tử tập hợp (Set Operations)
    matched_lower = jd_set_lower & cv_set_lower
    missing_lower = jd_set_lower - cv_set_lower
    additional_lower = cv_set_lower - jd_set_lower

    # Khôi phục tên gốc chuẩn hóa (Canonical names)
    matched_skills = sorted([jd_map[k] for k in matched_lower])
    missing_skills = sorted([jd_map[k] for k in missing_lower])
    additional_skills = sorted([cv_map[k] for k in additional_lower])

    # Tính điểm kỹ năng (Skill Score)
    total_required = len(jd_list)
    if total_required == 0:
        skill_score = 100.0  # Không yêu cầu kỹ năng cụ thể
    else:
        skill_score = round((len(matched_skills) / total_required) * 100.0, 2)

    return {
        "skill_score": skill_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "match_ratio": f"{len(matched_skills)}/{total_required}",
        "total_required": total_required,
        "total_matched": len(matched_skills),
    }
