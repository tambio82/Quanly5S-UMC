import streamlit as st
import pandas as pd
import plotly.express as px
from db_utils import run_query
from datetime import datetime

st.set_page_config(page_title="Trang Chủ", page_icon="🏠", layout="wide")
st.header("DASHBOARD TỔNG QUAN 5S")

today = datetime.now().strftime("%d/%m/%Y")
st.info(f"📅 Hôm nay: {today}")

# Query dữ liệu tổng quát
df_evals = run_query("""
    SELECT e.eval_date, d.unit_name, ed.is_pass 
    FROM evaluations e
    JOIN evaluation_details ed ON e.id = ed.evaluation_id
    JOIN departments d ON e.department_id = d.id
""")

if not df_evals.empty:
    # 1. Metrics
    total_depts = df_evals['unit_name'].nunique()
    total_items = len(df_evals)
    pass_items = len(df_evals[df_evals['is_pass'] == True])
    pass_rate = (pass_items / total_items * 100) if total_items > 0 else 0
    fail_rate = 100 - pass_rate

    col1, col2, col3 = st.columns(3)
    col1.metric("Khoa/Phòng tham gia", total_depts)
    col2.metric("Tỷ lệ Tuân thủ (Đạt)", f"{pass_rate:.1f}%")
    col3.metric("Tỷ lệ Không Đạt", f"{fail_rate:.1f}%")

    # 2. Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Xu hướng theo ngày")
        df_daily = df_evals.groupby('eval_date').apply(lambda x: (x['is_pass'].sum()/len(x)*100)).reset_index(name='rate')
        fig_line = px.line(df_daily, x='eval_date', y='rate', markers=True, title="Tỷ lệ Đạt trung bình (%)")
        st.plotly_chart(fig_line, use_container_width=True)

    with col_chart2:
        st.subheader("Tỷ lệ Đạt/Không Đạt theo ngày")
        df_stack = df_evals.groupby(['eval_date', 'is_pass']).size().reset_index(name='count')
        df_stack['Status'] = df_stack['is_pass'].map({True: 'Đạt', False: 'Không Đạt'})
        fig_bar = px.bar(df_stack, x='eval_date', y='count', color='Status', barmode='group',
                         color_discrete_map={'Đạt':'#00CC96', 'Không Đạt':'#EF553B'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Recent Table
    st.subheader("Hoạt động gần đây")
    recent_df = df_evals[['eval_date', 'unit_name', 'is_pass']].tail(10)
    st.dataframe(recent_df, use_container_width=True)
else:
    st.warning("Hệ thống chưa có dữ liệu đánh giá nào.")
