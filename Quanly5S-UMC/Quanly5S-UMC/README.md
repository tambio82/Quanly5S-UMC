# 🏥 HỆ THỐNG QUẢN LÝ HOẠT ĐỘNG 5S - UMC

Ứng dụng web quản lý chất lượng 5S cho bệnh viện được xây dựng bằng Streamlit và PostgreSQL.

## 📋 Tính năng chính

- **🏠 Dashboard tổng quan**: Thống kê, biểu đồ xu hướng tuân thủ 5S
- **🏢 Quản lý đơn vị**: Thêm Khoa/Phòng và Nhân sự phụ trách
- **⚙️ Cấu hình 5S**: Thiết lập Khu vực và Tiêu chí kiểm tra
- **📝 Đánh giá 5S**: Checklist điện tử, đánh giá trực tuyến
- **📊 Thống kê sâu**: Heatmap vi phạm, phân tích theo khu vực
- **📑 Xuất báo cáo**: Tạo báo cáo PDF tự động
- **💾 Quản lý dữ liệu**: Import/Export dữ liệu Excel

## 🚀 Cài đặt và Chạy

### 1. Clone repository

```bash
git clone https://github.com/your-username/Quanly5S-UMC.git
cd Quanly5S-UMC
```

### 2. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 3. Tải Font chữ tiếng Việt

- Tải file `Roboto-Regular.ttf` từ [Google Fonts](https://fonts.google.com/specimen/Roboto)
- Tạo thư mục `fonts/` trong root folder
- Copy file `.ttf` vào thư mục `fonts/`

### 4. Cấu hình Database

Tạo file `.streamlit/secrets.toml` với nội dung:

```toml
[postgres]
host = "your-database-host"
dbname = "your-database-name"
user = "your-username"
password = "your-password"
port = "5432"
```

**⚠️ LƯU Ý**: File `secrets.toml` đã được thêm vào `.gitignore` để bảo mật thông tin.

### 5. Tạo Database Schema

Chạy script SQL để tạo các bảng cần thiết:

```sql
-- Bảng Departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    unit_code VARCHAR(20) UNIQUE NOT NULL,
    unit_name VARCHAR(200) NOT NULL,
    locations JSONB
);

-- Bảng Staff
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id),
    name VARCHAR(200) NOT NULL,
    staff_code VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200),
    role VARCHAR(100)
);

-- Bảng Areas
CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(200) NOT NULL,
    area_code VARCHAR(20) NOT NULL,
    definition TEXT
);

-- Bảng Criteria
CREATE TABLE criteria (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    location_name VARCHAR(200),
    category VARCHAR(500),
    requirement TEXT
);

-- Bảng Evaluations
CREATE TABLE evaluations (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id),
    eval_date DATE NOT NULL
);

-- Bảng Evaluation Details
CREATE TABLE evaluation_details (
    id SERIAL PRIMARY KEY,
    evaluation_id INTEGER REFERENCES evaluations(id),
    criteria_id INTEGER REFERENCES criteria(id),
    quantity INTEGER DEFAULT 0,
    is_pass BOOLEAN DEFAULT FALSE,
    staff_id INTEGER REFERENCES staff(id)
);
```

### 6. Chạy ứng dụng

```bash
streamlit run main.py
```

Ứng dụng sẽ mở tại `http://localhost:8501`

## 📦 Cấu trúc thư mục

```
Quanly5S-UMC/
├── .gitignore
├── requirements.txt
├── db_utils.py
├── main.py
├── README.md
├── fonts/
│   └── Roboto-Regular.ttf
└── pages/
    ├── 1_🏠_Trang_Chu.py
    ├── 2_🏢_Quan_Ly_Don_Vi.py
    ├── 3_⚙️_Cau_Hinh_Khu_Vuc.py
    ├── 4_📝_Danh_Gia_5S.py
    ├── 5_📊_Thong_Ke.py
    ├── 6_📑_Xuat_Bao_Cao.py
    └── 7_💾_Du_Lieu.py
```

## 🌐 Deploy lên Streamlit Cloud

1. Push code lên GitHub
2. Truy cập [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect GitHub repository
4. Vào **Settings → Secrets** và paste nội dung file `secrets.toml`
5. Deploy!

## 🔒 Bảo mật

- ✅ File `.gitignore` đã cấu hình không push mật khẩu
- ✅ Sử dụng Streamlit Secrets cho thông tin nhạy cảm
- ✅ Không hard-code credentials trong source code

## 📝 Hướng dẫn sử dụng

### Thêm Khoa/Phòng mới
1. Vào menu **🏢 Quản lý đơn vị**
2. Điền thông tin: Mã đơn vị, Tên đơn vị
3. Thêm vị trí địa lý (tối đa 8)
4. Thêm nhân sự phụ trách (tối đa 5)
5. Nhấn **Lưu thông tin**

### Cấu hình Khu vực 5S
1. Vào menu **⚙️ Cấu hình 5S**
2. Tab **Quy định Khu vực**: Thêm khu vực mới (VD: Hành chính, Y tế...)
3. Tab **Vị trí & Hạng mục**: Thêm tiêu chí kiểm tra cho từng khu vực

### Thực hiện Đánh giá
1. Vào menu **📝 Đánh giá**
2. Chọn Khoa/Phòng cần đánh giá
3. Chọn ngày đánh giá
4. Điền thông tin vào bảng checklist
5. Nhấn **Lưu Kết Quả**

## 🛠️ Công nghệ sử dụng

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Database**: PostgreSQL
- **Visualization**: Plotly
- **Report**: FPDF
- **Data Processing**: Pandas, SQLAlchemy

## 📞 Liên hệ & Hỗ trợ

Nếu bạn gặp vấn đề hoặc cần hỗ trợ, vui lòng tạo Issue trên GitHub.

## 📄 License

MIT License - Tự do sử dụng cho mục đích học tập và thương mại.

---

**Phát triển bởi**: UMC Quality Team  
**Phiên bản**: 1.0.0  
**Cập nhật**: 2024
