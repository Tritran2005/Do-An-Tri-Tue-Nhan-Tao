import os
import docx
from docx.shared import Pt, Inches, RGBColor
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register TrueType Arial for Vietnamese Unicode support
FONT_REGULAR = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'
if os.path.exists('C:/Windows/Fonts/arial.ttf'):
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
    FONT_REGULAR = 'Arial'
    FONT_BOLD = 'Arial-Bold'

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_cvs')
os.makedirs(SAMPLE_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# HELPER: CREATE PDF CV USING REPORTLAB
# ----------------------------------------------------------------------
def create_pdf_cv(filename, name, title, contact, summary, skills, experience, education):
    filepath = os.path.join(SAMPLE_DIR, filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles with Unicode Arial font
    title_style = ParagraphStyle(
        'CVTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e1b4b')
    )
    sub_title_style = ParagraphStyle(
        'CVSubTitle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4f46e5')
    )
    section_style = ParagraphStyle(
        'CVSection',
        parent=styles['Heading2'],
        fontName=FONT_BOLD,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=4
    )
    normal_style = ParagraphStyle(
        'CVNormal',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155')
    )
    bold_style = ParagraphStyle(
        'CVBold',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#0f172a')
    )

    story = []

    # Header: Name & Contact
    story.append(Paragraph(name, title_style))
    story.append(Paragraph(title, sub_title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(contact, normal_style))
    story.append(Spacer(1, 10))

    # Summary
    story.append(Paragraph("TỔNG QUAN NGHỀ NGHIỆP / PROFESSIONAL SUMMARY", section_style))
    story.append(Paragraph(summary, normal_style))
    story.append(Spacer(1, 8))

    # Technical Skills
    story.append(Paragraph("KỸ NĂNG CHUYÊN MÔN / CORE TECHNICAL SKILLS", section_style))
    skill_text = ", ".join(skills)
    story.append(Paragraph(f"<b>Kỹ năng:</b> {skill_text}", normal_style))
    story.append(Spacer(1, 8))

    # Work Experience
    story.append(Paragraph("KINH NGHIỆM LÀM VIỆC / WORK EXPERIENCE", section_style))
    for exp in experience:
        story.append(Paragraph(f"<b>{exp['role']}</b> | {exp['company']} ({exp['period']})", bold_style))
        story.append(Paragraph(exp['desc'], normal_style))
        story.append(Spacer(1, 6))

    # Education
    story.append(Paragraph("TRÌNH ĐỘ HỌC VẤN / EDUCATION", section_style))
    for edu in education:
        story.append(Paragraph(f"<b>{edu['degree']}</b> - {edu['school']} ({edu['year']})", bold_style))
        story.append(Paragraph(edu.get('detail', ''), normal_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    print(f"Created PDF: {filepath}")


# ----------------------------------------------------------------------
# HELPER: CREATE DOCX CV USING PYTHON-DOCX
# ----------------------------------------------------------------------
def create_docx_cv(filename, name, title, contact, summary, skills, experience, education):
    filepath = os.path.join(SAMPLE_DIR, filename)
    doc = docx.Document()

    # Title & Subtitle
    h1 = doc.add_paragraph()
    h1_run = h1.add_run(name)
    h1_run.font.size = Pt(20)
    h1_run.font.bold = True
    h1_run.font.color.rgb = RGBColor(30, 27, 75)

    sub = doc.add_paragraph()
    sub_run = sub.add_run(title)
    sub_run.font.size = Pt(12)
    sub_run.font.bold = True
    sub_run.font.color.rgb = RGBColor(79, 70, 229)

    contact_p = doc.add_paragraph(contact)
    contact_p.runs[0].font.size = Pt(9.5)
    contact_p.runs[0].font.color.rgb = RGBColor(100, 116, 139)

    # Summary
    s_h = doc.add_paragraph()
    s_run = s_h.add_run("TỔNG QUAN NGHỀ NGHIỆP / PROFESSIONAL SUMMARY")
    s_run.font.size = Pt(11.5)
    s_run.font.bold = True
    s_run.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(summary)

    # Skills in a Table
    sk_h = doc.add_paragraph()
    sk_run = sk_h.add_run("KỸ NĂNG CHUYÊN MÔN / CORE TECHNICAL SKILLS")
    sk_run.font.size = Pt(11.5)
    sk_run.font.bold = True
    sk_run.font.color.rgb = RGBColor(15, 23, 42)

    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Nhóm Kỹ Năng"
    hdr_cells[1].text = "Danh Sách Kỹ Năng Bóc Tách"
    
    row_cells = table.add_row().cells
    row_cells[0].text = "Technical Stack"
    row_cells[1].text = ", ".join(skills)

    # Work Experience
    exp_h = doc.add_paragraph()
    exp_run = exp_h.add_run("KINH NGHIỆM LÀM VIỆC / WORK EXPERIENCE")
    exp_run.font.size = Pt(11.5)
    exp_run.font.bold = True
    exp_run.font.color.rgb = RGBColor(15, 23, 42)

    for exp in experience:
        p_exp = doc.add_paragraph()
        run_role = p_exp.add_run(f"{exp['role']} - {exp['company']} ({exp['period']})\n")
        run_role.font.bold = True
        p_exp.add_run(exp['desc'])

    # Education
    edu_h = doc.add_paragraph()
    edu_run = edu_h.add_run("TRÌNH ĐỘ HỌC VẤN / EDUCATION")
    edu_run.font.size = Pt(11.5)
    edu_run.font.bold = True
    edu_run.font.color.rgb = RGBColor(15, 23, 42)

    for edu in education:
        p_edu = doc.add_paragraph()
        p_edu.add_run(f"{edu['degree']} - {edu['school']} ({edu['year']})\n").font.bold = True
        p_edu.add_run(edu.get('detail', ''))

    doc.save(filepath)
    print(f"Created DOCX: {filepath}")


# ======================================================================
# GENERATE 5 SAMPLE CVS
# ======================================================================

def generate_all_cvs():
    print("Generating 5 sample CVs...")

    # ------------------------------------------------------------------
    # 1. CV 1 (PDF) - High Match for Senior AI & NLP Engineer (Job 1)
    # ------------------------------------------------------------------
    create_pdf_cv(
        filename="CV_01_Nguyen_Van_An_Senior_AI_NLP.pdf",
        name="NGUYỄN VĂN AN",
        title="Senior AI & NLP Engineer | Sentence-BERT & LLM Specialist",
        contact="Email: an.nguyen.ai@example.com | Phone: 0988123456 | Ha Noi, Viet Nam | GitHub: github.com/annguyen-ai",
        summary="Kỹ sư Trí tuệ Nhân tạo với 4 năm kinh nghiệm nghiên cứu và triển khai thực tế các giải pháp Xử lý Ngôn ngữ Tự nhiên (NLP) và Học sâu. Chuyên sâu về Sentence-BERT, Transformers, PyTorch, và tích hợp mô hình ngôn ngữ lớn LLM vào hệ thống doanh nghiệp.",
        skills=[
            "Python", "PyTorch", "NLP", "Sentence-BERT", "Transformers",
            "Docker", "MySQL", "Machine Learning", "Deep Learning",
            "Scikit-learn", "Git", "Linux", "REST API"
        ],
        experience=[
            {
                "role": "Senior AI Engineer",
                "company": "FPT Smart Cloud",
                "period": "2023 - Hiện tại (2 năm làm việc)",
                "desc": "Chủ trì kiến trúc mô hình NLP Sentence-BERT để xây dựng công cụ semantic search và trích xuất thực thể. Đóng gói mô hình bằng Docker và triển khai REST API trên nền tảng đám mây, tối ưu hóa tốc độ suy luận dưới 100ms."
            },
            {
                "role": "NLP Research Engineer",
                "company": "Viettel AI Labs",
                "period": "2021 - 2023 (2 năm kinh nghiệm)",
                "desc": "Huấn luyện mô hình PyTorch và HuggingFace Transformers phân loại văn bản tiếng Việt. Quản lý cơ sở dữ liệu MySQL và xử lý dữ liệu lớn với Pandas, NumPy. Tổng cộng hơn 4 năm kinh nghiệm trong ngành."
            }
        ],
        education=[
            {
                "degree": "Thạc sĩ (Master) Khoa học Máy tính",
                "school": "Đại học Bách Khoa Hà Nội",
                "year": "2021 - 2023",
                "detail": "Nghiên cứu luận văn về Multilingual Sentence Embeddings và Semantic Textual Similarity."
            },
            {
                "degree": "Kỹ sư Công nghệ Thông tin (Bachelor)",
                "school": "Đại học Bách Khoa Hà Nội",
                "year": "2017 - 2021",
                "detail": "Tốt nghiệp loại Xuất sắc, GPA: 3.65/4.0."
            }
        ]
    )

    # ------------------------------------------------------------------
    # 2. CV 2 (DOCX) - High Match for Fullstack Django & React (Job 2)
    # ------------------------------------------------------------------
    create_docx_cv(
        filename="CV_02_Tran_Thi_Bich_Fullstack_Django_React.docx",
        name="TRẦN THỊ BÍCH",
        title="Fullstack Web Developer | Python, Django & React Specialist",
        contact="Email: bich.tran@example.com | Phone: 0912345678 | TP. Ho Chi Minh | LinkedIn: linkedin.com/in/bichtran",
        summary="Lập trình viên Fullstack với 3 năm kinh nghiệm phát triển ứng dụng Web thương mại SaaS hiện đại. Thành thạo Backend với Python, Django, REST API, MySQL và Frontend với React, JavaScript, Tailwind CSS.",
        skills=[
            "Python", "Django", "MySQL", "JavaScript", "React",
            "Tailwind CSS", "REST API", "HTML", "CSS", "Git", "Docker"
        ],
        experience=[
            {
                "role": "Fullstack Developer",
                "company": "VNG Corporation",
                "period": "2023 - 2026 (3 năm kinh nghiệm làm việc)",
                "desc": "Thiết kế và phát triển hệ thống quản lý dữ liệu sử dụng Django REST Framework kết nối CSDL MySQL. Xây dựng giao diện Single Page Application hiện đại với React, JavaScript và Tailwind CSS."
            },
            {
                "role": "Frontend / Junior Web Developer",
                "company": "One Mount Group",
                "period": "2022 - 2023 (1 năm làm việc)",
                "desc": "Xây dựng các module giao diện người dùng bằng HTML, CSS, JavaScript và React, tích hợp API Backend."
            }
        ],
        education=[
            {
                "degree": "Cử nhân Đại học (Bachelor) Công nghệ Thông tin",
                "school": "Đại học Khoa học Tự nhiên - ĐHQG TP.HCM",
                "year": "2018 - 2022",
                "detail": "Chuyên ngành Kỹ thuật Phần mềm. Tốt nghiệp loại Giỏi."
            }
        ]
    )

    # ------------------------------------------------------------------
    # 3. CV 3 (PDF) - Mid Match (Backend Python, thiếu React/Tailwind hoặc AI)
    # ------------------------------------------------------------------
    create_pdf_cv(
        filename="CV_03_Le_Van_Cuong_Backend_Python.pdf",
        name="LÊ VĂN CƯỜNG",
        title="Backend Software Engineer | Python & Django",
        contact="Email: cuong.le@example.com | Phone: 0977889900 | Da Nang, Viet Nam | GitHub: github.com/cuongle-dev",
        summary="Kỹ sư Backend với 2 năm kinh nghiệm làm việc tập trung vào kiến trúc máy chủ, tối ưu truy vấn cơ sở dữ liệu MySQL và xây dựng REST API bằng Python và Django. Có khả năng làm việc với Docker và Git.",
        skills=[
            "Python", "Django", "MySQL", "REST API", "Git",
            "Docker", "Linux", "OOP"
        ],
        experience=[
            {
                "role": "Backend Developer",
                "company": "FPT Software Da Nang",
                "period": "2024 - 2026 (2 năm kinh nghiệm)",
                "desc": "Xây dựng các microservice Backend bằng Django và FastAPI, thiết kế schema CSDL MySQL, viết unit test và quản lý phiên bản với Git và Docker."
            }
        ],
        education=[
            {
                "degree": "Cử nhân Đại học (Bachelor) Kỹ thuật Phần mềm",
                "school": "Đại học Bách Khoa - Đại học Đà Nẵng",
                "year": "2019 - 2023",
                "detail": "Tốt nghiệp loại Khá, nghiên cứu chuyên sâu về Kiến trúc hướng Dịch vụ."
            }
        ]
    )

    # ------------------------------------------------------------------
    # 4. CV 4 (DOCX) - Fresher Python / AI Trainee (Job 3)
    # ------------------------------------------------------------------
    create_docx_cv(
        filename="CV_04_Pham_Minh_Dung_Fresher_Python.docx",
        name="PHẠM MINH DŨNG",
        title="Fresher Python Developer | AI & Backend Trainee",
        contact="Email: dung.pham@example.com | Phone: 0933557799 | Ha Noi | Portfolio: dungpham.dev",
        summary="Sinh viên mới tốt nghiệp ngành Công nghệ Thông tin, có nền tảng tư duy lập trình vững chắc về Python, Lập trình Hướng đối tượng (OOP), CSDL MySQL và Git. Đam mê học hỏi và sẵn sàng thử sức với các bài toán AI và Web.",
        skills=[
            "Python", "Django", "MySQL", "Git", "OOP", "Regex", "HTML", "CSS"
        ],
        experience=[
            {
                "role": "Python Intern / Trainee",
                "company": "TMA Solutions",
                "period": "2025 - 2026 (1 năm kinh nghiệm)",
                "desc": "Tham gia dự án nội bộ xây dựng ứng dụng web với Django và MySQL. Sử dụng Regex bóc tách chuỗi dữ liệu log và quản lý code bằng Git."
            }
        ],
        education=[
            {
                "degree": "Cử nhân Đại học (Bachelor) Công nghệ Thông tin",
                "school": "Đại học Công nghiệp Hà Nội (HaUI)",
                "year": "2021 - 2025",
                "detail": "GPA: 3.3/4.0. Hoàn thành đồ án tốt nghiệp ứng dụng Python và MySQL đạt điểm 9.0."
            }
        ]
    )

    # ------------------------------------------------------------------
    # 5. CV 5 (PDF) - Low Match / Unrelated Domain (PHP, Vue, Frontend)
    # ------------------------------------------------------------------
    create_pdf_cv(
        filename="CV_05_Hoang_Van_Em_Frontend_Vue_PHP.pdf",
        name="HOÀNG VĂN EM",
        title="Web Designer & Junior Frontend Developer",
        contact="Email: em.hoang@example.com | Phone: 0909112233 | Can Tho, Viet Nam",
        summary="Lập trình viên giao diện với 1 năm kinh nghiệm làm việc với các trang web bán hàng cơ bản sử dụng PHP, Laravel, Vue.js, Bootstrap và SQLite.",
        skills=[
            "PHP", "Laravel", "Vue.js", "Bootstrap", "SQLite", "HTML", "CSS"
        ],
        experience=[
            {
                "role": "Junior Web Developer",
                "company": "Mekong Soft",
                "period": "2025 - 2026 (1 năm kinh nghiệm)",
                "desc": "Xây dựng giao diện landing page bằng HTML, CSS, Bootstrap và Vue.js. Xử lý backend đơn giản với PHP và SQLite."
            }
        ],
        education=[
            {
                "degree": "Cao đẳng (College) Tin học Ứng dụng",
                "school": "Cao đẳng Cần Thơ",
                "year": "2022 - 2025",
                "detail": "Tốt nghiệp loại Khá."
            }
        ]
    )

    # ------------------------------------------------------------------
    # 6. CV 6 (PDF) - Data Scientist & MLOps Specialist
    # ------------------------------------------------------------------
    create_pdf_cv(
        filename="CV_06_Vo_Thi_Mai_Data_Scientist_MLOps.pdf",
        name="VÕ THỊ MAI",
        title="Data Scientist & MLOps Specialist | Machine Learning, PyTorch, Docker",
        contact="Email: mai.vo.ds@example.com | Phone: 0918776655 | TP. Ho Chi Minh | LinkedIn: linkedin.com/in/maivo-ds",
        summary="Chuyên gia Khoa học Dữ liệu và MLOps với hơn 3 năm kinh nghiệm phát triển mô hình Machine Learning, Deep Learning, và xây dựng pipeline triển khai tự động hóa. Thành thạo Python, PyTorch, Pandas, Scikit-learn, Docker, MySQL và REST API.",
        skills=[
            "Python", "PyTorch", "Machine Learning", "Deep Learning", "NLP",
            "Pandas", "NumPy", "Scikit-learn", "Docker", "MySQL", "Git", "REST API"
        ],
        experience=[
            {
                "role": "Data Scientist & MLOps Engineer",
                "company": "Shopee Vietnam",
                "period": "2023 - 2026 (3 năm kinh nghiệm)",
                "desc": "Nghiên cứu và tối ưu mô hình Machine Learning dự đoán nhu cầu người dùng. Xây dựng pipeline dữ liệu với Pandas, NumPy, Scikit-learn và đóng gói container với Docker, phục vụ qua REST API."
            },
            {
                "role": "AI / Data Analyst",
                "company": "Zalo AI Lab",
                "period": "2022 - 2023 (1 năm kinh nghiệm)",
                "desc": "Xử lý dữ liệu ngôn ngữ tiếng Việt (NLP), trích xuất đặc trưng và truy vấn cơ sở dữ liệu MySQL quy mô lớn."
            }
        ],
        education=[
            {
                "degree": "Thạc sĩ (Master) Khoa học Dữ liệu",
                "school": "Đại học Khoa học Tự nhiên - ĐHQG TP.HCM",
                "year": "2022 - 2024",
                "detail": "Luận văn tốt nghiệp về MLOps và tối ưu suy luận mô hình Deep Learning."
            },
            {
                "degree": "Cử nhân (Bachelor) Toán Tin Ứng Dụng",
                "school": "Đại học Sư phạm TP.HCM",
                "year": "2018 - 2022",
                "detail": "Tốt nghiệp loại Giỏi, GPA: 3.6/4.0."
            }
        ]
    )

    # ------------------------------------------------------------------
    # 7. CV 7 (DOCX) - DevOps & Cloud Infrastructure Engineer
    # ------------------------------------------------------------------
    create_docx_cv(
        filename="CV_07_Do_Gia_Huy_DevOps_Cloud_Engineer.docx",
        name="ĐỖ GIA HUY",
        title="DevOps & Cloud Infrastructure Engineer | Docker, Kubernetes, CI/CD",
        contact="Email: huy.dogia@example.com | Phone: 0945112288 | Ha Noi | GitHub: github.com/giahuy-devops",
        summary="Kỹ sư DevOps với 3.5 năm kinh nghiệm thiết kế hạ tầng đám mây, tự động hóa quy trình CI/CD và quản lý hạ tầng bằng mã (IaC). Thành thạo Docker, Kubernetes, Linux, Git, Python scripting và cơ sở dữ liệu MySQL.",
        skills=[
            "Docker", "Linux", "Git", "Python", "MySQL", "CI/CD", "Kubernetes", "AWS", "REST API"
        ],
        experience=[
            {
                "role": "Senior DevOps Engineer",
                "company": "MoMo (M-Service)",
                "period": "2023 - 2026 (3 năm làm việc)",
                "desc": "Quản lý cụm Kubernetes và container Docker cho hệ thống vi dịch vụ chịu tải cao. Tự động hóa CI/CD pipeline, giám sát hạ tầng Linux và tối ưu hóa chi phí đám mây AWS."
            },
            {
                "role": "System Admin & DevOps",
                "company": "VTI Cloud",
                "period": "2022 - 2023 (1 năm kinh nghiệm)",
                "desc": "Vận hành hệ thống máy chủ Linux, viết script tự động hóa sao lưu và bảo trì MySQL bằng Python và Bash."
            }
        ],
        education=[
            {
                "degree": "Kỹ sư Công nghệ Thông tin (Bachelor)",
                "school": "Đại học Bách Khoa Hà Nội",
                "year": "2017 - 2022",
                "detail": "Chuyên ngành Mạng máy tính & An toàn thông tin. Tốt nghiệp loại Giỏi."
            }
        ]
    )

    # ------------------------------------------------------------------
    # 8. CV 8 (PDF) - Senior React & Frontend UI-UX Engineer
    # ------------------------------------------------------------------
    create_pdf_cv(
        filename="CV_08_Phan_Thanh_Tam_React_Frontend_Lead.pdf",
        name="PHAN THANH TÂM",
        title="Senior Frontend Engineer | React, JavaScript, Tailwind CSS Specialist",
        contact="Email: tam.phan.frontend@example.com | Phone: 0922334455 | Da Nang | Portfolio: phanthanhtam.dev",
        summary="Lập trình viên Frontend cao cấp với 4 năm kinh nghiệm chuyên sâu về React, JavaScript, TypeScript, Tailwind CSS và kiến trúc Web SPA. Tối ưu hiệu năng tải trang, chuẩn SEO và trải nghiệm người dùng hiện đại.",
        skills=[
            "JavaScript", "React", "Tailwind CSS", "HTML", "CSS", "REST API", "Git", "Docker"
        ],
        experience=[
            {
                "role": "Lead Frontend Developer",
                "company": "KMS Technology",
                "period": "2023 - 2026 (3 năm kinh nghiệm)",
                "desc": "Xây dựng Single Page Application phức tạp với React và Tailwind CSS, tích hợp REST API với backend Django/NodeJS. Quản lý source code với Git và triển khai Docker container."
            },
            {
                "role": "Frontend Developer",
                "company": "Enouvo IT Solutions",
                "period": "2021 - 2023 (2 năm kinh nghiệm)",
                "desc": "Phát triển giao diện web responsive với HTML, CSS, JavaScript và ReactJS, tối ưu hóa Core Web Vitals."
            }
        ],
        education=[
            {
                "degree": "Cử nhân Đại học (Bachelor) Kỹ thuật Phần mềm",
                "school": "Đại học Công nghệ Thông tin - ĐHQG TP.HCM (UIT)",
                "year": "2017 - 2021",
                "detail": "Tốt nghiệp loại Giỏi, giải Ba Nghiên cứu Khoa học Sinh viên."
            }
        ]
    )

    # ------------------------------------------------------------------
    # 9. CV 9 (DOCX) - Java Backend & Microservices Developer
    # ------------------------------------------------------------------
    create_docx_cv(
        filename="CV_09_Bui_Quoc_Tuan_Java_Spring_Backend.docx",
        name="BÙI QUỐC TUẤN",
        title="Java Backend Developer | Spring Boot, Microservices & MySQL",
        contact="Email: tuan.bui.java@example.com | Phone: 0966778899 | Ha Noi | LinkedIn: linkedin.com/in/tuanbuijava",
        summary="Kỹ sư phát triển Backend với 3 năm kinh nghiệm chuyên sâu về Java, Spring Boot, Microservices và tối ưu cơ sở dữ liệu quan hệ MySQL, PostgreSQL. Có kiến thức tốt về Docker, Git và bảo mật REST API.",
        skills=[
            "Java", "Spring Boot", "MySQL", "REST API", "Docker", "Git", "Linux", "OOP"
        ],
        experience=[
            {
                "role": "Java Backend Engineer",
                "company": "Techcombank",
                "period": "2023 - 2026 (3 năm làm việc)",
                "desc": "Phát triển các module ngân hàng điện tử sử dụng Spring Boot và microservices. Tối ưu hóa truy vấn CSDL MySQL, thiết kế chuẩn REST API an toàn và triển khai trên Docker."
            }
        ],
        education=[
            {
                "degree": "Cử nhân (Bachelor) Công nghệ Thông tin",
                "school": "Học viện Công nghệ Bưu chính Viễn thông (PTIT)",
                "year": "2018 - 2022",
                "detail": "Tốt nghiệp loại Giỏi, GPA 3.55/4.0."
            }
        ]
    )

    # ------------------------------------------------------------------
    # 10. CV 10 (PDF) - QA / QC Automation Tester
    # ------------------------------------------------------------------
    create_pdf_cv(
        filename="CV_10_Nguyen_Thi_Lan_Anh_QA_Automation.pdf",
        name="NGUYỄN THỊ LAN ANH",
        title="QA Automation Engineer | Python, Selenium, PyTest, API Testing",
        contact="Email: lananh.qa@example.com | Phone: 0971223344 | Ha Noi | LinkedIn: linkedin.com/in/lananhqa",
        summary="Kỹ sư Đảm bảo Chất lượng Phần mềm (QA/QC) với 2.5 năm kinh nghiệm trong kiểm thử tự động (Automation Testing) cho các hệ thống Web và REST API bằng ngôn ngữ Python, PyTest, Selenium và Postman. Có hiểu biết về MySQL, Git và CI/CD.",
        skills=[
            "Python", "MySQL", "Git", "REST API", "Selenium", "PyTest", "CI/CD", "HTML", "CSS"
        ],
        experience=[
            {
                "role": "QA Automation Engineer",
                "company": "NashTech Vietnam",
                "period": "2023 - 2026 (2.5 năm kinh nghiệm)",
                "desc": "Xây dựng test framework tự động hóa bằng Python và PyTest để kiểm thử các luồng chức năng Web và REST API. Viết kịch bản kiểm tra cơ sở dữ liệu MySQL và tích hợp test suite vào Git CI/CD pipeline."
            }
        ],
        education=[
            {
                "degree": "Cử nhân Đại học (Bachelor) Hệ thống Thông tin",
                "school": "Đại học Bách Khoa Hà Nội",
                "year": "2019 - 2023",
                "detail": "Tốt nghiệp loại Khá, chứng chỉ ISTQB Foundation Level."
            }
        ]
    )

    print("\n--- All 10 sample CVs generated successfully in 'sample_cvs/' ---")

if __name__ == "__main__":
    generate_all_cvs()
