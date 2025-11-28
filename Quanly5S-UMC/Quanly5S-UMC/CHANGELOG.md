# 📝 CHANGELOG

Tất cả các thay đổi quan trọng của dự án được ghi lại tại đây.

## [1.0.0] - 2024-11-28

### 🎉 Phiên bản đầu tiên

#### ✨ Tính năng mới

##### Core Features
- **Dashboard tổng quan** (Trang chủ)
  - Metrics: Khoa/Phòng tham gia, Tỷ lệ Đạt/Không Đạt
  - Biểu đồ xu hướng theo ngày
  - Biểu đồ cột Đạt/Không Đạt
  - Bảng hoạt động gần đây

- **Quản lý Đơn vị**
  - Thêm Khoa/Phòng với mã số và tên
  - Quản lý tối đa 8 vị trí địa lý
  - Thêm tối đa 5 nhân sự phụ trách
  - Phân quyền: Thành viên tổ 5S / Điều phối chính

- **Cấu hình 5S**
  - Tab 1: Quản lý khu vực (Hành chính, Y tế, Kỹ thuật...)
  - Tab 2: Thêm tiêu chí/hạng mục kiểm tra cho từng khu vực
  - Hiển thị tổng hợp vị trí theo khu vực

- **Đánh giá 5S**
  - Checklist điện tử với data editor
  - Chọn Khoa/Phòng và ngày đánh giá
  - Nhập số lượng, trạng thái Đạt/Không Đạt
  - Gán nhân sự phụ trách từng hạng mục
  - Lưu kết quả vào database

- **Thống kê & Phân tích**
  - Bộ lọc theo khoảng thời gian
  - KPI: Tổng lượt, Số Đạt, Số Không Đạt
  - Heatmap: Điểm nóng vi phạm (Khu vực × Hạng mục)
  - Visualization với Plotly

- **Xuất báo cáo PDF**
  - Chọn Khoa/Phòng và ngày cần xuất
  - Tạo PDF với font tiếng Việt Roboto
  - Bảng kết quả với highlight màu đỏ cho không đạt
  - Header/Footer tự động
  - Download PDF

- **Quản lý Dữ liệu**
  - Export danh sách nhân sự ra Excel
  - Import nhân sự hàng loạt từ Excel
  - Validation dữ liệu import

##### Database
- Schema với 6 bảng: departments, staff, areas, criteria, evaluations, evaluation_details
- Foreign keys và constraints
- Indexes để tối ưu performance
- Support JSON cho locations field

##### UI/UX
- Responsive layout với Streamlit
- Emoji icons cho navigation
- Multi-page app với sidebar
- Data editor cho checklist
- Interactive charts với Plotly
- Toast notifications

#### 🔧 Cấu hình & Tools

- **Database Connection**
  - PostgreSQL support
  - SQLAlchemy integration
  - Connection pooling
  - Secrets management với Streamlit

- **Development**
  - Python 3.8+ support
  - Virtual environment ready
  - Git configuration (.gitignore, .gitattributes)

- **Documentation**
  - README.md: Tổng quan dự án
  - INSTALLATION.md: Hướng dẫn cài đặt chi tiết
  - QUICKSTART.md: Hướng dẫn nhanh 5 phút
  - STRUCTURE.md: Giải thích cấu trúc dự án
  - CONTRIBUTING.md: Hướng dẫn đóng góp
  - SQL schema với comments

- **Deployment**
  - Streamlit Cloud ready
  - Requirements.txt đầy đủ
  - Secrets template
  - Font configuration

#### 📦 Dependencies

- streamlit: Web framework
- pandas: Data processing
- psycopg2-binary: PostgreSQL adapter
- plotly: Interactive visualization
- fpdf: PDF generation
- xlsxwriter: Excel export
- sqlalchemy: Database ORM
- openpyxl: Excel import

#### 📄 Files Structure

```
Quanly5S-UMC/
├── main.py
├── db_utils.py
├── requirements.txt
├── setup.sql
├── .streamlit/
│   └── secrets.toml.example
├── fonts/
│   └── README.md
├── pages/
│   ├── 1_🏠_Trang_Chu.py
│   ├── 2_🏢_Quan_Ly_Don_Vi.py
│   ├── 3_⚙️_Cau_Hinh_Khu_Vuc.py
│   ├── 4_📝_Danh_Gia_5S.py
│   ├── 5_📊_Thong_Ke.py
│   ├── 6_📑_Xuat_Bao_Cao.py
│   └── 7_💾_Du_Lieu.py
└── docs/
    ├── README.md
    ├── INSTALLATION.md
    ├── QUICKSTART.md
    ├── STRUCTURE.md
    └── CONTRIBUTING.md
```

---

## 🔮 Roadmap - Tính năng tương lai

### Version 1.1 (Planned)
- [ ] Authentication & Authorization
- [ ] User roles management
- [ ] Email notifications
- [ ] Export multiple formats (Excel, CSV)
- [ ] Advanced filtering in statistics
- [ ] Mobile responsive improvements

### Version 1.2 (Planned)
- [ ] Multi-language support (EN/VI)
- [ ] Dark mode
- [ ] Audit logs
- [ ] Bulk operations
- [ ] Advanced charts (Gantt, Sankey)
- [ ] API endpoints

### Version 2.0 (Future)
- [ ] Real-time collaboration
- [ ] Photo upload for evaluations
- [ ] Mobile app (React Native)
- [ ] AI-powered insights
- [ ] Integration with other systems

---

## 📌 Note

Format changelog theo [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

### Categories
- **Added**: Tính năng mới
- **Changed**: Thay đổi trong tính năng hiện có
- **Deprecated**: Tính năng sắp bị loại bỏ
- **Removed**: Tính năng đã bị loại bỏ
- **Fixed**: Sửa lỗi
- **Security**: Cập nhật bảo mật
