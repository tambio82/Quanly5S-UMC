import streamlit as st
import pandas as pd
import plotly.express as px
from db_utils import run_query

st.set_page_config(page_title="Thống Kê", page_icon="📊", layout="wide")
st.title("📊 DASHBOARD PHÂN TÍCH SÂU")

df = run_query("""
    SELECT e.eval_date, d.unit_name, a.area_name, c.category, ed.is_pass
    FROM evaluation_details ed
    JOIN evaluations e ON ed.evaluation_id = e.id
    JOIN departments d ON e.department_id = d.id
    JOIN criteria c ON ed.criteria_id = c.id
    JOIN areas a ON c.area_id = a.id
""")

if not df.empty:
    df['eval_date'] = pd.to_datetime(df['eval_date']).dt.date
    
    # Filter
    col1, col2 = st.columns(2)
    s_date = col1.date_input("Từ ngày", df['eval_date'].min())
    e_date = col2.date_input("Đến ngày", df['eval_date'].max())
    
    mask = (df['eval_date'] >= s_date) & (df['eval_date'] <= e_date)
    df_f = df[mask]
    
    # KPI
    pass_c = df_f['is_pass'].sum()
    total = len(df_f)
    rate = (pass_c/total*100) if total else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng lượt", total)
    c2.metric("Đạt", pass_c, f"{rate:.1f}%")
    c3.metric("Không Đạt", total - pass_c)
    
    # Heatmap
    st.subheader("🔥 Điểm nóng vi phạm (Khu vực vs Hạng mục)")
    df_fail = df_f[df_f['is_pass'] == False]
    if not df_fail.empty:
        heat_data = df_fail.groupby(['area_name', 'category']).size().reset_index(name='Lỗi')
        fig = px.density_heatmap(heat_data, x='area_name', y='category', z='Lỗi', color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Không có lỗi vi phạm trong giai đoạn này!")
else:
    st.info("Chưa có dữ liệu.")
