import io
import warnings
warnings.filterwarnings("ignore")
import unicodedata

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Phan tich KH - Hoa Sen",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.risk-high   {background:#4a1010;border-left:4px solid #e74c3c;padding:10px 14px;border-radius:6px;margin:6px 0;color:#fff;}
.risk-medium {background:#3d2e10;border-left:4px solid #f39c12;padding:10px 14px;border-radius:6px;margin:6px 0;color:#fff;}
.risk-low    {background:#0f3020;border-left:4px solid #26c281;padding:10px 14px;border-radius:6px;margin:6px 0;color:#fff;}
.section-title{font-size:16px;font-weight:700;color:#e0e0e0;margin:20px 0 10px 0;
               padding-bottom:6px;border-bottom:1px solid #2e3350;}
.info-box{background:#1a2035;border-radius:8px;padding:14px;margin:8px 0;color:#ccc;}
.kpi-card{background:#1a2035;border-radius:8px;padding:14px 16px;text-align:center;}
.kpi-val{font-size:22px;font-weight:800;color:#fff;}
.kpi-lab{font-size:11px;color:#9aa0b0;margin-top:4px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────────────────────

st.sidebar.markdown("## 📂 Upload dữ liệu")
uploaded_files = st.sidebar.file_uploader(
    "Upload file Excel báo cáo bán hàng",
    type=["xlsx"], accept_multiple_files=True
)

if not uploaded_files:
    st.markdown("## 👈 Upload file Excel để bắt đầu phân tích")
    st.stop()

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Đang xử lý dữ liệu…")
def load_all(file_data):
    frames = []
    for name, fb in file_data:
        try:
            df = pd.read_excel(io.BytesIO(fb), engine="openpyxl")
            df["Nguồn file"] = name
            frames.append(df)
        except Exception as e:
            st.warning(f"Lỗi đọc file {name}: {e}")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

file_data = [(uf.name, uf.read()) for uf in uploaded_files]
df_all = load_all(file_data)

if df_all.empty:
    st.error("Không có dữ liệu hợp lệ. Vui lòng kiểm tra file.")
    st.stop()

# Chuẩn hóa ngày
if "Ngày chứng từ" in df_all.columns:
    df_all["Ngày chứng từ"] = pd.to_datetime(df_all["Ngày chứng từ"], dayfirst=True, errors="coerce")
    df_all["Tháng"] = df_all["Ngày chứng từ"].dt.to_period("M").astype(str)
    df_all["Quý"] = df_all["Ngày chứng từ"].dt.to_period("Q").astype(str)

# ─────────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 Bộ lọc")

kh_list = sorted(df_all["Tên khách hàng"].dropna().astype(str).unique()) if "Tên khách hàng" in df_all.columns else []
kh = st.sidebar.selectbox("👤 Khách hàng", kh_list) if kh_list else None

quy_list = sorted(df_all["Quý"].dropna().unique()) if "Quý" in df_all.columns else []
quy_chon = st.sidebar.multiselect("📅 Quý", quy_list, default=quy_list) if quy_list else []

df = df_all.copy()
if kh:
    df = df[df["Tên khách hàng"] == kh]
if quy_chon:
    df = df[df["Quý"].isin(quy_chon)]

df_ban = df.copy()

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────

ngay_min = df["Ngày chứng từ"].min() if "Ngày chứng từ" in df.columns else None
ngay_max = df["Ngày chứng từ"].max() if "Ngày chứng từ" in df.columns else None
st.markdown(f"# 📊 Phân tích: **{kh}**")
st.markdown(f"*Dữ liệu: {ngay_min.strftime('%d/%m/%Y') if pd.notna(ngay_min) else '?'} → "
            f"{ngay_max.strftime('%d/%m/%Y') if pd.notna(ngay_max) else '?'} "
            f"| {len(df):,} dòng*")

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["📦 Sản phẩm", "📈 Doanh thu"])

# TAB 1
with tab1:
    if "Tên hàng" in df_ban.columns:
        df_nhom = (df_ban.groupby("Tên hàng")
                   .agg(SL=("Tên hàng", "count"),
                        DT=("Thành tiền bán", "sum"))
                   .reset_index().sort_values("DT", ascending=False))
        st.dataframe(df_nhom, use_container_width=True)

# TAB 2
with tab2:
    if "Tháng" in df_ban.columns:
        df_m = (df_ban.groupby("Tháng")
                .agg(DT=("Thành tiền bán", "sum"))
                .reset_index())
        fig = px.bar(df_m, x="Tháng", y="DT", text_auto=".3s", title="Doanh thu theo tháng")
        st.plotly_chart(fig, use_container_width=True)
