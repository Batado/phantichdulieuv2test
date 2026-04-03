import io
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Ignore warnings
warnings.filterwarnings("ignore")

# Set page configuration
st.set_page_config(
    page_title="Phân Tích Dữ Liệu",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# CSS Style
CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800&display=swap");
html,body,[class*="css"]{font-family: "Be Vietnam Pro", sans-serif;}
section[data-testid="stSidebar"]{background: linear-gradient(180deg,#0d1117 0%,#161b22 100%); border-right: 1px solid #21262d;}
section[data-testid="stSidebar"] *{color: #c9d1d9 !important;}
.stApp{background: #0d1117;}
.kpi-card{background: linear-gradient(135deg,#161b22 0%,#1c2128 100%); border: 1px solid #21262d; border-radius: 10px; padding: 16px 20px;}
.kpi-val{font-size: 20px; font-weight: 800; color: #f0f6fc;}
.kpi-lab{font-size: 12px; margin-top: 4px; color: #6e7681;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Load Data Function
@st.cache_data(show_spinner="Đang tải dữ liệu...")
def load_excel_file(uploaded_file):
    try:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), engine="openpyxl")
    except Exception as e:
        st.error(f"Lỗi load file: {e}")
        return pd.DataFrame()

# KPI Card Function
def display_kpi(label, value):
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-val">{value}</div>
            <div class="kpi-lab">{label}</div>
        </div>
    """, unsafe_allow_html=True)

# Sidebar File Uploader
st.sidebar.markdown("## Tải Dữ Liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel của bạn", type=["xlsx"])

if uploaded_file is not None:
    # Load Data
    df = load_excel_file(uploaded_file)

    if df.empty:
        st.error("Không có dữ liệu hợp lệ. Vui lòng kiểm tra file của bạn.")
    else:
        # Summary KPIs
        st.markdown("<h1 style='text-align: center;'>📊 Tổng Quan</h1>", unsafe_allow_html=True)
        
        total_rows = df.shape[0]
        total_columns = df.shape[1]

        # Ensure example column names exist
        if "DoanhThu" in df.columns and "LoiNhuan" in df.columns:
            total_sales = df["DoanhThu"].sum()
            total_profit = df["LoiNhuan"].sum()
        else:
            total_sales = "Không tìm thấy 'DoanhThu'"
            total_profit = "Không tìm thấy 'LoiNhuan'"

        # Metrics display
        metrics = [
            {"label": "Tổng Số Dòng", "value": f"{total_rows:,}"},
            {"label": "Tổng Số Cột", "value": f"{total_columns:,}"},
            {"label": "Tổng Doanh Thu", "value": f"{total_sales:,} VND"},
            {"label": "Tổng Lợi Nhuận", "value": f"{total_profit:,} VND"}
        ]

        # Display KPIs
        cols = st.columns(len(metrics))
        for col, metric in zip(cols, metrics):
            with col:
                display_kpi(metric["label"], metric["value"])

        # Data Display
        st.markdown("<h2>Dữ Liệu Chi Tiết</h2>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

        # Visualization Example (Plotly)
        if "DoanhThu" in df.columns and "LoiNhuan" in df.columns:
            st.markdown("<h2>💹 Phân Tích Doanh Thu & Lợi Nhuận</h2>", unsafe_allow_html=True)
            fig = px.scatter(df, x="DoanhThu", y="LoiNhuan", title="Doanh Thu vs Lợi Nhuận", color_discrete_sequence=["#388bfd"])
            st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown('<div style="text-align: center;"><h1>📊 Phân Tích Dữ Liệu</h1></div>', unsafe_allow_html=True)
    st.info("Vui lòng tải file Excel của bạn để bắt đầu phân tích.")
    st.stop()