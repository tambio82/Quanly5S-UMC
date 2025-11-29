import streamlit as st
from db_utils import run_insert
import json

st.set_page_config(page_title="Quản lý Đơn vị", page_icon="🏢", layout="wide")
st.header("THÊM KHOA/ĐƠN VỊ/PHÒNG VÀ NHÂN SỰ")

with st.form("add_dept_form"):
    col1, col2 = st.columns(2)
    unit_code = col1.text_input("Mã số đơn vị (Ví dụ: K01)")
    unit_name = col2.text_input("Tên đơn vị (Ví dụ: Khoa Cấp Cứu)")
    
    st.subheader("Vị trí địa lý (Tối đa 8)")
    locs = []
    cols_loc = st.columns(4)
    for i in range(8):
        val = cols_loc[i%4].text_input(f"Vị trí {i+1}", key=f"loc_{i}")
        if val: locs.append(val)
    
    st.subheader("Nhân sự phụ trách (Tối đa 5)")
    staff_list = []
    for i in range(5):
        st.markdown(f"**Nhân viên {i+1}**")
        c1, c2, c3, c4 = st.columns(4)
        s_name = c1.text_input("Tên NV", key=f"sn_{i}")
        s_code = c2.text_input("Mã NV", key=f"sc_{i}")
        s_email = c3.text_input("Email", key=f"se_{i}")
        s_role = c4.selectbox("Phân quyền", ["Thành viên tổ 5S", "Điều phối chính"], key=f"sr_{i}")
        
        if s_name and s_code:
            staff_list.append((s_name, s_code, s_email, s_role))

    submitted = st.form_submit_button("Lưu thông tin")

    if submitted:
        if unit_code and unit_name:
            loc_json = json.dumps(locs)
            try:
                # Sử dụng raw connection để lấy ID vừa insert
                conn = st.connection("postgres", type="sql").engine.raw_connection()
                cur = conn.cursor()
                
                # 1. Insert Department
                cur.execute("INSERT INTO departments (unit_code, unit_name, locations) VALUES (%s, %s, %s) RETURNING id", 
                            (unit_code, unit_name, loc_json))
                new_dept_id = cur.fetchone()[0]
                
                # 2. Insert Staff
                for s in staff_list:
                    cur.execute("INSERT INTO staff (department_id, name, staff_code, email, role) VALUES (%s, %s, %s, %s, %s)",
                                (new_dept_id, s[0], s[1], s[2], s[3]))
                
                conn.commit()
                st.success(f"Đã thêm đơn vị {unit_name} thành công!")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Lỗi: {e}")
        else:
            st.error("Vui lòng nhập Mã và Tên đơn vị.")
