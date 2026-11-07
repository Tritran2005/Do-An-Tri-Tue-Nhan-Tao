# 🗺️ LỘ TRÌNH PHÁT TRIỂN DỰ ÁN (PROJECT ROADMAP)
## Nền Tảng Tuyển Dụng & Sàng Lọc Hồ Sơ Ứng Viên Ứng Dụng AI (AI Recruitment Portal)

Tài liệu này ghi nhận hiện trạng hoàn thành các giai đoạn ưu tiên (P1, P2, P3) và lộ trình chi tiết cho các hạng mục phát triển tiếp theo (**Ưu tiên 4 & 5: GenAI Integration & Production Scale**).

---

## 📌 BẢNG TỔNG QUAN TIẾN ĐỘ & PHÂN KỲ PHÁT TRIỂN

| Phân kỳ | Tên giai đoạn | Trọng tâm công việc | Trạng thái |
| :--- | :--- | :--- | :---: |
| **P1** | **Quick Wins & Core Fixes** | Regex SĐT/Email, Migration DB, Sửa seed data, Bộ kiểm thử độc lập | <span style="color:green">✅ Hoàn thành 100%</span> |
| **P2** | **Complete Business Features** | Xuất Excel (.xlsx) định dạng cao cấp, Thông báo Email SMTP/HTML, Trang Hồ sơ cá nhân | <span style="color:green">✅ Hoàn thành 100%</span> |
| **P3** | **AI Engine Improvements** | Phát hiện nhồi từ khóa (Keyword Stuffing), Entity Extraction (Tên, Kinh nghiệm), Phone Edge Cases | <span style="color:green">✅ Hoàn thành 100%</span> |
| **P4** | **GenAI & LLM Integration** | Tóm tắt ứng viên bằng LLM, Tự động sinh câu hỏi phỏng vấn từ Missing Skills, AI Market Trends | <span style="color:blue">⏳ Dự kiến tiếp theo</span> |
| **P5** | **Cloud Scale & Analytics** | Triển khai Docker Swarm/K8s, GPU Inference, Redis Vector Caching, Dashboard BI Phễu tuyển dụng | <span style="color:purple">📋 Kế hoạch tương lai</span> |

---

## 🚀 CHI TIẾT CÁC HẠNG MỤC CÒN LẠI (P4 & P5)

### 🌟 ƯU TIÊN 4 (P4): TÍCH HỢP GENAI & LLM (LARGE LANGUAGE MODELS)
> **Mục tiêu:** Nâng tầm hệ thống từ "AI So khớp định lượng (Matching)" sang "AI Trợ lý tuyển dụng thông minh (Generative Recruiter Copilot)".

#### 1. Tự động sinh câu hỏi phỏng vấn kỹ thuật từ Kỹ năng còn thiếu (Missing Skills)
* **Mô tả:** Khi HR mở hồ sơ ứng viên, hệ thống dựa vào danh sách `missing_skills` và yêu cầu JD để gọi LLM (Gemini 1.5 Pro / GPT-4o / Llama 3) sinh ra:
  * 3–5 câu hỏi phỏng vấn kỹ thuật xoáy sâu vào kỹ năng còn thiếu để kiểm tra ứng viên có thực tế hiểu biết hay không.
  * Đáp án gợi ý (Rubric) cho HR không chuyên kỹ thuật có thể chấm điểm câu trả lời ngay tại buổi phỏng vấn.
* **Kiến trúc đề xuất:**
  * Endpoint backend: `POST /jobs/applications/<id>/generate-interview-questions/`
  * Dùng Prompt Engineering cấu trúc hóa dạng JSON Output (`question`, `skill_tested`, `difficulty`, `expected_answer`).
  * Cache kết quả vào trường `interview_questions = models.JSONField()` trong model `Application`.

#### 2. Tóm tắt hồ sơ thông minh (Executive Candidate Summary)
* **Mô tả:** Rút gọn toàn bộ CV dài 3–4 trang thành một đoạn tóm tắt 3 gạch đầu dòng dành riêng cho Ban Giám đốc / Tuyển dụng:
  * Điểm mạnh nổi bật nhất (Core Strengths).
  * Rủi ro tiềm ẩn hoặc lỗ hổng kinh nghiệm (Potential Flags).
  * Kết luận khuyến nghị tuyển dụng (Hiring Recommendation).
* **Kiến trúc:** Tích hợp với `ai_engine/summarizer.py` gọi LangChain / LiteLLM / Gemini API.

#### 3. Phân tích xu hướng kỹ năng thị trường (Talent Market Trends)
* **Mô tả:** Thu thập và phân tích dữ liệu tổng hợp từ tất cả các JD và CV trong hệ thống để đưa ra báo cáo xu hướng:
  * Top 10 kỹ năng có mức cầu cao nhất nhưng nguồn cung ứng viên đang khan hiếm.
  * Mức lương đề xuất tự động dựa trên số năm kinh nghiệm và kỹ năng trọng điểm của JD.

---

### 🌐 ƯU TIÊN 5 (P5): NÂNG CẤP HẠ TẦNG CLOUD, HIỆU NĂNG & PHÂN TÍCH CHUYÊN SÂU
> **Mục tiêu:** Đảm bảo hệ thống vận hành ổn định phục vụ quy mô hàng trăm nghìn hồ sơ tải lên đồng thời và cung cấp góc nhìn dữ liệu toàn diện cho lãnh đạo HR.

#### 1. Đóng gói & Triển khai Cloud Hoàn Chỉnh (Production-Ready Deployment)
* **Mô tả:** Đưa hệ thống lên môi trường đám mây (AWS EC2 / GCP Cloud Run / Render / DigitalOcean) với cơ chế bảo mật cao:
  * Cấu hình Reverse Proxy Nginx với chứng chỉ SSL/TLS tự động (Let's Encrypt).
  * Tách biệt Static/Media storage lên AWS S3 hoặc Cloudinary để bảo vệ tệp CV của ứng viên.
  * Thiết lập giám sát container qua Prometheus & Grafana.

#### 2. Tối ưu hóa suy luận AI (GPU Inference & Embeddings Caching)
* **Mô tả:** Sentence-BERT (`paraphrase-multilingual-MiniLM-L12-v2`) khi chạy CPU trên lượng lớn CV có thể tốn 0.5–1.5s mỗi hồ sơ:
  * Lưu Vector Embeddings của JD vào Redis Vector Store / FAISS / Qdrant để tái sử dụng ngay lập tức mà không cần nhúng lại.
  * Chuyển đổi mô hình PyTorch sang ONNX Runtime hoặc TensorRT để tăng tốc độ suy luận từ 3x – 5x trên GPU hoặc CPU thông thường.

#### 3. Bảng điều khiển phân tích phễu tuyển dụng chuyên sâu (HR Analytics BI Dashboard)
* **Mô tả:** Xây dựng trang Dashboard nâng cao với biểu đồ trực quan hóa dữ liệu (Chart.js / ApexCharts):
  * Phễu chuyển đổi tuyển dụng: `Ứng tuyển` ➔ `Đã xem` ➔ `Chấp thuận` ➔ `Nhận việc`.
  * Biểu đồ phân bổ điểm số AI (Histogram) cho từng vị trí tuyển dụng.
  * Thời gian xử lý hồ sơ trung bình (Time-to-Hire) của từng HR Recruiter.
  * Tỷ lệ ứng viên nộp CV dạng Scan/OCR so với CV văn bản số.

---

## 🛠️ HƯỚNG DẪN KÍCH HOẠT NHANH CÁC TÍNH NĂNG P1 – P3 ĐÃ TRIỂN KHAI

Để áp dụng toàn bộ các nâng cấp từ Ưu tiên 1 đến 3 vào cơ sở dữ liệu hiện tại, vui lòng chạy các lệnh sau:

### 1. Áp dụng Migration cơ sở dữ liệu MySQL:
```bash
python manage.py migrate
```
*(Lệnh này sẽ thực thi `0005_application_extracted_contact_info.py` và `0006_application_keyword_stuffing_flag.py`, bổ sung các cột `extracted_email`, `extracted_phone`, và `keyword_stuffing_flag` vào bảng `jobs_application`)*

### 2. Khởi tạo tài khoản Quản trị & Dữ liệu mẫu (nếu chưa có):
```bash
python seed_hr_demo.py
```
*Tài khoản mặc định: Admin (`admin` / `admin123`), HR (`hr_demo` / `hr123`), Candidate (`candidate_demo` / `candidate123`)*

### 3. Chạy bộ kiểm thử toàn diện AI Engine (Contact, Regex, Entity, Keyword Stuffing):
```bash
python test_contact_extractor.py
```

### 4. Bật chế độ gửi Email thông báo (SMTP):
Mở file `.env` và cấu hình tài khoản Gmail hoặc dịch vụ SMTP của bạn:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=email_cua_ban@gmail.com
EMAIL_HOST_PASSWORD=mat_khau_ung_dung_app_password
```
*(Nếu giữ nguyên mặc định `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`, email sẽ được in trực tiếp ra cửa sổ console/terminal để kiểm tra định dạng)*

---

*Tài liệu được cập nhật tự động bởi Hệ Thống AI Recruitment Portal.*

