import streamlit as st
import pandas as pd
from datetime import date
from db_utils import run_query, get_connection

st.set_page_config(page_title="Đánh giá 5S", page_icon="📝", layout="wide")

st.title("📝 CHECKLIST ĐÁNH GIÁ 5S")

# Chọn Khoa/Phòng
st.write("### Chọn Khoa/Phòng")
df_depts = run_query("SELECT id, unit_code, unit_name FROM departments ORDER BY unit_code")

if df_depts.empty:
    st.warning("⚠️ Chưa có Khoa/Phòng. Vui lòng thêm ở trang 'Quan Ly Don Vi'")
    st.stop()

dept_options = {f"{row['unit_name']}": row['id'] for _, row in df_depts.iterrows()}
selected_dept_name = st.selectbox("Chọn Khoa/Phòng", options=list(dept_options.keys()))
selected_dept_id = dept_options[selected_dept_name]

# Ngày đánh giá
st.write("### Ngày đánh giá")
eval_date = st.date_input("Ngày đánh giá", value=date.today())

st.divider()

# Lấy tiêu chí theo khu vực đã gán
df_criteria = run_query("""
    SELECT 
        c.id,
        a.area_code,
        a.area_name,
        c.location_name,
        c.category,
        c.requirement,
        a.definition as area_definition
    FROM criteria c
    JOIN areas a ON c.area_id = a.id
    JOIN department_areas da ON a.id = da.area_id
    WHERE da.department_id = %s
    ORDER BY a.area_code, c.location_name, c.category
""", params=(selected_dept_id,))

if df_criteria.empty:
    st.warning(f"⚠️ **{selected_dept_name}** chưa có cấu hình khu vực!")
    st.info("💡 Vui lòng vào **'Cau Hinh Khu Vuc'** → Tab **'Gán Khu vực cho Khoa/Phòng'** để cấu hình.")
    st.stop()

# Lấy nhân sự
df_staff = run_query(
    "SELECT id, name, staff_code FROM staff WHERE department_id = %s ORDER BY name",
    params=(selected_dept_id,)
)

if df_staff.empty:
    st.warning("⚠️ Chưa có nhân sự. Vui lòng thêm ở 'Quan Ly Don Vi'")
    st.stop()

# Tạo 2 dictionaries cho staff mapping
staff_display_to_id = {}
staff_id_to_display = {}

for _, row in df_staff.iterrows():
    display_name = f"{row['name']} ({row['staff_code']})"
    staff_display_to_id[display_name] = row['id']
    staff_id_to_display[row['id']] = display_name

staff_options_list = list(staff_display_to_id.keys())

# Hiển thị thông tin
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.info(f"**Khoa/Phòng:** {selected_dept_name}")
    st.info(f"**Ngày đánh giá:** {eval_date}")

with col_info2:
    st.info(f"**Số tiêu chí:** {len(df_criteria)}")
    st.info(f"**Số nhân sự:** {len(df_staff)}")

st.divider()

# Chuẩn bị dataframe
df_display = df_criteria.copy()

# Thêm cột "Định nghĩa" từ area_definition (định nghĩa khu vực)
df_display['Định nghĩa'] = df_display['area_definition'].fillna('')

# Thêm các cột mặc định
df_display['Số lượng'] = 1
df_display['Đạt'] = True
df_display['Nhân sự phụ trách'] = staff_options_list[0] if staff_options_list else ""

# Thêm 2 cột mới
df_display['Nội dung điều chỉnh'] = ""
df_display['Link minh chứng'] = ""

# Hiển thị bảng có thể edit
st.write("### Checklist đánh giá")

edited_df = st.data_editor(
    df_display,
    column_config={
        "id": None,
        "requirement": None,  # Ẩn requirement
        "area_definition": None,  # Ẩn area_definition
        "area_code": st.column_config.TextColumn("Mã KV", disabled=True, width="small"),
        "area_name": st.column_config.TextColumn("Khu vực", disabled=True, width="medium"),
        "location_name": st.column_config.TextColumn("Vị trí", disabled=True, width="medium"),
        "category": st.column_config.TextColumn("Hạng mục", disabled=True, width="large"),
        "Định nghĩa": st.column_config.TextColumn(
            "Định nghĩa", 
            help="Vị trí thực tế trong bệnh viện",
            disabled=True, 
            width="large"
        ),
        "Số lượng": st.column_config.NumberColumn(
            "Số lượng",
            min_value=0,
            max_value=100,
            step=1,
            width="small"
        ),
        "Đạt": st.column_config.CheckboxColumn("Đạt", default=True, width="small"),
        "Nhân sự phụ trách": st.column_config.SelectboxColumn(
            "Nhân sự phụ trách",
            options=staff_options_list,
            width="medium"
        ),
        "Nội dung điều chỉnh": st.column_config.TextColumn(
            "Nội dung điều chỉnh",
            help="Ghi chú định tính của người kiểm tra",
            width="large",
            max_chars=500
        ),
        "Link minh chứng": st.column_config.LinkColumn(
            "Link minh chứng",
            help="URL tài liệu tham khảo",
            width="medium",
            max_chars=200
        )
    },
    hide_index=True,
    use_container_width=True,
    height=600  # Tăng chiều cao để hiển thị nhiều hàng hơn
)

# Nút Lưu
if st.button("💾 Lưu Kết Quả", type="primary", use_container_width=True):
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Tạo evaluation
        cur.execute(
            "INSERT INTO evaluations (department_id, eval_date) VALUES (%s, %s) RETURNING id",
            (selected_dept_id, eval_date)
        )
        eval_id = cur.fetchone()[0]
        
        # Lưu details với error handling
        errors = []
        success_count = 0
        
        for idx, row in edited_df.iterrows():
            try:
                criteria_id = row['id']
                quantity = row['Số lượng']
                is_pass = row['Đạt']
                staff_display_name = row['Nhân sự phụ trách']
                adjustment_note = row['Nội dung điều chỉnh'] if row['Nội dung điều chỉnh'] else None
                evidence_link = row['Link minh chứng'] if row['Link minh chứng'] else None
                
                # Tìm staff_id từ display name với fallback
                if staff_display_name in staff_display_to_id:
                    staff_id = staff_display_to_id[staff_display_name]
                else:
                    # Fallback: tìm theo tên không có mã
                    staff_name_only = staff_display_name.split('(')[0].strip() if '(' in staff_display_name else staff_display_name
                    matching_staff = df_staff[df_staff['name'] == staff_name_only]
                    
                    if not matching_staff.empty:
                        staff_id = matching_staff.iloc[0]['id']
                    else:
                        errors.append(f"Dòng {idx+1}: Không tìm thấy nhân sự '{staff_display_name}'")
                        continue
                
                cur.execute(
                    """
                    INSERT INTO evaluation_details 
                    (evaluation_id, criteria_id, quantity, is_pass, staff_id, adjustment_note, evidence_link)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (eval_id, criteria_id, quantity, is_pass, staff_id, adjustment_note, evidence_link)
                )
                success_count += 1
                
            except Exception as e:
                errors.append(f"Dòng {idx+1}: {str(e)}")
        
        if errors:
            conn.rollback()
            st.error("❌ Lỗi khi lưu:")
            for error in errors:
                st.error(f"- {error}")
        else:
            conn.commit()
            st.success(f"✅ Đã lưu {success_count} tiêu chí cho **{selected_dept_name}** ngày **{eval_date}**")
            st.balloons()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        st.error(f"❌ Lỗi hệ thống: {e}")

# Thống kê
st.divider()
st.write("### 📊 Thống kê nhanh")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total = len(edited_df)
    st.metric("Tổng số tiêu chí", total)

with col2:
    passed = edited_df['Đạt'].sum()
    st.metric("Đạt", passed, delta=f"{passed/total*100:.1f}%")

with col3:
    failed = total - passed
    st.metric("Không Đạt", failed, delta=f"{failed/total*100:.1f}%", delta_color="inverse")

with col4:
    has_notes = len(edited_df[edited_df['Nội dung điều chỉnh'] != ""])
    st.metric("Có ghi chú", has_notes)

# Tiêu chí không đạt
if failed > 0:
    st.write("### ⚠️ Danh sách KHÔNG ĐẠT")
    df_failed = edited_df[edited_df['Đạt'] == False][
        ['area_name', 'location_name', 'category', 'Nhân sự phụ trách', 'Nội dung điều chỉnh', 'Link minh chứng']
    ]
    st.dataframe(df_failed, use_container_width=True, hide_index=True)

# Tiêu chí có nội dung điều chỉnh
has_adjustment = edited_df[edited_df['Nội dung điều chỉnh'] != ""]
if len(has_adjustment) > 0:
    st.write("### 📝 Danh sách có Nội dung điều chỉnh")
    df_adjustment = has_adjustment[
        ['area_name', 'location_name', 'category', 'Nhân sự phụ trách', 'Nội dung điều chỉnh', 'Link minh chứng']
    ]
    st.dataframe(df_adjustment, use_container_width=True, hide_index=True)

# Lịch sử
st.divider()
st.write("### 📋 Lịch sử đánh giá")

df_history = run_query("""
    SELECT 
        e.eval_date,
        d.unit_name,
        COUNT(ed.id) as tong_so,
        SUM(CASE WHEN ed.is_pass THEN 1 ELSE 0 END) as so_dat,
        ROUND(AVG(CASE WHEN ed.is_pass THEN 100.0 ELSE 0.0 END), 1) as ty_le_dat,
        COUNT(CASE WHEN ed.adjustment_note IS NOT NULL AND ed.adjustment_note != '' THEN 1 END) as co_ghi_chu
    FROM evaluations e
    JOIN departments d ON e.department_id = d.id
    JOIN evaluation_details ed ON e.id = ed.evaluation_id
    WHERE e.department_id = %s
    GROUP BY e.id, e.eval_date, d.unit_name
    ORDER BY e.eval_date DESC
    LIMIT 10
""", params=(selected_dept_id,))

if not df_history.empty:
    st.dataframe(
        df_history,
        column_config={
            "eval_date": "Ngày",
            "unit_name": "Khoa/Phòng",
            "tong_so": "Tổng",
            "so_dat": "Đạt",
            "ty_le_dat": st.column_config.ProgressColumn(
                "Tỷ lệ (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "co_ghi_chu": "Có ghi chú"
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Chưa có lịch sử.")
