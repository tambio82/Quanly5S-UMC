import streamlit as st
import json
from db_utils import run_query, run_insert

st.set_page_config(page_title="Quản lý Đơn vị", page_icon="🏢", layout="wide")

st.title("🏢 QUẢN LÝ ĐƠN VỊ")

# Form thêm đơn vị mới
with st.form("add_department", clear_on_submit=True):
    st.subheader("Thêm Khoa/Phòng mới")
    
    col1, col2 = st.columns(2)
    with col1:
        unit_code = st.text_input("Mã đơn vị", placeholder="VD: K01, P02")
        unit_name = st.text_input("Tên đơn vị", placeholder="VD: Khoa Nội")
    
    with col2:
        st.write("**Vị trí địa lý (tối đa 8 vị trí):**")
        locations = []
        num_locations = st.number_input("Số lượng vị trí", min_value=1, max_value=8, value=1)
        
        for i in range(int(num_locations)):
            loc = st.text_input(f"Vị trí {i+1}", key=f"loc_{i}", placeholder=f"VD: Tầng {i+1}, Phòng...")
            if loc:
                locations.append(loc)
    
    st.divider()
    
    # Phần nhân sự
    st.write("**Nhân sự phụ trách (tối đa 5 người):**")
    num_staff = st.number_input("Số lượng nhân sự", min_value=0, max_value=5, value=1)
    
    staff_list = []
    for i in range(int(num_staff)):
        st.write(f"**Nhân viên {i+1}**")
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            name = st.text_input("Tên NV", key=f"staff_name_{i}", placeholder="Nguyễn Văn A")
        with col_b:
            staff_code = st.text_input("Mã NV", key=f"staff_code_{i}", placeholder="D03-046")
        with col_c:
            email = st.text_input("Email", key=f"email_{i}", placeholder="email@umc.edu.vn")
        with col_d:
            role = st.selectbox("Phân quyền", ["Thành viên tổ 5S", "Điều phối chính"], key=f"role_{i}")
        
        if name and staff_code:
            staff_list.append({
                "name": name,
                "staff_code": staff_code,
                "email": email,
                "role": role
            })
    
    submitted = st.form_submit_button("💾 Lưu thông tin", type="primary")
    
    if submitted:
        if not unit_code or not unit_name:
            st.error("Vui lòng nhập đầy đủ Mã và Tên đơn vị!")
        else:
            try:
                # Thêm department
                dept_query = """
                    INSERT INTO departments (unit_code, unit_name, locations)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """
                locations_json = json.dumps(locations) if locations else None
                
                # Lấy ID của department vừa tạo
                import psycopg2
                from db_utils import get_connection
                
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(dept_query, (unit_code, unit_name, locations_json))
                dept_id = cur.fetchone()[0]
                
                # Thêm staff
                if staff_list:
                    staff_query = """
                        INSERT INTO staff (department_id, name, staff_code, email, role)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    for staff in staff_list:
                        cur.execute(staff_query, (
                            dept_id,
                            staff["name"],
                            staff["staff_code"],
                            staff["email"],
                            staff["role"]
                        ))
                
                conn.commit()
                cur.close()
                conn.close()
                
                st.success(f"✅ Đã thêm đơn vị '{unit_name}' với {len(staff_list)} nhân sự!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")

st.divider()

# Hiển thị danh sách đơn vị
st.subheader("📋 Danh sách Khoa/Phòng")

df_depts = run_query("""
    SELECT 
        d.id,
        d.unit_code,
        d.unit_name,
        d.locations,
        COUNT(s.id) as so_nhan_su,
        STRING_AGG(s.name, ', ') as danh_sach_nv
    FROM departments d
    LEFT JOIN staff s ON d.id = s.department_id
    GROUP BY d.id, d.unit_code, d.unit_name, d.locations
    ORDER BY d.unit_code
""")

if not df_depts.empty:
    for idx, row in df_depts.iterrows():
        with st.expander(f"**{row['unit_code']}** - {row['unit_name']} ({row['so_nhan_su']} nhân sự)"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.write("**Thông tin:**")
                st.write(f"- Mã: `{row['unit_code']}`")
                st.write(f"- Số nhân sự: {row['so_nhan_su']} người")
                
                if row['locations']:
                    try:
                        locs = json.loads(row['locations'])
                        st.write(f"- Vị trí: {', '.join(locs)}")
                    except:
                        pass
            
            with col2:
                st.write("**Nhân sự:**")
                if row['danh_sach_nv']:
                    st.write(row['danh_sach_nv'])
                else:
                    st.info("Chưa có nhân sự")
                
                # Hiển thị chi tiết nhân sự
                df_staff = run_query(
                    "SELECT name, staff_code, email, role FROM staff WHERE department_id = %s",
                    params=(row['id'],)
                )
                if not df_staff.empty:
                    st.dataframe(df_staff, use_container_width=True, hide_index=True)
else:
    st.info("Chưa có đơn vị nào. Hãy thêm mới!")
