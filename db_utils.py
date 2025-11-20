import streamlit as st
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

# Lấy thông tin từ secrets của Streamlit
# Khi chạy local, cần file .streamlit/secrets.toml
# Khi deploy, cần cài đặt trong phần Settings của Streamlit Cloud
try:
    DB_CONFIG = st.secrets["postgres"]
except Exception:
    st.error("Không tìm thấy thông tin kết nối Database (secrets).")
    st.stop()

def get_connection():
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"]
    )

def get_engine():
    url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    return create_engine(url)

def run_query(query, params=None):
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Lỗi truy vấn: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def run_insert(query, params):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Lỗi ghi dữ liệu: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
