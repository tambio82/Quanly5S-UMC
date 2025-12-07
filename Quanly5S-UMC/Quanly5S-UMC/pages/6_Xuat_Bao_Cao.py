import streamlit as st
import pandas as pd
from datetime import datetime
from db_utils import run_query, get_connection
from fpdf import FPDF
import os

st.set_page_config(page_title="Xuất Báo Cáo", page_icon="📄", layout="wide")
st.title("📄 XUẤT BÁO CÁO PDF")

# PDF class with safe font handling
class PDF5S(FPDF):
    def __init__(self):
        super().__init__()
        self.use_dejavu = False
        
        # Try to load DejaVu
        dejavu_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/dejavu/DejaVuSans.ttf',
        ]
        
        for path in dejavu_paths:
            if os.path.exists(path):
                try:
                    base_dir = os.path.dirname(path)
                    self.add_font('DejaVu', '', path, uni=True)
                    
                    bold_path = os.path.join(base_dir, 'DejaVuSans-Bold.ttf')
                    if os.path.exists(bold_path):
                        self.add_font('DejaVu', 'B', bold_path, uni=True)
                    
                    self.use_dejavu = True
                    break
                except:
                    pass
    
    def header(self):
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        if self.use_dejavu:
            self.set_font('DejaVu', '', 8)
        else:
            self.set_font('Arial', '', 8)
        self.cell(0, 10, f'Trang {self.page_no()}', 0, 0, 'C')

# Tabs
tab1, tab2 = st.tabs(["📝 Tạo Báo Cáo", "📋 Quản Lý Báo Cáo"])

with tab1:
    st.subheader("Tạo Báo Cáo Đánh Giá 5S")
    
    df_depts = run_query("SELECT id, unit_code, unit_name FROM departments ORDER BY unit_code")
    
    if df_depts.empty:
        st.warning("⚠️ Chưa có Khoa/Phòng")
        st.stop()
    
    dept_options = {f"{row['unit_code']} - {row['unit_name']}": row['id'] for _, row in df_depts.iterrows()}
    selected_dept = st.selectbox("Chọn Khoa/Phòng", list(dept_options.keys()), key="dept")
    selected_dept_id = dept_options[selected_dept]
    
    df_evals = run_query("""
        SELECT e.id, e.eval_date, 
               COUNT(ed.id) as total,
               SUM(CASE WHEN ed.is_pass THEN 1 ELSE 0 END) as passed
        FROM evaluations e
        JOIN evaluation_details ed ON e.id = ed.evaluation_id
        WHERE e.department_id = %s
        GROUP BY e.id, e.eval_date
        ORDER BY e.eval_date DESC
    """, params=(selected_dept_id,))
    
    if df_evals.empty:
        st.info("📭 Chưa có đợt đánh giá")
    else:
        eval_options = {f"{row['eval_date']} ({row['passed']}/{row['total']} đạt)": row['id'] for _, row in df_evals.iterrows()}
        selected_eval = st.selectbox("Chọn đợt đánh giá", list(eval_options.keys()), key="eval")
        selected_eval_id = eval_options[selected_eval]
        
        st.divider()
        
        df_preview = run_query("""
            SELECT 
                a.area_name, c.location_name, c.category,
                CASE WHEN ed.is_pass THEN 'Đạt' ELSE 'Không đạt' END as result,
                s.name as staff
            FROM evaluation_details ed
            JOIN criteria c ON ed.criteria_id = c.id
            JOIN areas a ON c.area_id = a.id
            JOIN staff s ON ed.staff_id = s.id
            WHERE ed.evaluation_id = %s
            ORDER BY a.area_name, c.location_name
        """, params=(selected_eval_id,))
        
        if not df_preview.empty:
            st.write("### Preview")
            st.dataframe(df_preview.rename(columns={
                'area_name': 'Khu vực', 'location_name': 'Vị trí',
                'category': 'Hạng mục', 'result': 'Kết quả', 'staff': 'Nhân sự'
            }), use_container_width=True, hide_index=True, height=250)
            
            st.divider()
            st.write("### Thông Tin Báo Cáo")
            
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Tiêu đề", f"BÁO CÁO 5S - {selected_dept.split(' - ')[1].upper()}")
                evaluator = st.text_input("Người kiểm tra")
            with col2:
                report_date = st.date_input("Ngày", datetime.now().date())
                supervisor = st.text_input("Điều phối")
            
            manager = st.text_input("P.Quản lý chất lượng")
            evaluation = st.text_area("Đánh giá", height=120)
            
            st.divider()
            
            if st.button("📄 Tạo PDF", type="primary", use_container_width=True):
                try:
                    pdf = PDF5S()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    # Set font
                    if pdf.use_dejavu:
                        pdf.set_font('DejaVu', 'B', 16)
                    else:
                        pdf.set_font('Arial', 'B', 16)
                    
                    # Title
                    pdf.cell(0, 10, title, 0, 1, 'C')
                    pdf.ln(5)
                    
                    # Info
                    if pdf.use_dejavu:
                        pdf.set_font('DejaVu', '', 10)
                    else:
                        pdf.set_font('Arial', '', 10)
                    
                    pdf.cell(0, 6, f"Khoa/Phong: {selected_dept}", 0, 1)
                    pdf.cell(0, 6, f"Thoi gian: {report_date}", 0, 1)
                    if evaluator:
                        pdf.cell(0, 6, f"Nguoi kiem tra: {evaluator}", 0, 1)
                    pdf.ln(10)
                    
                    # Table
                    if pdf.use_dejavu:
                        pdf.set_font('DejaVu', 'B', 9)
                    else:
                        pdf.set_font('Arial', 'B', 9)
                    
                    pdf.set_fill_color(66, 153, 225)
                    pdf.set_text_color(255, 255, 255)
                    
                    widths = [35, 45, 55, 25, 30]
                    headers = ['Khu vuc', 'Vi tri', 'Hang muc', 'Ket qua', 'Nhan su']
                    
                    for i, h in enumerate(headers):
                        pdf.cell(widths[i], 8, h, 1, 0, 'C', True)
                    pdf.ln()
                    
                    if pdf.use_dejavu:
                        pdf.set_font('DejaVu', '', 8)
                    else:
                        pdf.set_font('Arial', '', 8)
                    
                    pdf.set_text_color(0, 0, 0)
                    
                    for idx, row in df_preview.iterrows():
                        if idx % 2 == 0:
                            pdf.set_fill_color(247, 250, 252)
                        else:
                            pdf.set_fill_color(255, 255, 255)
                        
                        data = [
                            str(row['area_name'])[:18],
                            str(row['location_name'])[:22],
                            str(row['category'])[:28],
                            str(row['result'])[:12],
                            str(row['staff'])[:15]
                        ]
                        
                        for i, val in enumerate(data):
                            pdf.cell(widths[i], 6, val, 1, 0, 'L', True)
                        pdf.ln()
                    
                    pdf.ln(10)
                    
                    # Evaluation
                    if evaluation:
                        if pdf.use_dejavu:
                            pdf.set_font('DejaVu', 'B', 11)
                        else:
                            pdf.set_font('Arial', 'B', 11)
                        
                        pdf.cell(0, 8, 'DANH GIA & NHAN XET', 0, 1)
                        
                        if pdf.use_dejavu:
                            pdf.set_font('DejaVu', '', 10)
                        else:
                            pdf.set_font('Arial', '', 10)
                        
                        pdf.multi_cell(0, 5, evaluation)
                        pdf.ln(10)
                    
                    # Signatures
                    pdf.ln(15)
                    if pdf.use_dejavu:
                        pdf.set_font('DejaVu', 'B', 10)
                    else:
                        pdf.set_font('Arial', 'B', 10)
                    
                    pdf.cell(60, 6, 'Nguoi kiem tra', 0, 0, 'C')
                    pdf.cell(65, 6, 'Dieu phoi', 0, 0, 'C')
                    pdf.cell(60, 6, 'P.Quan ly CL', 0, 1, 'C')
                    pdf.ln(20)
                    
                    if pdf.use_dejavu:
                        pdf.set_font('DejaVu', '', 9)
                    else:
                        pdf.set_font('Arial', '', 9)
                    
                    pdf.cell(60, 6, evaluator or '', 0, 0, 'C')
                    pdf.cell(65, 6, supervisor or '', 0, 0, 'C')
                    pdf.cell(60, 6, manager or '', 0, 1, 'C')
                    
                    # Save
                    pdf_bytes = pdf.output(dest='S').encode('latin-1')
                    
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO reports 
                        (evaluation_id, report_title, report_date, evaluator_name, supervisor_name, manager_name, evaluation_text, pdf_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (selected_eval_id, title, report_date, evaluator or None, supervisor or None, manager or None, evaluation or None, pdf_bytes))
                    
                    report_id = cur.fetchone()[0]
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    st.success(f"✅ Đã tạo báo cáo #{report_id}")
                    
                    if pdf.use_dejavu:
                        st.info("✅ Sử dụng font DejaVu (tiếng Việt đầy đủ)")
                    else:
                        st.warning("⚠️ Dùng Arial - tiếng Việt có thể lỗi. Thêm packages.txt với 'fonts-dejavu'")
                    
                    st.balloons()
                    
                    st.download_button(
                        "📥 Tải PDF",
                        data=pdf_bytes,
                        file_name=f"BC_5S_{selected_dept.split(' - ')[0]}_{report_date}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")
                    import traceback
                    st.code(traceback.format_exc())

with tab2:
    st.subheader("Danh Sách Báo Cáo")
    
    df_reports = run_query("""
        SELECT r.id, r.report_title, r.report_date, d.unit_name, r.evaluator_name, r.created_at
        FROM reports r
        JOIN evaluations e ON r.evaluation_id = e.id
        JOIN departments d ON e.department_id = d.id
        ORDER BY r.created_at DESC
    """)
    
    if not df_reports.empty:
        st.write(f"**Tổng: {len(df_reports)} báo cáo**")
        
        for idx, rpt in df_reports.iterrows():
            with st.expander(f"📄 {rpt['report_title']} - {rpt['report_date']}"):
                col_i, col_a = st.columns([3, 1])
                
                with col_i:
                    st.write(f"**Khoa/Phòng:** {rpt['unit_name']}")
                    st.write(f"**Ngày:** {rpt['report_date']}")
                    if rpt['evaluator_name']:
                        st.write(f"**Kiểm tra:** {rpt['evaluator_name']}")
                
                with col_a:
                    df_pdf = run_query("SELECT pdf_data FROM reports WHERE id = %s", params=(rpt['id'],))
                    if not df_pdf.empty and df_pdf.iloc[0]['pdf_data']:
                        st.download_button(
                            "📥 Tải",
                            data=bytes(df_pdf.iloc[0]['pdf_data']),
                            file_name=f"Report_{rpt['id']}.pdf",
                            mime="application/pdf",
                            key=f"dl{rpt['id']}",
                            use_container_width=True
                        )
                    
                    if st.button("🗑️", key=f"del{rpt['id']}", use_container_width=True):
                        st.session_state[f"cf{rpt['id']}"] = True
                
                if st.session_state.get(f"cf{rpt['id']}", False):
                    st.warning("⚠️ Xóa?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅", key=f"y{rpt['id']}", type="primary"):
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("DELETE FROM reports WHERE id=%s", (rpt['id'],))
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("✅ Đã xóa!")
                            st.rerun()
                    with c2:
                        if st.button("❌", key=f"n{rpt['id']}"):
                            st.session_state[f"cf{rpt['id']}"] = False
                            st.rerun()
    else:
        st.info("📭 Chưa có báo cáo")
