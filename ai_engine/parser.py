import os
import re
import logging
import pdfplumber
import docx
from PIL import Image

logger = logging.getLogger(__name__)

# Cờ kiểm tra tính khả dụng của thư viện OCR
HAS_TESSERACT = False
HAS_EASYOCR = False

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    pass

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    pass


def clean_text(text: str) -> str:
    """
    Làm sạch văn bản thô:
    - Loại bỏ ký tự điều khiển/null byte
    - Chuẩn hóa khoảng trắng và dòng trống liên tiếp
    """
    if not text:
        return ""
    # Loại bỏ null bytes
    text = text.replace('\x00', ' ')
    # Chuẩn hóa các dấu xuống dòng và khoảng trắng
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_text_via_ocr(image_input) -> str:
    """
    Trích xuất văn bản từ hình ảnh (PIL Image hoặc đường dẫn tệp) bằng Tesseract OCR hoặc EasyOCR.
    Tự động áp dụng ngôn ngữ tiếng Việt + tiếng Anh.
    """
    ocr_text = ""

    # Nếu đầu vào là đường dẫn tệp
    if isinstance(image_input, str):
        if not os.path.exists(image_input):
            return ""
        try:
            image_obj = Image.open(image_input)
        except Exception as e:
            logger.warning(f"Không thể mở file ảnh để OCR: {e}")
            return ""
    else:
        image_obj = image_input

    # 1. Thử nghiệm với PyTesseract (nhanh, chuẩn khi có tesseract-ocr)
    if HAS_TESSERACT:
        try:
            # Thử với đa ngữ vie + eng, nếu thiếu data thì fallback sang eng
            try:
                ocr_text = pytesseract.image_to_string(image_obj, lang='vie+eng')
            except Exception:
                ocr_text = pytesseract.image_to_string(image_obj, lang='eng')
            if ocr_text.strip():
                return clean_text(ocr_text)
        except Exception as err:
            logger.warning(f"PyTesseract OCR thất bại: {err}")

    # 2. Thử nghiệm với EasyOCR (Deep Learning OCR chuyên dụng)
    if HAS_EASYOCR:
        try:
            import numpy as np
            reader = easyocr.Reader(['vi', 'en'], gpu=False)
            img_arr = np.array(image_obj)
            results = reader.readtext(img_arr, detail=0)
            ocr_text = " ".join(results)
            if ocr_text.strip():
                return clean_text(ocr_text)
        except Exception as err:
            logger.warning(f"EasyOCR thất bại: {err}")

    if not HAS_TESSERACT and not HAS_EASYOCR:
        logger.info(
            "Gợi ý: Cài đặt 'pip install pytesseract' hoặc 'pip install easyocr' "
            "để kích hoạt khả năng bóc tách CV scan dạng ảnh tự động."
        )

    return clean_text(ocr_text)


def extract_text_from_pdf_ocr_fallback(file_path: str) -> str:
    """
    Quét từng trang PDF, render thành hình ảnh độ phân giải cao (200 DPI)
    và chạy động cơ OCR để bóc tách chữ từ các CV scan/ảnh chụp.
    """
    logger.info(f"Bắt đầu OCR Fallback cho tệp PDF scan: {file_path}")
    ocr_parts = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                try:
                    # pdfplumber có sẵn phương thức to_image() trả về PIL Image
                    page_img = page.to_image(resolution=200).original
                    page_text = extract_text_via_ocr(page_img)
                    if page_text:
                        ocr_parts.append(page_text)
                except Exception as page_err:
                    logger.warning(f"Lỗi OCR tại trang {page_idx + 1}: {page_err}")

        return clean_text("\n".join(ocr_parts))
    except Exception as e:
        logger.error(f"Lỗi khi thực hiện OCR fallback cho PDF {file_path}: {e}")
        return ""


def extract_text_from_pdf(file_path: str) -> str:
    """
    Trích xuất toàn bộ văn bản từ tệp PDF sử dụng pdfplumber.
    Tự động kích hoạt OCR Fallback nếu phát hiện PDF scan (văn bản < 50 ký tự).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file PDF tại: {file_path}")

    text_parts = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                
                # Bóc tách thêm nội dung bảng biểu (tables) nếu có
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        row_text = " | ".join([str(cell) for cell in row if cell])
                        if row_text:
                            text_parts.append(row_text)

        full_text = clean_text("\n".join(text_parts))

        # Kiểm tra nếu PDF là ảnh scan (dưới 50 ký tự) -> Tự động kích hoạt OCR Fallback
        if len(full_text) < 50:
            logger.warning(
                f"Tệp PDF '{file_path}' có dung lượng chữ quá ít ({len(full_text)} ký tự). "
                "Hệ thống tự động kích hoạt chế độ OCR (Optical Character Recognition)..."
            )
            ocr_text = extract_text_from_pdf_ocr_fallback(file_path)
            if len(ocr_text) > len(full_text):
                return ocr_text

        return full_text
    except Exception as e:
        logger.error(f"Lỗi khi đọc file PDF {file_path}: {e}")
        raise ValueError(f"Không thể xử lý file PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """
    Trích xuất toàn bộ văn bản từ tệp DOCX sử dụng python-docx.
    Bao gồm cả các đoạn văn (paragraphs) và các ô trong bảng (tables).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file DOCX tại: {file_path}")

    try:
        doc = docx.Document(file_path)
        text_parts = []

        # 1. Trích xuất các đoạn văn bản chính
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        # 2. Trích xuất nội dung trong các bảng (kinh nghiệm/học vấn hay đặt trong table)
        for table in doc.tables:
            for row in table.rows:
                row_content = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_content:
                    # Loại bỏ trùng lặp nếu ô bị merge
                    dedup_row = list(dict.fromkeys(row_content))
                    text_parts.append(" | ".join(dedup_row))

        full_text = "\n".join(text_parts)
        return clean_text(full_text)
    except Exception as e:
        logger.error(f"Lỗi khi đọc file DOCX {file_path}: {e}")
        raise ValueError(f"Không thể xử lý file DOCX: {str(e)}")


def extract_text_from_file(file_path: str) -> str:
    """
    Hàm Dispatcher trung tâm tự động nhận diện phần mở rộng (.pdf, .docx, .png, .jpg)
    và gọi module parser tương ứng, kèm OCR Fallback thông minh.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ('.docx', '.doc'):
        if ext == '.doc':
            # doc cũ cần thông báo hoặc chuyển đổi, docx được hỗ trợ trực tiếp
            raise ValueError("Định dạng .doc cũ không được hỗ trợ trực tiếp. Vui lòng chuyển sang .docx hoặc .pdf.")
        return extract_text_from_docx(file_path)
    elif ext in ('.png', '.jpg', '.jpeg'):
        text = extract_text_via_ocr(file_path)
        if not text:
            raise ValueError(
                f"Không thể trích xuất chữ từ tệp hình ảnh '{ext}'. "
                "Vui lòng đảm bảo tệp ảnh rõ nét hoặc cài đặt thư viện 'easyocr'/'pytesseract'."
            )
        return text
    else:
        raise ValueError(f"Định dạng tệp '{ext}' không được hỗ trợ. Chỉ hỗ trợ .pdf, .docx, .png, .jpg.")

