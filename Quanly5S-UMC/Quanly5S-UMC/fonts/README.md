# 🔤 Font Configuration

## Yêu cầu

Ứng dụng cần file font **Roboto-Regular.ttf** để xuất báo cáo PDF với tiếng Việt.

## Cách tải Font

### Cách 1: Tải từ Google Fonts (Khuyến nghị)

1. Truy cập: https://fonts.google.com/specimen/Roboto
2. Click nút "Download family"
3. Giải nén file ZIP đã tải
4. Tìm file `Roboto-Regular.ttf` trong thư mục `static`
5. Copy file vào thư mục này (`fonts/`)

### Cách 2: Tải trực tiếp từ GitHub

```bash
cd fonts
wget https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Regular.ttf
```

### Cách 3: Sử dụng curl

```bash
cd fonts
curl -L -o Roboto-Regular.ttf "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Regular.ttf"
```

## Kiểm tra

Sau khi tải, đảm bảo cấu trúc như sau:

```
fonts/
├── README.md          (file này)
└── Roboto-Regular.ttf (file font - khoảng 170KB)
```

## Lưu ý

- File font CẦN được push lên GitHub để deploy lên Streamlit Cloud hoạt động
- Nếu không có font, chức năng xuất PDF sẽ báo lỗi
- Font Roboto được cấp phép Apache License 2.0 (miễn phí sử dụng)

## Troubleshooting

**Lỗi: "Thiếu file fonts/Roboto-Regular.ttf"**
- Kiểm tra file đã được tải về đúng tên
- Đảm bảo file nằm đúng thư mục `fonts/` (cùng cấp với `main.py`)

**File bị lỗi khi mở**
- Tải lại file từ nguồn chính thức
- Kiểm tra file không bị corrupt (size khoảng 170KB)
