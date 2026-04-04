import io
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
.section-title { font-size:18px; font-weight:700; color:#f0f6fc; margin:20px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────
st.sidebar.header("📂 Tải lên dữ liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel báo cáo bán hàng", type=["xlsx"])

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

pkd_list = sorted(df["Tên nhóm KH"].dropna().unique()) if "Tên nhóm KH" in df.columns else []
pkd = st.sidebar.multiselect("🏢 Phòng KD", pkd_list, default=pkd_list)

kv_list = sorted(df["Khu vực"].dropna().unique()) if "Khu vực" in df.columns else []
kv = st.sidebar.multiselect("🌍 Khu vực", kv_list, default=kv_list)

kh_list = sorted(df["Tên khách hàng"].dropna().unique()) if "Tên khách hàng" in df.columns else []
kh = st.sidebar.selectbox("👤 Khách hàng", kh_list) if kh_list else None

quy_list = sorted(df["Quý"].dropna().unique()) if "Quý" in df.columns else []
quy = st.sidebar.multiselect("📅 Quý", quy_list, default=quy_list)

df_filtered = df.copy()
if pkd: df_filtered = df_filtered[df_filtered["Tên nhóm KH"].isin(pkd)]
if kv: df_filtered = df_filtered[df_filtered["Khu vực"].isin(kv)]
if kh: df_filtered = df_filtered[df_filtered["Tên khách hàng"] == kh]
if quy: df_filtered = df_filtered[df_filtered["Quý"].isin(quy)]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("📊 Phân tích dữ liệu bán hàng")
if kh: st.subheader(f"Khách hàng: {kh}")

if "Ngày chứng từ" in df_filtered.columns:
    dmin = df_filtered["Ngày chứng từ"].min()
    dmax = df_filtered["Ngày chứng từ"].max()
    st.markdown(f"**Khoảng thời gian:** {dmin.strftime('%d/%m/%Y')} → {dmax.strftime('%d/%m/%Y')}")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📦 Thói quen mua hàng",
    "📈 Doanh thu & Khối lượng",
    "💹 Lợi nhuận & Chính sách",
    "🚚 Giao hàng",
    "📄 BCCN & Rủi ro",
    "🌍 Thị phần KH",
    "🏆 Top KH theo Phòng KD"
])

# TAB 1 – Thói quen mua hàng
with tab1:
    st.markdown('<div class="section-title">📦 Thói quen mua hàng theo sản phẩm</div>', unsafe_allow_html=True)
    if "Tên hàng" in df_filtered.columns:
        df_nhom = (df_filtered.groupby("Tên hàng")
                   .agg(Số_lần=("Tên hàng","count"),
                        Doanh_thu=("Thành tiền bán","sum"))
                   .reset_index().sort_values("Doanh_thu", ascending=False))
        st.dataframe(df_nhom, use_container_width=True)

# TAB 2 – Doanh thu & Khối lượng
with tab2:
    st.markdown('<div class="section-title">📈 Doanh thu & Khối lượng theo tháng</div>', unsafe_allow_html=True)
    if "Tháng" in df_filtered.columns:
        df_m = (df_filtered.groupby("Tháng")
                .agg(Doanh_thu=("Thành tiền bán","sum"),
                     Khối_lượng=("Khối lượng","sum"))
                .reset_index())
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=("Doanh thu (VNĐ)", "Khối lượng (tấn)"))
        fig.add_trace(go.Bar(x=df_m["Tháng"], y=df_m["Doanh_thu"], name="Doanh thu"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_m["Tháng"], y=df_m["Khối_lượng"]/1000, name="Khối lượng (tấn)",
                                 mode="lines+markers"), row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)

# TAB 3 – Lợi nhuận & Chính sách
with tab3:
    st.markdown('<div class="section-title">💹 Lợi nhuận & Chính sách</div>', unsafe_allow_html=True)
    if "Tháng" in df_filtered.columns:
        df_ln = (df_filtered.groupby("Tháng")
                 .agg(Doanh_thu=("Thành tiền bán","sum"),
                      Lợi_nhuận=("Lợi nhuận","sum"))
                 .reset_index())
        df_ln["Biên (%)"] = (df_ln["Lợi_nhuận"]/df_ln["Doanh_thu"].replace(0,float("nan"))*100).round(1)
        fig2 = px.line(df_ln, x="Tháng", y="Biên (%)", markers=True, title="Biên lợi nhuận theo tháng")
        st.plotly_chart(fig2, use_container_width=True)

# TAB 4 – Giao hàng
with tab4:
    st.markdown('<div class="section-title">🚚 Hình thức & địa điểm giao hàng</div>', unsafe_allow_html=True)
    if "Nơi giao hàng" in df_filtered.columns:
        df_noi = df_filtered["Nơi giao hàng"].value_counts().reset_index()
        df_noi.columns = ["Địa điểm","Số lần"]
        st.dataframe(df_noi, use_container_width=True)

# TAB 5 – BCCN & Rủi ro
with tab5:
    st.markdown('<div class="section-title">📄 BCCN & Rủi ro</div>', unsafe_allow_html=True)
    if "Ghi chú" in df_filtered.columns:
        tra_hang = df_filtered[df_filtered["Ghi chú"].str.contains("Trả hàng", na=False)]
        st.metric("↩️ Phiếu trả hàng", len(tra_hang))
        st.metric("💰 Giá trị trả hàng", f"{abs(tra_hang['Thành tiền bán'].sum()):,.0f}")

# TAB 6 – Thị phần KH
with tab6:
    st.markdown('<div class="section-title">🌍 Thị phần KH theo khu vực</div>', unsafe_allow_html=True)
    if "Khu vực" in df.columns and "Tên khách hàng" in df.columns:
        df_region = (df.groupby(["Khu vực","Tên khách hàng"])
                     .agg(Doanh_thu=("Thành tiền bán","sum"))
                     .reset_index())
        df_region["Thị phần (%)"] = df_region.groupby("Khu vực")["Doanh_thu"].apply(lambda x: x/x.sum()*100)
        df_region["Rank"] = df_region.groupby("Khu vực")["Doanh_thu"].rank(method="dense", ascending=False)
        st.dataframe(df_region, use_container_width=True)

# TAB 7 – Top KH theo Phòng KD
with tab7:
    st.markdown('<div class="section-title">🏆 Top KH theo Phòng KD</div>', unsafe_allow_html=True)
   Đạt ơi, lỗi line 163 là do đoạn code bị viết dở dang, thiếu đóng ngoặc và thiếu phần hiển thị bảng/thị phần. Tôi đã viết lại toàn bộ file `app.py` hoàn chỉnh, sạch cú pháp, để bạn có thể copy lên GitHub và chạy ngay trên Streamlit Cloud.  

---

### 📦 Code hoàn chỉnh

```python
import io
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
.section-title { font-size:18px; font-weight:700; color:#f0f6fc; margin:20px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────
st.sidebar.header("📂 Tải lên dữ liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel báo cáo bán hàng", type=["xlsx"])

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

pkd_list = sorted(df["Tên nhóm KH"].dropna().unique()) if "Tên nhóm KH" in df.columns else []
pkd = st.sidebar.multiselect("🏢 Phòng KD", pkd_list, default=pkd_list)

kv_list = sorted(df["Khu vực"].dropna().unique()) if "Khu vực" in df.columns else []
kv = st.sidebar.multiselect("🌍 Khu vực", kv_list, default=kv_list)

kh_list = sorted(df["Tên khách hàng"].dropna().unique()) if "Tên khách hàng" in df.columns else []
kh = st.sidebar.selectbox("👤 Khách hàng", kh_list) if kh_list else None

quy_list = sorted(df["Quý"].dropna().unique()) if "Quý" in df.columns else []
quy = st.sidebar.multiselect("📅 Quý", quy_list, default=quy_list)

df_filtered = df.copy()
if pkd: df_filtered = df_filtered[df_filtered["Tên nhóm KH"].isin(pkd)]
if kv: df_filtered = df_filtered[df_filtered["Khu vực"].isin(kv)]
if kh: df_filtered = df_filtered[df_filtered["Tên khách hàng"] == kh]
if quy: df_filtered = df_filtered[df_filtered["Quý"].isin(quy)]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("📊 Phân tích dữ liệu bán hàng")
if kh: st.subheader(f"Khách hàng: {kh}")

if "Ngày chứng từ" in df_filtered.columns:
    dmin = df_filtered["Ngày chứng từ"].min()
    dmax = df_filtered["Ngày chứng từ"].max()
    st.markdown(f"**Khoảng thời gian:** {dmin.strftime('%d/%m/%Y')} → {dmax.strftime('%d/%m/%Y')}")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📦 Thói quen mua hàng",
    "📈 Doanh thu & Khối lượng",
    "💹 Lợi nhuận & Chính sách",
    "🚚 Giao hàng",
    "📄 BCCN & Rủi ro",
    "🌍 Thị phần KH",
    "🏆 Top KH theo Phòng KD"
])

# TAB 1 – Thói quen mua hàng
with tab1:
    st.markdown('<div class="section-title">📦 Thói quen mua hàng theo sản phẩm</div>', unsafe_allow_html=True)
    if "Tên hàng" in df_filtered.columns:
        df_nhom = (df_filtered.groupby("Tên hàng")
                   .agg(Số_lần=("Tên hàng","count"),
                        Doanh_thu=("Thành tiền bán","sum"))
                   .reset_index().sort_values("Doanh_thu", ascending=False))
        st.dataframe(df_nhom, use_container_width=True)

# TAB 2 – Doanh thu & Khối lượng
with tab2:
    st.markdown('<div class="section-title">📈 Doanh thu & Khối lượng theo tháng</div>', unsafe_allow_html=True)
    if "Tháng" in df_filtered.columns:
        df_m = (df_filtered.groupby("Tháng")
                .agg(Doanh_thu=("Thành tiền bán","sum"),
                     Khối_lượng=("Khối lượng","sum"))
                .reset_index())
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=("Doanh thu (VNĐ)", "Khối lượng (tấn)"))
        fig.add_trace(go.Bar(x=df_m["Tháng"], y=df_m["Doanh_thu"], name="Doanh thu"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_m["Tháng"], y=df_m["Khối_lượng"]/1000, name="Khối lượng (tấn)",
                                 mode="lines+markers"), row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)

# TAB 3 – Lợi nhuận & Chính sách
with tab3:
    st.markdown('<div class="section-title">💹 Lợi nhuận & Chính sách</div>', unsafe_allow_html=True)
    if "Tháng" in df_filtered.columns:
        df_ln = (df_filtered.groupby("Tháng")
                 .agg(Doanh_thu=("Thành tiền bán","sum"),
                      Lợi_nhuận=("Lợi nhuận","sum"))
                 .reset_index())
        df_ln["Biên (%)"] = (df_ln["Lợi_nhuận"]/df_ln["Doanh_thu"].replace(0,float("nan"))*100).round(1)
        fig2 = px.line(df_ln, x="Tháng", y="Biên (%)", markers=True, title="Biên lợi nhuận theo tháng")
        st.plotly_chart(fig2, use_container_width=True)

# TAB 4 – Giao hàng
with tab4:
    st.markdown('<div class="section-title">🚚 Hình thức & địa điểm giao hàng</div>', unsafe_allow_html=True)
    if "Nơi giao hàng" in df_filtered.columns:
        df_noi = df_filtered["Nơi giao hàng"].value_counts().reset_index()
        df_noi.columns = ["Địa điểm","Số lần"]
        st.dataframe(df_noi, use_container_width=True)

# TAB 5 – BCCN & Rủi ro
with tab5:
    st.markdown('<div class="section-title">📄 BCCN & Rủi ro</div>', unsafe_allow_html=True)
    if "Ghi chú" in df_filtered.columns:
        tra_hang = df_filtered[df_filtered["Ghi chú"].str.contains("Trả hàng", na=False)]
        st.metric("↩️ Phiếu trả hàng", len(tra_hang))
        st.metric("💰 Giá trị trả hàng", f"{abs(tra_hang['Thành tiền bán'].sum()):,.0f}")

# TAB 6 – Thị phần KH
with tab6:
    st.markdown('<div class="section-title">🌍 Thị phần KH theo khu vực</div>', unsafe_allow_html=True)
    if "Khu vực" in df.columns and "Tên khách hàng" in df.columns:
        df_region = (df.groupby(["Khu vực","Tên khách hàng"])
                     .agg(Doanh_thu=("Thành tiền bán","sum"))
                     .reset_index())
        df_region["Thị phần (%)"] = df_region.groupby("Khu vực")["Doanh_thu"].apply(lambda x: x/x.sum()*100)
        df_region["Rank"] = df_region.groupby("Khu vực")["Doanh_thu"].rank(method="dense", ascending=False)
        st.dataframe(df_region, use_container_width=True)

# TAB 7 – Top KH theo Phòng KD
with tab7:
    st.markdown('<div class="section-title">🏆 Top KH theo Phòng KD</div>', unsafe_allow_html=True)
    if "Tên nhóm
