import streamlit as st

st.set_page_config(
    page_title="5S - UMC",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 HỆ THỐNG QUẢN LÝ HOẠT ĐỘNG 5S - UMC")
st.sidebar.success("Chọn module chức năng.")

st.markdown("""
### Chào mừng đến với Hệ thống Quản lý Chất lượng 5S
Vui lòng chọn các chức năng từ thanh bên trái (sidebar) để thao tác:

* **🏠 Trang chủ:** Xem Dashboard tổng quan tình hình 5S toàn viện.
* **🏢 Quản lý đơn vị:** Thêm mới Khoa/Phòng và Nhân sự phụ trách.
* **⚙️ Cấu hình 5S:** Thiết lập danh mục Khu vực và Tiêu chí kiểm tra.
* **📝 Đánh giá:** Thực hiện Checklist 5S điện tử.
* **📊 Thống kê:** Phân tích sâu dữ liệu, biểu đồ Heatmap, xu hướng.
* **📑 Xuất báo cáo:** Tạo báo cáo PDF kết quả kiểm tra.
* **💾 Dữ liệu:** Nhập/Xuất dữ liệu hàng loạt từ Excel.
""")
