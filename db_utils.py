import streamlit as st
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

# Lấy thông tin từ secrets của Streamlit
try:
    DB_CONFIG = st.secrets["postgres"]
except KeyError:
    st.error("❌ Không tìm thấy thông tin kết nối Database trong Secrets.")
    st.info("Vui lòng cấu hình Secrets với định dạng:\n\n[postgres]\nhost = \"...\"\ndbname = \"...\"\nuser = \"...\"\npassword = \"...\"\nport = \"5432\"")
    st.stop()
except Exception as e:
    st.error(f"❌ Lỗi đọc Secrets: {e}")
    st.stop()

def get_connection():
    """Tạo kết nối PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG.get("port", 5432),
            connect_timeout=10
        )
        return conn
    except psycopg2.OperationalError as e:
        st.error(f"❌ Lỗi kết nối Database: {str(e)}")
        st.info("Kiểm tra lại thông tin trong Secrets:\n- Host đúng?\n- User đúng?\n- Password đúng?\n- Port đúng?")
        st.stop()
    except Exception as e:
        st.error(f"❌ Lỗi không xác định: {str(e)}")
        st.stop()

def get_engine():
    """Tạo SQLAlchemy engine"""
    try:
        url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG.get('port', 5432)}/{DB_CONFIG['dbname']}"
        return create_engine(url)
    except Exception as e:
        st.error(f"❌ Lỗi tạo engine: {e}")
        st.stop()

def run_query(query, params=None):
    """Thực thi SELECT query và trả về DataFrame"""
    conn = None
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"❌ Lỗi truy vấn: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def run_insert(query, params):
    """Thực thi INSERT/UPDATE/DELETE query"""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"❌ Lỗi ghi dữ liệu: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
