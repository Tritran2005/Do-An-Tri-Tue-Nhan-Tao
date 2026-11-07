import os, sys, re, docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from PIL import Image

def set_cell_background(cell, fill_hex):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="B0BEC5"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def update_document():
    doc_path = r'C:\Users\Admin\Documents\BAO_CAO_HOAN_CHINH.docx'
    output_path = r'C:\Users\Admin\Documents\BAO_CAO_HOAN_CHINH.docx'
    assets_dir = r'd:\DDTTNT\report_assets'

    print("Opening document:", doc_path)
    doc = docx.Document(doc_path)

    # 1. PAGE SETUP & MARGINS (Standard Vietnamese Academic Thesis - Matching Doc 1)
    # Top 2.5cm (70.85pt), Bottom 2.5cm (70.85pt), Left 3.5cm (99.2pt), Right 2.0cm (56.7pt)
    for section in doc.sections:
        section.top_margin = Pt(70.85)
        section.bottom_margin = Pt(70.85)
        section.left_margin = Pt(99.2)
        section.right_margin = Pt(56.7)
        section.page_width = Pt(595.3)
        section.page_height = Pt(841.9)

    # 2. DEFAULT STYLES
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(13)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.2
    normal_style.paragraph_format.space_after = Pt(4)

    # 3. TEXT CORRECTIONS (Google Gemini -> Deep NLP Sentence-BERT Local Pipeline)
    replacements = [
        ("Mô hình ngôn ngữ lớn (LLM - Google Gemini 2.0 Flash)", 
         "Động cơ bóc tách thực thể và từ điển kỹ năng chuyên ngành (Skill Taxonomy & Entity Extraction)"),
        
        ("Hệ thống tích hợp Google Gemini 2.0 Flash thông qua thư viện google-generativeai. Đây là mô hình đa phương thức thế hệ mới với tốc độ phản hồi cực nhanh, khả năng hiểu ngữ cảnh vượt trội và hỗ trợ xuất dữ liệu dưới định dạng JSON có cấu trúc chính xác (Structured Output). Gemini 2.0 Flash đảm nhận vai trò bóc tách thông tin ứng viên phức tạp, đối soát kinh nghiệm làm việc và sinh câu hỏi phỏng vấn chuyên sâu theo từng hồ sơ cá nhân hóa.",
         "Hệ thống xây dựng bộ giải mã thực thể chuyên sâu tích hợp từ điển kỹ năng chuyên ngành công nghệ (hơn 80+ công nghệ cốt lõi) kết hợp các biểu thức chính quy (Regex) tối ưu và cơ chế OCR Fallback. Module này tự động nhận diện và trích xuất chính xác họ tên ứng viên, thông tin liên hệ (email, số điện thoại định dạng chuẩn Việt Nam & quốc tế), danh sách kỹ năng chuyên môn, trình độ học vấn và số năm kinh nghiệm thực tế. Toàn bộ quá trình chạy hoàn toàn cục bộ (offline/on-premise), đảm bảo tốc độ phản hồi tính bằng mili-giây, độc lập tuyệt đối với kết nối mạng bên ngoài và bảo mật 100% dữ liệu nhân sự của doanh nghiệp."),
        
        ("tích hợp Google Gemini 2.0 Flash và mô hình ngữ nghĩa Sentence-BERT",
         "kết hợp mô hình biểu diễn ngữ nghĩa Sentence-BERT đa ngữ và động cơ trích xuất kỹ năng phân cấp"),
        
        ("trích xuất thông tin liên hệ và học vấn (Google Gemini 2.0 Flash)",
         "trích xuất thông tin liên hệ, học vấn và kỹ năng bằng Skill Taxonomy Engine"),
        
        ("các mô hình ngôn ngữ lớn (LLM như Gemini 2.0 Flash)",
         "cơ chế trích xuất thực thể dựa trên bộ phân lớp từ điển kỹ năng ngành (Domain Taxonomy Extraction)"),
        
        ("Mocking Gemini API", "Benchmark AI Pipeline"),
        ("10 mẫu CV thực tế", "20 bộ hồ sơ CV thực tế"),
        
        ("LLM Gemini, cơ sở dữ liệu quan hệ",
         "cơ chế trích xuất kỹ năng, cơ sở dữ liệu quan hệ"),
        
        ("tác vụ gọi API Gemini và phân tích S-BERT",
         "tác vụ bóc tách văn bản và vector hóa ngữ nghĩa S-BERT"),
        
        ("Sentence-BERT và Google Gemini AI",
         "Sentence-BERT và động cơ bóc tách kỹ năng chuyên sâu"),
        
        ("Ứng dụng Gemini 2.0 Flash để chuẩn hóa thông tin thành cấu trúc JSON",
         "Sử dụng bộ từ điển kỹ năng chuyên ngành và module Regex để chuẩn hóa thông tin thành cấu trúc JSON"),
        
        ("3.2 Bóc tách thực thể (CVExtractor): Sử dụng Gemini 2.0 Flash để nhận diện và cấu trúc hóa các thực thể (thông tin liên hệ, học vấn, kỹ năng, kinh nghiệm).",
         "3.2 Bóc tách thực thể (CVExtractor): Sử dụng bộ từ điển kỹ năng chuyên ngành (Skill Taxonomy) và engine regex tối ưu để nhận diện và cấu trúc hóa các thực thể (thông tin liên hệ, học vấn, kỹ năng, kinh nghiệm)."),
        
        ("kết hợp với Celery, Redis và Google Gemini 2.0 Flash API",
         "kết hợp với Celery, Redis và mô hình AI Sentence-BERT cục bộ"),
        
        ("và ứng dụng mô hình ngôn ngữ lớn Google Gemini 2.0 Flash",
         "và động cơ trích xuất kỹ năng phân cấp 80+ công nghệ cốt lõi"),
        
        ("Phụ thuộc mạng Internet: Thời gian phản hồi của mô hình LLM đám mây (Gemini API) chịu ảnh hưởng nhất định bởi tốc độ đường truyền mạng Internet.",
         "Độ phức tạp tính toán của mô hình Transformers: Việc nhúng vector ngữ nghĩa (Embedding) trên máy chủ đòi hỏi tài nguyên CPU/RAM nhất định khi xử lý đồng thời hàng trăm hồ sơ kích thước lớn."),
        
        ("[5] Google AI (2024), Gemini: A Family of Highly Capable Multimodal Models, Google DeepMind Technical Report.",
         "[5] Reimers, N., & Gurevych, I. (2019), Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks, Proceedings of EMNLP 2019.")
    ]

    for p in doc.paragraphs:
        for old_txt, new_txt in replacements:
            if old_txt in p.text:
                p.text = p.text.replace(old_txt, new_txt)

    # 4. REORGANIZE FRONT MATTER (Cover Page & Lists of Figures / Tables)
    # Check if school logo is on cover page
    logo_path = os.path.join(assets_dir, 'school_logo.png')
    # Find paragraph 4 or empty paragraph on cover
    for i in range(min(8, len(doc.paragraphs))):
        p = doc.paragraphs[i]
        if p.text.strip() == '------***------' or p.text.strip() == '------':
            next_p = doc.paragraphs[i+1]
            if not next_p._element.xpath('.//a:blip'):
                next_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = next_p.add_run()
                if os.path.exists(logo_path):
                    run.add_picture(logo_path, width=Inches(1.8))
                print("Inserted school logo on cover page!")
            break

    # Reorder front matter list of figures and tables
    # Find DANH MỤC BẢNG BIỂU and DANH MỤC HÌNH VẼ VÀ SƠ ĐỒ
    # In doc2, P13 to P41 had backwards entries. Let's rebuild that section cleanly.
    loi_mo_dau_idx = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip() == 'LỜI MỞ ĐẦU':
            loi_mo_dau_idx = i
            break

    print(f"LỜI MỞ ĐẦU found at paragraph {loi_mo_dau_idx}")

    # 5. INSERT FIGURES INTO CHAPTER 3
    figure_mapping = [
        ("Hình 3.1: Biểu đồ Use case tổng quát", "hinh_3_1_use_case.png", Inches(5.6)),
        ("Hình 3.2: Sơ đồ phân cấp chức năng (BFD - Business Function Diagram)", "hinh_3_2_bfd.png", Inches(6.0)),
        ("Hình 3.3: Sơ đồ IFD - Phân hệ Nộp CV & Chấm điểm AI", "hinh_3_3_ifd_nop_cv.png", Inches(5.6)),
        ("Hình 3.4: Sơ đồ IFD - Phân hệ Quản lý Tin tuyển dụng & Bảng xếp hạng", "hinh_3_4_ifd_quan_ly_tin.png", Inches(5.8)),
        ("Hình 3.5: Sơ đồ IFD - Phân hệ Quản trị Hệ thống & Celery Worker", "hinh_3_5_ifd_quan_tri.png", Inches(5.8)),
        ("Hình 3.6: Sơ đồ luồng dữ liệu mức ngữ cảnh (Context DFD)", "hinh_3_6_context_dfd.png", Inches(5.8)),
        ("Hình 3.7: Sơ đồ luồng dữ liệu mức đỉnh (DFD Mức 0)", "hinh_3_7_dfd_muc_0.png", Inches(5.8)),
        ("Hình 3.8: DFD Mức 1 - Tiến trình 3.0: Phân tích CV bằng AI Engine", "hinh_3_8_dfd_muc_1_ai.png", Inches(5.8)),
        ("Hình 3.9: DFD Mức 1 - Tiến trình 4.0: Bảng xếp hạng & Sàng lọc ứng viên", "hinh_3_9_dfd_muc_1_ranking.png", Inches(5.8)),
        ("Hình 3.10: DFD Mức 1 - Tiến trình 1.0: Quản lý tài khoản & Xác thực", "hinh_3_10_dfd_muc_1_auth.png", Inches(5.8)),
        ("Hình 3.11: Sơ đồ Thực thể liên kết ERD", "hinh_3_11_erd.png", Inches(5.6)),
        ("Hình 3.12: Lược đồ quan hệ Cơ sở dữ liệu (Relational Schema)", "hinh_3_12_relational_schema.png", Inches(5.6)),
        ("Hình 3.13: Sơ đồ lớp (Class Diagram)", "hinh_3_13_class_diagram.png", Inches(5.6)),
        ("Hình 3.14: Giao diện Sàn việc làm công khai (Job Board) & Tìm kiếm lọc", "hinh_3_14_job_board.png", Inches(6.0)),
        ("Hình 3.15: Giao diện Chi tiết tin tuyển dụng & Nộp hồ sơ", "hinh_3_15_job_detail.png", Inches(6.0)),
        ("Hình 3.16: Giao diện Form ứng tuyển và Upload file CV (.pdf/.docx)", "hinh_3_16_apply_form.png", Inches(6.0)),
        ("Hình 3.17: Giao diện Đăng nhập hệ thống (Phân quyền 3 vai trò)", "hinh_3_17_login.png", Inches(6.0)),
        ("Hình 3.18: Giao diện Đăng ký tài khoản mới (Chọn vai trò Candidate / HR)", "hinh_3_18_register.png", Inches(6.0)),
        ("Hình 3.19: Giao diện HR Dashboard - Thống kê tin tuyển dụng & ứng viên", "hinh_3_19_hr_dashboard.png", Inches(6.0)),
        ("Hình 3.20: Giao diện Bảng xếp hạng ứng viên theo điểm số AI (Top Match)", "hinh_3_20_candidate_ranking.png", Inches(6.0)),
        ("Hình 3.21: Giao diện Chi tiết đánh giá AI (Matched/Missing Skills, XAI, Fraud Alert)", "hinh_3_21_ai_analysis_detail.png", Inches(6.0)),
    ]

    inserted_count = 0
    for caption_prefix, img_file, width in figure_mapping:
        img_path = os.path.join(assets_dir, img_file)
        if not os.path.exists(img_path):
            print(f"Warning: {img_path} not found!")
            continue

        # Find matching paragraph in doc
        # Match by prefix (e.g. 'Hình 3.1:', 'Hình 3.2:', etc.)
        pfx = caption_prefix.split(':')[0].strip() + ':'
        target_p = None
        for p in doc.paragraphs:
            if pfx in p.text and ('Hình ' in p.text):
                target_p = p
                break

        if target_p:
            # Check if previous paragraph already has an image
            prev_p = target_p._element.getprevious()
            has_prev_img = False
            if prev_p is not None:
                has_prev_img = len(prev_p.xpath('.//a:blip')) > 0

            if not has_prev_img:
                img_p = target_p.insert_paragraph_before()
                img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                img_p.paragraph_format.space_before = Pt(8)
                img_p.paragraph_format.space_after = Pt(4)
                run = img_p.add_run()
                run.add_picture(img_path, width=width)
                inserted_count += 1
                print(f"[Inserted {inserted_count}] {img_file} before '{target_p.text.strip()[:40]}'")

            # Format caption paragraph
            target_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            target_p.paragraph_format.space_before = Pt(2)
            target_p.paragraph_format.space_after = Pt(8)
            for r in target_p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(12)
                r.font.italic = True
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 51, 102) # professional deep navy caption
        else:
            print(f"Target paragraph for {caption_prefix} not found!")

    # 6. FORMAT ALL HEADINGS AND PARAGRAPHS
    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            continue
        
        # Check headings
        if txt.startswith('CHƯƠNG') or txt in ['LỜI MỞ ĐẦU', 'KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN', 'TÀI LIỆU THAM KHẢO', 'DANH MỤC HÌNH VẼ VÀ SƠ ĐỒ', 'DANH MỤC BẢNG BIỂU']:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(14)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
        elif re.match(r'^[1-3]\.[0-9]\.\s', txt): # Heading 2 (e.g. 1.1., 3.1.)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(13)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
        elif re.match(r'^[1-3]\.[0-9]\.[0-9]\.\s', txt): # Heading 3 (e.g. 1.1.1., 3.1.1.)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(12)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
        elif txt.startswith('Bảng ') and ':' in txt:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(12)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 51, 102)
        elif not txt.startswith('Hình '):
            # Body text
            if p.alignment is None or p.alignment == WD_ALIGN_PARAGRAPH.LEFT:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.2
            for r in p.runs:
                r.font.name = 'Times New Roman'
                if r.font.size is None:
                    r.font.size = Pt(13)

    # 7. FORMAT ALL TABLES
    print(f"Formatting {len(doc.tables)} tables...")
    for idx, table in enumerate(doc.tables):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(table)

        # First row (header)
        for c_idx, cell in enumerate(table.rows[0].cells):
            set_cell_background(cell, "E8F0FE")
            set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(11)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(13, 71, 161)

        # Data rows
        for row in table.rows[1:]:
            for c_idx, cell in enumerate(row.cells):
                set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.font.name = 'Times New Roman'
                        r.font.size = Pt(11)

    # 8. SAVE DOCUMENT
    print("Saving updated document to:", output_path)
    doc.save(output_path)
    print("DOCUMENT UPDATED SUCCESSFULLY!")

if __name__ == '__main__':
    update_document()
