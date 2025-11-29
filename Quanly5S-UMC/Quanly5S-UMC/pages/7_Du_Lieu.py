import streamlit as st
import pandas as pd
import io
from db_utils import run_query, run_insert

st.set_page_config(page_title="Dữ Liệu", page_icon="💾", layout="wide")
st.title("💾 IMPORT / EXPORT")

tab1, tab2 = st.tabs(["Export", "Import"])

with tab1:
    if st.button("Xuất Excel Danh sách Nhân sự"):
        df = run_query("SELECT d.unit_name, s.name, s.staff_code FROM staff s JOIN departments d ON s.department_id=d.id")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("Tải file", buffer, "NhanSu.xlsx")

with tab2:
    st.info("Import nhân sự từ Excel")
    up_file = st.file_uploader("File Excel", type=['xlsx'])
    if up_file and st.button("Import ngay"):
        try:
            df = pd.read_excel(up_file)
            # Giả định file có cột: Ma_Khoa, Ten_NV, Ma_NV, Email, Role
            depts = run_query("SELECT id, unit_code FROM departments")
            d_map = {r['unit_code']: r['id'] for i, r in depts.iterrows()}
            
            count = 0
            for i, r in df.iterrows():
                d_id = d_map.get(str(r['Ma_Khoa_Phong']).strip())
                if d_id:
                    run_insert("INSERT INTO staff (department_id, name, staff_code, email, role) VALUES (%s,%s,%s,%s,%s)",
                               (d_id, r['Ten_Nhan_Vien'], r['Ma_Nhan_Vien'], r['Email'], r['Chuc_Vu']))
                    count += 1
            st.success(f"Import thành công {count} dòng.")
        except Exception as e:
            st.error(f"Lỗi: {e}")
