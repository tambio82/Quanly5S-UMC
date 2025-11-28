import streamlit as st
import pandas as pd
from db_utils import run_query, run_insert

st.set_page_config(page_title="Cấu hình 5S", page_icon="⚙️", layout="wide")
st.title("⚙️ CẤU HÌNH KHU VỰC VÀ TIÊU CHÍ")

tab1, tab2 = st.tabs(["3.1. Quy định Khu vực", "3.2. Thống kê Vị trí & Hạng mục"])

# TAB 1
with tab1:
    st.subheader("Bảng 3.1: Quy định chung khu vực kiểm tra")
    with st.expander("➕ Thêm Khu vực mới"):
        with st.form("add_area"):
            c1, c2 = st.columns(2)
            a_name = c1.text_input("Tên khu vực (VD: Hành chính)")
            a_code = c2.text_input("Ký hiệu (VD: HC)")
            a_def = st.text_area("Định nghĩa")
            if st.form_submit_button("Lưu Khu Vực"):
                if run_insert("INSERT INTO areas (area_name, area_code, definition) VALUES (%s, %s, %s)", (a_name, a_code, a_def)):
                    st.success("Đã thêm khu vực!")
                    st.rerun()

    df_areas = run_query("""
        SELECT a.id, a.area_name, a.area_code, STRING_AGG(DISTINCT c.location_name, ', ') as locations
        FROM areas a LEFT JOIN criteria c ON a.id = c.area_id
        GROUP BY a.id, a.area_name, a.area_code ORDER BY a.id
    """)
    st.dataframe(df_areas, use_container_width=True)

# TAB 2
with tab2:
    st.subheader("Bảng 3.2: Thống kê vị trí và hạng mục 5S")
    areas = run_query("SELECT id, area_name FROM areas")
    if not areas.empty:
        area_map = {row['area_name']: row['id'] for i, row in areas.iterrows()}
        sel_area = st.selectbox("Chọn khu vực:", list(area_map.keys()))
        sel_id = area_map[sel_area]

        with st.form("add_crit"):
            c1, c2 = st.columns(2)
            loc = c1.text_input("Tên vị trí 5S")
            cat = c2.text_input("Tên hạng mục đánh giá")
            req = st.text_area("Yêu cầu")
            if st.form_submit_button("Lưu Hạng Mục"):
                if run_insert("INSERT INTO criteria (area_id, location_name, category, requirement) VALUES (%s, %s, %s, %s)", 
                              (sel_id, loc, cat, req)):
                    st.success("Đã lưu!")
                    st.rerun()
        
        df_crit = run_query(f"SELECT location_name, category, requirement FROM criteria WHERE area_id = {sel_id}")
        st.dataframe(df_crit, use_container_width=True)
    else:
        st.warning("Chưa có khu vực nào.")
