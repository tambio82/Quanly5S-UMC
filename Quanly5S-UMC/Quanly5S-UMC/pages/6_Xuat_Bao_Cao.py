import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from db_utils import run_query

st.set_page_config(page_title="Báo cáo Điều chỉnh", page_icon="📊", layout="wide")

st.title("📊 BÁO CÁO NỘI DUNG ĐIỀU CHỈNH")

st.info("💡 **Báo cáo này** tổng hợp các ghi chú điều chỉnh từ quá trình đánh giá 5S")

# Bộ lọc
st.write("### 🔍 Bộ lọc")

col1, col2, col3 = st.columns(3)

with col1:
    # Chọn Khoa/Phòng
    df_depts = run_query("SELECT id, unit_code, unit_name FROM departments ORDER BY unit_code")
    
    if df_depts.empty:
        st.warning("⚠️ Chưa có dữ liệu")
        st.stop()
    
    dept_filter_options = ["Tất cả"] + [f"{row['unit_code']} - {row['unit_name']}" for _, row in df_depts.iterrows()]
    selected_dept_filter = st.selectbox("Khoa/Phòng", options=dept_filter_options)

with col2:
    # Chọn khoảng thời gian
    date_range = st.selectbox(
        "Khoảng thời gian",
        options=["7 ngày qua", "30 ngày qua", "90 ngày qua", "Tất cả"],
        index=1
    )

with col3:
    # Chọn loại
    filter_type = st.selectbox(
        "Hiển thị",
        options=["Tất cả", "Chỉ có ghi chú", "Chỉ không đạt"]
    )

# Tính toán date filter
if date_range == "7 ngày qua":
    date_filter = (datetime.now() - timedelta(days=7)).date()
elif date_range == "30 ngày qua":
    date_filter = (datetime.now() - timedelta(days=30)).date()
elif date_range == "90 ngày qua":
    date_filter = (datetime.now() - timedelta(days=90)).date()
else:
    date_filter = None

st.divider()

# Query dữ liệu
query = """
    SELECT 
        e.eval_date as "Ngày đánh giá",
        d.unit_name as "Khoa/Phòng",
        a.area_name as "Khu vực",
        c.location_name as "Vị trí",
        c.category as "Hạng mục",
        s.name as "Nhân sự",
        ed.is_pass as "Đạt",
        ed.adjustment_note as "Nội dung điều chỉnh",
        ed.evidence_link as "Link minh chứng",
        e.id as eval_id,
        ed.id as detail_id
    FROM evaluation_details ed
    JOIN evaluations e ON ed.evaluation_id = e.id
    JOIN departments d ON e.department_id = d.id
    JOIN criteria c ON ed.criteria_id = c.id
    JOIN areas a ON c.area_id = a.id
    JOIN staff s ON ed.staff_id = s.id
    WHERE 1=1
"""

params = []

# Filter theo department
if selected_dept_filter != "Tất cả":
    dept_code = selected_dept_filter.split(" - ")[0]
    query += " AND d.unit_code = %s"
    params.append(dept_code)

# Filter theo date
if date_filter:
    query += " AND e.eval_date >= %s"
    params.append(date_filter)

# Filter theo type
if filter_type == "Chỉ có ghi chú":
    query += " AND ed.adjustment_note IS NOT NULL AND ed.adjustment_note != ''"
elif filter_type == "Chỉ không đạt":
    query += " AND ed.is_pass = FALSE"

query += " ORDER BY e.eval_date DESC, d.unit_name, a.area_name, c.location_name"

df_results = run_query(query, params=tuple(params) if params else None)

# Hiển thị kết quả
if not df_results.empty:
    st.write(f"### 📋 Kết quả: {len(df_results)} bản ghi")
    
    # Thống kê tổng quan
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        total_records = len(df_results)
        st.metric("Tổng số bản ghi", total_records)
    
    with col_stat2:
        total_not_pass = len(df_results[df_results['Đạt'] == False])
        st.metric("Không đạt", total_not_pass, delta=f"{total_not_pass/total_records*100:.1f}%")
    
    with col_stat3:
        total_with_notes = len(df_results[df_results['Nội dung điều chỉnh'].notna() & (df_results['Nội dung điều chỉnh'] != '')])
        st.metric("Có ghi chú", total_with_notes)
    
    with col_stat4:
        total_with_links = len(df_results[df_results['Link minh chứng'].notna() & (df_results['Link minh chứng'] != '')])
        st.metric("Có link minh chứng", total_with_links)
    
    st.divider()
    
    # Hiển thị bảng
    display_df = df_results.drop(columns=['eval_id', 'detail_id']).copy()
    
    # Format cột Đạt
    display_df['Đạt'] = display_df['Đạt'].apply(lambda x: '✅ Đạt' if x else '❌ Không đạt')
    
    st.dataframe(
        display_df,
        column_config={
            "Ngày đánh giá": st.column_config.DateColumn("Ngày", format="DD/MM/YYYY"),
            "Khoa/Phòng": st.column_config.TextColumn("Khoa/Phòng", width="medium"),
            "Khu vực": st.column_config.TextColumn("Khu vực", width="small"),
            "Vị trí": st.column_config.TextColumn("Vị trí", width="medium"),
            "Hạng mục": st.column_config.TextColumn("Hạng mục", width="large"),
            "Nhân sự": st.column_config.TextColumn("Nhân sự", width="medium"),
            "Đạt": st.column_config.TextColumn("Kết quả", width="small"),
            "Nội dung điều chỉnh": st.column_config.TextColumn("Nội dung điều chỉnh", width="large"),
            "Link minh chứng": st.column_config.LinkColumn("Link", width="medium")
        },
        use_container_width=True,
        hide_index=True,
        height=500
    )
    
    # Nút xuất Excel
    st.divider()
    
    col_export1, col_export2 = st.columns([3, 1])
    
    with col_export2:
        # Tạo CSV để download
        csv = display_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Tải xuống CSV",
            data=csv,
            file_name=f"bao_cao_dieu_chinh_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Phân tích theo Khoa/Phòng
    st.divider()
    st.write("### 📊 Thống kê theo Khoa/Phòng")
    
    df_by_dept = df_results.groupby('Khoa/Phòng').agg({
        'Ngày đánh giá': 'count',
        'Đạt': lambda x: (x == False).sum(),
        'Nội dung điều chỉnh': lambda x: (x.notna() & (x != '')).sum()
    }).reset_index()
    
    df_by_dept.columns = ['Khoa/Phòng', 'Tổng số', 'Không đạt', 'Có ghi chú']
    df_by_dept['Tỷ lệ không đạt (%)'] = (df_by_dept['Không đạt'] / df_by_dept['Tổng số'] * 100).round(1)
    
    st.dataframe(
        df_by_dept,
        column_config={
            "Tỷ lệ không đạt (%)": st.column_config.ProgressColumn(
                "Tỷ lệ không đạt (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100
            )
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Phân tích theo Hạng mục
    st.divider()
    st.write("### 📊 Thống kê theo Hạng mục")
    
    df_by_category = df_results.groupby('Hạng mục').agg({
        'Ngày đánh giá': 'count',
        'Đạt': lambda x: (x == False).sum()
    }).reset_index()
    
    df_by_category.columns = ['Hạng mục', 'Tổng số', 'Không đạt']
    df_by_category['Tỷ lệ không đạt (%)'] = (df_by_category['Không đạt'] / df_by_category['Tổng số'] * 100).round(1)
    df_by_category = df_by_category.sort_values('Không đạt', ascending=False)
    
    st.dataframe(
        df_by_category,
        column_config={
            "Tỷ lệ không đạt (%)": st.column_config.ProgressColumn(
                "Tỷ lệ không đạt (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100
            )
        },
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("📭 Không tìm thấy dữ liệu với bộ lọc này")
