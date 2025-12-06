import streamlit as st
import pandas as pd
from datetime import datetime
from db_utils import run_query, get_connection
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import os

st.set_page_config(page_title="Xuất Báo Cáo", page_icon="📄", layout="wide")

st.title("📄 XUẤT BÁO CÁO PDF")

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
        st.info("📭 Chưa có đợt đánh giá nào cho Khoa/Phòng này")
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
                s.name as "Nhân sự",
                ed.adjustment_note as "Ghi chú"
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
            
            # Form nhập thông tin báo cáo
            st.write("### Thông Tin Báo Cáo")
            
            col1, col2 = st.columns(2)
            
            with col1:
                report_title = st.text_input(
                    "Tiêu đề báo cáo",
                    value=f"BÁO CÁO ĐÁNH GIÁ 5S - {selected_dept.split(' - ')[1].upper()}",
                    key="report_title"
                )
                
                evaluator_name = st.text_input("Người đi kiểm tra", placeholder="Nguyễn Văn A", key="evaluator")
            
            with col2:
                report_date = st.date_input("Ngày báo cáo", value=datetime.now().date(), key="report_date")
                
                supervisor_name = st.text_input("Điều phối/Giám sát", placeholder="Trần Thị B", key="supervisor")
            
            manager_name = st.text_input("P.Quản lý chất lượng", placeholder="Lê Văn C", key="manager")
            
            evaluation_text = st.text_area(
                "Đánh giá & Nhận xét",
                placeholder="Nhập đánh giá tổng quát về kết quả đánh giá 5S...",
                height=150,
                key="eval_text"
            )
            
            st.divider()
            
            # Nút tạo báo cáo
            if st.button("📄 Tạo Báo Cáo PDF", type="primary", use_container_width=True):
                try:
                    # Tạo PDF
                    pdf_buffer = io.BytesIO()
                    
                    # Setup document
                    doc = SimpleDocTemplate(
                        pdf_buffer,
                        pagesize=A4,
                        rightMargin=2*cm,
                        leftMargin=2*cm,
                        topMargin=2*cm,
                        bottomMargin=2*cm
                    )
                    
                    # Register font (nếu có)
                    # Nếu không có font tiếng Việt, dùng Helvetica
                    styles = getSampleStyleSheet()
                    
                    # Custom styles
                    title_style = ParagraphStyle(
                        'CustomTitle',
                        parent=styles['Heading1'],
                        fontSize=16,
                        textColor=colors.HexColor('#1f4788'),
                        spaceAfter=20,
                        alignment=TA_CENTER,
                        fontName='Helvetica-Bold'
                    )
                    
                    heading_style = ParagraphStyle(
                        'CustomHeading',
                        parent=styles['Heading2'],
                        fontSize=12,
                        textColor=colors.HexColor('#2c5282'),
                        spaceAfter=10,
                        fontName='Helvetica-Bold'
                    )
                    
                    normal_style = ParagraphStyle(
                        'CustomNormal',
                        parent=styles['Normal'],
                        fontSize=10,
                        fontName='Helvetica'
                    )
                    
                    # Build content
                    story = []
                    
                    # Title
                    story.append(Paragraph(report_title, title_style))
                    story.append(Spacer(1, 0.5*cm))
                    
                    # Info section
                    info_data = [
                        ['Khoa/Phong:', selected_dept],
                        ['Thoi gian:', str(report_date)],
                        ['Nguoi kiem tra:', evaluator_name if evaluator_name else '']
                    ]
                    
                    info_table = Table(info_data, colWidths=[4*cm, 12*cm])
                    info_table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c5282')),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    
                    story.append(info_table)
                    story.append(Spacer(1, 0.8*cm))
                    
                    # Results table
                    story.append(Paragraph('KET QUA DANH GIA CHI TIET', heading_style))
                    story.append(Spacer(1, 0.3*cm))
                    
                    # Prepare table data
                    table_data = [['Khu vuc', 'Vi tri', 'Hang muc', 'Ket qua', 'Nhan su']]
                    
                    for _, row in df_preview.iterrows():
                        table_data.append([
                            str(row['Khu vực'])[:20],
                            str(row['Vị trí'])[:25],
                            str(row['Hạng mục'])[:30],
                            str(row['Kết quả']),
                            str(row['Nhân sự'])[:20]
                        ])
                    
                    results_table = Table(table_data, colWidths=[3.5*cm, 4*cm, 5*cm, 2*cm, 2.5*cm])
                    results_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299e1')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
                    ]))
                    
                    story.append(results_table)
                    story.append(Spacer(1, 0.8*cm))
                    
                    # Evaluation section
                    if evaluation_text:
                        story.append(Paragraph('DANH GIA & NHAN XET', heading_style))
                        story.append(Spacer(1, 0.3*cm))
                        
                        eval_para = Paragraph(evaluation_text, normal_style)
                        story.append(eval_para)
                        story.append(Spacer(1, 1*cm))
                    
                    # Signature section
                    story.append(Spacer(1, 1*cm))
                    
                    sig_data = [
                        ['Nguoi kiem tra', 'Dieu phoi/Giam sat', 'P.Quan ly chat luong'],
                        ['', '', ''],
                        ['', '', ''],
                        [evaluator_name if evaluator_name else '', supervisor_name if supervisor_name else '', manager_name if manager_name else '']
                    ]
                    
                    sig_table = Table(sig_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm], rowHeights=[0.8*cm, 2*cm, 0.5*cm, 0.8*cm])
                    sig_table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica'),
                        ('FONTSIZE', (0, 3), (-1, 3), 9),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                        ('VALIGN', (0, 3), (-1, 3), 'TOP'),
                        ('LINEABOVE', (0, 3), (-1, 3), 0.5, colors.black),
                    ]))
                    
                    story.append(sig_table)
                    
                    # Build PDF
                    doc.build(story)
                    
                    # Save to database
                    pdf_bytes = pdf_buffer.getvalue()
                    
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

# ==================== TAB 2: QUẢN LÝ BÁO CÁO ====================
with tab2:
    st.subheader("Danh Sách Báo Cáo")
    
    # Lấy danh sách báo cáo
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
                    st.write(f"**Ngày báo cáo:** {report['report_date']}")
                    st.write(f"**Người kiểm tra:** {report['evaluator_name']}")
                    st.write(f"**Tạo lúc:** {report['created_at']}")
                
                with col_actions:
                    if st.button("🔍 Xem", key=f"view_{report['id']}", use_container_width=True):
                        st.session_state['viewing_report_id'] = report['id']
                        st.rerun()
                    
                    if st.button("✏️ Sửa", key=f"edit_{report['id']}", use_container_width=True):
                        st.session_state[f"editing_report_{report['id']}"] = True
                    
                    if st.button("🗑️ Xóa", key=f"delete_{report['id']}", use_container_width=True):
                        st.session_state[f"confirm_delete_report_{report['id']}"] = True
                
                # Form sửa
                if st.session_state.get(f"editing_report_{report['id']}", False):
                    st.divider()
                    st.write("### ✏️ Chỉnh sửa Báo cáo")
                    
                    # Lấy dữ liệu báo cáo
                    df_report_data = run_query(
                        "SELECT * FROM reports WHERE id = %s",
                        params=(report['id'],)
                    )
                    
                    if not df_report_data.empty:
                        report_data = df_report_data.iloc[0]
                        
                        new_title = st.text_input("Tiêu đề", value=report_data['report_title'], key=f"edit_title_{report['id']}")
                        new_eval_text = st.text_area("Đánh giá", value=report_data['evaluation_text'] or "", key=f"edit_eval_{report['id']}", height=150)
                        
                        col_save, col_cancel = st.columns(2)
                        
                        with col_save:
                            if st.button("💾 Lưu", type="primary", key=f"save_{report['id']}", use_container_width=True):
                                try:
                                    conn = get_connection()
                                    cur = conn.cursor()
                                    cur.execute(
                                        "UPDATE reports SET report_title=%s, evaluation_text=%s WHERE id=%s",
                                        (new_title, new_eval_text, report['id'])
                                    )
                                    conn.commit()
                                    cur.close()
                                    conn.close()
                                    
                                    st.success("✅ Đã cập nhật!")
                                    st.session_state[f"editing_report_{report['id']}"] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Lỗi: {e}")
                        
                        with col_cancel:
                            if st.button("❌ Hủy", key=f"cancel_{report['id']}", use_container_width=True):
                                st.session_state[f"editing_report_{report['id']}"] = False
                                st.rerun()
                
                # Xóa
                if st.session_state.get(f"confirm_delete_report_{report['id']}", False):
                    st.warning(f"⚠️ Xác nhận xóa báo cáo **{report['report_title']}**?")
                    
                    col_yes, col_no = st.columns(2)
                    
                    with col_yes:
                        if st.button("✅ Xóa", type="primary", key=f"yes_delete_{report['id']}"):
                            try:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("DELETE FROM reports WHERE id=%s", (report['id'],))
                                conn.commit()
                                cur.close()
                                conn.close()
                                
                                st.success("✅ Đã xóa!")
                                st.session_state[f"confirm_delete_report_{report['id']}"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Lỗi: {e}")
                    
                    with col_no:
                        if st.button("❌ Hủy", key=f"no_delete_{report['id']}"):
                            st.session_state[f"confirm_delete_report_{report['id']}"] = False
                            st.rerun()
    else:
        st.info("📭 Chưa có báo cáo nào")

# ==================== TAB 3: XEM & IN BÁO CÁO ====================
with tab3:
    st.subheader("Xem & In Báo Cáo")
    
    if 'viewing_report_id' in st.session_state:
        # Lấy dữ liệu báo cáo
        df_view = run_query(
            "SELECT * FROM reports WHERE id = %s",
            params=(st.session_state['viewing_report_id'],)
        )
        
        if not df_view.empty:
            report_view = df_view.iloc[0]
            
            st.write(f"### {report_view['report_title']}")
            st.write(f"**Ngày:** {report_view['report_date']}")
            
            # Display PDF
            if report_view['pdf_data']:
                pdf_bytes = bytes(report_view['pdf_data'])
                
                # Download button
                st.download_button(
                    label="📥 Tải PDF",
                    data=pdf_bytes,
                    file_name=f"Report_{report_view['id']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.divider()
                
                # Embed PDF viewer (base64)
                import base64
                base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.warning("⚠️ PDF không có dữ liệu")
        else:
            st.error("❌ Không tìm thấy báo cáo")
    else:
        st.info("💡 Chọn báo cáo từ Tab 'Quản Lý Báo Cáo' để xem")
