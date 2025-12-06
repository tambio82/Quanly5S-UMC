import streamlit as st
import pandas as pd
from datetime import datetime
from db_utils import run_query, get_connection
from fpdf import FPDF
import io

st.set_page_config(page_title="Xuất Báo Cáo", page_icon="📄", layout="wide")

st.title("📄 XUẤT BÁO CÁO PDF")

# Custom PDF class
class PDF5S(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, '', 0, 1, 'C')
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Trang {self.page_no()}', 0, 0, 'C')

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 Tạo Báo Cáo Mới", "📋 Quản Lý Báo Cáo", "🔍 Xem & In Báo Cáo"])

# ==================== TAB 1: TẠO BÁO CÁO MỚI ====================
with tab1:
    st.subheader("Tạo Báo Cáo Đánh Giá 5S")
    
    # Chọn Khoa/Phòng
    df_depts = run_query("SELECT id, unit_code, unit_name FROM departments ORDER BY unit_code")
    
    if df_depts.empty:
        st.warning("⚠️ Chưa có Khoa/Phòng")
        st.stop()
    
    dept_options = {f"{row['unit_code']} - {row['unit_name']}": row['id'] for _, row in df_depts.iterrows()}
    selected_dept = st.selectbox("Chọn Khoa/Phòng", options=list(dept_options.keys()), key="dept_report")
    selected_dept_id = dept_options[selected_dept]
    
    # Chọn đợt đánh giá
    df_evals = run_query("""
        SELECT e.id, e.eval_date, 
               COUNT(ed.id) as tong_so,
               SUM(CASE WHEN ed.is_pass THEN 1 ELSE 0 END) as so_dat
        FROM evaluations e
        JOIN evaluation_details ed ON e.id = ed.evaluation_id
        WHERE e.department_id = %s
        GROUP BY e.id, e.eval_date
        ORDER BY e.eval_date DESC
    """, params=(selected_dept_id,))
    
    if df_evals.empty:
        st.info("📭 Chưa có đợt đánh giá nào")
    else:
        eval_options = {
            f"{row['eval_date']} ({row['so_dat']}/{row['tong_so']} đạt)": row['id'] 
            for _, row in df_evals.iterrows()
        }
        selected_eval = st.selectbox("Chọn đợt đánh giá", options=list(eval_options.keys()), key="eval_report")
        selected_eval_id = eval_options[selected_eval]
        
        st.divider()
        
        # Preview dữ liệu
        st.write("### Preview Dữ Liệu")
        
        df_preview = run_query("""
            SELECT 
                a.area_name as "Khu vực",
                c.location_name as "Vị trí",
                c.category as "Hạng mục",
                CASE WHEN ed.is_pass THEN 'Đạt' ELSE 'Không đạt' END as "Kết quả",
                s.name as "Nhân sự"
            FROM evaluation_details ed
            JOIN criteria c ON ed.criteria_id = c.id
            JOIN areas a ON c.area_id = a.id
            JOIN staff s ON ed.staff_id = s.id
            WHERE ed.evaluation_id = %s
            ORDER BY a.area_name, c.location_name
        """, params=(selected_eval_id,))
        
        if not df_preview.empty:
            st.dataframe(df_preview, use_container_width=True, hide_index=True, height=300)
            
            st.divider()
            
            # Form nhập thông tin
            st.write("### Thông Tin Báo Cáo")
            
            col1, col2 = st.columns(2)
            
            with col1:
                report_title = st.text_input(
                    "Tiêu đề báo cáo",
                    value=f"BAO CAO DANH GIA 5S - {selected_dept.split(' - ')[1].upper()}",
                    key="report_title"
                )
                evaluator_name = st.text_input("Người kiểm tra", key="evaluator")
            
            with col2:
                report_date = st.date_input("Ngày báo cáo", value=datetime.now().date(), key="report_date")
                supervisor_name = st.text_input("Điều phối/Giám sát", key="supervisor")
            
            manager_name = st.text_input("P.Quản lý chất lượng", key="manager")
            evaluation_text = st.text_area("Đánh giá & Nhận xét", height=150, key="eval_text")
            
            st.divider()
            
            # Nút tạo báo cáo
            if st.button("📄 Tạo Báo Cáo PDF", type="primary", use_container_width=True):
                try:
                    # Tạo PDF với FPDF
                    pdf = PDF5S()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    # Title
                    pdf.set_font('Arial', 'B', 16)
                    pdf.cell(0, 10, report_title.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'C')
                    pdf.ln(5)
                    
                    # Info
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(0, 6, f"Khoa/Phong: {selected_dept.encode('latin-1', 'replace').decode('latin-1')}", 0, 1)
                    pdf.cell(0, 6, f"Thoi gian: {report_date}", 0, 1)
                    if evaluator_name:
                        pdf.cell(0, 6, f"Nguoi kiem tra: {evaluator_name.encode('latin-1', 'replace').decode('latin-1')}", 0, 1)
                    pdf.ln(10)
                    
                    # Table header
                    pdf.set_font('Arial', 'B', 9)
                    pdf.set_fill_color(66, 153, 225)
                    pdf.set_text_color(255, 255, 255)
                    
                    col_widths = [35, 45, 55, 25, 30]
                    headers = ['Khu vuc', 'Vi tri', 'Hang muc', 'Ket qua', 'Nhan su']
                    
                    for i, header in enumerate(headers):
                        pdf.cell(col_widths[i], 8, header, 1, 0, 'C', True)
                    pdf.ln()
                    
                    # Table rows
                    pdf.set_font('Arial', '', 8)
                    pdf.set_text_color(0, 0, 0)
                    
                    for idx, row in df_preview.iterrows():
                        if idx % 2 == 0:
                            pdf.set_fill_color(247, 250, 252)
                        else:
                            pdf.set_fill_color(255, 255, 255)
                        
                        data = [
                            str(row['Khu vực'])[:18],
                            str(row['Vị trí'])[:22],
                            str(row['Hạng mục'])[:28],
                            str(row['Kết quả'])[:12],
                            str(row['Nhân sự'])[:15]
                        ]
                        
                        for i, val in enumerate(data):
                            pdf.cell(col_widths[i], 6, val.encode('latin-1', 'replace').decode('latin-1'), 1, 0, 'L', True)
                        pdf.ln()
                    
                    pdf.ln(10)
                    
                    # Evaluation section
                    if evaluation_text:
                        pdf.set_font('Arial', 'B', 11)
                        pdf.cell(0, 8, 'DANH GIA & NHAN XET', 0, 1)
                        pdf.set_font('Arial', '', 10)
                        pdf.multi_cell(0, 5, evaluation_text.encode('latin-1', 'replace').decode('latin-1'))
                        pdf.ln(10)
                    
                    # Signatures
                    pdf.ln(15)
                    pdf.set_font('Arial', 'B', 10)
                    
                    x_start = pdf.get_x()
                    y_start = pdf.get_y()
                    
                    # 3 columns for signatures
                    pdf.cell(60, 6, 'Nguoi kiem tra', 0, 0, 'C')
                    pdf.cell(65, 6, 'Dieu phoi/Giam sat', 0, 0, 'C')
                    pdf.cell(60, 6, 'P.Quan ly chat luong', 0, 1, 'C')
                    
                    pdf.ln(20)
                    
                    pdf.set_font('Arial', '', 9)
                    if evaluator_name:
                        pdf.cell(60, 6, evaluator_name.encode('latin-1', 'replace').decode('latin-1'), 0, 0, 'C')
                    else:
                        pdf.cell(60, 6, '', 0, 0, 'C')
                    
                    if supervisor_name:
                        pdf.cell(65, 6, supervisor_name.encode('latin-1', 'replace').decode('latin-1'), 0, 0, 'C')
                    else:
                        pdf.cell(65, 6, '', 0, 0, 'C')
                    
                    if manager_name:
                        pdf.cell(60, 6, manager_name.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'C')
                    else:
                        pdf.cell(60, 6, '', 0, 1, 'C')
                    
                    # Get PDF bytes
                    pdf_bytes = pdf.output(dest='S').encode('latin-1')
                    
                    # Save to database
                    conn = get_connection()
                    cur = conn.cursor()
                    
                    cur.execute("""
                        INSERT INTO reports 
                        (evaluation_id, report_title, report_date, evaluator_name, supervisor_name, manager_name, evaluation_text, pdf_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        selected_eval_id,
                        report_title,
                        report_date,
                        evaluator_name if evaluator_name else None,
                        supervisor_name if supervisor_name else None,
                        manager_name if manager_name else None,
                        evaluation_text if evaluation_text else None,
                        pdf_bytes
                    ))
                    
                    report_id = cur.fetchone()[0]
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    st.success(f"✅ Đã tạo báo cáo #{report_id}")
                    st.balloons()
                    
                    # Download button
                    st.download_button(
                        label="📥 Tải Báo Cáo PDF",
                        data=pdf_bytes,
                        file_name=f"Bao_cao_5S_{selected_dept.split(' - ')[0]}_{report_date}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")
                    import traceback
                    st.code(traceback.format_exc())

# ==================== TAB 2: QUẢN LÝ BÁO CÁO ====================
with tab2:
    st.subheader("Danh Sách Báo Cáo")
    
    df_reports = run_query("""
        SELECT 
            r.id,
            r.report_title,
            r.report_date,
            d.unit_name as department,
            r.evaluator_name,
            r.created_at
        FROM reports r
        JOIN evaluations e ON r.evaluation_id = e.id
        JOIN departments d ON e.department_id = d.id
        ORDER BY r.created_at DESC
    """)
    
    if not df_reports.empty:
        st.write(f"**Tổng số: {len(df_reports)} báo cáo**")
        
        for idx, report in df_reports.iterrows():
            with st.expander(f"📄 {report['report_title']} - {report['report_date']}"):
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    st.write(f"**Khoa/Phòng:** {report['department']}")
                    st.write(f"**Ngày:** {report['report_date']}")
                    st.write(f"**Người kiểm tra:** {report['evaluator_name']}")
                
                with col_actions:
                    # Get PDF
                    df_pdf = run_query("SELECT pdf_data FROM reports WHERE id = %s", params=(report['id'],))
                    if not df_pdf.empty and df_pdf.iloc[0]['pdf_data']:
                        pdf_data = bytes(df_pdf.iloc[0]['pdf_data'])
                        st.download_button(
                            "📥 Tải PDF",
                            data=pdf_data,
                            file_name=f"Report_{report['id']}.pdf",
                            mime="application/pdf",
                            key=f"download_{report['id']}",
                            use_container_width=True
                        )
                    
                    if st.button("🗑️ Xóa", key=f"del_{report['id']}", use_container_width=True):
                        st.session_state[f"confirm_del_{report['id']}"] = True
                
                if st.session_state.get(f"confirm_del_{report['id']}", False):
                    st.warning("⚠️ Xác nhận xóa?")
                    col_y, col_n = st.columns(2)
                    
                    with col_y:
                        if st.button("✅ Xóa", key=f"yes_{report['id']}", type="primary"):
                            try:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("DELETE FROM reports WHERE id=%s", (report['id'],))
                                conn.commit()
                                cur.close()
                                conn.close()
                                st.success("✅ Đã xóa!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Lỗi: {e}")
                    
                    with col_n:
                        if st.button("❌ Hủy", key=f"no_{report['id']}"):
                            st.session_state[f"confirm_del_{report['id']}"] = False
                            st.rerun()
    else:
        st.info("📭 Chưa có báo cáo")

# ==================== TAB 3: XEM BÁO CÁO ====================
with tab3:
    st.info("💡 Sử dụng nút 'Tải PDF' ở Tab 'Quản Lý Báo Cáo' để tải và xem báo cáo")
