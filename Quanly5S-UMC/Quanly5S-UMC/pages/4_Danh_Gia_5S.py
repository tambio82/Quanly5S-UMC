import streamlit as st
import pandas as pd
from db_utils import run_query
from datetime import date

st.set_page_config(page_title="Đánh Giá 5S", page_icon="📝", layout="wide")
st.header("CHECKLIST ĐÁNH GIÁ 5S")

depts = run_query("SELECT id, unit_name FROM departments")
dept_opts = {row['unit_name']: row['id'] for i, row in depts.iterrows()} if not depts.empty else {}

sel_dept = st.selectbox("Chọn Khoa/Phòng", list(dept_opts.keys()))
eval_date = st.date_input("Ngày đánh giá", date.today())

if sel_dept:
    d_id = dept_opts[sel_dept]
    staffs = run_query(f"SELECT id, name FROM staff WHERE department_id = {d_id}")
    staff_opts = {row['name']: row['id'] for i, row in staffs.iterrows()} if not staffs.empty else {}

    checklist = run_query("""
        SELECT a.area_code, a.area_name, c.location_name, c.category, c.id as crit_id
        FROM criteria c JOIN areas a ON c.area_id = a.id ORDER BY a.id, c.id
    """)

    if not checklist.empty:
        checklist["Số lượng"] = 0
        checklist["Đạt"] = False
        checklist["Nhân sự"] = ""
        
        edited = st.data_editor(
            checklist,
            column_config={
                "crit_id": None,
                "Số lượng": st.column_config.NumberColumn(min_value=0),
                "Đạt": st.column_config.CheckboxColumn(default=False),
                "Nhân sự": st.column_config.SelectboxColumn(options=list(staff_opts.keys()))
            },
            use_container_width=True,
            hide_index=True
        )

        if st.button("Lưu Kết Quả"):
            try:
                conn = st.connection("postgres", type="sql").engine.raw_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO evaluations (department_id, eval_date) VALUES (%s, %s) RETURNING id", (d_id, eval_date))
                e_id = cur.fetchone()[0]
                
                count = 0
                for i, row in edited.iterrows():
                    s_id = staff_opts.get(row['Nhân sự'])
                    if s_id:
                        cur.execute("""
                            INSERT INTO evaluation_details (evaluation_id, criteria_id, quantity, is_pass, staff_id)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (e_id, row['crit_id'], row['Số lượng'], row['Đạt'], s_id))
                        count += 1
                conn.commit()
                st.success(f"Đã lưu {count} hạng mục!")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Lỗi: {e}")
