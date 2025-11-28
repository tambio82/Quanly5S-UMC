import streamlit as st
import pandas as pd
from fpdf import FPDF
from db_utils import run_query
import os

st.set_page_config(page_title="Xuất Báo Cáo", page_icon="📑", layout="wide")

class PDF(FPDF):
    def header(self):
        self.set_font('Roboto', 'B', 14)
        self.cell(0, 10, 'HỆ THỐNG QUẢN LÝ 5S - UMC', 0, 1, 'C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Roboto', 'I', 8)
        self.cell(0, 10, f'Trang {self.page_no()}', 0, 0, 'C')

def create_pdf(dept, date_str, data):
    pdf = PDF()
    # Check Font
    font_path = 'fonts/Roboto-Regular.ttf'
    if not os.path.exists(font_path):
        st.error("Thiếu file fonts/Roboto-Regular.ttf")
        return None
        
    pdf.add_font('Roboto', '', font_path, uni=True)
    pdf.add_font('Roboto', 'B', font_path, uni=True)
    pdf.add_font('Roboto', 'I', font_path, uni=True)
    
    pdf.add_page()
    pdf.set_font("Roboto", size=11)
    pdf.cell(0, 10, f"Báo cáo: {dept} - Ngày: {date_str}", 0, 1)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(80, 10, "Hạng mục", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Kết quả", 1, 0, 'C', 1)
    pdf.cell(80, 10, "Phụ trách", 1, 1, 'C', 1)
    
    for i, row in data.iterrows():
        res = "Đạt" if row['is_pass'] else "K.Đạt"
        cat = (row['category'][:35] + '..') if len(row['category'])>35 else row['category']
        stf = str(row['staff_name'])
        
        if not row['is_pass']: pdf.set_text_color(255, 0, 0)
        pdf.cell(80, 10, cat, 1)
        pdf.cell(30, 10, res, 1, 0, 'C')
        pdf.set_text_color(0)
        pdf.cell(80, 10, stf, 1, 1)
        
    return pdf.output(dest='S').encode('latin-1')

st.header("📑 XUẤT BÁO CÁO PDF")
depts = run_query("SELECT id, unit_name FROM departments")
d_map = {r['unit_name']: r['id'] for i, r in depts.iterrows()} if not depts.empty else {}
sel_d = st.selectbox("Khoa", list(d_map.keys()))

if sel_d:
    dates = run_query(f"SELECT DISTINCT eval_date FROM evaluations WHERE department_id={d_map[sel_d]} ORDER BY eval_date DESC")
    sel_date = st.selectbox("Ngày", dates['eval_date']) if not dates.empty else None
    
    if sel_date and st.button("Tạo PDF"):
        df = run_query(f"""
            SELECT c.category, ed.is_pass, s.name as staff_name
            FROM evaluation_details ed 
            JOIN evaluations e ON ed.evaluation_id=e.id
            JOIN criteria c ON ed.criteria_id=c.id
            LEFT JOIN staff s ON ed.staff_id=s.id
            WHERE e.department_id={d_map[sel_d]} AND e.eval_date='{sel_date}'
        """)
        pdf_data = create_pdf(sel_d, sel_date, df)
        if pdf_data:
            st.download_button("⬇️ Tải PDF", pdf_data, f"BaoCao_{sel_d}.pdf", "application/pdf")
