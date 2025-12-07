import streamlit as st
import pandas as pd
import io
from datetime import datetime
from db_utils import run_query, get_connection
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

st.set_page_config(page_title="Dữ Liệu", page_icon="💾", layout="wide")
st.title("💾 IMPORT / EXPORT DỮ LIỆU")

tab1, tab2 = st.tabs(["📤 Export", "📥 Import"])

# ==================== TAB 1: EXPORT ====================
with tab1:
    st.subheader("📤 Xuất Template Excel")
    
    st.markdown("""
    ### 📋 Hướng dẫn sử dụng:
    1. **Chọn Khoa/Phòng** cần nhập liệu
    2. **Tải Template Excel** - File sẽ chứa:
       - Tất cả khu vực của Khoa/Phòng
       - Tất cả tiêu chí đánh giá (104 hạng mục)
       - Danh sách nhân sự của Khoa/Phòng
    3. **Nhập liệu** trên Excel:
       - Cột "Kết quả": Nhập `Đạt` hoặc `Không đạt`
       - Cột "Nhân sự": Chọn tên từ danh sách (sheet "Nhân sự")
       - Cột "Nội dung điều chỉnh": Ghi chú nếu cần
       - Cột "Link minh chứng": URL ảnh/file
    4. **Import lại** file Excel ở tab "Import"
    """)
    
    st.divider()
    
    # Chọn Khoa/Phòng
    df_depts = run_query("SELECT id, unit_code, unit_name FROM departments ORDER BY unit_code")
    
    if df_depts.empty:
        st.warning("⚠️ Chưa có Khoa/Phòng nào")
    else:
        dept_options = {f"{row['unit_code']} - {row['unit_name']}": row['id'] 
                       for _, row in df_depts.iterrows()}
        
        selected_dept = st.selectbox(
            "🏢 Chọn Khoa/Phòng cần tạo template",
            options=list(dept_options.keys()),
            key="export_dept"
        )
        
        selected_dept_id = dept_options[selected_dept]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"**Khoa/Phòng:** {selected_dept}")
        
        with col2:
            if st.button("📥 Tạo Template Excel", type="primary", use_container_width=True):
                try:
                    # Get data
                    df_criteria = run_query("""
                        SELECT 
                            a.area_name,
                            c.location_name,
                            c.category,
                            a.definition as area_definition
                        FROM criteria c
                        JOIN areas a ON c.area_id = a.id
                        JOIN department_areas da ON a.id = da.area_id
                        WHERE da.department_id = %s
                        ORDER BY a.area_name, c.location_name, c.category
                    """, params=(selected_dept_id,))
                    
                    df_staff = run_query("""
                        SELECT name, staff_code, role
                        FROM staff
                        WHERE department_id = %s
                        ORDER BY name
                    """, params=(selected_dept_id,))
                    
                    if df_criteria.empty:
                        st.error("❌ Khoa/Phòng này chưa có khu vực/tiêu chí nào")
                    else:
                        # Create Excel with template
                        output = io.BytesIO()
                        
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            # Sheet 1: Dữ liệu đánh giá
                            df_template = pd.DataFrame({
                                'Khu vực': df_criteria['area_name'],
                                'Định nghĩa': df_criteria['area_definition'],
                                'Vị trí': df_criteria['location_name'],
                                'Hạng mục': df_criteria['category'],
                                'Kết quả': '',  # User fills
                                'Nhân sự': '',  # User fills
                                'Nội dung điều chỉnh': '',  # Optional
                                'Link minh chứng': ''  # Optional
                            })
                            
                            df_template.to_excel(writer, sheet_name='Đánh giá 5S', index=False)
                            
                            # Sheet 2: Danh sách nhân sự (reference)
                            if not df_staff.empty:
                                df_staff_ref = pd.DataFrame({
                                    'Tên nhân sự': df_staff['name'],
                                    'Mã NV': df_staff['staff_code'],
                                    'Chức vụ': df_staff['role']
                                })
                                df_staff_ref.to_excel(writer, sheet_name='Danh sách nhân sự', index=False)
                            
                            # Sheet 3: Hướng dẫn
                            df_guide = pd.DataFrame({
                                'Bước': [1, 2, 3, 4, 5],
                                'Hướng dẫn': [
                                    'Mở sheet "Đánh giá 5S"',
                                    'Cột "Kết quả": Nhập "Đạt" hoặc "Không đạt"',
                                    'Cột "Nhân sự": Copy tên từ sheet "Danh sách nhân sú"',
                                    'Các cột khác (Nội dung điều chỉnh, Link): Tùy chọn',
                                    'Lưu file và import lại vào hệ thống'
                                ]
                            })
                            df_guide.to_excel(writer, sheet_name='Hướng dẫn', index=False)
                            
                            # Format Excel
                            workbook = writer.book
                            worksheet = writer.sheets['Đánh giá 5S']
                            
                            # Header style
                            header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
                            header_font = Font(bold=True, color='FFFFFF', size=11)
                            header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                            
                            for cell in worksheet[1]:
                                cell.fill = header_fill
                                cell.font = header_font
                                cell.alignment = header_alignment
                            
                            # Column widths
                            worksheet.column_dimensions['A'].width = 25  # Khu vực
                            worksheet.column_dimensions['B'].width = 30  # Định nghĩa
                            worksheet.column_dimensions['C'].width = 25  # Vị trí
                            worksheet.column_dimensions['D'].width = 35  # Hạng mục
                            worksheet.column_dimensions['E'].width = 15  # Kết quả
                            worksheet.column_dimensions['F'].width = 25  # Nhân sự
                            worksheet.column_dimensions['G'].width = 30  # Nội dung điều chỉnh
                            worksheet.column_dimensions['H'].width = 35  # Link
                            
                            # Freeze first row
                            worksheet.freeze_panes = 'A2'
                            
                            # Format staff sheet
                            if 'Danh sách nhân sự' in writer.sheets:
                                ws_staff = writer.sheets['Danh sách nhân sự']
                                for cell in ws_staff[1]:
                                    cell.fill = header_fill
                                    cell.font = header_font
                                    cell.alignment = header_alignment
                                
                                ws_staff.column_dimensions['A'].width = 30
                                ws_staff.column_dimensions['B'].width = 15
                                ws_staff.column_dimensions['C'].width = 20
                        
                        output.seek(0)
                        
                        # Download button
                        filename = f"Template_5S_{selected_dept.split(' - ')[0]}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                        
                        st.success(f"✅ Đã tạo template với {len(df_criteria)} tiêu chí đánh giá")
                        
                        st.download_button(
                            label="📥 Tải Template Excel",
                            data=output,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        
                        # Preview
                        with st.expander("👁️ Xem trước dữ liệu"):
                            st.write(f"**Tổng số tiêu chí:** {len(df_criteria)}")
                            st.write(f"**Số nhân sự:** {len(df_staff)}")
                            st.dataframe(df_template.head(10), use_container_width=True)
                        
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")
                    import traceback
                    st.code(traceback.format_exc())

# ==================== TAB 2: IMPORT ====================
with tab2:
    st.subheader("📥 Import Dữ Liệu Đánh Giá")
    
    st.markdown("""
    ### 📋 Quy trình Import:
    1. Chọn Khoa/Phòng (phải trùng với file template)
    2. Upload file Excel đã điền đầy đủ
    3. Hệ thống sẽ kiểm tra dữ liệu
    4. Xem preview và xác nhận import
    """)
    
    st.divider()
    
    # Chọn Khoa/Phòng
    df_depts_import = run_query("SELECT id, unit_code, unit_name FROM departments ORDER BY unit_code")
    
    if not df_depts_import.empty:
        dept_options_import = {f"{row['unit_code']} - {row['unit_name']}": row['id'] 
                              for _, row in df_depts_import.iterrows()}
        
        selected_dept_import = st.selectbox(
            "🏢 Chọn Khoa/Phòng",
            options=list(dept_options_import.keys()),
            key="import_dept"
        )
        
        selected_dept_id_import = dept_options_import[selected_dept_import]
        
        st.divider()
        
        # Upload file
        uploaded_file = st.file_uploader(
            "📂 Upload file Excel Template",
            type=['xlsx'],
            help="File phải là template đã tải từ tab Export"
        )
        
        if uploaded_file is not None:
            try:
                # Read Excel
                df_import = pd.read_excel(uploaded_file, sheet_name='Đánh giá 5S')
                
                st.success(f"✅ Đọc file thành công: {len(df_import)} dòng")
                
                # Validate
                st.write("### 🔍 Kiểm tra dữ liệu")
                
                errors = []
                warnings = []
                
                # Check required columns
                required_cols = ['Khu vực', 'Vị trí', 'Hạng mục', 'Kết quả', 'Nhân sự']
                missing_cols = [col for col in required_cols if col not in df_import.columns]
                
                if missing_cols:
                    errors.append(f"Thiếu các cột: {', '.join(missing_cols)}")
                
                # Check empty results
                if 'Kết quả' in df_import.columns:
                    empty_results = df_import['Kết quả'].isna().sum()
                    if empty_results > 0:
                        warnings.append(f"{empty_results} dòng chưa điền Kết quả")
                
                # Check empty staff
                if 'Nhân sự' in df_import.columns:
                    empty_staff = df_import['Nhân sự'].isna().sum()
                    if empty_staff > 0:
                        warnings.append(f"{empty_staff} dòng chưa điền Nhân sự")
                
                # Check valid results
                if 'Kết quả' in df_import.columns:
                    valid_results = ['Đạt', 'Không đạt', 'dat', 'khong dat', 'DAT', 'KHONG DAT']
                    invalid = df_import[~df_import['Kết quả'].isna() & 
                                       ~df_import['Kết quả'].isin(valid_results)]
                    if len(invalid) > 0:
                        errors.append(f"{len(invalid)} dòng có Kết quả không hợp lệ (phải là 'Đạt' hoặc 'Không đạt')")
                
                # Display validation results
                if errors:
                    st.error("❌ **Lỗi nghiêm trọng:**")
                    for err in errors:
                        st.error(f"- {err}")
                
                if warnings:
                    st.warning("⚠️ **Cảnh báo:**")
                    for warn in warnings:
                        st.warning(f"- {warn}")
                
                if not errors:
                    st.success("✅ Dữ liệu hợp lệ!")
                    
                    # Preview
                    with st.expander("👁️ Xem trước dữ liệu", expanded=True):
                        st.dataframe(df_import.head(20), use_container_width=True, height=400)
                    
                    st.divider()
                    
                    # Ngày đánh giá
                    eval_date = st.date_input(
                        "📅 Ngày đánh giá",
                        value=datetime.now().date(),
                        help="Ngày thực hiện đánh giá 5S"
                    )
                    
                    # Import button
                    if st.button("✅ Xác nhận Import", type="primary", use_container_width=True):
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            
                            # Get staff mapping
                            df_staff = run_query("""
                                SELECT id, name FROM staff WHERE department_id = %s
                            """, params=(selected_dept_id_import,))
                            
                            staff_map = {}
                            for _, row in df_staff.iterrows():
                                clean_name = ' '.join(row['name'].split())
                                staff_map[clean_name] = row['id']
                            
                            # Get criteria mapping
                            df_criteria = run_query("""
                                SELECT c.id, a.area_name, c.location_name, c.category
                                FROM criteria c
                                JOIN areas a ON c.area_id = a.id
                                JOIN department_areas da ON a.id = da.area_id
                                WHERE da.department_id = %s
                            """, params=(selected_dept_id_import,))
                            
                            criteria_map = {}
                            for _, row in df_criteria.iterrows():
                                key = f"{row['area_name']}|{row['location_name']}|{row['category']}"
                                criteria_map[key] = row['id']
                            
                            # Create evaluation
                            cur.execute("""
                                INSERT INTO evaluations (department_id, eval_date)
                                VALUES (%s, %s)
                                RETURNING id
                            """, (selected_dept_id_import, eval_date))
                            
                            eval_id = cur.fetchone()[0]
                            
                            # Import details
                            success_count = 0
                            error_lines = []
                            
                            for idx, row in df_import.iterrows():
                                try:
                                    # Skip if no result
                                    if pd.isna(row['Kết quả']):
                                        continue
                                    
                                    # Get criteria_id
                                    key = f"{row['Khu vực']}|{row['Vị trí']}|{row['Hạng mục']}"
                                    criteria_id = criteria_map.get(key)
                                    
                                    if not criteria_id:
                                        error_lines.append(f"Dòng {idx+2}: Không tìm thấy tiêu chí")
                                        continue
                                    
                                    # Get staff_id
                                    staff_name = ' '.join(str(row['Nhân sự']).split())
                                    staff_id = staff_map.get(staff_name)
                                    
                                    if not staff_id:
                                        error_lines.append(f"Dòng {idx+2}: Không tìm thấy nhân sự '{staff_name}'")
                                        continue
                                    
                                    # Parse result
                                    result_text = str(row['Kết quả']).strip().lower()
                                    is_pass = result_text in ['đạt', 'dat']
                                    
                                    # Get optional fields
                                    adjustment = row.get('Nội dung điều chỉnh', '')
                                    evidence_link = row.get('Link minh chứng', '')
                                    
                                    # Insert
                                    cur.execute("""
                                        INSERT INTO evaluation_details 
                                        (evaluation_id, criteria_id, staff_id, is_pass, adjustment_note, evidence_link)
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                    """, (
                                        eval_id,
                                        criteria_id,
                                        staff_id,
                                        is_pass,
                                        adjustment if pd.notna(adjustment) else None,
                                        evidence_link if pd.notna(evidence_link) else None
                                    ))
                                    
                                    success_count += 1
                                    
                                except Exception as e:
                                    error_lines.append(f"Dòng {idx+2}: {str(e)}")
                            
                            if error_lines:
                                st.warning(f"⚠️ Có {len(error_lines)} dòng lỗi:")
                                for err in error_lines[:10]:  # Show first 10 errors
                                    st.warning(f"- {err}")
                                if len(error_lines) > 10:
                                    st.warning(f"... và {len(error_lines) - 10} lỗi khác")
                            
                            if success_count > 0:
                                conn.commit()
                                st.success(f"✅ Import thành công {success_count}/{len(df_import)} dòng!")
                                st.success(f"📋 Đợt đánh giá ID: {eval_id}")
                                st.balloons()
                            else:
                                conn.rollback()
                                st.error("❌ Không có dòng nào được import!")
                            
                            cur.close()
                            conn.close()
                            
                        except Exception as e:
                            st.error(f"❌ Lỗi khi import: {e}")
                            import traceback
                            st.code(traceback.format_exc())
                
            except Exception as e:
                st.error(f"❌ Lỗi đọc file: {e}")
                import traceback
                st.code(traceback.format_exc())
