# 📖 HƯỚNG DẪN CÀI ĐÁT CHI TIẾT

## 📋 Yêu cầu hệ thống

- Python 3.8 trở lên
- PostgreSQL 12 trở lên
- Git
- Kết nối Internet (để cài đặt packages)

## 🔧 Bước 1: Chuẩn bị môi trường

### 1.1. Cài đặt Python

**Windows:**
- Tải Python từ [python.org](https://www.python.org/downloads/)
- Chọn "Add Python to PATH" khi cài đặt

**macOS:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 1.2. Kiểm tra phiên bản Python

```bash
python --version
# Hoặc
python3 --version
```

## 💾 Bước 2: Clone dự án

```bash
git clone https://github.com/your-username/Quanly5S-UMC.git
cd Quanly5S-UMC
```

## 📦 Bước 3: Tạo môi trường ảo (khuyến nghị)

### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Sau khi kích hoạt, bạn sẽ thấy `(venv)` xuất hiện ở đầu dòng lệnh.

## 📚 Bước 4: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

**Lưu ý:** Nếu gặp lỗi với `psycopg2-binary`, thử:
```bash
pip install psycopg2-binary --no-binary psycopg2-binary
```

## 🗄️ Bước 5: Cấu hình Database

### 5.1. Tạo PostgreSQL Database

#### Sử dụng Local PostgreSQL:

```sql
CREATE DATABASE umc_5s;
```

#### Sử dụng Cloud Database (khuyến nghị cho người mới):

**Option 1: Neon.tech (Free, không cần thẻ tín dụng)**
1. Truy cập [neon.tech](https://neon.tech)
2. Đăng ký tài khoản miễn phí
3. Tạo project mới
4. Copy thông tin kết nối

**Option 2: Supabase (Free)**
1. Truy cập [supabase.com](https://supabase.com)
2. Tạo project mới
3. Vào Settings → Database
4. Copy Connection String

**Option 3: ElephantSQL (Free 20MB)**
1. Truy cập [elephantsql.com](https://www.elephantsql.com)
2. Tạo instance mới (chọn Tiny Turtle - Free)
3. Copy URL/Details

### 5.2. Chạy Schema SQL

Kết nối vào database của bạn và chạy file `setup.sql`:

```bash
psql -h your-host -U your-user -d your-database -f setup.sql
```

Hoặc sử dụng GUI tools như pgAdmin, DBeaver, hoặc TablePlus.

### 5.3. Cấu hình Secrets

Tạo thư mục và file secrets:

```bash
mkdir .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Mở file `.streamlit/secrets.toml` và điền thông tin:

```toml
[postgres]
host = "your-database-host"
dbname = "your-database-name"
user = "your-username"
password = "your-password"
port = "5432"
```

**⚠️ QUAN TRỌNG:** File này đã được thêm vào `.gitignore` - KHÔNG được push lên GitHub!

## 🎨 Bước 6: Tải Font chữ

### 6.1. Tạo thư mục fonts

```bash
mkdir fonts
```

### 6.2. Tải Roboto Font

**Cách 1: Tải từ Google Fonts**
1. Truy cập [Google Fonts - Roboto](https://fonts.google.com/specimen/Roboto)
2. Click "Download family"
3. Giải nén file ZIP
4. Copy file `Roboto-Regular.ttf` vào thư mục `fonts/`

**Cách 2: Sử dụng wget (Linux/macOS)**
```bash
cd fonts
wget https://github.com/google/roboto/releases/download/v2.138/roboto-unhinted.zip
unzip roboto-unhinted.zip
mv Roboto-Regular.ttf .
rm roboto-unhinted.zip
cd ..
```

### 6.3. Kiểm tra cấu trúc

```
Quanly5S-UMC/
├── fonts/
│   └── Roboto-Regular.ttf  ✅ Phải có file này
```

## 🚀 Bước 7: Chạy ứng dụng

```bash
streamlit run main.py
```

Ứng dụng sẽ tự động mở tại: `http://localhost:8501`

## ✅ Bước 8: Kiểm tra

1. Mở trình duyệt tại `http://localhost:8501`
2. Bạn sẽ thấy trang chủ với tiêu đề "HỆ THỐNG QUẢN LÝ HOẠT ĐỘNG 5S - UMC"
3. Thử click vào các menu bên trái để kiểm tra các trang

## 🐛 Xử lý lỗi thường gặp

### Lỗi: "No module named 'streamlit'"
```bash
pip install streamlit
```

### Lỗi: "Không tìm thấy thông tin kết nối Database"
- Kiểm tra file `.streamlit/secrets.toml` đã được tạo
- Kiểm tra định dạng TOML đúng (không có tab, chỉ dùng spaces)

### Lỗi: "Connection refused" khi kết nối DB
- Kiểm tra thông tin host, port, username, password
- Kiểm tra firewall/network cho phép kết nối
- Đảm bảo database đã được tạo

### Lỗi: "Font file not found"
- Kiểm tra file `fonts/Roboto-Regular.ttf` tồn tại
- Đảm bảo đường dẫn chính xác (fonts/ ở cùng cấp với main.py)

### Lỗi: Module 'psycopg2' has no attribute 'connect'
```bash
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary
```

## 🌐 Deploy lên Streamlit Cloud

### Bước 1: Push code lên GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Bước 2: Deploy trên Streamlit Cloud

1. Truy cập [share.streamlit.io](https://share.streamlit.io)
2. Đăng nhập bằng GitHub
3. Click "New app"
4. Chọn repository: `your-username/Quanly5S-UMC`
5. Main file: `main.py`
6. Click "Deploy"

### Bước 3: Cấu hình Secrets

1. Vào app settings (⚙️)
2. Chọn "Secrets"
3. Paste nội dung file `.streamlit/secrets.toml` vào
4. Click "Save"

### Bước 4: Thêm Font

**Lưu ý:** Bạn CẦN push file font lên GitHub:

```bash
git add fonts/Roboto-Regular.ttf
git commit -m "Add Roboto font"
git push
```

Streamlit Cloud sẽ tự động rebuild app.

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra lại từng bước
2. Xem phần "Xử lý lỗi thường gặp"
3. Tạo Issue trên GitHub với thông tin chi tiết lỗi

## 🎉 Hoàn thành!

Bây giờ bạn đã có một hệ thống quản lý 5S hoàn chỉnh!

**Bước tiếp theo:**
- Thêm Khoa/Phòng vào hệ thống
- Cấu hình Khu vực và Tiêu chí 5S
- Bắt đầu đánh giá!
