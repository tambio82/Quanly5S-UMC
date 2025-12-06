import streamlit as st
import pandas as pd
from datetime import datetime
from db_utils import run_query, get_connection
from fpdf import FPDF
import io
import os
import glob

st.set_page_config(page_title="Xuất Báo Cáo", page_icon="📄", layout="wide")

st.title("📄 XUẤT BÁO CÁO PDF")

# Find DejaVu font
def find_dejavu_font():
    """Auto-detect DejaVu font location"""
    possible_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans.ttf',
        '/System/Library/Fonts/Supplemental/DejaVuSans.ttf',
        'C:\\Windows\\Fonts\\DejaVuSans.ttf',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.dirname(path)
    
    # Try to find via glob
    for pattern in ['/usr/share/fonts/**/DejaVuSans.ttf', '/System/**/DejaVuSans.ttf']:
        results = glob.glob(pattern, recursive=True)
        if results:
            return os.path.dirname(results[0])
    
    return None

# Custom PDF class with Unicode support
class PDF5S(FPDF):
    def __init__(self):
        super().__init__()
        
        # Try to add DejaVu font
        font_dir = find_dejavu_font()
        
        if font_dir:
            try:
                self.add_font('DejaVu', '', f'{font_dir}/DejaVuSans.ttf', uni=True)
                self.add_font('DejaVu', 'B', f'{font_dir}/DejaVuSans-Bold.ttf', uni=True)
                self.font_available = True
            except:
                self.font_available = False
        else:
            self.font_available = False
        
        # Fallback to Arial if DejaVu not found
        if not self.font_available:
            st.warning("⚠️ DejaVu font không tìm thấy. Sử dụng Arial (có thể lỗi font tiếng Việt)")
    
    def header(self):
        font = 'DejaVu' if self.font_available else 'Arial'
        self.set_font(font, 'B', 16)
        self.cell(0, 10, '', 0, 1, 'C')
    
    def footer(self):
        self.set_y(-15)
        font = 'DejaVu' if self.font_available else 'Arial'
        self.set_font(font, 'I', 8)
        self.cell(0, 10, f'Trang {self.page_no()}', 0, 0, 'C')

# Tabs
tab1, tab2 = st.tabs(["📝 Tạo Báo Cáo Mới", "📋 Quản Lý Báo Cáo"])

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
                a.area_name,
                c.location_name,
                c.category,
                CASE WHEN ed.is_pass THEN 'Đạt' ELSE 'Không đạt' END as result,
                s.name as staff_name
            FROM evaluation_details ed
            JOIN criteria c ON ed.criteria_id = c.id
            JOIN areas a ON c.area_id = a.id
            JOIN staff s ON ed.staff_id = s.id
            WHERE ed.evaluation_id = %s
            ORDER BY a.area_name, c.location_name
        """, params=(selected_eval_id,))
        
        if not df_preview.empty:
            # Rename for display
            df_display = df_preview.rename(columns={
                'area_name': 'Khu vực',
                'location_name': 'Vị trí',
                'category': 'Hạng mục',
                'result': 'Kết quả',
                'staff_name': 'Nhân sự'
            })
            
            st.dataframe(df_display, use_container_width=True, hide_index=True, height=300)
            
            st.divider()
            
            # Form nhập thông tin
            st.write("### Thông Tin Báo Cáo")
            
            col1, col2 = st.columns(2)
            
            with col1:
                report_title = st.text_input(
                    "Tiêu đề báo cáo",
                    value=f"BÁO CÁO ĐÁNH GIÁ 5S - {selected_dept.split(' - ')[1].upper()}",
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
                    # Tạo PDF
                    pdf = PDF5S()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    font = 'DejaVu' if pdf.font_available else 'Arial'
                    
                    # Title
                    pdf.set_font(font, 'B', 16)
                    pdf.cell(0, 10, report_title, 0, 1, 'C')
                    pdf.ln(5)
                    
                    # Info
                    pdf.set_font(font, '', 10)
                    pdf.cell(0, 6, f"Khoa/Phòng: {selected_dept}", 0, 1)
                    pdf.cell(0, 6, f"Thời gian: {report_date}", 0, 1)
                    if evaluator_name:
                        pdf.cell(0, 6, f"Người kiểm tra: {evaluator_name}", 0, 1)
                    pdf.ln(10)
                    
                    # Table header
                    pdf.set_font(font, 'B', 9)
                    pdf.set_fill_color(66, 153, 225)
                    pdf.set_text_color(255, 255, 255)
                    
                    col_widths = [35, 45, 55, 25, 30]
                    headers = ['Khu vực', 'Vị trí', 'Hạng mục', 'Kết quả', 'Nhân sự']
                    
                    for i, header in enumerate(headers):
                        pdf.cell(col_widths[i], 8, header, 1, 0, 'C', True)
                    pdf.ln()
                    
                    # Table rows
                    pdf.set_font(font, '', 8)
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
                            str(row['staff_name'])[:15]
                        ]
                        
                        for i, val in enumerate(data):
                            pdf.cell(col_widths[i], 6, val, 1, 0, 'L', True)
                        pdf.ln()
                    
                    pdf.ln(10)
                    
                    # Evaluation section
                    if evaluation_text:
                        pdf.set_font(font, 'B', 11)
                        pdf.cell(0, 8, 'ĐÁNH GIÁ & NHẬN XÉT', 0, 1)
                        pdf.set_font(font, '', 10)
                        pdf.multi_cell(0, 5, evaluation_text)
                        pdf.ln(10)
                    
                    # Signatures
                    pdf.ln(15)
                    pdf.set_font(font, 'B', 10)
                    
                    pdf.cell(60, 6, 'Người kiểm tra', 0, 0, 'C')
                    pdf.cell(65, 6, 'Điều phối/Giám sát', 0, 0, 'C')
                    pdf.cell(60, 6, 'P.Quản lý chất lượng', 0, 1, 'C')
                    
                    pdf.ln(20)
                    
                    pdf.set_font(font, '', 9)
                    pdf.cell(60, 6, evaluator_name or '', 0, 0, 'C')
                    pdf.cell(65, 6, supervisor_name or '', 0, 0, 'C')
                    pdf.cell(60, 6, manager_name or '', 0, 1, 'C')
                    
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
                        evaluator_name or None,
                        supervisor_name or None,
                        manager_name or None,
                        evaluation_text or None,
                        pdf_bytes
                    ))
                    
                    report_id = cur.fetchone()[0]
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    st.success(f"✅ Đã tạo báo cáo #{report_id}")
                    
                    if pdf.font_available:
                        st.info("✅ Font tiếng Việt: DejaVu (đầy đủ)")
                    else:
                        st.warning("⚠️ Font tiếng Việt: Arial (có thể lỗi dấu)")
                    
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
                    if report['evaluator_name']:
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
