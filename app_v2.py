import io
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Phân tích KH - Hoa Sen",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
<style>
body { background-color: #0e1117; color: #c9d1d9; }
.sidebar .sidebar-content { background-color: #161b22; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────
st.sidebar.header("📂 Tải lên dữ liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel", type=["xlsx"])

if not uploaded_file:
    st.markdown("## 👈 Vui lòng tải lên file Excel để bắt đầu phân tích")
    st.stop()

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data(file):
    df = pd.read_excel(file, engine="openpyxl")
    df.columns = df.columns.str.strip()
    if "Ngày chứng từ" in df.columns:
        df["Ngày chứng từ"] = pd.to_datetime(df["Ngày chứng từ"], dayfirst=True, errors="coerce")
        df["Tháng"] = df["Ngày chứng từ"].dt.to_period("M").astype(str)
        df["Quý"] = df["Ngày chứng từ"].dt.to_period("Q").astype(str)
    return df

df = load_data(uploaded_file)

# ─────────────────────────────────────────────
# FILTERS
# ─────────────────────────────────────────────
st.sidebar.header("🔍 Bộ lọc")

kh_list = sorted(df["Tên khách hàng"].dropna().unique()) if "Tên khách hàng" in df.columns else []
kh = st.sidebar.selectbox("👤 Khách hàng", kh_list) if kh_list else None

quy_list = sorted(df["Quý"].dropna().unique()) if "Quý" in df.columns else []
quy_chon = st.sidebar.multiselect("📅 Quý", quy_list, default=quy_list) if quy_list else []

df_filtered = df.copy()
if kh:
    df_filtered = df_filtered[df_filtered["Tên khách hàng"] == kh]
if quy_chon:
    df_filtered = df_filtered[df_filtered["Quý"].isin(quy_chon)]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("📊 Phân tích dữ liệu bán hàng")
if kh:
    st.subheader(f"Khách hàng: {kh}")
if "Ngày chứng từ" in df_filtered.columns:
    dmin = df_filtered["Ngày chứng từ"].min()
    dmax = df_filtered["Ngày chứng từ"].max()
    st.markdown(f"**Khoảng thời gian:** {dmin.strftime('%d/%m/%Y')} → {dmax.strftime('%d/%m/%Y')}")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["📦 Sản phẩm", "📈 Doanh thu theo tháng"])

with tab1:
    if "Tên hàng" in df_filtered.columns and "Thành tiền bán" in df_filtered.columns:
        df_top = (df_filtered.groupby("Tên hàng")
                  .agg(Số_lần=("Tên hàng", "count"),
                       Doanh_thu=("Thành tiền bán", "sum"))
                  .reset_index().sort_values("Doanh_thu", ascending=False).head(15))
        st.markdown("### 🏆 Top 15 sản phẩm theo doanh thu")
        st.dataframe(df_top, use_container_width=True)
        fig = px.bar(df_top, x="Doanh_thu", y="Tên hàng", orientation="h", text="Số_lần",
                     labels={"Doanh_thu": "Doanh thu (VNĐ)", "Tên hàng": "Sản phẩm"})
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    if "Tháng" in df_filtered.columns and "Thành tiền bán" in df_filtered.columns:
        df_month = (df_filtered.groupby("Tháng")
                    .agg(Doanh_thu=("Thành tiền bán", "sum"))
                    .reset_index())
        st.markdown("### 📅 Doanh thu theo tháng")
        fig2 = px.line(df_month, x="Tháng", y="Doanh_thu", markers=True,
                       labels={"Doanh_thu": "Doanh thu (VNĐ)"})
        st.plotly_chart(fig2, use_container_width=True)
