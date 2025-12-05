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
    st.warning("⚠️ Chưa có Khoa/Phòng nào. Vui lòng thêm ở trang 'Quản Ly Don Vi'")
    st.stop()

dept_options = {f"{row['unit_name']}": row['id'] for _, row in df_depts.iterrows()}
selected_dept_name = st.selectbox("Chọn Khoa/Phòng", options=list(dept_options.keys()))
selected_dept_id = dept_options[selected_dept_name]

# Ngày đánh giá
st.write("### Ngày đánh giá")
eval_date = st.date_input("Ngày đánh giá", value=date.today())

# Lấy danh sách tiêu chí từ tất cả khu vực
df_criteria = run_query("""
    SELECT 
        c.id,
        a.area_code,
        a.area_name,
        c.location_name,
        c.category,
        c.requirement
    FROM criteria c
    JOIN areas a ON c.area_id = a.id
    ORDER BY a.area_code, c.location_name, c.category
""")

if df_criteria.empty:
    st.warning("⚠️ Chưa có tiêu chí đánh giá. Vui lòng thêm ở trang 'Cau Hinh Khu Vuc'")
    st.stop()

# Lấy danh sách nhân sự
df_staff = run_query(
    "SELECT id, name, staff_code FROM staff WHERE department_id = %s ORDER BY name",
    params=(selected_dept_id,)
)

if df_staff.empty:
    st.warning("⚠️ Chưa có nhân sự trong đơn vị này. Vui lòng thêm nhân sự ở trang 'Quan Ly Don Vi'")
    st.stop()

staff_options = {f"{row['name']} ({row['staff_code']})": row['id'] for _, row in df_staff.iterrows()}

# Chuẩn bị dataframe để hiển thị
df_display = df_criteria.copy()
df_display['Số lượng'] = 1
df_display['Đạt'] = True
df_display['Nhân sự phụ trách'] = list(staff_options.keys())[0]  # Default first staff

# Hiển thị bảng có thể edit
st.write("### Checklist đánh giá")

edited_df = st.data_editor(
    df_display,
    column_config={
        "id": None,  # Ẩn cột id
        "area_code": st.column_config.TextColumn("Mã KV", disabled=True, width="small"),
        "area_name": st.column_config.TextColumn("Khu vực", disabled=True, width="medium"),
        "location_name": st.column_config.TextColumn("Vị trí", disabled=True, width="medium"),
        "category": st.column_config.TextColumn("Hạng mục", disabled=True, width="large"),
        "requirement": None,  # Ẩn requirement để gọn
        "Số lượng": st.column_config.NumberColumn(
            "Số lượng",
            min_value=0,
            max_value=100,
            step=1,
            width="small"
        ),
        "Đạt": st.column_config.CheckboxColumn(
            "Đạt",
            default=True,
            width="small"
        ),
        "Nhân sự phụ trách": st.column_config.SelectboxColumn(
            "Nhân sự phụ trách",
            options=list(staff_options.keys()),
            width="medium"
        )
    },
    hide_index=True,
    use_container_width=True
)

# Nút Lưu
if st.button("💾 Lưu Kết Quả", type="primary", use_container_width=True):
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Tạo evaluation record
        cur.execute(
            "INSERT INTO evaluations (department_id, eval_date) VALUES (%s, %s) RETURNING id",
            (selected_dept_id, eval_date)
        )
        eval_id = cur.fetchone()[0]
        
        # Lưu từng chi tiết
        for idx, row in edited_df.iterrows():
            criteria_id = row['id']
            quantity = row['Số lượng']
            is_pass = row['Đạt']
            staff_name = row['Nhân sự phụ trách']
            staff_id = staff_options[staff_name]
            
            cur.execute(
                """
                INSERT INTO evaluation_details 
                (evaluation_id, criteria_id, quantity, is_pass, staff_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (eval_id, criteria_id, quantity, is_pass, staff_id)
            )
        
        conn.commit()
        cur.close()
        conn.close()
        
        st.success(f"✅ Đã lưu kết quả đánh giá cho {selected_dept_name} ngày {eval_date}")
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ Lỗi khi lưu: {e}")

# Thống kê nhanh
st.divider()
st.write("### 📊 Thống kê nhanh")

col1, col2, col3 = st.columns(3)

with col1:
    total = len(edited_df)
    st.metric("Tổng số tiêu chí", total)

with col2:
    passed = edited_df['Đạt'].sum()
    st.metric("Số tiêu chí Đạt", passed, delta=f"{passed/total*100:.1f}%")

with col3:
    failed = total - passed
    st.metric("Số tiêu chí Không Đạt", failed, delta=f"{failed/total*100:.1f}%", delta_color="inverse")

# Hiển thị các tiêu chí không đạt
if failed > 0:
    st.write("### ⚠️ Danh sách tiêu chí KHÔNG ĐẠT")
    df_failed = edited_df[edited_df['Đạt'] == False][['area_name', 'location_name', 'category', 'Nhân sự phụ trách']]
    st.dataframe(df_failed, use_container_width=True, hide_index=True)

# Xem lịch sử đánh giá
st.divider()
st.write("### 📋 Lịch sử đánh giá gần đây")

df_history = run_query("""
    SELECT 
        e.eval_date,
        d.unit_name,
        COUNT(ed.id) as tong_so,
        SUM(CASE WHEN ed.is_pass THEN 1 ELSE 0 END) as so_dat,
        ROUND(AVG(CASE WHEN ed.is_pass THEN 100.0 ELSE 0.0 END), 1) as ty_le_dat
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
            "eval_date": "Ngày đánh giá",
            "unit_name": "Khoa/Phòng",
            "tong_so": "Tổng số tiêu chí",
            "so_dat": "Số đạt",
            "ty_le_dat": st.column_config.ProgressColumn(
                "Tỷ lệ đạt (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100
            )
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Chưa có lịch sử đánh giá cho đơn vị này.")
