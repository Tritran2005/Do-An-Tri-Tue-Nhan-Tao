import re
from typing import List, Dict, Set

# ==============================================================================
# SKILL TAXONOMY DICTIONARY (Cấu trúc từ điển kỹ năng chuẩn hóa)
# ==============================================================================
# Khóa (Key): Tên kỹ năng chuẩn hóa (Canonical Name)
# Giá trị (Value): Biểu thức chính quy Regex xử lý biên từ (\b), ký tự đặc biệt (+, #, .) và từ đồng nghĩa/viết tắt
SKILL_TAXONOMY: Dict[str, str] = {
    # Ngôn ngữ lập trình (Programming Languages)
    "Python": r"\bpython\b",
    "Java": r"\bjava\b(?!\s*script)",
    "JavaScript": r"\b(javascript|js|es6)\b",
    "TypeScript": r"\b(typescript|ts)\b",
    "C++": r"\bc\+\+\b",
    "C#": r"\bc\#|csharp\b",
    "C": r"\b(c\s*programming|ngôn\s*ngữ\s*c)\b",
    "PHP": r"\bphp\b",
    "Golang": r"\b(golang|go\s*language)\b",
    "Rust": r"\brust\b",
    "Ruby": r"\bruby\b",
    "Kotlin": r"\bkotlin\b",
    "Swift": r"\bswift\b",
    "R": r"\b(r\s*programming|ngôn\s*ngữ\s*r)\b",

    # AI / Machine Learning / Data Science / NLP
    "Machine Learning": r"\b(machine\s*learning|ml)\b",
    "Deep Learning": r"\b(deep\s*learning|dl)\b",
    "NLP": r"\b(nlp|natural\s*language\s*processing|xử\s*lý\s*ngôn\s*ngữ\s*tự\s*nhiên)\b",
    "Computer Vision": r"\b(computer\s*vision|thị\s*giác\s*máy\s*tính)\b",
    "PyTorch": r"\bpytorch\b",
    "TensorFlow": r"\btensorflow\b",
    "Keras": r"\bkeras\b",
    "Sentence-BERT": r"\b(sentence-bert|sbert|sentence\s*transformers?)\b",
    "BERT": r"\bbert\b",
    "Transformers": r"\b(transformers|huggingface)\b",
    "Scikit-learn": r"\b(scikit-learn|sklearn)\b",
    "Pandas": r"\bpandas\b",
    "NumPy": r"\bnumpy\b",
    "OpenCV": r"\bopencv\b",
    "LLM": r"\b(llm|large\s*language\s*models?)\b",

    # Web Frameworks & Backend
    "Django": r"\bdjango\b",
    "FastAPI": r"\bfastapi\b",
    "Flask": r"\bflask\b",
    "Spring Boot": r"\b(spring\s*boot|spring\s*framework)\b",
    "Node.js": r"\b(node\.?js|nodejs)\b",
    "Express.js": r"\b(express\.?js|expressjs)\b",
    "NestJS": r"\bnestjs\b",
    "ASP.NET": r"\b(asp\.net|\.net\s*core|\.net)\b",
    "Laravel": r"\blaravel\b",

    # Frontend Frameworks & UI
    "React": r"\b(react\.?js|reactjs|react)\b",
    "Vue.js": r"\b(vue\.?js|vuejs|vue)\b",
    "Angular": r"\bangular\b",
    "Next.js": r"\b(next\.?js|nextjs)\b",
    "HTML": r"\bhtml5?\b",
    "CSS": r"\bcss3?\b",
    "Tailwind CSS": r"\b(tailwind\s*css|tailwind)\b",
    "Bootstrap": r"\bbootstrap\b",

    # Cơ sở dữ liệu (Databases)
    "MySQL": r"\bmysql\b",
    "PostgreSQL": r"\b(postgresql|postgres)\b",
    "MongoDB": r"\bmongodb\b",
    "Redis": r"\bredis\b",
    "SQLite": r"\bsqlite3?\b",
    "Oracle": r"\boracle\s*(db|database)?\b",
    "SQL Server": r"\b(sql\s*server|mssql)\b",
    "SQL": r"\bsql\b",

    # Cloud, DevOps & Công cụ
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\b(kubernetes|k8s)\b",
    "AWS": r"\b(aws|amazon\s*web\s*services)\b",
    "Google Cloud": r"\b(gcp|google\s*cloud)\b",
    "Azure": r"\bazure\b",
    "Git": r"\b(git|github|gitlab)\b",
    "CI/CD": r"\b(ci/cd|cicd|jenkins|github\s*actions)\b",
    "Linux": r"\b(linux|ubuntu|centos)\b",
    "Nginx": r"\bnginx\b",
    "REST API": r"\b(rest\s*api|restful\s*api|restful)\b",
    "GraphQL": r"\bgraphql\b",
    "Microservices": r"\bmicroservices?\b",
}

# Tiền biên dịch (Pre-compile) các pattern regex để tối ưu hóa hiệu năng khi duyệt nhiều CV
COMPILED_PATTERNS = {
    skill: re.compile(pattern, re.IGNORECASE)
    for skill, pattern in SKILL_TAXONOMY.items()
}


def extract_skills(raw_text: str) -> List[str]:
    """
    Quét toàn bộ văn bản thô (raw text) của CV và bóc tách các kỹ năng ứng viên sở hữu
    dựa trên bộ quy tắc Regular Expressions và Skill Taxonomy.

    Args:
        raw_text (str): Văn bản thô đã được trích xuất từ CV.

    Returns:
        List[str]: Danh sách kỹ năng chuẩn hóa (Canonical names), không trùng lặp, sắp xếp theo thứ tự bảng chữ cái.
    """
    if not raw_text:
        return []

    matched_skills: Set[str] = set()

    for canonical_name, regex in COMPILED_PATTERNS.items():
        if regex.search(raw_text):
            matched_skills.add(canonical_name)

    return sorted(list(matched_skills))


# ==============================================================================
# CONTACT EXTRACTION REGEX PATTERNS (SĐT, Email, GitHub, LinkedIn)
# ==============================================================================

EMAIL_REGEX = re.compile(
    r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b',
    re.IGNORECASE
)

# Nhận diện số điện thoại Việt Nam & quốc tế phổ biến:
# +84 912 345 678, 0987.654.321, 090-123-4567, (+84) 934567890, 024 37891234
PHONE_REGEX = re.compile(
    r'(?:\+?84|0)(?:\s*|\.|\-)?(?:\(?\d{2,3}\)?|\d{2,3})(?:\s*|\.|\-)?\d{3}(?:\s*|\.|\-)?\d{3,4}\b'
)

GITHUB_REGEX = re.compile(
    r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)',
    re.IGNORECASE
)

LINKEDIN_REGEX = re.compile(
    r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_%-]+)',
    re.IGNORECASE
)


def extract_contact_info(raw_text: str) -> Dict[str, str]:
    """
    Bóc tách các thông tin liên hệ và hồ sơ số từ nội dung CV:
    - Email liên hệ
    - Số điện thoại (chuẩn hóa về chuỗi số liền mạch hoặc định dạng chuẩn)
    - Đường dẫn GitHub
    - Đường dẫn LinkedIn

    Args:
        raw_text (str): Toàn bộ văn bản thô trích xuất từ CV.

    Returns:
        Dict[str, str]: Từ điển chứa {'email': ..., 'phone': ..., 'github': ..., 'linkedin': ...}
    """
    if not raw_text:
        return {'email': '', 'phone': '', 'github': '', 'linkedin': ''}

    # 1. Trích xuất Email
    email = ''
    email_matches = EMAIL_REGEX.findall(raw_text)
    if email_matches:
        for match in email_matches:
            if not match.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                email = match.strip()
                break

    # 2. Trích xuất Số điện thoại
    phone = ''
    phone_matches = PHONE_REGEX.findall(raw_text)
    if phone_matches:
        for match in phone_matches:
            cleaned_digits = re.sub(r'\D', '', match)
            if 10 <= len(cleaned_digits) <= 12:
                phone = match.strip()
                break

    # 3. Trích xuất GitHub
    github = ''
    gh_match = GITHUB_REGEX.search(raw_text)
    if gh_match:
        github = f"https://github.com/{gh_match.group(1)}"

    # 4. Trích xuất LinkedIn
    linkedin = ''
    li_match = LINKEDIN_REGEX.search(raw_text)
    if li_match:
        linkedin = f"https://linkedin.com/in/{li_match.group(1)}"

    return {
        'email': email,
        'phone': phone,
        'github': github,
        'linkedin': linkedin,
    }


# ==============================================================================
# P3 – ENTITY EXTRACTION (Bóc tách Tên ứng viên & Kinh nghiệm làm việc)
# ==============================================================================

# Danh sách từ phổ biến không phải tên người (tiêu đề mục CV, từ khóa kỹ thuật)
_NON_NAME_KEYWORDS = {
    'curriculum', 'vitae', 'resume', 'cv', 'profile', 'contact', 'information',
    'experience', 'education', 'skills', 'objective', 'summary', 'references',
    'email', 'phone', 'address', 'website', 'linkedin', 'github', 'portfolio',
    'python', 'java', 'django', 'react', 'sql', 'mysql', 'docker', 'aws',
    'kinh', 'nghiệm', 'học', 'vấn', 'kỹ', 'năng', 'mục', 'tiêu', 'liên', 'hệ',
    'trình', 'độ', 'dự', 'án', 'thông', 'tin', 'cá', 'nhân',
}

# Biểu thức nhận diện khoảng thời gian làm việc (VD: 03/2020 – 06/2022, 2019 - nay)
_DATE_RANGE_PATTERN = re.compile(
    r'(?:'
    r'(?:\d{1,2}[\/\-]\d{4})'          # MM/YYYY hoặc MM-YYYY
    r'|(?:\d{4})'                       # Chỉ năm
    r')'
    r'\s*(?:–|—|-)(?:\s*)'
    r'(?:'
    r'(?:\d{1,2}[\/\-]\d{4})'
    r'|(?:\d{4})'
    r'|(?:nay|present|current|now|hiện tại)'
    r')',
    re.IGNORECASE
)

# Nhận diện tiêu đề section "Kinh nghiệm làm việc"
_EXPERIENCE_SECTION_PATTERN = re.compile(
    r'(?:KINH\s*NGHIỆM|WORK\s*EXPERIENCE|EXPERIENCE|EMPLOYMENT|PROFESSIONAL\s*EXPERIENCE)',
    re.IGNORECASE
)


def extract_candidate_name(raw_text: str) -> str:
    """
    Bóc tách tên ứng viên bằng heuristic từ đầu văn bản CV.

    Chiến lược:
    1. Quét 8 dòng đầu tiên không rỗng của CV.
    2. Tên người thường là chuỗi title-case hoặc ALLCAPS, 2-5 từ, không chứa ký tự đặc biệt.
    3. Loại trừ các từ khóa phổ biến không phải tên.

    Args:
        raw_text (str): Văn bản thô từ CV.

    Returns:
        str: Tên ứng viên ước lượng hoặc chuỗi rỗng '' nếu không xác định được.
    """
    if not raw_text:
        return ''

    # Lấy 8 dòng đầu không rỗng
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()][:8]

    for line in lines:
        # Bỏ qua dòng quá dài (> 80 ký tự) hoặc quá ngắn (< 3 ký tự)
        if len(line) > 80 or len(line) < 3:
            continue

        # Bỏ qua dòng chứa email / số điện thoại / URL
        if re.search(r'[@://\d{4,}]', line):
            continue

        # Tách từ, loại bỏ dấu câu đầu/cuối
        words = re.findall(r"[A-ZÀ-Ỹa-zà-ỹ][a-zà-ỹA-ZÀ-Ỹ']*", line)
        if len(words) < 2 or len(words) > 6:
            continue

        # Kiểm tra dòng không chứa từ khóa phi-tên
        words_lower = {w.lower() for w in words}
        if words_lower & _NON_NAME_KEYWORDS:
            continue

        # Kiểm tra: ít nhất 1 từ được viết hoa chữ cái đầu (Title Case) hoặc toàn chữ hoa
        has_title_or_upper = any(
            (w[0].isupper() and (w[1:].islower() or not w[1:].isalpha())) or w.isupper()
            for w in words
        )
        if not has_title_or_upper:
            continue

        # Candidate name found
        return ' '.join(words)

    return ''


def extract_work_experience_entries(raw_text: str) -> list:
    """
    Bóc tách danh sách các mục kinh nghiệm làm việc từ văn bản CV.

    Chiến lược:
    - Tìm các chuỗi chứa khoảng thời gian (03/2020 – 06/2022) và 1-2 dòng xung quanh.
    - Gom nhóm thành các entry: {'date_range': ..., 'context': ...}

    Args:
        raw_text (str): Văn bản thô từ CV.

    Returns:
        list[dict]: Danh sách các entry kinh nghiệm, mỗi entry có 'date_range' và 'context'.
    """
    if not raw_text:
        return []

    entries = []
    lines = raw_text.splitlines()

    for i, line in enumerate(lines):
        date_match = _DATE_RANGE_PATTERN.search(line)
        if not date_match:
            continue

        date_range = date_match.group(0).strip()

        # Lấy ngữ cảnh: dòng hiện tại + dòng trước/sau (tối đa 3 dòng)
        context_lines = []
        for j in range(max(0, i - 1), min(len(lines), i + 3)):
            stripped = lines[j].strip()
            if stripped and stripped != date_range:
                context_lines.append(stripped)

        context = ' | '.join(context_lines[:3])  # Gộp tối đa 3 dòng ngữ cảnh

        # Tránh trùng lặp nếu cùng date_range đã được ghi nhận
        existing_ranges = {e['date_range'] for e in entries}
        if date_range not in existing_ranges:
            entries.append({
                'date_range': date_range,
                'context': context,
            })

    return entries

