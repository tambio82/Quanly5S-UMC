import streamlit as st
from db_utils import run_query, get_connection

st.set_page_config(page_title="Cấu hình Khu vực", page_icon="⚙️", layout="wide")

st.title("⚙️ CẤU HÌNH KHU VỰC VÀ TIÊU CHÍ")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏢 Gán Khu vực cho Khoa/Phòng", 
    "📋 Quản lý Khu vực chung",
    "📝 Quản lý Tiêu chí", 
    "✏️ Chỉnh sửa"
])

# ==================== TAB 1: GÁN KHU VỰC CHO KHOA/PHÒNG ====================
with tab1:
    st.subheader("🏢 Cấu hình Khu vực cho từng Khoa/Phòng")
    
    st.info("💡 **Hướng dẫn:** Chọn Khoa/Phòng, sau đó chọn các Khu vực áp dụng. Mỗi Khoa/Phòng có thể có cấu hình riêng.")
    
    # Lấy danh sách departments
    df_depts = run_query("SELECT id, unit_code, unit_name FROM departments ORDER BY unit_code")
    
    if df_depts.empty:
        st.warning("⚠️ Chưa có Khoa/Phòng. Vui lòng thêm ở trang 'Quan Ly Don Vi'")
    else:
        dept_options = {f"{row['unit_code']} - {row['unit_name']}": row['id'] for _, row in df_depts.iterrows()}
        selected_dept = st.selectbox("Chọn Khoa/Phòng", options=list(dept_options.keys()), key="dept_select_tab1")
        selected_dept_id = dept_options[selected_dept]
        
        st.divider()
        
        # Lấy danh sách areas
        df_areas = run_query("SELECT id, area_code, area_name, definition FROM areas ORDER BY area_code")
        
        if df_areas.empty:
            st.warning("⚠️ Chưa có Khu vực nào. Vui lòng thêm ở Tab 'Quản lý Khu vực chung'")
        else:
            # Lấy areas đã được gán cho department này
            df_assigned = run_query(
                "SELECT area_id FROM department_areas WHERE department_id = %s",
                params=(selected_dept_id,)
            )
            assigned_area_ids = df_assigned['area_id'].tolist() if not df_assigned.empty else []
            
            st.write(f"### Chọn các Khu vực cho: **{selected_dept}**")
            
            # Hiển thị checkboxes cho từng area
            selected_areas = []
            
            for idx, area in df_areas.iterrows():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    is_checked = st.checkbox(
                        f"**{area['area_code']}**",
                        value=area['id'] in assigned_area_ids,
                        key=f"area_check_{area['id']}"
                    )
                
                with col2:
                    st.write(f"**{area['area_name']}**")
                    if area['definition']:
                        st.caption(area['definition'])
                
                if is_checked:
                    selected_areas.append(area['id'])
            
            st.divider()
            
            # Nút lưu
            if st.button("💾 Lưu Cấu hình", type="primary", use_container_width=True):
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    
                    # Xóa cấu hình cũ
                    cur.execute("DELETE FROM department_areas WHERE department_id = %s", (selected_dept_id,))
                    
                    # Thêm cấu hình mới
                    for area_id in selected_areas:
                        cur.execute(
                            "INSERT INTO department_areas (department_id, area_id) VALUES (%s, %s)",
                            (selected_dept_id, area_id)
                        )
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    st.success(f"✅ Đã lưu cấu hình cho {selected_dept}: {len(selected_areas)} khu vực")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")
            
            # Hiển thị tóm tắt
            if assigned_area_ids:
                st.write("### 📊 Cấu hình hiện tại")
                df_current = df_areas[df_areas['id'].isin(assigned_area_ids)]
                st.dataframe(
                    df_current[['area_code', 'area_name', 'definition']],
                    use_container_width=True,
                    hide_index=True
                )

# ==================== TAB 2: QUẢN LÝ KHU VỰC CHUNG ====================
with tab2:
    st.subheader("📋 Quản lý Khu vực chung")
    
    st.info("💡 **Lưu ý:** Đây là danh sách Khu vực chung. Sau khi tạo, bạn gán chúng cho từng Khoa/Phòng ở Tab 1.")
    
    # Form thêm khu vực mới
    with st.expander("➕ Thêm Khu vực mới", expanded=False):
        with st.form("add_area", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                area_name = st.text_input("Tên khu vực*", placeholder="VD: Khu vực Hành chính")
                area_code = st.text_input("Ký hiệu*", placeholder="VD: HC")
            
            with col2:
                definition = st.text_area("Định nghĩa", placeholder="Văn phòng, phòng họp...", height=100)
            
            submit = st.form_submit_button("💾 Lưu Khu vực", type="primary")
            
            if submit:
                if not area_name or not area_code:
                    st.error("⚠️ Vui lòng nhập đầy đủ!")
                else:
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO areas (area_name, area_code, definition) VALUES (%s, %s, %s)",
                            (area_name, area_code, definition)
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        
                        st.success(f"✅ Đã thêm khu vực '{area_name}'")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Lỗi: {e}")
    
    # Hiển thị danh sách
    df_areas_list = run_query("""
        SELECT a.id, a.area_code, a.area_name, a.definition,
               COUNT(DISTINCT da.department_id) as so_khoa_phong,
               COUNT(DISTINCT c.id) as so_tieu_chi
        FROM areas a
        LEFT JOIN department_areas da ON a.id = da.area_id
        LEFT JOIN criteria c ON a.id = c.area_id
        GROUP BY a.id, a.area_code, a.area_name, a.definition
        ORDER BY a.area_code
    """)
    
    if not df_areas_list.empty:
        st.dataframe(
            df_areas_list,
            column_config={
                "id": None,
                "area_code": "Ký hiệu",
                "area_name": "Tên khu vực",
                "definition": "Định nghĩa",
                "so_khoa_phong": "Số Khoa/Phòng sử dụng",
                "so_tieu_chi": "Số tiêu chí"
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Chưa có khu vực nào.")

# ==================== TAB 3: QUẢN LÝ TIÊU CHÍ ====================
with tab3:
    st.subheader("📝 Quản lý Tiêu chí")
    
    st.info("💡 **Hướng dẫn:** Tiêu chí được thêm vào Khu vực. Sau đó sẽ tự động áp dụng cho các Khoa/Phòng đã chọn khu vực đó.")
    
    # Chọn khu vực
    df_areas_criteria = run_query("SELECT id, area_code, area_name FROM areas ORDER BY area_code")
    
    if df_areas_criteria.empty:
        st.warning("⚠️ Vui lòng thêm Khu vực trước!")
    else:
        area_options = {f"{row['area_code']} - {row['area_name']}": row['id'] for _, row in df_areas_criteria.iterrows()}
        selected_area = st.selectbox("Chọn Khu vực", options=list(area_options.keys()), key="area_select_tab3")
        selected_area_id = area_options[selected_area]
        
        st.divider()
        
        # Form thêm tiêu chí
        with st.expander("➕ Thêm Tiêu chí mới", expanded=False):
            with st.form("add_criteria", clear_on_submit=True):
                st.write(f"**Thêm tiêu chí cho: {selected_area}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    location_name = st.text_input("Vị trí cần kiểm tra*", placeholder="VD: Bàn làm việc")
                    category = st.text_input("Hạng mục đánh giá*", placeholder="VD: Sắp xếp")
                
                with col2:
                    requirement = st.text_area("Yêu cầu chi tiết", placeholder="Mô tả...", height=100)
                
                submit_criteria = st.form_submit_button("💾 Lưu Tiêu chí", type="primary")
                
                if submit_criteria:
                    if not location_name or not category:
                        st.error("⚠️ Vui lòng nhập đầy đủ!")
                    else:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO criteria (area_id, location_name, category, requirement) VALUES (%s, %s, %s, %s)",
                                (selected_area_id, location_name, category, requirement)
                            )
                            conn.commit()
                            cur.close()
                            conn.close()
                            
                            st.success(f"✅ Đã thêm tiêu chí '{category}'")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Lỗi: {e}")
        
        # Hiển thị danh sách tiêu chí
        df_criteria = run_query(
            """
            SELECT id, location_name, category, requirement
            FROM criteria 
            WHERE area_id = %s
            ORDER BY location_name, category
            """,
            params=(selected_area_id,)
        )
        
        if not df_criteria.empty:
            st.write(f"**Số lượng: {len(df_criteria)} tiêu chí**")
            st.dataframe(df_criteria, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có tiêu chí nào.")

# ==================== TAB 4: CHỈNH SỬA ====================
with tab4:
    st.subheader("✏️ Chỉnh sửa & Xóa")
    
    edit_tab1, edit_tab2 = st.tabs(["🏢 Sửa Khu vực", "📋 Sửa Tiêu chí"])
    
    # Sửa khu vực
    with edit_tab1:
        df_areas_edit = run_query("SELECT id, area_code, area_name, definition FROM areas ORDER BY area_code")
        
        if not df_areas_edit.empty:
            for idx, area in df_areas_edit.iterrows():
                with st.expander(f"**{area['area_code']}** - {area['area_name']}"):
                    with st.form(f"edit_area_{area['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_code = st.text_input("Ký hiệu", value=area['area_code'], key=f"code_{area['id']}")
                            new_name = st.text_input("Tên", value=area['area_name'], key=f"name_{area['id']}")
                        
                        with col2:
                            new_def = st.text_area("Định nghĩa", value=area['definition'] or "", key=f"def_{area['id']}")
                        
                        col_save, col_del = st.columns(2)
                        
                        with col_save:
                            save = st.form_submit_button("💾 Lưu", type="primary", use_container_width=True)
                        with col_del:
                            delete = st.form_submit_button("🗑️ Xóa", use_container_width=True)
                        
                        if save:
                            try:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute(
                                    "UPDATE areas SET area_code=%s, area_name=%s, definition=%s WHERE id=%s",
                                    (new_code, new_name, new_def, area['id'])
                                )
                                conn.commit()
                                cur.close()
                                conn.close()
                                st.success("✅ Đã cập nhật!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Lỗi: {e}")
                        
                        if delete:
                            try:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("DELETE FROM areas WHERE id=%s", (area['id'],))
                                conn.commit()
                                cur.close()
                                conn.close()
                                st.success("✅ Đã xóa!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Lỗi: {e}")
        else:
            st.info("Chưa có khu vực.")
    
    # Sửa tiêu chí
    with edit_tab2:
        df_areas_crit = run_query("SELECT id, area_code, area_name FROM areas ORDER BY area_code")
        
        if not df_areas_crit.empty:
            area_opts = {f"{r['area_code']} - {r['area_name']}": r['id'] for _, r in df_areas_crit.iterrows()}
            sel_area = st.selectbox("Chọn Khu vực", options=list(area_opts.keys()), key="edit_crit_area")
            sel_area_id = area_opts[sel_area]
            
            df_crit_edit = run_query(
                "SELECT id, location_name, category, requirement FROM criteria WHERE area_id=%s ORDER BY location_name",
                params=(sel_area_id,)
            )
            
            if not df_crit_edit.empty:
                for idx, crit in df_crit_edit.iterrows():
                    with st.expander(f"📍 {crit['location_name']} - {crit['category']}"):
                        with st.form(f"edit_crit_{crit['id']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_loc = st.text_input("Vị trí", value=crit['location_name'], key=f"loc_{crit['id']}")
                                new_cat = st.text_input("Hạng mục", value=crit['category'], key=f"cat_{crit['id']}")
                            
                            with col2:
                                new_req = st.text_area("Yêu cầu", value=crit['requirement'] or "", key=f"req_{crit['id']}")
                            
                            col_s, col_d = st.columns(2)
                            
                            with col_s:
                                save_c = st.form_submit_button("💾 Lưu", type="primary", use_container_width=True)
                            with col_d:
                                del_c = st.form_submit_button("🗑️ Xóa", use_container_width=True)
                            
                            if save_c:
                                try:
                                    conn = get_connection()
                                    cur = conn.cursor()
                                    cur.execute(
                                        "UPDATE criteria SET location_name=%s, category=%s, requirement=%s WHERE id=%s",
                                        (new_loc, new_cat, new_req, crit['id'])
                                    )
                                    conn.commit()
                                    cur.close()
                                    conn.close()
                                    st.success("✅ Đã cập nhật!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Lỗi: {e}")
                            
                            if del_c:
                                try:
                                    conn = get_connection()
                                    cur = conn.cursor()
                                    cur.execute("DELETE FROM criteria WHERE id=%s", (crit['id'],))
                                    conn.commit()
                                    cur.close()
                                    conn.close()
                                    st.success("✅ Đã xóa!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Lỗi: {e}")
            else:
                st.info("Chưa có tiêu chí.")
        else:
            st.warning("Chưa có khu vực!")
