# 🚀 HƯỚNG DẪN ĐĂNG DỰ ÁN LÊN GITHUB

## 📋 Chuẩn bị

### Bước 1: Tạo tài khoản GitHub (nếu chưa có)

1. Truy cập [github.com](https://github.com)
2. Click "Sign up"
3. Điền thông tin và xác nhận email

### Bước 2: Cài đặt Git

**Windows:**
- Tải Git từ [git-scm.com](https://git-scm.com)
- Chạy file cài đặt với cấu hình mặc định

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

### Bước 3: Cấu hình Git lần đầu

```bash
git config --global user.name "Tên của bạn"
git config --global user.email "email@example.com"
```

## 🌐 Tạo Repository trên GitHub

### Option A: Tạo mới trên Web

1. Đăng nhập GitHub
2. Click nút "+" → "New repository"
3. Điền thông tin:
   - **Repository name**: `Quanly5S-UMC`
   - **Description**: "Hệ thống Quản lý Hoạt động 5S cho Bệnh viện UMC"
   - **Public/Private**: Chọn Public (hoặc Private nếu muốn)
   - ❌ **KHÔNG** tích "Initialize with README" (vì đã có rồi)
4. Click "Create repository"

### Option B: Tạo từ Command Line

GitHub sẽ hiển thị các lệnh, nhưng chúng ta làm theo hướng dẫn dưới.

## 📤 Đẩy Code lên GitHub

### Bước 1: Di chuyển vào thư mục dự án

```bash
cd path/to/Quanly5S-UMC
```

**Ví dụ Windows:**
```bash
cd C:\Users\YourName\Downloads\Quanly5S-UMC
```

**Ví dụ macOS/Linux:**
```bash
cd ~/Downloads/Quanly5S-UMC
```

### Bước 2: Khởi tạo Git repository

```bash
git init
```

### Bước 3: Kiểm tra file .gitignore

Đảm bảo file `.gitignore` có nội dung:

```
.streamlit/
__pycache__/
*.pyc
venv/
.env
.DS_Store
```

### Bước 4: Tải Font Roboto (QUAN TRỌNG)

**⚠️ Trước khi commit, PHẢI tải font:**

```bash
cd fonts
wget https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Regular.ttf
cd ..
```

Hoặc tải thủ công từ [Google Fonts](https://fonts.google.com/specimen/Roboto)

### Bước 5: Add tất cả files

```bash
git add .
```

### Bước 6: Commit lần đầu

```bash
git commit -m "Initial commit: Web app Quản lý 5S UMC v1.0"
```

### Bước 7: Thêm remote repository

**Thay `your-username` bằng username GitHub của bạn:**

```bash
git remote add origin https://github.com/your-username/Quanly5S-UMC.git
```

### Bước 8: Đẩy code lên GitHub

```bash
git branch -M main
git push -u origin main
```

**Nếu yêu cầu đăng nhập:**
- Username: GitHub username
- Password: Personal Access Token (không phải password GitHub)

### 🔐 Tạo Personal Access Token (nếu cần)

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Chọn scopes: `repo` (full control)
4. Copy token và dùng làm password khi push

## ✅ Kiểm tra

1. Truy cập `https://github.com/your-username/Quanly5S-UMC`
2. Bạn sẽ thấy:
   - ✅ README.md hiển thị đẹp
   - ✅ Tất cả files và folders
   - ✅ File `fonts/Roboto-Regular.ttf` có trong repo

## 📝 Chỉnh sửa README trên GitHub (Optional)

1. Vào file README.md trên GitHub
2. Sửa dòng:
   ```
   git clone https://github.com/your-username/Quanly5S-UMC.git
   ```
   Thay `your-username` bằng username thực của bạn

3. Commit changes

## 🔄 Cập nhật sau này

Khi có thay đổi:

```bash
git add .
git commit -m "Mô tả thay đổi"
git push
```

## 🌟 Làm đẹp Repository

### Thêm Topics (Tags)

Vào Settings → Manage topics, thêm:
- `streamlit`
- `healthcare`
- `5s-management`
- `quality-control`
- `postgresql`
- `python`

### Thêm GitHub Social Preview

1. Settings → General
2. Scroll xuống "Social preview"
3. Upload ảnh screenshot app (1200×630 px)

### Tạo Release

1. Vào tab "Releases"
2. "Create a new release"
3. Tag: `v1.0.0`
4. Title: "Version 1.0.0 - Initial Release"
5. Description: Copy từ CHANGELOG.md

## 🚢 Deploy lên Streamlit Cloud

### Bước 1: Kết nối GitHub

1. Vào [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Authorize Streamlit

### Bước 2: Deploy App

1. Click "New app"
2. Chọn:
   - **Repository**: `your-username/Quanly5S-UMC`
   - **Branch**: `main`
   - **Main file path**: `main.py`
3. Advanced settings → Python version: `3.10`

### Bước 3: Cấu hình Secrets

1. Click "Advanced settings"
2. Vào tab "Secrets"
3. Paste nội dung file `.streamlit/secrets.toml`:

```toml
[postgres]
host = "your-database-host"
dbname = "your-database-name"
user = "your-username"
password = "your-password"
port = "5432"
```

4. Click "Save"

### Bước 4: Deploy!

1. Click "Deploy!"
2. Đợi 2-3 phút
3. App sẽ có URL: `https://quanly5s-umc-xxxxx.streamlit.app`

## 🎉 Hoàn thành!

Repository của bạn đã online tại:
```
https://github.com/your-username/Quanly5S-UMC
```

Web app đã deploy tại:
```
https://your-app-name.streamlit.app
```

## 📌 Checklist cuối cùng

- [ ] Repository đã public/private đúng ý muốn
- [ ] README.md hiển thị đẹp
- [ ] Font `Roboto-Regular.ttf` đã có trong repo
- [ ] File `.streamlit/secrets.toml` KHÔNG có trong repo (đã gitignore)
- [ ] Topics/Tags đã thêm
- [ ] License đã chọn (MIT)
- [ ] App đã deploy thành công trên Streamlit Cloud
- [ ] Database secrets đã cấu hình trên Streamlit Cloud

## 🔗 Links hữu ích

- GitHub Guide: https://guides.github.com
- Git Cheat Sheet: https://education.github.com/git-cheat-sheet-education.pdf
- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- Markdown Guide: https://www.markdownguide.org

---

**Chúc mừng! Dự án của bạn đã sẵn sàng cho cộng đồng! 🎊**
