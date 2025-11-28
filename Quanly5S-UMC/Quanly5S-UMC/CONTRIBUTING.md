# 🤝 Hướng dẫn Đóng góp

Cảm ơn bạn quan tâm đến việc đóng góp cho dự án Hệ thống Quản lý 5S - UMC!

## 📋 Cách đóng góp

### 1. Báo cáo lỗi (Bug Reports)

Nếu bạn phát hiện lỗi, vui lòng tạo Issue với các thông tin sau:
- Mô tả chi tiết lỗi
- Các bước tái hiện lỗi
- Kết quả mong đợi vs kết quả thực tế
- Screenshots (nếu có)
- Thông tin môi trường (OS, Python version, Browser)

### 2. Đề xuất tính năng mới

Tạo Issue với nhãn "enhancement" bao gồm:
- Mô tả tính năng
- Lý do cần tính năng này
- Cách tính năng sẽ hoạt động
- Mockup/wireframe (nếu có)

### 3. Pull Requests

#### Quy trình:

1. **Fork repository**
2. **Tạo branch mới**
   ```bash
   git checkout -b feature/ten-tinh-nang
   # hoặc
   git checkout -b fix/ten-loi
   ```

3. **Thực hiện thay đổi**
   - Tuân thủ coding style hiện có
   - Thêm comments cho code phức tạp
   - Test kỹ trước khi commit

4. **Commit với message rõ ràng**
   ```bash
   git commit -m "Add: Thêm chức năng xuất Excel theo khu vực"
   git commit -m "Fix: Sửa lỗi hiển thị biểu đồ khi không có dữ liệu"
   ```

5. **Push lên GitHub**
   ```bash
   git push origin feature/ten-tinh-nang
   ```

6. **Tạo Pull Request**
   - Mô tả chi tiết thay đổi
   - Link đến Issue liên quan (nếu có)
   - Screenshot kết quả (nếu là UI)

## 📝 Coding Style

### Python
- Tuân thủ PEP 8
- Sử dụng 4 spaces cho indentation
- Đặt tên biến, hàm rõ ràng, có ý nghĩa
- Comments bằng tiếng Việt hoặc tiếng Anh

### SQL
- Viết keywords bằng chữ HOA (SELECT, FROM, WHERE)
- Format query dễ đọc với line breaks

### Streamlit
- Sử dụng emojis phù hợp cho titles
- Tổ chức code theo structure: imports → config → functions → UI

## 🧪 Testing

Trước khi submit PR, đảm bảo:
- [ ] Code chạy không lỗi
- [ ] Test trên database mẫu
- [ ] Kiểm tra UI responsive
- [ ] Không có hardcoded credentials
- [ ] File `.gitignore` đã được update (nếu cần)

## 🎯 Ưu tiên đóng góp

Các vấn đề đang cần giúp đỡ:
- [ ] Unit tests cho các functions
- [ ] Thêm validation cho forms
- [ ] Cải thiện UI/UX
- [ ] Tối ưu performance queries
- [ ] Thêm tiếng Anh (i18n)
- [ ] Mobile responsive
- [ ] Dark mode

## 📞 Liên hệ

Nếu có câu hỏi, tạo Issue hoặc comment trong PR.

## ⚖️ License

Khi đóng góp code, bạn đồng ý với việc code được phân phối dưới MIT License.

---

**Cảm ơn sự đóng góp của bạn! 🙏**
