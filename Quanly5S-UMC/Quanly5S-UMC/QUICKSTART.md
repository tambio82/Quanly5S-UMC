# ⚡ HƯỚNG DẪN NHANH (5 PHÚT)

Hướng dẫn cài đặt và chạy ứng dụng trong 5 phút!

## 🎯 Bước 1: Clone & Cài đặt (2 phút)

```bash
# Clone repository
git clone https://github.com/your-username/Quanly5S-UMC.git
cd Quanly5S-UMC

# Cài đặt packages
pip install -r requirements.txt
```

## 🗄️ Bước 2: Setup Database (1 phút)

### Option A: Sử dụng Neon.tech (Miễn phí, Khuyến nghị)

1. Đăng ký tài khoản tại [neon.tech](https://neon.tech) (30 giây)
2. Tạo project mới → Copy connection string
3. Chạy SQL từ file `setup.sql` trong Neon SQL Editor

### Option B: PostgreSQL Local

```bash
# Tạo database
createdb umc_5s

# Chạy schema
psql -d umc_5s -f setup.sql
```

## 🔐 Bước 3: Cấu hình Secrets (30 giây)

```bash
# Tạo thư mục và file
mkdir .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Mở `.streamlit/secrets.toml` và điền thông tin:

```toml
[postgres]
host = "your-host.neon.tech"
dbname = "neondb"
user = "your-username"
password = "your-password"
port = "5432"
```

## 🎨 Bước 4: Tải Font (1 phút)

### Cách nhanh nhất:

```bash
cd fonts
wget https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Regular.ttf
cd ..
```

### Hoặc tải thủ công:
1. Vào [Google Fonts - Roboto](https://fonts.google.com/specimen/Roboto)
2. Download → Giải nén → Copy `Roboto-Regular.ttf` vào `fonts/`

## 🚀 Bước 5: Chạy App (10 giây)

```bash
streamlit run main.py
```

Mở trình duyệt: `http://localhost:8501`

## ✅ Kiểm tra hoạt động

1. ✅ Trang chủ hiển thị "HỆ THỐNG QUẢN LÝ HOẠT ĐỘNG 5S - UMC"
2. ✅ Sidebar có 7 menu
3. ✅ Không có lỗi kết nối Database

## 🎉 Xong! Bắt đầu sử dụng

### Khởi đầu:

1. **Thêm Khoa/Phòng**: Vào menu "🏢 Quản lý đơn vị"
2. **Cấu hình 5S**: Vào menu "⚙️ Cấu hình Khu vực"
3. **Đánh giá**: Vào menu "📝 Đánh giá 5S"

## 🐛 Gặp lỗi?

### Lỗi: "No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### Lỗi: "Không tìm thấy Database"
- Kiểm tra file `.streamlit/secrets.toml` đã tạo
- Kiểm tra thông tin kết nối đúng

### Lỗi: "Font not found"
- Đảm bảo file `fonts/Roboto-Regular.ttf` tồn tại

## 📱 Deploy lên Internet (Bonus - 3 phút)

```bash
# Push lên GitHub
git add .
git commit -m "Initial commit"
git push origin main
```

1. Vào [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub repo
3. Paste nội dung `secrets.toml` vào Settings → Secrets
4. Deploy!

---

**Tổng thời gian**: 5-7 phút ⚡

Xem hướng dẫn chi tiết tại [INSTALLATION.md](INSTALLATION.md)
