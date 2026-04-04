import io
import warnings
import unicodedata

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================

# TẮT CẢNH BÁO
warnings.filterwarnings("ignore")

# CẤU HÌNH ỨNG DỤNG
st.set_page_config(
    page_title="Phân tích KH - Hoa Sen",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# CSS TÙY CHỈNH
st.markdown(
    """
    <style>
        .risk-high {
            background: #4a1010;
            border-left: 4px solid #e74c3c;
            padding: 10px 14px;
            border-radius: 6px;
            margin: 6px 0;
            color: #fff;
        }
        .risk-low {
            background: #0f3020;
            border-left: 4px solid #26c281;
            padding: 10px 14px;
            border-radius: 6px;
            margin: 6px 0;
            color: #fff;
        }
        .section-title {
            font-size: 16px;
            font-weight: 700;
            color: #e0e0e0;
            margin: 20px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid #2e3350;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================

# TIỆN ÍCH

# ============================================================

def normalize_columns(df):
    """Chuẩn hóa tên cột trong DataFrame."""
    for col in df.columns:
        clean_col = unicodedata.normalize('NFKD', str(col).strip()).lower()
        clean_col = clean_col.replace(" ", "_").replace("\n", "").replace("\r", "")
        df.rename(columns={col: clean_col}, inplace=True)
    return df

@st.cache_data(show_spinner="Processing data...")
def load_data(file):
    """Tải file Excel và chuẩn hóa dữ liệu."""
    try:
        df = pd.read_excel(io.BytesIO(file), engine="openpyxl")
        df.dropna(how="all", axis=1, inplace=True)  # Bỏ cột toàn NaN
        df = normalize_columns(df)  # Chuẩn hóa tên cột
        return df
    except Exception as e:
        st.error(f"Không thể tải file. Chi tiết lỗi: {e}")
        return pd.DataFrame()

# ============================================================

# PHẦN TẢI DỮ LIỆU

# ============================================================

st.sidebar.markdown("## 📂 Tải file dữ liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel (.xlsx)", type=["xlsx"])

if not uploaded_file:
    st.markdown("### Vui lòng tải file dữ liệu để bắt đầu.")
    st.info("Ứng dụng hỗ trợ xử lý các file Excel (.xlsx)")
    st.stop()

# Tải dữ liệu
df = load_data(uploaded_file)

# Kiểm tra dữ liệu rỗng
if df.empty:
    st.error("Không có dữ liệu trong file vừa tải.")
    st.stop()

# ============================================================

# BỘ LỌC DỮ LIỆU

# ============================================================

st.sidebar.markdown("## 🔍 Bộ lọc dữ liệu")

# Kiểm tra và lọc các cột cần thiết
if "tên_khách_hàng" in df.columns:
    customers = sorted(df["tên_khách_hàng"].dropna().unique())
    selected_customers = st.sidebar.multiselect("Chọn khách hàng", customers, default=customers[:5])
else:
    st.error("Thiếu cột 'Tên Khách Hàng' trong dữ liệu.")
    st.stop()

# Lọc dữ liệu theo khách hàng
df_filtered = df[df["tên_khách_hàng"].isin(selected_customers)]

# ============================================================

# HIỂN THỊ DỮ LIỆU

# ============================================================

st.markdown("### 📊 Dữ liệu sau bộ lọc:")
st.dataframe(df_filtered.head(10))

# ============================================================

# BIỂU ĐỒ

# ============================================================

# Biểu đồ doanh thu theo tháng
if "ngày_chứng_từ" in df_filtered.columns:
    df_filtered["tháng"] = pd.to_datetime(df_filtered["ngày_chứng_từ"]).dt.to_period("M")
    revenue_by_month = df_filtered.groupby("tháng")["thành_tiền_bán"].sum().reset_index()
    fig_revenue = px.bar(
        revenue_by_month,
        x="tháng",
        y="thành_tiền_bán",
        title="Doanh thu theo tháng",
        labels={"tháng": "Tháng", "thành_tiền_bán": "Doanh Thu (VND)"}
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

# ============================================================