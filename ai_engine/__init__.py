"""
AI Engine Module - Hỗ trợ phân tích & sàng lọc CV tự động.
Bao gồm:
- parser: Trích xuất raw text từ file PDF/DOCX
- extractor: Bóc tách kỹ năng theo Skill Taxonomy bằng Regex
- matcher: Tính tương đồng Sentence-BERT & So khớp kỹ năng Set Operations (XAI)
- evaluator: Tính điểm đa tiêu chí tổng hợp S_total (Kỹ năng, Ngữ nghĩa, Kinh nghiệm, Học vấn)
"""

from .parser import extract_text_from_file, extract_text_from_pdf, extract_text_from_docx
from .extractor import extract_skills, SKILL_TAXONOMY
from .matcher import calculate_semantic_similarity, match_skills, get_sentence_bert_model
from .evaluator import (
    evaluate_candidate_application,
    calculate_total_score,
    calculate_experience_score,
    calculate_education_score,
    DEFAULT_WEIGHTS,
)

__all__ = [
    'extract_text_from_file',
    'extract_text_from_pdf',
    'extract_text_from_docx',
    'extract_skills',
    'SKILL_TAXONOMY',
    'calculate_semantic_similarity',
    'match_skills',
    'get_sentence_bert_model',
    'evaluate_candidate_application',
    'calculate_total_score',
    'calculate_experience_score',
    'calculate_education_score',
    'DEFAULT_WEIGHTS',
]
