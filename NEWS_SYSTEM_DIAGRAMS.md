# CHƯƠNG 3: THIẾT KẾ CƠ SỞ DỮ LIỆU VÀ DEMO ỨNG DỤNG
## Hệ Thống Sàng Lọc & Đánh Giá CV Bằng Trí Tuệ Nhân Tạo
### (AI-Powered Resume Screener & Recruiter Portal)

---

## 3.1. Biểu đồ Use Case tổng quát

### 3.1.1. Phân tích các Tác nhân (Actors) trong hệ thống

Hệ thống có 3 tác nhân chính:

| Tác nhân | Mô tả |
|---|---|
| **Ứng viên (Candidate)** | Tìm việc, nộp CV, xem kết quả AI, theo dõi trạng thái hồ sơ |
| **Nhà tuyển dụng (HR Recruiter)** | Đăng tin, chấm điểm AI, quản lý ứng viên, xuất báo cáo |
| **Quản trị viên (System Admin)** | Quản lý người dùng, phân quyền 3-Tier RBAC, giám sát hệ thống |

```mermaid
graph LR
    UV["🎓 Ứng viên\n(Candidate)"]
    HR["🏢 Nhà tuyển dụng\n(HR Recruiter)"]
    AD["👑 Quản trị viên\n(System Admin)"]

    subgraph HT["Hệ Thống Sàng Lọc CV Bằng Trí Tuệ Nhân Tạo"]
        UC1["Xem sàn việc làm\n(Job Board)"]
        UC2["Nộp CV ứng tuyển\n(.pdf / .docx / .png)"]
        UC3["Xem kết quả AI & XAI\n(Báo cáo 4 trụ cột)"]
        UC4["Theo dõi trạng thái\nhồ sơ đã nộp"]
        UC5["Chỉnh sửa hồ sơ\ncá nhân (Profile)"]
        UC6["Đăng ký / Đăng nhập"]

        UC7["Đăng tin tuyển dụng\n(Job Posting CRUD)"]
        UC8["Xem bảng xếp hạng\nứng viên AI"]
        UC9["Cập nhật trạng thái\nhàng loạt (Batch Action)"]
        UC10["Tải lên CV hàng loạt\n(Batch Upload)"]
        UC11["Sàng lọc đa vị trí\n(Multi-Job Screening)"]
        UC12["Xuất báo cáo\nExcel / CSV"]
        UC13["Xem HR Dashboard\n(Thống kê tổng quan)"]

        UC14["Quản lý người dùng\n& Phân quyền RBAC"]
        UC15["Truy cập\nDjango Admin Portal"]
    end

    UV --> UC1
    UV --> UC2
    UV --> UC3
    UV --> UC4
    UV --> UC5
    UV --> UC6

    HR --> UC7
    HR --> UC8
    HR --> UC9
    HR --> UC10
    HR --> UC11
    HR --> UC12
    HR --> UC13
    HR --> UC6

    AD --> UC14
    AD --> UC15
    AD --> UC6

    UC2 -.->|include| UC6
    UC7 -.->|include| UC6
    UC8 -.->|include| UC2
```

> **Hình 3.1: Biểu đồ Use Case tổng quát**

---

## 3.2. Sơ đồ phân cấp chức năng (BFD – Business Function Diagram)

```mermaid
graph TD
    ROOT(["PHÂN TÍCH THIẾT KẾ HỆ THỐNG\nSàng Lọc & Đánh Giá CV\nBằng Trí Tuệ Nhân Tạo"])

    ROOT --> F1["1. Quản lý\ntài khoản"]
    ROOT --> F2["2. Quản lý\ntin tuyển dụng"]
    ROOT --> F3["3. Phân tích\nCV bằng AI"]
    ROOT --> F4["4. Cổng ứng\nviên"]
    ROOT --> F5["5. Cổng nhà\ntuyển dụng"]
    ROOT --> F6["6. Quản trị\nhệ thống"]

    F1 --> F11["1.1 Đăng ký\ntài khoản"]
    F1 --> F12["1.2 Đăng nhập\n/ Đăng xuất"]
    F1 --> F13["1.3 Chỉnh sửa\nhồ sơ cá nhân"]
    F1 --> F14["1.4 Phân quyền\nRBAC 3 cấp"]

    F2 --> F21["2.1 Tạo tin\ntuyển dụng (JD)"]
    F2 --> F22["2.2 Chỉnh sửa\n/ Xóa tin đăng"]
    F2 --> F23["2.3 Cấu hình\nkỹ năng & yêu cầu"]
    F2 --> F24["2.4 Kích hoạt\n/ Ẩn tin đăng"]

    F3 --> F31["3.1 Trích xuất\nvăn bản CV\n(Parser + OCR)"]
    F3 --> F32["3.2 Nhận diện\nkỹ năng IT\n(80+ Taxonomy)"]
    F3 --> F33["3.3 Tính điểm\nS-BERT Semantic\nMatching"]
    F3 --> F34["3.4 Chấm điểm\n4 trụ cột S_total"]
    F3 --> F35["3.5 Phát hiện\nKeyword Stuffing"]

    F4 --> F41["4.1 Xem sàn\nviệc làm"]
    F4 --> F42["4.2 Nộp CV\nứng tuyển"]
    F4 --> F43["4.3 Xem kết quả\nAI & AI Coach"]
    F4 --> F44["4.4 Theo dõi\nhồ sơ đã nộp"]

    F5 --> F51["5.1 HR Dashboard\n(Thống kê)"]
    F5 --> F52["5.2 Bảng xếp\nhạng ứng viên AI"]
    F5 --> F53["5.3 Sàng lọc\nđa vị trí"]
    F5 --> F54["5.4 Tải CV\nhàng loạt"]
    F5 --> F55["5.5 Xuất báo cáo\nExcel / CSV"]

    F6 --> F61["6.1 Quản lý\nngười dùng"]
    F6 --> F62["6.2 Django\nAdmin Portal"]
    F6 --> F63["6.3 Giám sát\nhàng đợi Celery"]
    F6 --> F64["6.4 Cấu hình\nhệ thống"]
```

> **Hình 3.2: Sơ đồ phân cấp chức năng (BFD – Business Function Diagram)**

---

## 3.3. Sơ đồ luồng thông tin (IFD)

### 3.3.1. Sơ đồ IFD – Phân hệ Nộp CV & Chấm điểm AI

```mermaid
flowchart TD
    subgraph col_time["THỜI ĐIỂM"]
        T1["Ứng viên\ntìm việc"]
        T2["Nộp CV"]
        T3["AI xử lý\n(< 1.8s)"]
        T4["Phản hồi\ntức thì"]
    end

    subgraph col_uv["ỨNG VIÊN"]
        UV1["Tìm kiếm\nviệc làm"]
        UV2["Chọn vị trí\n& Upload CV\n(.pdf/.docx/.png)"]
        UV3["Xem kết quả\nAI & điểm 4 trụ cột"]
        UV4["Nhận lời khuyên\ntừ AI Career Coach"]
    end

    subgraph col_sys["HỆ THỐNG AI ENGINE"]
        S1["Parser:\nbóc tách văn bản\n+ OCR Fallback"]
        S2["Extractor:\nNhận diện 80+\nkỹ năng IT"]
        S3["Matcher:\nS-BERT Cosine\nSimilarity"]
        S4["Evaluator:\nTính S_total\n4 trụ cột"]
        S5["Lưu kết quả\nvào Application DB"]
    end

    subgraph col_hr["NHÂN TUYỂN DỤNG (HR)"]
        HR1["Xem Bảng\nxếp hạng AI"]
        HR2["Lọc &\nSo sánh ứng viên"]
        HR3["Cập nhật\ntrạng thái hồ sơ"]
    end

    T1 --- UV1
    UV1 --> UV2
    T2 --- UV2
    UV2 --> S1
    T3 --- S1
    S1 --> S2 --> S3 --> S4 --> S5
    S5 --> UV3
    T4 --- UV3
    UV3 --> UV4
    S5 --> HR1
    HR1 --> HR2 --> HR3
```

> **Hình 3.3: Sơ đồ IFD – Phân hệ Nộp CV & Chấm điểm AI**

---

### 3.3.2. Sơ đồ IFD – Phân hệ Quản lý Tin tuyển dụng & Bảng xếp hạng

```mermaid
flowchart TD
    subgraph col_time["THỜI ĐIỂM"]
        T1["Mở đợt\ntuyển dụng"]
        T2["Tiếp nhận\nhồ sơ"]
        T3["Sàng lọc\nAI"]
        T4["Ra quyết\nđịnh"]
    end

    subgraph col_hr["NHÂN TUYỂN DỤNG (HR)"]
        HR1["Tạo bài đăng JD\n(Tiêu đề, Kỹ năng,\nKN tối thiểu, Lương)"]
        HR2["Xem CV\nhàng loạt đến"]
        HR3["Xem bảng xếp hạng\nAI tự động"]
        HR4["Dùng bộ lọc &\ntìm kiếm"]
        HR5["Cập nhật trạng thái\n(Accept/Reject/Review)"]
        HR6["Xuất Excel/CSV\nbáo cáo"]
    end

    subgraph col_sys["HỆ THỐNG"]
        S1["Lưu JobPosting\nvào DB"]
        S2["Nhận CV &\nkích hoạt AI Engine"]
        S3["Sắp xếp theo\nmatch_score DESC"]
        S4["Gắn huy chương\n🥇🥈🥉 TOP 3"]
        S5["Cảnh báo\n⚠️ Keyword Stuffing"]
        S6["Gửi email\nthông báo tự động"]
    end

    T1 --- HR1
    HR1 --> S1
    T2 --- HR2
    HR2 --> S2
    S2 --> S3
    T3 --- S3
    S3 --> S4
    S3 --> S5
    S4 --> HR3
    S5 --> HR3
    HR3 --> HR4
    T4 --- HR4
    HR4 --> HR5
    HR5 --> S6
    HR5 --> HR6
```

> **Hình 3.4: Sơ đồ IFD – Phân hệ Quản lý Tin tuyển dụng & Bảng xếp hạng**

---

### 3.3.3. Sơ đồ IFD – Phân hệ Quản trị Hệ thống & Hàng đợi Celery

```mermaid
flowchart TD
    subgraph col_admin["QUẢN TRỊ VIÊN (System Admin)"]
        A1["Đăng nhập\nAdmin Portal"]
        A2["Quản lý người dùng\n& Phân quyền RBAC"]
        A3["Xem nhật ký\nhoạt động"]
        A4["Giám sát\nCelery Workers"]
    end

    subgraph col_sys["HỆ THỐNG"]
        S1["Xác thực\nSuperuser"]
        S2["CRUD User:\ncandidate / hr / admin"]
        S3["Ghi log\nhành động"]
        S4["Monitor hàng đợi\nRedis + Celery"]
        S5["Fallback đồng bộ\nnếu Celery offline"]
    end

    subgraph col_db["CƠ SỞ DỮ LIỆU"]
        DB1[("MySQL\nai_recruitment_db")]
        DB2[("Redis 7\nTask Queue")]
        DB3[("File Storage\nmedia/cv_uploads/")]
    end

    A1 --> S1 --> A2
    A2 --> S2 --> DB1
    S2 --> S3 --> DB1
    A3 --> DB1
    A4 --> S4 --> DB2
    S4 --> S5
    DB2 --> DB1
    DB3 --> DB1
```

> **Hình 3.5: Sơ đồ IFD – Phân hệ Quản trị Hệ thống & Hàng đợi Celery**

---

## 3.4. Sơ đồ Luồng dữ liệu (DFD – Data Flow Diagram)

### 3.4.1. Sơ đồ luồng dữ liệu mức ngữ cảnh (Context DFD)

```mermaid
flowchart TD
    UV["Ứng viên\n(Candidate)"]
    HR["Nhà tuyển dụng\n(HR Recruiter)"]
    AD["Quản trị viên\n(System Admin)"]

    HT(["Hệ Thống Sàng Lọc CV\nBằng Trí Tuệ Nhân Tạo\n(AI-Powered Recruiter Portal)"])

    UV -->|"Nộp file CV (.pdf/.docx/.png)\nThông tin ứng tuyển"| HT
    HT -->|"Điểm AI 4 trụ cột & XAI\nLời khuyên AI Career Coach\nTrạng thái hồ sơ"| UV

    HR -->|"Bài đăng tuyển dụng (JD)\nKỹ năng & yêu cầu\nCập nhật trạng thái ứng viên"| HT
    HT -->|"Bảng xếp hạng AI\nBáo cáo Excel/CSV\nThống kê HR Dashboard"| HR

    AD -->|"Quản lý người dùng\nPhân quyền RBAC"| HT
    HT -->|"Nhật ký hệ thống\nTrạng thái hàng đợi Celery"| AD
```

> **Hình 3.6: Sơ đồ luồng dữ liệu mức ngữ cảnh (Context DFD)**

---

### 3.4.2. Sơ đồ luồng dữ liệu mức đỉnh (DFD Mức 0)

```mermaid
flowchart TD
    UV["Ứng viên"]
    HR["HR Recruiter"]
    AD["System Admin"]

    P1(["1.0\nQuản lý\ntài khoản\n& xác thực"])
    P2(["2.0\nQuản lý\ntin tuyển dụng"])
    P3(["3.0\nPhân tích CV\nbằng AI Engine"])
    P4(["4.0\nBảng xếp hạng\n& Sàng lọc"])
    P5(["5.0\nXuất báo cáo\n& Thông báo"])
    P6(["6.0\nQuản trị\nhệ thống"])

    DS_USER[("Người dùng\n(User)")]
    DS_JOB[("Tin tuyển dụng\n(JobPosting)")]
    DS_APP[("Hồ sơ ứng tuyển\n(Application)")]
    DS_FILE[("File CV\n(media/cv_uploads/)")]

    UV -->|"Thông tin đăng ký/đăng nhập"| P1
    HR -->|"Thông tin đăng ký/đăng nhập"| P1
    P1 -->|"Lưu User profile"| DS_USER
    P1 -->|"Thông tin phiên làm việc"| DS_USER

    HR -->|"Thông tin JD & kỹ năng"| P2
    P2 -->|"Lưu tin tuyển dụng"| DS_JOB
    DS_JOB -->|"Danh sách việc làm"| UV

    UV -->|"File CV & chọn vị trí"| P3
    DS_JOB -->|"Yêu cầu JD & kỹ năng"| P3
    P3 -->|"Upload file CV"| DS_FILE
    P3 -->|"Lưu kết quả AI & điểm số"| DS_APP

    DS_APP -->|"Dữ liệu ứng viên"| P4
    HR -->|"Bộ lọc & yêu cầu xem"| P4
    P4 -->|"Bảng xếp hạng AI"| HR

    DS_APP -->|"Dữ liệu hồ sơ"| P5
    HR -->|"Yêu cầu xuất báo cáo"| P5
    P5 -->|"File Excel/CSV"| HR

    AD -->|"Lệnh quản trị & phân quyền"| P6
    P6 -->|"Cập nhật quyền User"| DS_USER
    P6 -->|"Nhật ký hệ thống"| AD
```

> **Hình 3.7: Sơ đồ luồng dữ liệu mức đỉnh (DFD Mức 0)**

---

### 3.4.3. Sơ đồ luồng dữ liệu mức dưới đỉnh (DFD Mức 1)

#### Phân rã tiến trình 3.0: Phân tích CV bằng AI Engine

```mermaid
flowchart TD
    UV["Ứng viên"]

    P31(["3.1 Trích xuất\nvăn bản CV\n(parser.py)"])
    P32(["3.2 Nhận diện\nkỹ năng & liên hệ\n(extractor.py)"])
    P33(["3.3 Tính toán\nngữ nghĩa S-BERT\n(matcher.py)"])
    P34(["3.4 Chấm điểm\ntổng hợp S_total\n(evaluator.py)"])

    DS_JOB[("Tin tuyển dụng\n(JobPosting)")]
    DS_APP[("Hồ sơ ứng tuyển\n(Application)")]
    DS_FILE[("File CV\n(media/)")]

    UV -->|"Upload CV\n(.pdf/.docx/.png)"| P31
    P31 -->|"Lưu file"| DS_FILE
    P31 -->|"Văn bản thô\n(parsed_text)"| P32

    DS_JOB -->|"Yêu cầu kỹ năng JD"| P32
    DS_JOB -->|"Nội dung JD"| P33

    P32 -->|"Danh sách kỹ năng,\nEmail, SĐT, GitHub"| P33
    P32 -->|"extracted_skills,\nextracted_email, extracted_phone"| DS_APP

    P33 -->|"Điểm ngữ nghĩa\nCosine Similarity"| P34
    P33 -->|"Kỹ năng Matched/Missing"| P34

    P34 -->|"S_total, skill_score,\nsemantic_score,\nexperience_score, education_score\nkeyword_stuffing_flag"| DS_APP
    DS_APP -->|"Hiển thị kết quả\nXAI & AI Coach"| UV
```

> **Hình 3.8: DFD Mức 1 – PHÂN TÍCH CV BẰNG AI ENGINE**

---

#### Phân rã tiến trình 4.0: Bảng xếp hạng & Sàng lọc

```mermaid
flowchart TD
    HR["HR Recruiter"]

    P41(["4.1 Tải &\nSắp xếp\nbảng xếp hạng"])
    P42(["4.2 Lọc &\nTìm kiếm\nứng viên"])
    P43(["4.3 Sàng lọc\nđa vị trí\n(Multi-Job)"])
    P44(["4.4 Cập nhật\ntrạng thái\nhàng loạt"])

    DS_APP[("Hồ sơ ứng tuyển\n(Application)")]
    DS_JOB[("Tin tuyển dụng\n(JobPosting)")]

    DS_APP -->|"Dữ liệu match_score\n& XAI"| P41
    P41 -->|"Hiển thị bảng xếp hạng\n(Giảm dần điểm AI)\n🥇🥈🥉 Huy chương Top 3"| HR

    HR -->|"Bộ lọc: trạng thái,\ntừ khóa, cấp bậc"| P42
    DS_APP -->|"Danh sách ứng viên"| P42
    P42 -->|"Kết quả lọc"| HR

    HR -->|"Upload CV\n1 ứng viên"| P43
    DS_JOB -->|"Tất cả vị trí\nđang tuyển"| P43
    P43 -->|"Ma trận so khớp\nBest Fit tự động"| HR

    HR -->|"Chọn nhiều ứng viên\n& trạng thái mới"| P44
    P44 -->|"Cập nhật status\nhàng loạt"| DS_APP
    P44 -->|"Kích hoạt gửi\nemail thông báo"| HR
```

> **Hình 3.9: DFD Mức 1 – BẢNG XẾP HẠNG & SÀNG LỌC**

---

#### Phân rã tiến trình 1.0: Quản lý tài khoản & Xác thực

```mermaid
flowchart TD
    UV["Ứng viên"]
    HR["HR Recruiter"]
    AD["System Admin"]

    P11(["1.1 Đăng ký\ntài khoản"])
    P12(["1.2 Đăng nhập\n/ Xác thực"])
    P13(["1.3 Chỉnh sửa\nhồ sơ cá nhân"])
    P14(["1.4 Phân quyền\nRBAC"])

    DS_USER[("Người dùng\n(User)")]

    UV -->|"Thông tin đăng ký\n(candidate)"| P11
    HR -->|"Thông tin đăng ký\n(hr + company)"| P11
    P11 -->|"Lưu tài khoản mới"| DS_USER

    UV -->|"Username + Password"| P12
    HR -->|"Username + Password"| P12
    P12 -->|"Kiểm tra xác thực"| DS_USER
    DS_USER -->|"Thông tin phiên\n(Session)"| P12

    UV -->|"Cập nhật thông tin\ncá nhân"| P13
    HR -->|"Cập nhật thông tin\ncông ty"| P13
    P13 -->|"Lưu profile"| DS_USER

    AD -->|"Thay đổi role\nngười dùng"| P14
    P14 -->|"Cập nhật\nrole/is_active"| DS_USER
```

> **Hình 3.10: DFD Mức 1 – QUẢN LÝ TÀI KHOẢN & XÁC THỰC**

---

## 3.5. Sơ đồ Thực thể liên kết (ERD – Entity Relationship Diagram)

```mermaid
erDiagram
    User {
        int id PK
        varchar username
        varchar password
        varchar email
        varchar first_name
        varchar last_name
        varchar role
        varchar phone_number
        varchar company_name
        bool is_active
        datetime date_joined
    }

    JobPosting {
        int id PK
        int hr_id FK
        varchar title
        text description
        text required_skills
        int min_experience
        varchar location
        varchar salary_range
        varchar job_type
        bool is_active
        datetime created_at
        datetime updated_at
    }

    Application {
        int id PK
        int job_id FK
        int candidate_id FK
        varchar cv_file
        text parsed_text
        json extracted_skills
        varchar extracted_email
        varchar extracted_phone
        float match_score
        float total_score
        float skill_score
        float semantic_score
        float experience_score
        float education_score
        json matched_skills
        json missing_skills
        bool keyword_stuffing_flag
        varchar status
        datetime created_at
        datetime updated_at
    }

    User ||--o{ JobPosting : "HR đăng tin (1 - 0,N)"
    User ||--o{ Application : "Ứng viên nộp (1 - 0,N)"
    JobPosting ||--o{ Application : "Có hồ sơ (1 - 0,N)"
```

> **Hình 3.11: Sơ đồ Thực thể liên kết (ERD)**

---

## 3.5.1. Lược đồ quan hệ Cơ sở dữ liệu (Relational Schema)

```mermaid
erDiagram
    User {
        int id PK
        varchar_150 username
        varchar_128 password
        varchar_254 email
        varchar_150 first_name
        varchar_150 last_name
        varchar_20 role
        varchar_20 phone_number
        varchar_255 company_name
        bool is_active
        bool is_staff
        datetime date_joined
    }

    JobPosting {
        int id PK
        int hr_id FK
        varchar_255 title
        text description
        text required_skills
        int min_experience
        varchar_100 location
        varchar_100 salary_range
        varchar_50 job_type
        bool is_active
        datetime created_at
        datetime updated_at
    }

    Application {
        int id PK
        int job_id FK
        int candidate_id FK
        varchar_100 cv_file
        text parsed_text
        json extracted_skills
        varchar_255 extracted_email
        varchar_50 extracted_phone
        float match_score
        float total_score
        float skill_score
        float semantic_score
        float experience_score
        float education_score
        json matched_skills
        json missing_skills
        bool keyword_stuffing_flag
        varchar_20 status
        datetime created_at
        datetime updated_at
    }

    User ||--o{ JobPosting : "hr_id FK (1 - 0,N)"
    User ||--o{ Application : "candidate_id FK (1 - 0,N)"
    JobPosting ||--o{ Application : "job_id FK (1 - 0,N)"
```

> **Hình 3.12: Lược đồ quan hệ Cơ sở dữ liệu (Relational Schema)**

---

## 3.5.2. Sơ Đồ Lớp (Class Diagram)

```mermaid
classDiagram
    class User {
        +int id
        +String username
        +String password
        +String email
        +String first_name
        +String last_name
        +String role
        +String phone_number
        +String company_name
        +bool is_active
        +bool is_admin()
        +bool is_candidate()
        +bool is_hr()
        +String __str__()
    }

    class JobPosting {
        +int id
        +User hr
        +String title
        +String description
        +String required_skills
        +int min_experience
        +String location
        +String salary_range
        +String job_type
        +bool is_active
        +DateTime created_at
        +DateTime updated_at
        +List get_skills_list()
        +String __str__()
    }

    class Application {
        +int id
        +JobPosting job
        +User candidate
        +String cv_file
        +String parsed_text
        +List extracted_skills
        +String extracted_email
        +String extracted_phone
        +float match_score
        +float total_score
        +float skill_score
        +float semantic_score
        +float experience_score
        +float education_score
        +List matched_skills
        +List missing_skills
        +bool keyword_stuffing_flag
        +String status
        +String cv_file_path()
        +String contact_email()
        +String contact_phone()
        +save()
        +String __str__()
    }

    class AIParser {
        +extract_text_from_pdf(file_path)
        +extract_text_from_docx(file_path)
        +extract_text_from_image_ocr(file_path)
        +extract_text_from_pdf_ocr_fallback(file_path)
        +extract_text_from_file(file_path)
    }

    class AIExtractor {
        +List SKILL_TAXONOMY
        +extract_skills(text)
        +extract_contact_info(text)
        +extract_candidate_name(text)
        +extract_work_experience_entries(text)
    }

    class AIMatcher {
        -model SentenceTransformer
        +calculate_semantic_similarity(jd_text, cv_text)
        +match_skills(jd_skills, cv_skills)
        +get_matched_skills(jd_skills, cv_skills)
        +get_missing_skills(jd_skills, cv_skills)
    }

    class AIEvaluator {
        +evaluate_candidate_application(jd, application)
        +calculate_skill_score(jd_skills, cv_skills)
        +calculate_experience_score(text, min_exp)
        +calculate_education_score(text)
        +detect_keyword_stuffing(cv_skills, semantic_score)
    }

    User "1" --> "0..*" JobPosting : đăng tin (HR)
    User "1" --> "0..*" Application : nộp hồ sơ (Candidate)
    JobPosting "1" --> "0..*" Application : có hồ sơ
    Application --> AIParser : sử dụng
    Application --> AIExtractor : sử dụng
    Application --> AIMatcher : sử dụng
    Application --> AIEvaluator : sử dụng
    AIEvaluator --> AIMatcher : gọi
```

> **Hình 3.13: Sơ đồ Lớp (Class Diagram)**

---

## 3.5.3. Từ điển dữ liệu (Data Dictionary)

### Bảng 1: User (Quản lý tài khoản người dùng – `accounts_user`)

| STT | Tên Trường | Kiểu dữ liệu | Mô tả |
|-----|-----------|--------------|-------|
| 1 | id | int (PK) | Mã định danh tự tăng (Auto Identity) |
| 2 | username | varchar(150) | Tên đăng nhập duy nhất trong hệ thống |
| 3 | password | varchar(128) | Mật khẩu đã mã hóa (PBKDF2 + SHA256) |
| 4 | email | varchar(254) | Địa chỉ email tài khoản |
| 5 | first_name | varchar(150) | Tên |
| 6 | last_name | varchar(150) | Họ |
| 7 | role | varchar(20) | Vai trò: `candidate` / `hr` / `admin` |
| 8 | phone_number | varchar(20) | Số điện thoại (tùy chọn) |
| 9 | company_name | varchar(255) | Tên công ty (chỉ dành cho HR) |
| 10 | is_active | bool | Tài khoản đang hoạt động hay bị khóa |
| 11 | date_joined | datetime | Thời điểm đăng ký tài khoản |

> **Bảng 1: Bảng User – accounts_user (database)**

---

### Bảng 2: JobPosting (Quản lý bài đăng tuyển dụng – `jobs_jobposting`)

| STT | Tên Trường | Kiểu dữ liệu | Mô tả |
|-----|-----------|--------------|-------|
| 1 | id | int (PK) | Mã định danh bài đăng tự tăng |
| 2 | hr_id | int (FK → User) | Nhà tuyển dụng phụ trách đăng bài |
| 3 | title | varchar(255) | Tiêu đề vị trí tuyển dụng |
| 4 | description | text | Mô tả chi tiết công việc (JD) phục vụ S-BERT |
| 5 | required_skills | text | Kỹ năng yêu cầu, phân tách bằng dấu phẩy |
| 6 | min_experience | int | Số năm kinh nghiệm tối thiểu (0 = Fresher) |
| 7 | location | varchar(100) | Địa điểm làm việc |
| 8 | salary_range | varchar(100) | Mức lương dự kiến |
| 9 | job_type | varchar(50) | Loại hình: Full-time / Part-time / Remote / Hybrid |
| 10 | is_active | bool | Tin đang hiển thị hay đã đóng |
| 11 | created_at | datetime | Thời điểm đăng bài |
| 12 | updated_at | datetime | Thời điểm cập nhật lần cuối |

> **Bảng 2: Bảng JobPosting – jobs_jobposting (database)**

---

### Bảng 3: Application (Quản lý hồ sơ ứng tuyển – `jobs_application`)

| STT | Tên Trường | Kiểu dữ liệu | Mô tả |
|-----|-----------|--------------|-------|
| 1 | id | int (PK) | Mã định danh hồ sơ ứng tuyển |
| 2 | job_id | int (FK → JobPosting) | Vị trí tuyển dụng được ứng tuyển |
| 3 | candidate_id | int (FK → User) | Ứng viên nộp hồ sơ |
| 4 | cv_file | varchar(100) | Đường dẫn file CV (media/cv_uploads/YYYY/MM/) |
| 5 | parsed_text | text | Văn bản trích xuất từ CV (Parser + OCR) |
| 6 | extracted_skills | json | Danh sách kỹ năng AI nhận diện từ CV |
| 7 | extracted_email | varchar(255) | Email bóc tách trực tiếp từ văn bản CV |
| 8 | extracted_phone | varchar(50) | SĐT bóc tách trực tiếp từ văn bản CV |
| 9 | match_score | float | Điểm phù hợp tổng thể 0–100% (xếp hạng) |
| 10 | total_score | float | Điểm S_total tổng hợp 4 trụ cột |
| 11 | skill_score | float | Điểm kỹ năng S_skill (trọng số 35%) |
| 12 | semantic_score | float | Điểm ngữ nghĩa S-BERT (trọng số 25%) |
| 13 | experience_score | float | Điểm kinh nghiệm S_exp (trọng số 25%) |
| 14 | education_score | float | Điểm học vấn S_edu (trọng số 15%) |
| 15 | matched_skills | json | Danh sách kỹ năng đã khớp với JD (badge xanh) |
| 16 | missing_skills | json | Danh sách kỹ năng còn thiếu so với JD (badge đỏ) |
| 17 | keyword_stuffing_flag | bool | Cờ cảnh báo nhồi từ khóa (True = có dấu hiệu gian lận) |
| 18 | status | varchar(20) | Trạng thái: pending / reviewed / accepted / rejected |
| 19 | created_at | datetime | Thời điểm nộp hồ sơ |
| 20 | updated_at | datetime | Thời điểm cập nhật trạng thái lần cuối |

> **Bảng 3: Bảng Application – jobs_application (database)**

---

## Phân tích các lớp AI Engine chính

- **AIParser (`ai_engine/parser.py`):** Trích xuất văn bản từ PDF, Word (.docx) và ảnh scan. Tự động kích hoạt OCR Fallback (Tesseract / EasyOCR) khi phát hiện CV dạng ảnh hoặc PDF ít chữ (< 50 ký tự).

- **AIExtractor (`ai_engine/extractor.py`):** Nhận diện 80+ kỹ năng IT chuẩn hóa qua từ điển Canonical Taxonomy và Regex xử lý biên từ đặc biệt (`C++`, `C#`, `Node.js`). Bóc tách thông tin liên hệ: SĐT Việt Nam, Email, GitHub, LinkedIn.

- **AIMatcher (`ai_engine/matcher.py`):** Sử dụng mô hình Sentence-BERT `paraphrase-multilingual-MiniLM-L12-v2` với Singleton Pattern (nạp 1 lần vào RAM). Tính khoảng cách Cosine Similarity giữa vector JD và vector CV. Phân tích XAI: tập hợp kỹ năng Matched và Missing.

- **AIEvaluator (`ai_engine/evaluator.py`):** Tổng hợp điểm $S_{total} = 0.35 \times S_{skill} + 0.25 \times S_{semantic} + 0.25 \times S_{exp} + 0.15 \times S_{edu}$. Phát hiện gian lận Keyword Stuffing khi mật độ kỹ năng > 15% kết hợp điểm ngữ nghĩa < 40%, áp dụng hệ số phạt 0.7.

---

*Tài liệu thiết kế hệ thống được vẽ theo chuẩn BA với 10 năm kinh nghiệm phân tích hệ thống.*  
*Dự án: AI-Powered Resume Screener & Recruiter Portal | Phiên bản: v1.0.0*
