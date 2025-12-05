import streamlit as st
from db_utils import run_query, get_connection

st.set_page_config(page_title="Cấu hình Khu vực", page_icon="⚙️", layout="wide")

st.title("⚙️ CẤU HÌNH KHU VỰC VÀ TIÊU CHÍ")

# Tabs
tab1, tab2, tab3 = st.tabs(["3.1. Quy định Khu vực", "3.2. Thông kê Vị trí & Hạng mục", "3.3. Quản lý & Chỉnh sửa"])

# ==================== TAB 1: QUY ĐỊNH KHU VỰC ====================
with tab1:
    st.subheader("Bảng 3.1: Quy định chung khu vực kiểm tra")
    
    # Form thêm khu vực mới
    with st.expander("➕ Thêm Khu vực mới", expanded=False):
        with st.form("add_area", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                area_name = st.text_input("Tên khu vực (VD: Hành chính)*", placeholder="Khu vực Hành chính")
                area_code = st.text_input("Ký hiệu (VD: HC)*", placeholder="HC")
            
            with col2:
                definition = st.text_area("Định nghĩa", placeholder="Văn phòng, phòng họp, khu vực làm việc...", height=100)
            
            submit = st.form_submit_button("💾 Lưu Khu Vực", type="primary")
            
            if submit:
                if not area_name or not area_code:
                    st.error("⚠️ Vui lòng nhập đầy đủ Tên và Ký hiệu!")
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
    
    # Hiển thị danh sách khu vực
    df_areas = run_query("""
        SELECT a.id, a.area_name, a.area_code, STRING_AGG(DISTINCT c.location_name, ', ') as locations
        FROM areas a LEFT JOIN criteria c ON a.id = c.area_id
        GROUP BY a.id, a.area_name, a.area_code ORDER BY a.id
    """)
    
    if not df_areas.empty:
        st.dataframe(df_areas, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có khu vực nào. Hãy thêm mới!")

# ==================== TAB 2: THÔNG KÊ VỊ TRÍ & HẠNG MỤC ====================
with tab2:
    st.subheader("Bảng 3.2: Các vị trí kiểm tra và hạng mục kiểm tra")
    
    # Lấy danh sách khu vực cho selectbox
    df_areas_list = run_query("SELECT id, area_name, area_code FROM areas ORDER BY area_code")
    
    if not df_areas_list.empty:
        area_options = {f"{row['area_code']} - {row['area_name']}": row['id'] for _, row in df_areas_list.iterrows()}
        selected_area_display = st.selectbox("Chọn khu vực", options=list(area_options.keys()), key="tab2_area_select")
        selected_area_id = area_options[selected_area_display]
        
        # Form thêm tiêu chí mới
        with st.expander("➕ Thêm Tiêu chí mới", expanded=False):
            with st.form("add_criteria", clear_on_submit=True):
                st.write(f"**Thêm tiêu chí cho: {selected_area_display}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    location_name = st.text_input("Vị trí cần kiểm tra*", placeholder="VD: Bàn làm việc, Tủ hồ sơ...")
                    category = st.text_input("Hạng mục đánh giá*", placeholder="VD: Sắp xếp, Vệ sinh...")
                
                with col2:
                    requirement = st.text_area("Yêu cầu chi tiết", placeholder="Mô tả chi tiết yêu cầu...", height=100)
                
                submit_criteria = st.form_submit_button("💾 Lưu Tiêu chí", type="primary")
                
                if submit_criteria:
                    if not location_name or not category:
                        st.error("⚠️ Vui lòng nhập đầy đủ Vị trí và Hạng mục!")
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
            SELECT id, location_name, category, requirement, created_at
            FROM criteria 
            WHERE area_id = %s
            ORDER BY location_name, category
            """,
            params=(selected_area_id,)
        )
        
        if not df_criteria.empty:
            st.write(f"**Số lượng tiêu chí: {len(df_criteria)}**")
            st.dataframe(df_criteria, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có tiêu chí nào cho khu vực này.")
    else:
        st.warning("⚠️ Vui lòng thêm Khu vực trước ở Tab 3.1")

# ==================== TAB 3: QUẢN LÝ & CHỈNH SỬA ====================
with tab3:
    st.subheader("✏️ Quản lý & Chỉnh sửa")
    
    manage_tab1, manage_tab2 = st.tabs(["🏢 Quản lý Khu vực", "📋 Quản lý Tiêu chí"])
    
    # ===== SUB-TAB 1: QUẢN LÝ KHU VỰC =====
    with manage_tab1:
        df_areas_manage = run_query("""
            SELECT a.id, a.area_name, a.area_code, a.definition,
                   COUNT(c.id) as so_tieu_chi
            FROM areas a
            LEFT JOIN criteria c ON a.id = c.area_id
            GROUP BY a.id, a.area_name, a.area_code, a.definition
            ORDER BY a.area_code
        """)
        
        if not df_areas_manage.empty:
            for idx, area in df_areas_manage.iterrows():
                with st.expander(f"**{area['area_code']}** - {area['area_name']} ({area['so_tieu_chi']} tiêu chí)"):
                    
                    # Hiển thị thông tin
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.write("**📌 Thông tin:**")
                        st.write(f"- Ký hiệu: `{area['area_code']}`")
                        st.write(f"- Tên: {area['area_name']}")
                        if area['definition']:
                            st.write(f"- Định nghĩa: {area['definition']}")
                        st.write(f"- Số tiêu chí: {area['so_tieu_chi']}")
                    
                    with col_actions:
                        st.write("**⚙️ Thao tác:**")
                        edit_area_btn = st.button("✏️ Sửa", key=f"edit_area_{area['id']}", use_container_width=True)
                        delete_area_btn = st.button("🗑️ Xóa", key=f"delete_area_{area['id']}", type="secondary", use_container_width=True)
                    
                    # Form sửa
                    if edit_area_btn:
                        st.session_state[f"editing_area_{area['id']}"] = True
                    
                    if st.session_state.get(f"editing_area_{area['id']}", False):
                        st.divider()
                        st.write("### ✏️ Chỉnh sửa Khu vực")
                        
                        with st.form(key=f"edit_area_form_{area['id']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_area_name = st.text_input("Tên khu vực", value=area['area_name'], key=f"new_area_name_{area['id']}")
                                new_area_code = st.text_input("Ký hiệu", value=area['area_code'], key=f"new_area_code_{area['id']}")
                            
                            with col2:
                                new_definition = st.text_area("Định nghĩa", value=area['definition'] or "", key=f"new_def_{area['id']}", height=100)
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                save_area = st.form_submit_button("💾 Lưu thay đổi", type="primary", use_container_width=True)
                            with col_cancel:
                                cancel_area = st.form_submit_button("❌ Hủy", use_container_width=True)
                            
                            if save_area:
                                try:
                                    conn = get_connection()
                                    cur = conn.cursor()
                                    cur.execute(
                                        "UPDATE areas SET area_name=%s, area_code=%s, definition=%s WHERE id=%s",
                                        (new_area_name, new_area_code, new_definition, area['id'])
                                    )
                                    conn.commit()
                                    cur.close()
                                    conn.close()
                                    
                                    st.success("✅ Đã cập nhật khu vực!")
                                    st.session_state[f"editing_area_{area['id']}"] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Lỗi: {e}")
                            
                            if cancel_area:
                                st.session_state[f"editing_area_{area['id']}"] = False
                                st.rerun()
                    
                    # Xóa khu vực
                    if delete_area_btn:
                        st.session_state[f"confirm_delete_area_{area['id']}"] = True
                    
                    if st.session_state.get(f"confirm_delete_area_{area['id']}", False):
                        st.warning(f"⚠️ Xóa khu vực **{area['area_name']}**? Tất cả {area['so_tieu_chi']} tiêu chí liên quan sẽ bị xóa!")
                        
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("✅ Xác nhận", key=f"yes_delete_area_{area['id']}", type="primary"):
                                try:
                                    conn = get_connection()
                                    cur = conn.cursor()
                                    cur.execute("DELETE FROM areas WHERE id=%s", (area['id'],))
                                    conn.commit()
                                    cur.close()
                                    conn.close()
                                    
                                    st.success(f"✅ Đã xóa khu vực '{area['area_name']}'")
                                    st.session_state[f"confirm_delete_area_{area['id']}"] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Lỗi: {e}")
                        
                        with col_no:
                            if st.button("❌ Hủy", key=f"no_delete_area_{area['id']}"):
                                st.session_state[f"confirm_delete_area_{area['id']}"] = False
                                st.rerun()
        else:
            st.info("Chưa có khu vực nào.")
    
    # ===== SUB-TAB 2: QUẢN LÝ TIÊU CHÍ =====
    with manage_tab2:
        # Chọn khu vực
        df_areas_criteria = run_query("SELECT id, area_name, area_code FROM areas ORDER BY area_code")
        
        if not df_areas_criteria.empty:
            area_options_manage = {f"{row['area_code']} - {row['area_name']}": row['id'] for _, row in df_areas_criteria.iterrows()}
            selected_area_manage = st.selectbox("Chọn khu vực để quản lý tiêu chí", options=list(area_options_manage.keys()), key="manage_criteria_select")
            selected_area_manage_id = area_options_manage[selected_area_manage]
            
            # Lấy danh sách tiêu chí
            df_criteria_manage = run_query(
                """
                SELECT id, location_name, category, requirement, created_at
                FROM criteria 
                WHERE area_id = %s
                ORDER BY location_name, category
                """,
                params=(selected_area_manage_id,)
            )
            
            if not df_criteria_manage.empty:
                st.write(f"**Tổng số: {len(df_criteria_manage)} tiêu chí**")
                
                for idx, crit in df_criteria_manage.iterrows():
                    with st.expander(f"📍 {crit['location_name']} - {crit['category']}"):
                        
                        col_info_crit, col_actions_crit = st.columns([3, 1])
                        
                        with col_info_crit:
                            st.write("**📌 Chi tiết:**")
                            st.write(f"- Vị trí: **{crit['location_name']}**")
                            st.write(f"- Hạng mục: **{crit['category']}**")
                            if crit['requirement']:
                                st.write(f"- Yêu cầu: {crit['requirement']}")
                        
                        with col_actions_crit:
                            st.write("**⚙️ Thao tác:**")
                            edit_crit_btn = st.button("✏️ Sửa", key=f"edit_crit_{crit['id']}", use_container_width=True)
                            delete_crit_btn = st.button("🗑️ Xóa", key=f"delete_crit_{crit['id']}", type="secondary", use_container_width=True)
                        
                        # Form sửa tiêu chí
                        if edit_crit_btn:
                            st.session_state[f"editing_crit_{crit['id']}"] = True
                        
                        if st.session_state.get(f"editing_crit_{crit['id']}", False):
                            st.divider()
                            
                            with st.form(key=f"edit_crit_form_{crit['id']}"):
                                st.write("### ✏️ Chỉnh sửa Tiêu chí")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    new_location = st.text_input("Vị trí", value=crit['location_name'], key=f"new_loc_{crit['id']}")
                                    new_category = st.text_input("Hạng mục", value=crit['category'], key=f"new_cat_{crit['id']}")
                                
                                with col2:
                                    new_requirement = st.text_area("Yêu cầu", value=crit['requirement'] or "", key=f"new_req_{crit['id']}", height=100)
                                
                                col_save_c, col_cancel_c = st.columns(2)
                                
                                with col_save_c:
                                    save_crit = st.form_submit_button("💾 Lưu", type="primary", use_container_width=True)
                                with col_cancel_c:
                                    cancel_crit = st.form_submit_button("❌ Hủy", use_container_width=True)
                                
                                if save_crit:
                                    try:
                                        conn = get_connection()
                                        cur = conn.cursor()
                                        cur.execute(
                                            "UPDATE criteria SET location_name=%s, category=%s, requirement=%s WHERE id=%s",
                                            (new_location, new_category, new_requirement, crit['id'])
                                        )
                                        conn.commit()
                                        cur.close()
                                        conn.close()
                                        
                                        st.success("✅ Đã cập nhật tiêu chí!")
                                        st.session_state[f"editing_crit_{crit['id']}"] = False
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Lỗi: {e}")
                                
                                if cancel_crit:
                                    st.session_state[f"editing_crit_{crit['id']}"] = False
                                    st.rerun()
                        
                        # Xóa tiêu chí
                        if delete_crit_btn:
                            st.session_state[f"confirm_delete_crit_{crit['id']}"] = True
                        
                        if st.session_state.get(f"confirm_delete_crit_{crit['id']}", False):
                            st.warning(f"⚠️ Xác nhận xóa tiêu chí **{crit['category']}**?")
                            
                            col_yes_c, col_no_c = st.columns(2)
                            with col_yes_c:
                                if st.button("✅ Xóa", key=f"yes_crit_{crit['id']}", type="primary"):
                                    try:
                                        conn = get_connection()
                                        cur = conn.cursor()
                                        cur.execute("DELETE FROM criteria WHERE id=%s", (crit['id'],))
                                        conn.commit()
                                        cur.close()
                                        conn.close()
                                        
                                        st.success("✅ Đã xóa tiêu chí!")
                                        st.session_state[f"confirm_delete_crit_{crit['id']}"] = False
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Lỗi: {e}")
                            
                            with col_no_c:
                                if st.button("❌ Hủy", key=f"no_crit_{crit['id']}"):
                                    st.session_state[f"confirm_delete_crit_{crit['id']}"] = False
                                    st.rerun()
            else:
                st.info("Chưa có tiêu chí nào cho khu vực này.")
        else:
            st.warning("⚠️ Vui lòng thêm Khu vực trước!")
