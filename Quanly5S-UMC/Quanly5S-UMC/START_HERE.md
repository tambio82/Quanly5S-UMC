# 👋 BẮT ĐẦU TẠI ĐÂY!

Chào mừng bạn đến với **Hệ thống Quản lý 5S - UMC**! 

## 📦 Bạn vừa nhận được gì?

Một ứng dụng web hoàn chỉnh để quản lý hoạt động 5S tại bệnh viện với:

✅ **7 modules chức năng** đầy đủ  
✅ **581 dòng code** Python đã được tối ưu  
✅ **Database schema** PostgreSQL hoàn chỉnh  
✅ **Documentation** chi tiết bằng tiếng Việt  
✅ **Sẵn sàng deploy** lên Streamlit Cloud  

## 🎯 Bạn muốn làm gì?

### 🚀 Tôi muốn chạy thử ngay (5 phút)
👉 Đọc [QUICKSTART.md](QUICKSTART.md)

### 📖 Tôi muốn hiểu rõ trước khi cài đặt
👉 Đọc [README.md](README.md) → [STRUCTURE.md](STRUCTURE.md)

### 🔧 Tôi cần hướng dẫn cài đặt chi tiết
👉 Đọc [INSTALLATION.md](INSTALLATION.md)

### 🌐 Tôi muốn đăng lên GitHub
👉 Đọc [GITHUB_GUIDE.md](GITHUB_GUIDE.md)

### 🤝 Tôi muốn đóng góp code
👉 Đọc [CONTRIBUTING.md](CONTRIBUTING.md)

## 📁 Cấu trúc Files

```
Quanly5S-UMC/
│
├── 📄 START_HERE.md           ← BẠN ĐANG Ở ĐÂY
├── 📄 README.md                  Tổng quan dự án
├── 📄 QUICKSTART.md              Hướng dẫn nhanh 5 phút
├── 📄 INSTALLATION.md            Hướng dẫn cài đặt chi tiết
├── 📄 STRUCTURE.md               Giải thích cấu trúc
├── 📄 GITHUB_GUIDE.md            Hướng dẫn đăng GitHub
├── 📄 CONTRIBUTING.md            Hướng dẫn đóng góp
├── 📄 CHANGELOG.md               Lịch sử thay đổi
├── 📄 LICENSE                    Giấy phép MIT
│
├── 📄 main.py                    ⭐ Trang chủ app
├── 📄 db_utils.py                🔧 Database utilities
├── 📄 requirements.txt           📦 Thư viện cần thiết
├── 📄 setup.sql                  🗄️ Database schema
│
├── 📁 .streamlit/
│   └── secrets.toml.example      🔐 Mẫu cấu hình DB
│
├── 📁 fonts/
│   ├── README.md                 Hướng dẫn tải font
│   └── Roboto-Regular.ttf        ⚠️ CẦN TẢI VỀ
│
└── 📁 pages/                     🎨 7 modules chính
    ├── 1_🏠_Trang_Chu.py        Dashboard
    ├── 2_🏢_Quan_Ly_Don_Vi.py   Quản lý Khoa/Phòng
    ├── 3_⚙️_Cau_Hinh_Khu_Vuc.py Cấu hình 5S
    ├── 4_📝_Danh_Gia_5S.py      Đánh giá
    ├── 5_📊_Thong_Ke.py         Thống kê
    ├── 6_📑_Xuat_Bao_Cao.py     Xuất PDF
    └── 7_💾_Du_Lieu.py          Import/Export
```

## ⚡ Hướng dẫn Siêu Nhanh

```bash
# 1. Cài đặt
pip install -r requirements.txt

# 2. Tải font (QUAN TRỌNG!)
cd fonts
wget https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Regular.ttf
cd ..

# 3. Cấu hình database
mkdir .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Sửa file secrets.toml với thông tin DB của bạn

# 4. Chạy app
streamlit run main.py
```

## 🎓 Học theo thứ tự

### Người mới bắt đầu:
1. ✅ START_HERE.md (bạn đang đọc)
2. ✅ QUICKSTART.md (chạy thử)
3. ✅ README.md (hiểu tổng quan)
4. ✅ Sử dụng app

### Developer:
1. ✅ START_HERE.md
2. ✅ STRUCTURE.md (hiểu cấu trúc code)
3. ✅ INSTALLATION.md (setup môi trường)
4. ✅ CONTRIBUTING.md (quy tắc đóng góp)

### DevOps/Deployment:
1. ✅ START_HERE.md
2. ✅ INSTALLATION.md
3. ✅ GITHUB_GUIDE.md (deploy)
4. ✅ Streamlit Cloud settings

## 🔴 Lưu ý QUAN TRỌNG

### ⚠️ TRƯỚC KHI CHẠY:

1. **Tải Font**: File `fonts/Roboto-Regular.ttf` PHẢI được tải về
2. **Cấu hình DB**: File `.streamlit/secrets.toml` PHẢI được tạo
3. **Chạy SQL**: Database schema từ `setup.sql` PHẢI được chạy

### ⚠️ TRƯỚC KHI ĐĂNG GITHUB:

1. **Tải Font**: Đảm bảo `Roboto-Regular.ttf` có trong `fonts/`
2. **Kiểm tra .gitignore**: File `secrets.toml` KHÔNG được push
3. **Test local**: Chạy thử trước khi push

### ⚠️ KHI DEPLOY STREAMLIT CLOUD:

1. **Font**: Phải có trong GitHub repo
2. **Secrets**: Paste vào Settings → Secrets trên Streamlit Cloud
3. **Database**: Dùng cloud DB (Neon, Supabase...)

## 🆘 Cần Giúp Đỡ?

### Vấn đề thường gặp:

**"No module named 'streamlit'"**
```bash
pip install -r requirements.txt
```

**"Không tìm thấy Database"**
- Kiểm tra file `.streamlit/secrets.toml`
- Kiểm tra thông tin kết nối đúng

**"Font not found"**
- Tải `Roboto-Regular.ttf` vào thư mục `fonts/`

**"Import Error"**
- Kiểm tra Python version >= 3.8
- Reinstall dependencies

### Đọc thêm:
- [INSTALLATION.md](INSTALLATION.md) - Phần "Xử lý lỗi"
- GitHub Issues (nếu đã có repo)

## 🎯 Bắt đầu ngay!

**Hành động tiếp theo:**

1. ✅ Đọc [QUICKSTART.md](QUICKSTART.md)
2. ✅ Cài đặt dependencies
3. ✅ Setup database
4. ✅ Chạy app lần đầu
5. ✅ Khám phá các chức năng

## 📞 Liên hệ & Hỗ trợ

- 📧 Email: [Thêm email của bạn]
- 🐛 Báo lỗi: GitHub Issues
- 💬 Thảo luận: GitHub Discussions

## ⭐ Thích dự án này?

- ⭐ Star trên GitHub
- 🔄 Fork và customize
- 🤝 Contribute code
- 📢 Chia sẻ với đồng nghiệp

---

## 📊 Thông tin Dự án

- **Phiên bản**: 1.0.0
- **Ngày tạo**: 28/11/2024
- **Ngôn ngữ**: Python 3.8+
- **Framework**: Streamlit
- **Database**: PostgreSQL
- **License**: MIT
- **Tổng dòng code**: ~581 lines
- **Số files**: 20+ files
- **Số modules**: 7 modules

---

**🎉 Chúc bạn thành công với dự án Quản lý 5S!**

*Nếu gặp khó khăn, đừng ngại hỏi - tạo Issue trên GitHub nhé!*
