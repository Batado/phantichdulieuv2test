import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Phân tích KH – Hoa Sen", layout="wide", page_icon="📊")

# ───────────────────────────────────────────────
#  UPLOAD
# ───────────────────────────────────────────────
st.sidebar.markdown("## 📂 Upload dữ liệu")
uploaded_files = st.sidebar.file_uploader(
    "Upload file Excel báo cáo bán hàng",
    type=["xlsx"], accept_multiple_files=True
)

if not uploaded_files:
    st.markdown("## 👈 Upload file Excel để bắt đầu phân tích")
    st.stop()

# ───────────────────────────────────────────────
#  LOAD & PROCESS DATA
# ───────────────────────────────────────────────
@st.cache_data(show_spinner="Đang xử lý dữ liệu…")
def load_all(file_data):
    frames = []
    for name, fb in file_data:
        df = pd.read_excel(io.BytesIO(fb), engine="openpyxl")
        df["Nguồn file"] = name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)

file_data = [(uf.name, uf.read()) for uf in uploaded_files]
df_all = load_all(file_data)

# Chuẩn hóa dữ liệu cơ bản
df_all["Ngày chứng từ"] = pd.to_datetime(df_all["Ngày chứng từ"], dayfirst=True, errors="coerce")
df_all["Tháng"] = df_all["Ngày chứng từ"].dt.to_period("M").astype(str)
df_all["Quý"] = df_all["Ngày chứng từ"].dt.to_period("Q").astype(str)

# ───────────────────────────────────────────────
#  SIDEBAR FILTERS
# ───────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 Bộ lọc")

kh_list = sorted(df_all["Tên khách hàng"].dropna().astype(str).unique())
kh = st.sidebar.selectbox("👤 Khách hàng", kh_list)

quy_list = sorted(df_all["Quý"].dropna().unique())
quy_chon = st.sidebar.multiselect("📅 Quý", quy_list, default=quy_list)

nhom_list = sorted(df_all["Tên nhóm hàng"].dropna().astype(str).unique()) if "Tên nhóm hàng" in df_all.columns else []
nhom_chon = st.sidebar.multiselect("🏢 Nhóm KH", nhom_list, default=nhom_list)

kv_list = sorted(df_all["Khu vực"].dropna().astype(str).unique()) if "Khu vực" in df_all.columns else []
kv_chon = st.sidebar.multiselect("🌍 Khu vực", kv_list, default=kv_list)

df = df_all[
    (df_all["Tên khách hàng"].astype(str) == kh) &
    (df_all["Quý"].isin(quy_chon)) &
    ((df_all["Tên nhóm hàng"].isin(nhom_chon)) if nhom_list else True) &
    ((df_all["Khu vực"].isin(kv_chon)) if kv_list else True)
].copy()

df_ban = df[df["Loại GD"] == "Xuất bán"].copy()

# ───────────────────────────────────────────────
#  HEADER
# ───────────────────────────────────────────────
ngay_min = df["Ngày chứng từ"].min()
ngay_max = df["Ngày chứng từ"].max()
st.markdown(f"# 📊 Phân tích: **{kh}**")
st.markdown(f"*Dữ liệu: {ngay_min.strftime('%d/%m/%Y') if pd.notna(ngay_min) else '?'} → "
            f"{ngay_max.strftime('%d/%m/%Y') if pd.notna(ngay_max) else '?'} "
            f"| {len(df):,} dòng*")

# ───────────────────────────────────────────────
#  TABs
# ───────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📦 Thói quen & Sản phẩm",
    "📈 Doanh thu & Sản lượng",
    "💹 Lợi nhuận & Chính sách",
    "🚚 Giao hàng",
    "🔁 Tần suất mua hàng",
    "⚠️ Rủi ro & BCCN",
    "🌍 Thị phần & Nhóm KH"
])

# ───────────────────────────────────────────────
#  TAB 1 – Thói quen mua hàng
# ───────────────────────────────────────────────
with tab1:
    df_nhom = (df_ban.groupby("Tên hàng")
               .agg(So_lan=("Tên hàng", "count"),
                    KL_tan=("Khối lượng", lambda x: round(x.sum()/1000,2)),
                    DT=("Thành tiền bán","sum"))
               .reset_index().sort_values("DT", ascending=False))
    st.dataframe(df_nhom, use_container_width=True)

# ───────────────────────────────────────────────
#  TAB 2 – Doanh thu & Sản lượng
# ───────────────────────────────────────────────
with tab2:
    df_m = (df_ban.groupby("Tháng")
            .agg(DT=("Thành tiền bán","sum"),
                 KL=("Khối lượng", lambda x: round(x.sum()/1000,2)))
            .reset_index())
    fig = px.bar(df_m, x="Tháng", y="DT", text_auto=".3s", title="Doanh thu theo tháng")
    st.plotly_chart(fig, use_container_width=True)

# ───────────────────────────────────────────────
#  TAB 3 – Lợi nhuận & Chính sách
# ───────────────────────────────────────────────
with tab3:
    df_ln = (df_ban.groupby("Tháng")
             .agg(DT=("Thành tiền bán","sum"),
                  LN=("Lợi nhuận","sum"))
             .reset_index())
    df_ln["Biên (%)"] = (df_ln["LN"]/df_ln["DT"].replace(0,float("nan"))*100).round(1)
    fig = px.line(df_ln, x="Tháng", y="Biên (%)", markers=True, title="Biên lợi nhuận theo tháng")
    st.plotly_chart(fig, use_container_width=True)

# ───────────────────────────────────────────────
#  TAB 4 – Giao hàng
# ───────────────────────────────────────────────
with tab4:
    if "Nơi giao hàng" in df_ban.columns:
        df_noi = df_ban["Nơi giao hàng"].value_counts().reset_index()
        df_noi.columns = ["Địa điểm","Số lần"]
        st.dataframe(df_noi, use_container_width=True)

# ───────────────────────────────────────────────
#  TAB 5 – Tần suất mua hàng
# ───────────────────────────────────────────────
with tab5:
    if "Tên hàng" in df_ban.columns:
        df_freq = (df_ban.groupby(["Tên hàng","Tháng"]).size().reset_index(name="Số lần"))
        df_piv = df_freq.pivot(index="Tên hàng", columns="Tháng", values="Số lần").fillna(0)
        fig_h = px.imshow(df_piv, labels=dict(x="Tháng", y="Sản phẩm", color="Số lần"),
                          color_continuous_scale="Blues", aspect="auto")
        st.plotly_chart(fig_h, use_container_width=True)

# ───────────────────────────────────────────────
#  TAB 6 – Rủi ro & BCCN
# ───────────────────────────────────────────────
with tab6:
    df_tra = df[df["Loại GD"]=="Trả hàng"]
    st.metric("↩️ Phiếu trả hàng", len(df_tra))
    st.metric("💰 Giá trị trả hàng", f"{abs(df_tra['Thành tiền bán'].sum()):,.0f}")

# ───────────────────────────────────────────────
#  TAB 7 – Thị phần & Nhóm KH
# ───────────────────────────────────────────────
with tab7:
    if "Khu vực" in df_all.columns:
        df_region = (df_all.groupby(["Khu vực","Tên khách hàng"])
                     .agg(DT=("Thành tiền bán","sum"))
                     .reset_index())
        df_region["Thị phần (%)"] = df_region.groupby("Khu vực")["DT"].apply(lambda x: x/x.sum()*100)
        df_region["Rank"] = df_region.groupby("Khu vực")["DT"].rank(method="dense", ascending=False)

        def risk_score(row):
            if row["Thị phần (%)"] < 5: return "Cao"
            elif row["Thị phần (%)"] < 15: return "Trung bình"
            else: return "Thấp"

        df_region["Điểm rủi ro"] = df_region.apply(risk_score, axis=1)
        df_region["DT"] = df_region["DT"].map("{:,.0f}".format)
        st.dataframe(df_region, use_container_width=True, hide_index=True)
