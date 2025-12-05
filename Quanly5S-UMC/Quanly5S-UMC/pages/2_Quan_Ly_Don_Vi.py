import streamlit as st
import json
from db_utils import run_query, run_insert, get_connection

st.set_page_config(page_title="Quản lý Đơn vị", page_icon="🏢", layout="wide")

st.title("🏢 QUẢN LÝ ĐƠN VỊ")

# Tab navigation
tab1, tab2 = st.tabs(["➕ Thêm mới", "📋 Danh sách & Chỉnh sửa"])

# ==================== TAB 1: THÊM MỚI ====================
with tab1:
    with st.form("add_department", clear_on_submit=True):
        st.subheader("Thêm Khoa/Phòng mới")
        
        col1, col2 = st.columns(2)
        with col1:
            unit_code = st.text_input("Mã đơn vị*", placeholder="VD: K01, P02")
            unit_name = st.text_input("Tên đơn vị*", placeholder="VD: Khoa Nội")
        
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
                name = st.text_input("Tên NV*", key=f"staff_name_{i}", placeholder="Nguyễn Văn A")
            with col_b:
                staff_code = st.text_input("Mã NV*", key=f"staff_code_{i}", placeholder="D03-046")
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
                st.error("⚠️ Vui lòng nhập đầy đủ Mã và Tên đơn vị!")
            else:
                try:
                    # Thêm department
                    dept_query = """
                        INSERT INTO departments (unit_code, unit_name, locations)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """
                    locations_json = json.dumps(locations) if locations else None
                    
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
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")

# ==================== TAB 2: DANH SÁCH & SỬA ====================
with tab2:
    st.subheader("📋 Danh sách Khoa/Phòng")
    
    # Lấy danh sách đơn vị
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
                
                # Hiển thị thông tin hiện tại
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    st.write("**📌 Thông tin:**")
                    st.write(f"- Mã: `{row['unit_code']}`")
                    st.write(f"- Tên: {row['unit_name']}")
                    st.write(f"- Số nhân sự: {row['so_nhan_su']} người")
                    
                    if row['locations']:
                        try:
                            locs = json.loads(row['locations'])
                            st.write(f"- Vị trí: {', '.join(locs)}")
                        except:
                            pass
                
                with col_actions:
                    st.write("**⚙️ Thao tác:**")
                    edit_btn = st.button("✏️ Sửa", key=f"edit_{row['id']}", use_container_width=True)
                    delete_btn = st.button("🗑️ Xóa", key=f"delete_{row['id']}", type="secondary", use_container_width=True)
                
                st.divider()
                
                # Hiển thị danh sách nhân sự
                st.write("**👥 Nhân sự:**")
                df_staff = run_query(
                    "SELECT id, name, staff_code, email, role FROM staff WHERE department_id = %s ORDER BY name",
                    params=(row['id'],)
                )
                
                if not df_staff.empty:
                    st.dataframe(df_staff, use_container_width=True, hide_index=True)
                else:
                    st.info("Chưa có nhân sự")
                
                # ===== XỬ LÝ NÚT SỬA =====
                if edit_btn:
                    st.session_state[f"editing_{row['id']}"] = True
                
                if st.session_state.get(f"editing_{row['id']}", False):
                    st.divider()
                    st.write("### ✏️ Chỉnh sửa thông tin")
                    
                    with st.form(key=f"edit_form_{row['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_unit_code = st.text_input("Mã đơn vị", value=row['unit_code'], key=f"new_code_{row['id']}")
                            new_unit_name = st.text_input("Tên đơn vị", value=row['unit_name'], key=f"new_name_{row['id']}")
                        
                        with col2:
                            st.write("**Vị trí địa lý:**")
                            current_locs = []
                            if row['locations']:
                                try:
                                    current_locs = json.loads(row['locations'])
                                except:
                                    pass
                            
                            new_locations = []
                            num_locs = st.number_input("Số lượng vị trí", min_value=1, max_value=8, value=len(current_locs) or 1, key=f"num_locs_{row['id']}")
                            
                            for i in range(int(num_locs)):
                                default_val = current_locs[i] if i < len(current_locs) else ""
                                loc = st.text_input(f"Vị trí {i+1}", value=default_val, key=f"edit_loc_{row['id']}_{i}")
                                if loc:
                                    new_locations.append(loc)
                        
                        col_save, col_cancel = st.columns(2)
                        
                        with col_save:
                            save_btn = st.form_submit_button("💾 Lưu thay đổi", type="primary", use_container_width=True)
                        with col_cancel:
                            cancel_btn = st.form_submit_button("❌ Hủy", use_container_width=True)
                        
                        if save_btn:
                            try:
                                conn = get_connection()
                                cur = conn.cursor()
                                
                                update_query = """
                                    UPDATE departments 
                                    SET unit_code = %s, unit_name = %s, locations = %s
                                    WHERE id = %s
                                """
                                locs_json = json.dumps(new_locations) if new_locations else None
                                cur.execute(update_query, (new_unit_code, new_unit_name, locs_json, row['id']))
                                
                                conn.commit()
                                cur.close()
                                conn.close()
                                
                                st.success("✅ Đã cập nhật thông tin!")
                                st.session_state[f"editing_{row['id']}"] = False
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Lỗi: {e}")
                        
                        if cancel_btn:
                            st.session_state[f"editing_{row['id']}"] = False
                            st.rerun()
                
                # ===== XỬ LÝ NÚT XÓA =====
                if delete_btn:
                    st.session_state[f"confirm_delete_{row['id']}"] = True
                
                if st.session_state.get(f"confirm_delete_{row['id']}", False):
                    st.warning(f"⚠️ Bạn có chắc muốn xóa đơn vị **{row['unit_name']}**? Tất cả nhân sự và dữ liệu liên quan sẽ bị xóa!")
                    
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Xác nhận xóa", key=f"confirm_yes_{row['id']}", type="primary"):
                            try:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("DELETE FROM departments WHERE id = %s", (row['id'],))
                                conn.commit()
                                cur.close()
                                conn.close()
                                
                                st.success(f"✅ Đã xóa đơn vị '{row['unit_name']}'")
                                st.session_state[f"confirm_delete_{row['id']}"] = False
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Lỗi: {e}")
                    
                    with col_no:
                        if st.button("❌ Hủy", key=f"confirm_no_{row['id']}"):
                            st.session_state[f"confirm_delete_{row['id']}"] = False
                            st.rerun()
    else:
        st.info("📭 Chưa có đơn vị nào. Hãy vào tab 'Thêm mới' để thêm!")

# ==================== THÊM/SỬA/XÓA NHÂN SỰ ====================
st.divider()
st.subheader("👤 Quản lý Nhân sự")

col_dept_select, col_action_select = st.columns([2, 1])

with col_dept_select:
    # Lấy danh sách đơn vị cho dropdown
    df_depts_list = run_query("SELECT id, unit_code, unit_name FROM departments ORDER BY unit_code")
    
    if not df_depts_list.empty:
        dept_options = {f"{row['unit_code']} - {row['unit_name']}": row['id'] for _, row in df_depts_list.iterrows()}
        selected_dept = st.selectbox("Chọn đơn vị", options=list(dept_options.keys()))
        selected_dept_id = dept_options[selected_dept]
    else:
        st.info("Vui lòng thêm đơn vị trước!")
        selected_dept_id = None

with col_action_select:
    st.write("")
    st.write("")
    action = st.radio("Thao tác", ["Thêm nhân sự", "Sửa/Xóa nhân sự"], horizontal=True)

if selected_dept_id:
    if action == "Thêm nhân sự":
        with st.form("add_staff_form"):
            st.write("**Thêm nhân sự mới**")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                new_staff_name = st.text_input("Tên NV*")
            with col2:
                new_staff_code = st.text_input("Mã NV*")
            with col3:
                new_staff_email = st.text_input("Email")
            with col4:
                new_staff_role = st.selectbox("Phân quyền", ["Thành viên tổ 5S", "Điều phối chính"])
            
            add_staff_btn = st.form_submit_button("➕ Thêm nhân sự", type="primary")
            
            if add_staff_btn:
                if not new_staff_name or not new_staff_code:
                    st.error("⚠️ Vui lòng nhập đầy đủ Tên và Mã NV!")
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO staff (department_id, name, staff_code, email, role) VALUES (%s, %s, %s, %s, %s)",
                            (selected_dept_id, new_staff_name, new_staff_code, new_staff_email, new_staff_role)
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        
                        st.success(f"✅ Đã thêm nhân sự '{new_staff_name}'")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Lỗi: {e}")
    
    else:  # Sửa/Xóa nhân sự
        df_staff_edit = run_query(
            "SELECT id, name, staff_code, email, role FROM staff WHERE department_id = %s ORDER BY name",
            params=(selected_dept_id,)
        )
        
        if not df_staff_edit.empty:
            for idx, staff in df_staff_edit.iterrows():
                with st.expander(f"👤 {staff['name']} ({staff['staff_code']})"):
                    with st.form(f"staff_edit_form_{staff['id']}"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            edit_name = st.text_input("Tên", value=staff['name'], key=f"edit_staff_name_{staff['id']}")
                        with col2:
                            edit_code = st.text_input("Mã", value=staff['staff_code'], key=f"edit_staff_code_{staff['id']}")
                        with col3:
                            edit_email = st.text_input("Email", value=staff['email'] or "", key=f"edit_staff_email_{staff['id']}")
                        with col4:
                            edit_role = st.selectbox("Phân quyền", ["Thành viên tổ 5S", "Điều phối chính"], 
                                                    index=0 if staff['role'] == "Thành viên tổ 5S" else 1,
                                                    key=f"edit_staff_role_{staff['id']}")
                        
                        col_save, col_delete = st.columns(2)
                        
                        with col_save:
                            save_staff = st.form_submit_button("💾 Lưu", type="primary", use_container_width=True)
                        with col_delete:
                            delete_staff = st.form_submit_button("🗑️ Xóa", use_container_width=True)
                        
                        if save_staff:
                            try:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute(
                                    "UPDATE staff SET name=%s, staff_code=%s, email=%s, role=%s WHERE id=%s",
                                    (edit_name, edit_code, edit_email, edit_role, staff['id'])
                                )
                                conn.commit()
                                cur.close()
                                conn.close()
                                
                                st.success("✅ Đã cập nhật!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Lỗi: {e}")
                        
                        if delete_staff:
                            try:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("DELETE FROM staff WHERE id=%s", (staff['id'],))
                                conn.commit()
                                cur.close()
                                conn.close()
                                
                                st.success(f"✅ Đã xóa '{staff['name']}'")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Lỗi: {e}")
        else:
            st.info("Chưa có nhân sự trong đơn vị này")
