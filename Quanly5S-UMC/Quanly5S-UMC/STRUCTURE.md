# 📁 CẤU TRÚC DỰ ÁN

## Tổng quan cấu trúc thư mục

```
Quanly5S-UMC/
│
├── 📄 main.py                      # File chính - trang chủ ứng dụng
├── 📄 db_utils.py                  # Utilities kết nối Database
├── 📄 requirements.txt             # Danh sách thư viện Python
├── 📄 setup.sql                    # Script tạo Database schema
│
├── 📁 .streamlit/                  # Cấu hình Streamlit
│   └── secrets.toml.example        # Mẫu file secrets (không push lên Git)
│
├── 📁 fonts/                       # Thư mục chứa font chữ
│   ├── README.md                   # Hướng dẫn tải font
│   └── Roboto-Regular.ttf          # Font tiếng Việt (cần tải về)
│
├── 📁 pages/                       # Các trang con của ứng dụng
│   ├── 1_🏠_Trang_Chu.py          # Dashboard tổng quan
│   ├── 2_🏢_Quan_Ly_Don_Vi.py     # Quản lý Khoa/Phòng/Nhân sự
│   ├── 3_⚙️_Cau_Hinh_Khu_Vuc.py   # Cấu hình Khu vực & Tiêu chí
│   ├── 4_📝_Danh_Gia_5S.py        # Checklist đánh giá 5S
│   ├── 5_📊_Thong_Ke.py           # Phân tích & Heatmap
│   ├── 6_📑_Xuat_Bao_Cao.py       # Xuất báo cáo PDF
│   └── 7_💾_Du_Lieu.py            # Import/Export Excel
│
├── 📄 .gitignore                   # File loại trừ khỏi Git
├── 📄 .gitattributes               # Cấu hình Git attributes
├── 📄 README.md                    # Hướng dẫn tổng quan
├── 📄 INSTALLATION.md              # Hướng dẫn cài đặt chi tiết
├── 📄 CONTRIBUTING.md              # Hướng dẫn đóng góp
└── 📄 LICENSE                      # Giấy phép MIT

```

## Chi tiết từng file/thư mục

### 🔵 Files gốc (Root Level)

#### `main.py`
- Trang chủ chính của ứng dụng
- Cấu hình page config (title, icon, layout)
- Hiển thị menu giới thiệu các chức năng

#### `db_utils.py`
- **`get_connection()`**: Tạo kết nối PostgreSQL
- **`get_engine()`**: Tạo SQLAlchemy engine
- **`run_query()`**: Thực thi SELECT queries, trả về DataFrame
- **`run_insert()`**: Thực thi INSERT/UPDATE queries

#### `requirements.txt`
Danh sách packages:
- `streamlit`: Framework web
- `pandas`: Xử lý dữ liệu
- `psycopg2-binary`: PostgreSQL adapter
- `plotly`: Vẽ biểu đồ tương tác
- `fpdf`: Tạo PDF
- `xlsxwriter`: Xuất Excel
- `sqlalchemy`: ORM/Database toolkit
- `openpyxl`: Đọc Excel

#### `setup.sql`
- Script SQL tạo schema database
- 6 bảng chính: departments, staff, areas, criteria, evaluations, evaluation_details
- Indexes để tối ưu performance
- Sample data (optional)

### 🔵 Thư mục `.streamlit/`

#### `secrets.toml.example`
- Mẫu file cấu hình kết nối Database
- Hướng dẫn với các providers: Neon, Supabase, ElephantSQL
- **LƯU Ý**: Copy thành `secrets.toml` và điền thông tin thực

### 🔵 Thư mục `fonts/`

#### `Roboto-Regular.ttf`
- Font tiếng Việt cho PDF
- **Cần tải về từ Google Fonts**
- Size: ~170KB
- License: Apache 2.0

### 🔵 Thư mục `pages/`

Streamlit tự động tạo sidebar menu từ các file trong thư mục này.

#### `1_🏠_Trang_Chu.py`
**Chức năng**: Dashboard tổng quan
- Metrics: Số Khoa/Phòng, Tỷ lệ Đạt/Không Đạt
- Biểu đồ: Xu hướng theo ngày
- Bảng: Hoạt động gần đây

#### `2_🏢_Quan_Ly_Don_Vi.py`
**Chức năng**: Quản lý đơn vị
- Form thêm Khoa/Phòng mới
- Nhập tối đa 8 vị trí địa lý
- Thêm tối đa 5 nhân sự phụ trách
- Phân quyền: Thành viên/Điều phối chính

#### `3_⚙️_Cau_Hinh_Khu_Vuc.py`
**Chức năng**: Cấu hình 5S
- **Tab 1**: Thêm/Xem khu vực (Hành chính, Y tế, Kỹ thuật...)
- **Tab 2**: Thêm tiêu chí/hạng mục cho từng khu vực

#### `4_📝_Danh_Gia_5S.py`
**Chức năng**: Đánh giá 5S
- Chọn Khoa/Phòng và ngày đánh giá
- Checklist dạng data editor
- Điền: Số lượng, Đạt/Không Đạt, Nhân sự phụ trách
- Lưu kết quả vào DB

#### `5_📊_Thong_Ke.py`
**Chức năng**: Phân tích sâu
- Bộ lọc theo thời gian
- KPI: Tổng lượt, Đạt, Không Đạt
- Heatmap: Điểm nóng vi phạm (Khu vực × Hạng mục)

#### `6_📑_Xuat_Bao_Cao.py`
**Chức năng**: Xuất PDF
- Chọn Khoa/Phòng và ngày
- Tạo báo cáo PDF với:
  - Header/Footer
  - Bảng kết quả (màu đỏ cho không đạt)
  - Font tiếng Việt Roboto

#### `7_💾_Du_Lieu.py`
**Chức năng**: Import/Export
- **Export**: Danh sách nhân sự → Excel
- **Import**: Upload Excel → Thêm nhân sự hàng loạt

### 🔵 Các file Documentation

#### `README.md`
- Giới thiệu tổng quan dự án
- Tính năng chính
- Hướng dẫn cài đặt cơ bản
- Hướng dẫn deploy

#### `INSTALLATION.md`
- Hướng dẫn cài đặt chi tiết từng bước
- Xử lý lỗi thường gặp
- Hướng dẫn deploy lên Streamlit Cloud

#### `CONTRIBUTING.md`
- Quy trình đóng góp code
- Coding style
- Quy tắc commit messages
- Testing guidelines

#### `LICENSE`
- MIT License
- Cho phép sử dụng tự do

### 🔵 Các file Git

#### `.gitignore`
Loại trừ:
- `.streamlit/` (chứa secrets)
- `__pycache__/`
- `*.pyc`
- `venv/`
- `.env`

#### `.gitattributes`
- Đảm bảo line endings nhất quán
- Binary files cho fonts

## 🔄 Luồng hoạt động

```
1. User → Streamlit UI (main.py/pages/*.py)
                ↓
2. UI → db_utils.py (get_connection, run_query)
                ↓
3. db_utils → PostgreSQL Database
                ↓
4. Database → Trả kết quả → pandas DataFrame
                ↓
5. DataFrame → Plotly Charts / PDF / Excel
                ↓
6. Results → Hiển thị cho User
```

## 📊 Database Schema

```
departments (Khoa/Phòng)
    ├── staff (Nhân sự)
    └── evaluations (Phiên đánh giá)
            └── evaluation_details (Chi tiết đánh giá)
                    ├── criteria (Tiêu chí)
                    │       └── areas (Khu vực)
                    └── staff (Người đánh giá)
```

## 🎨 UI Components

- **Metrics**: `st.metric()` - KPI numbers
- **Charts**: `plotly.express` - Interactive charts
- **Forms**: `st.form()` - Data input
- **Data Editor**: `st.data_editor()` - Editable tables
- **Tabs**: `st.tabs()` - Organized content

## 🚀 Deployment Flow

```
Local Development
    ↓ (git push)
GitHub Repository
    ↓ (connect)
Streamlit Cloud
    ↓ (auto deploy)
Production App
```

## 📞 Support Files

Mỗi thư mục con có README.md riêng:
- `fonts/README.md`: Hướng dẫn tải font
- Có thể thêm README cho pages/ nếu cần

---

**Tổng số files**: ~20 files
**Tổng số dòng code Python**: ~1,000 lines
**Database tables**: 6 tables
**Pages**: 7 functional pages
