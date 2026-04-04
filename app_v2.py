import io
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Phân tích KH - Hoa Sen", layout="wide", page_icon="📊")

# Upload
st.sidebar.header("📂 Tải lên dữ liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel báo cáo bán hàng", type=["xlsx"])
if not uploaded_file:
    st.markdown("## 👈 Vui lòng tải lên file Excel để bắt đầu phân tích")
    st.stop()

# Load data
@st.cache_data
def load_data(file):
    df = pd.read_excel(file, engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower()
    rename_map = {
        "ngày chứng từ": "Ngày chứng từ",
        "tên khách hàng": "Tên khách hàng",
        "tên nhóm kh": "Tên nhóm KH",
        "phòng kd": "Tên nhóm KH",
        "khu vực": "Khu vực",
        "thành tiền bán": "Thành tiền bán",
        "doanh thu": "Thành tiền bán",
        "khối lượng": "Khối lượng",
        "lợi nhuận": "Lợi nhuận",
        "nơi giao hàng": "Nơi giao hàng",
        "ghi chú": "Ghi chú",
        "bccn": "BCCN",
        "rủi ro": "Rủi ro"
    }
    df = df.rename(columns=lambda c: rename_map.get(c, c))
    if "Ngày chứng từ" in df.columns:
        df["Ngày chứng từ"] = pd.to_datetime(df["Ngày chứng từ"], dayfirst=True, errors="coerce")
        df["Tháng"] = df["Ngày chứng từ"].dt.to_period("M").astype(str)
        df["Quý"] = df["Ngày chứng từ"].dt.to_period("Q").astype(str)
    return df

df = load_data(uploaded_file)

# Bộ lọc
st.sidebar.header("🔍 Bộ lọc")
pkd_list = sorted(df["Tên nhóm KH"].dropna().unique()) if "Tên nhóm KH" in df.columns else []
pkd = st.sidebar.multiselect("🏢 Phòng KD", pkd_list, default=pkd_list)

kv_list = sorted(df["Khu vực"].dropna().unique()) if "Khu vực" in df.columns else []
kv = st.sidebar.multiselect("🌍 Khu vực", kv_list, default=kv_list)

kh_list = sorted(df["Tên khách hàng"].dropna().unique()) if "Tên khách hàng" in df.columns else []
kh = st.sidebar.selectbox("👤 Khách hàng", kh_list) if kh_list else None

quy_list = sorted(df["Quý"].dropna().unique()) if "Quý" in df.columns else []
quy = st.sidebar.multiselect("📅 Quý", quy_list, default=quy_list)

rr_list = sorted(df["Rủi ro"].dropna().unique()) if "Rủi ro" in df.columns else []
rr = st.sidebar.multiselect("⚠️ Điểm rủi ro", rr_list, default=rr_list)

df_filtered = df.copy()
if pkd: df_filtered = df_filtered[df_filtered["Tên nhóm KH"].isin(pkd)]
if kv: df_filtered = df_filtered[df_filtered["Khu vực"].isin(kv)]
if kh: df_filtered = df_filtered[df_filtered["Tên khách hàng"] == kh]
if quy: df_filtered = df_filtered[df_filtered["Quý"].isin(quy)]
if rr: df_filtered = df_filtered[df_filtered["Rủi ro"].isin(rr)]

# Header
st.title("📊 Phân tích dữ liệu bán hàng")
if kh: st.subheader(f"Khách hàng: {kh}")

if "Ngày chứng từ" in df_filtered.columns:
    dmin = df_filtered["Ngày chứng từ"].min()
    dmax = df_filtered["Ngày chứng từ"].max()
    st.markdown(f"**Khoảng thời gian:** {dmin.strftime('%d/%m/%Y')} → {dmax.strftime('%d/%m/%Y')}")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📦 Thói quen mua hàng",
    "📈 Doanh thu & Khối lượng",
    "💹 Lợi nhuận",
    "🚚 Giao hàng",
    "📄 BCCN & Rủi ro",
    "🌍 Thị phần KH",
    "🏆 Top KH theo Phòng KD"
])

# TAB 1
with tab1:
    if "Tên hàng" in df_filtered.columns:
        df_nhom = (df_filtered.groupby("Tên hàng")
                   .agg(Số_lần=("Tên hàng","count"),
                        Doanh_thu=("Thành tiền bán","sum"))
                   .reset_index().sort_values("Doanh_thu", ascending=False))
        st.markdown("### 📦 Thói quen mua hàng theo sản phẩm")
        st.dataframe(df_nhom, use_container_width=True)
        fig = px.pie(df_nhom, names="Tên hàng", values="Doanh_thu", title="Tỷ trọng doanh thu theo sản phẩm")
        st.plotly_chart(fig, use_container_width=True)

# TAB 2
with tab2:
    if "Tháng" in df_filtered.columns:
        df_m = (df_filtered.groupby("Tháng")
                .agg(Doanh_thu=("Thành tiền bán","sum"),
                     Khối_lượng=("Khối lượng","sum"))
                .reset_index())
        st.markdown("### 📈 Doanh thu & Khối lượng theo tháng")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=("Doanh thu (VNĐ)", "Khối lượng (tấn)"))
        fig.add_trace(go.Bar(x=df_m["Tháng"], y=df_m["Doanh_thu"], name="Doanh thu"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_m["Tháng"], y=df_m["Khối_lượng"]/1000, name="Khối lượng (tấn)",
                                 mode="lines+markers"), row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)

# TAB 3
with tab3:
    if "Tháng" in df_filtered.columns and "Lợi nhuận" in df_filtered.columns:
        df_ln = (df_filtered.groupby("Tháng")
                 .agg(Doanh_thu=("Thành tiền bán","sum"),
                      Lợi_nhuận=("Lợi nhuận","sum"))
                 .reset_index())
        df_ln["Biên (%)"] = (df_ln["Lợi_nhuận"]/df_ln["Doanh_thu"].replace(0,float("nan"))*100).round(1)
        st.markdown("### 💹 Biên lợi nhuận theo tháng")
        fig2 = px.line(df_ln, x="Tháng", y="Biên (%)", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

# TAB 4
with tab4:
    if "Nơi giao hàng" in df_filtered.columns:
        df_noi = df_filtered["Nơi giao hàng"].value_counts().reset_index()
        df_noi.columns = ["Địa điểm","Số lần"]
        st.markdown("### 🚚 Địa điểm giao hàng")
        st.dataframe(df_noi, use_container_width=True)
        fig3 = px.bar(df_noi, x="Địa điểm", y="Số lần", title="Số lần giao hàng theo địa điểm")
        st.plotly_chart(fig3, use_container_width=True)

# TAB 5
with tab5:
    if "BCCN" in df_filtered.columns:
        df_bccn = df_filtered.groupby("Tên khách hàng")["BCCN"].mean().reset_index()
        st.markdown("### 📄 Thói quen thanh toán (BCCN)")
        st.dataframe(df_bccn, use_container_width=True)
    if "Ghi chú" in df_filtered.columns:
        tra_hang = df_filtered[df_filtered["Ghi chú"].str.contains("Trả hàng", na=False)]
        st.metric("↩️ Phiếu trả hàng", len(tra_hang))
Đạt ơi, tôi sẽ viết lại code mới hoàn chỉnh cho ứng dụng Streamlit theo đúng yêu cầu phân tích của bạn. Code này:

- Cho phép upload file Excel OM_RPT_055.  
- Chuẩn hóa tên cột để tránh lỗi.  
- Bộ lọc theo **Phòng KD**, **Khu vực**, **Khách hàng**, **Quý**, **Điểm rủi ro**.  
- Các tab phân tích:  
  - Thói quen mua hàng theo sản phẩm (biểu đồ tròn).  
  - Doanh thu & khối lượng theo tháng/quý (biểu đồ cột + đường).  
  - Lợi nhuận (biểu đồ đường).  
  - Giao hàng (biểu đồ cột).  
  - BCCN & rủi ro (thanh toán, phiếu trả hàng).  
  - Thị phần KH theo khu vực (bảng + top).  
  - Top KH theo Phòng KD.  

---

### 📦 File `app.py`

```python
import io
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Phân tích KH - Hoa Sen", layout="wide", page_icon="📊")

# Upload
st.sidebar.header("📂 Tải lên dữ liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel báo cáo bán hàng", type=["xlsx"])
if not uploaded_file:
    st.markdown("## 👈 Vui lòng tải lên file Excel để bắt đầu phân tích")
    st.stop()

# Load data
@st.cache_data
def load_data(file):
    df = pd.read_excel(file, engine="openpyxl")
    df.columns = df.columns.str.strip().str.lower()
    rename_map = {
        "ngày chứng từ": "Ngày chứng từ",
        "tên khách hàng": "Tên khách hàng",
        "tên nhóm kh": "Tên nhóm KH",
        "phòng kd": "Tên nhóm KH",
        "khu vực": "Khu vực",
        "thành tiền bán": "Thành tiền bán",
        "doanh thu": "Thành tiền bán",
        "khối lượng": "Khối lượng",
        "lợi nhuận": "Lợi nhuận",
        "nơi giao hàng": "Nơi giao hàng",
        "ghi chú": "Ghi chú",
        "bccn": "BCCN",
        "rủi ro": "Rủi ro",
        "tên hàng": "Tên hàng"
    }
    df = df.rename(columns=lambda c: rename_map.get(c, c))
    if "Ngày chứng từ" in df.columns:
        df["Ngày chứng từ"] = pd.to_datetime(df["Ngày chứng từ"], dayfirst=True, errors="coerce")
        df["Tháng"] = df["Ngày chứng từ"].dt.to_period("M").astype(str)
        df["Quý"] = df["Ngày chứng từ"].dt.to_period("Q").astype(str)
    return df

df = load_data(uploaded_file)

# Bộ lọc
st.sidebar.header("🔍 Bộ lọc")
pkd_list = sorted(df["Tên nhóm KH"].dropna().unique()) if "Tên nhóm KH" in df.columns else []
pkd = st.sidebar.multiselect("🏢 Phòng KD", pkd_list, default=pkd_list)

kv_list = sorted(df["Khu vực"].dropna().unique()) if "Khu vực" in df.columns else []
kv = st.sidebar.multiselect("🌍 Khu vực", kv_list, default=kv_list)

kh_list = sorted(df["Tên khách hàng"].dropna().unique()) if "Tên khách hàng" in df.columns else []
kh = st.sidebar.selectbox("👤 Khách hàng", kh_list) if kh_list else None

quy_list = sorted(df["Quý"].dropna().unique()) if "Quý" in df.columns else []
quy = st.sidebar.multiselect("📅 Quý", quy_list, default=quy_list)

rr_list = sorted(df["Rủi ro"].dropna().unique()) if "Rủi ro" in df.columns else []
rr = st.sidebar.multiselect("⚠️ Điểm rủi ro", rr_list, default=rr_list)

df_filtered = df.copy()
if pkd: df_filtered = df_filtered[df_filtered["Tên nhóm KH"].isin(pkd)]
if kv: df_filtered = df_filtered[df_filtered["Khu vực"].isin(kv)]
if kh: df_filtered = df_filtered[df_filtered["Tên khách hàng"] == kh]
if quy: df_filtered = df_filtered[df_filtered["Quý"].isin(quy)]
if rr: df_filtered = df_filtered[df_filtered["Rủi ro"].isin(rr)]

# Header
st.title("📊 Phân tích dữ liệu bán hàng")
if kh: st.subheader(f"Khách hàng: {kh}")

if "Ngày chứng từ" in df_filtered.columns:
    dmin = df_filtered["Ngày chứng từ"].min()
    dmax = df_filtered["Ngày chứng từ"].max()
    st.markdown(f"**Khoảng thời gian:** {dmin.strftime('%d/%m/%Y')} → {dmax.strftime('%d/%m/%Y')}")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📦 Thói quen mua hàng",
    "📈 Doanh thu & Khối lượng",
    "💹 Lợi nhuận",
    "🚚 Giao hàng",
    "📄 BCCN & Rủi ro",
    "🌍 Thị phần KH",
    "🏆 Top KH theo Phòng KD"
])

# TAB 1
with tab1:
    if "Tên hàng" in df_filtered.columns:
        df_nhom = (df_filtered.groupby("Tên hàng")
                   .agg(Số_lần=("Tên hàng","count"),
                        Doanh_thu=("Thành tiền bán","sum"))
                   .reset_index().sort_values("Doanh_thu", ascending=False))
        st.markdown("### 📦 Thói quen mua hàng theo sản phẩm")
        st.dataframe(df_nhom, use_container_width=True)
        fig = px.pie(df_nhom, names="Tên hàng", values="Doanh_thu", title="Tỷ trọng doanh thu theo sản phẩm")
        st.plotly_chart(fig, use_container_width=True)

# TAB 2
with tab2:
    if "Tháng" in df_filtered.columns:
        df_m = (df_filtered.groupby("Tháng")
                .agg(Doanh_thu=("Thành tiền bán","sum"),
                     Khối_lượng=("Khối lượng","sum"))
                .reset_index())
        st.markdown("### 📈 Doanh thu & Khối lượng theo tháng")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=("Doanh thu (VNĐ)", "Khối lượng (tấn)"))
        fig.add_trace(go.Bar(x=df_m["Tháng"], y=df_m["Doanh_thu"], name="Doanh thu"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_m["Tháng"], y=df_m["Khối_lượng"]/1000, name="Khối lượng (tấn)",
                                 mode="lines+markers"), row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)

# TAB 3
with tab3:
    if "Tháng" in df_filtered.columns and "Lợi nhuận" in df_filtered.columns:
        df_ln = (df_filtered.groupby("Tháng")
                 .agg(Doanh_thu=("Thành tiền bán","sum"),
                      Lợi_nhuận=("Lợi nhuận","sum"))
                 .reset_index())
        df_ln["Biên (%)"] = (df_ln["Lợi_nhuận"]/df_ln["Doanh_thu"].replace(0,float("nan"))*100).round(1)
        st.markdown("### 💹 Biên lợi nhuận theo tháng")
        fig2 = px.line(df_ln, x="Tháng", y="Biên (%)", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

# TAB 4
with tab4:
    if "Nơi giao hàng" in df_filtered.columns:
        df_noi = df_filtered["Nơi giao hàng"].value_counts().reset_index()
        df_noi.columns = ["Địa điểm","Số lần"]
        st.markdown("### 🚚 Địa điểm giao hàng")
        st.dataframe(df_noi, use_container_width=True)
        fig3 = px.bar(df_noi, x="Địa điểm", y="Số lần", title="Số lần giao hàng theo địa điểm")
        st.plotly_chart(fig3, use_container_width=True)

# TAB 5
with tab5:
    if "BCCN" in df_filtered.columns:
        df_bccn = df_filtered.groupby("Tên khách hàng")["BCCN"].mean().reset_index()
        st.markdown("### 📄 Thói quen thanh toán (BCCN)")
        st.dataframe(df_bccn, use_container_width=True)
    if "Ghi chú" in df_filtered.columns:
        tra_hang = df_filtered[df_filtered["Ghi chú"].str.contains("Trả hàng", na=False)]
        st.metric("↩️ Phiếu trả hàng", len(tra_hang))
        st.metric("
