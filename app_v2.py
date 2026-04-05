import io
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')
import unicodedata
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ───────────────────────────────────────────────────────
# Cấu hình trang Streamlit
# ───────────────────────────────────────────────────────
st.set_page_config(page_title='Phân tích KH - Hoa Sen', layout='wide', page_icon="📊")

# Thay đổi định dạng CSS
st.markdown('''
<style>
.risk-high { background:#4a1010; border-left:4px solid #e74c3c; padding:10px 14px; border-radius:6px; color:#fff; }
.risk-medium { background:#3d2e10; border-left:4px solid #f39c12; padding:10px 14px; border-radius:6px; color:#fff; }
.risk-low { background:#0f3020; border-left:4px solid #26c281; padding:10px 14px; border-radius:6px; color:#fff; }
.section-title { font-size:17px; font-weight:700; color:#e0e0e0; margin:20px 0 10px 0; border-bottom:1px solid #2e3350; padding-bottom:6px; }
.info-box { background:#1a2035; border-radius:8px; padding:14px; margin:8px 0; color:#ccc; }
</style>
''', unsafe_allow_html=True)

# ───────────────────────────────────────────────────────
# Utility functions
# ───────────────────────────────────────────────────────

def normalize_text(s):
    """Chuẩn hóa unicode và xóa dấu tiếng Việt"""
    s = unicodedata.normalize('NFD', str(s))
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower().strip()

def find_header_row(file_bytes):
    """Hàm để xác định header hàng trên file Excel"""
    try:
        df_raw = pd.read_excel(io.BytesIO(file_bytes), header=None, engine='openpyxl')
    except Exception:
        return 0

    keywords = ['số chứng từ', 'ngày chứng từ', 'tên khách hàng', 'tên hàng', 'thành tiền bán', 'khu vực', 'nhóm KH']
    for i in range(df_raw.shape[0]):
        row_text = ' '.join([str(val).strip().lower() for val in df_raw.iloc[i] if pd.notna(val)])
        matches = [kw for kw in keywords if kw in row_text]
        if len(matches) >= 3:
            return i
    return 0

def rename_columns(df, alias_map):
    """Đổi tên các cột trong DataFrame dựa vào alias_map"""
    col_map = {normalize_text(col): col for col in df.columns}
    rename_map = {}
    for target, aliases in alias_map.items():
        for alias in aliases:
            alias_normalized = normalize_text(alias)
            if alias_normalized in col_map:
                rename_map[col_map[alias_normalized]] = target
                break
    df.rename(columns=rename_map, inplace=True)

def process_numeric(df, columns):
    """Chuyển các cột sang dạng số, điền giá trị NaN bằng 0"""
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# ───────────────────────────────────────────────────────
# Phần chính: Xử lý file Excel và phân tích dữ liệu
# ───────────────────────────────────────────────────────

@st.cache_data(show_spinner="🔄 Đang xử lý dữ liệu...")
def load_and_process_data(uploaded_files):
    """Load và xử lý dữ liệu từ các file Excel"""
    data_frames = []
    alias_map = {
        "Tên khách hàng": ["ten khach hang", "khach hang", "customer_name"],
        "Ngày chứng từ": ["ngay chung tu", "date"],
        "Số chứng từ": ["so chung tu", "voucher_no"],
        "Tên hàng": ["ten hang", "product_name"],
        "Thành tiền bán": ["thanh tien ban", "doanh thu", "revenue"],
        "Thành tiền vốn": ["thanh tien von", "cost"],
        "Lợi nhuận": ["loi nhuan", "profit"],
        "Khu vực": ["khu vuc", "region"],
        "Nhóm KH": ["ten nhom kh", "nhom kh"],
    }

    for file_name, file_bytes in uploded_files:
        try:
            header_index = find_header_row(file_bytes)
            df = pd.read_excel(io.BytesIO(file_bytes), header=header_index, engine='openpyxl')

            # Chuẩn hóa tên các cột
            rename_columns(df, alias_map)

            # Xử lý các cột số
            numeric_columns = ["Thành tiền bán", "Thành tiền vốn", "Lợi nhuận", "Khối lượng"]
            process_numeric(df, numeric_columns)

            # Thêm dữ liệu processed vào danh sách
            data_frames.append(df)
        except Exception as e:
            st.warning(f"Lỗi xử lý file {file_name}: {e}")

    # Gộp tất cả các file lại thành 1 DataFrame
    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()

# ───────────────────────────────────────────────────────
# Giao diện và hiển thị các tab
# ───────────────────────────────────────────────────────

# Upload files
st.sidebar.markdown("### 📂 Upload dữ liệu")
uploaded_files = st.sidebar.file_uploader("Tải file Excel báo cáo", type=["xlsx"], accept_multiple_files=True)

if not uploaded_files:
    st.info("Hãy tải file Excel để bắt đầu phân tích! Hỗ trợ định dạng báo cáo OM_RPT_055.")
    st.stop()

# Load và xử lý dữ liệu
uploaded_file_data = [(file.name, file.read()) for file in uploaded_files]
data = load_and_process_data(uploaded_file_data)

if data.empty:
    st.error("Dữ liệu đầu vào trống hoặc không hợp lệ. Hãy kiểm tra file Excel.")
    st.stop()

# Hiển thị dữ liệu tổng quan
st.markdown("### 📝 Tổng quan dữ liệu")
st.dataframe(data.head(), use_container_width=True)

# Tabs
tabs = st.tabs(["📊 Phân tích chung", "📈 Doanh thu & Lợi nhuận", "⚠️ Rủi ro khách hàng"])

# 1. Phân tích chung
with tabs[0]:
    st.markdown("### 📊 Phân tích chung")
    # Hiển thị các thông số cơ bản
    unique_customers = data["Tên khách hàng"].nunique()
    total_revenue = data["Thành tiền bán"].sum()
    total_profit = data["Lợi nhuận"].sum()

    st.write(f"**Số lượng khách hàng:** {unique_customers}")
    st.write(f"**Tổng doanh thu:** {total_revenue:,.0f} VNĐ")
    st.write(f"**Tổng lợi nhuận:** {total_profit:,.0f} VNĐ")

# 2. Doanh thu & Lợi nhuận
with tabs[1]:
    st.markdown("### 📈 Phân tích doanh thu và lợi nhuận")
    if "Tháng" in data.columns:
        chart_data = data.groupby("Tháng").agg({"Thành tiền bán": "sum", "Lợi nhuận": "sum"}).reset_index()
        fig = px.bar(chart_data, x="Tháng", y=["Thành tiền bán", "Lợi nhuận"],
                     barmode="group", title="Biến động doanh thu và lợi nhuận theo tháng")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Không tìm thấy dữ liệu tháng trong tệp đã tải.")

# 3. Rủi ro
with tabs[2]:
    st.markdown("### ⚠️ Phân tích rủi ro khách hàng")
    risk_analysis = data.groupby("Tên khách hàng").agg({
        "Thành tiền bán": "sum",
        "Lợi nhuận": "sum"
    })
    risk_analysis["Tỷ lệ lợi nhuận (%)"] = (risk_analysis["Lợi nhuận"] / risk_analysis["Thành tiền bán"] * 100).round(2)
    st.dataframe(risk_analysis, use_container_width=True)