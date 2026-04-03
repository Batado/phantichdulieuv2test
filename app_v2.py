import io
import warnings
warnings.filterwarnings(“ignore”)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ══════════════════════════════════════════════════════════════

# PAGE CONFIG

# ══════════════════════════════════════════════════════════════

st.set_page_config(
page_title=“Phân tích KH - Hoa Sen”,
layout=“wide”,
page_icon=“📊”,
initial_sidebar_state=“expanded”
)

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Be Vietnam Pro', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    border-right: 1px solid #21262d;
}
section[data-testid="stSidebar"] * {
    color: #c9d1d9 !important;
}

/* Main background */
.stApp { background: #0d1117; }

/* Risk cards */
.risk-high   { background: rgba(218,54,51,0.12); border-left: 3px solid #da3633; padding: 10px 16px; border-radius: 6px; margin: 5px 0; color: #ffa198; }
.risk-medium { background: rgba(187,128,9,0.12);  border-left: 3px solid #bb8009; padding: 10px 16px; border-radius: 6px; margin: 5px 0; color: #e3b341; }
.risk-low    { background: rgba(35,134,54,0.12);  border-left: 3px solid #238636; padding: 10px 16px; border-radius: 6px; margin: 5px 0; color: #56d364; }
.risk-info   { background: rgba(31,111,235,0.12); border-left: 3px solid #1f6feb; padding: 10px 16px; border-radius: 6px; margin: 5px 0; color: #79c0ff; }

/* Section titles */
.section-title {
    font-size: 14px; font-weight: 700; color: #8b949e;
    margin: 22px 0 10px 0; padding-bottom: 6px;
    border-bottom: 1px solid #21262d;
    text-transform: uppercase; letter-spacing: 0.05em;
}

/* KPI cards */
.kpi-row { display: flex; gap: 12px; margin: 10px 0 20px 0; flex-wrap: wrap; }
.kpi-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    border: 1px solid #21262d; border-radius: 10px;
    padding: 16px 20px; flex: 1; min-width: 140px;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #388bfd; }
.kpi-val  { font-size: 20px; font-weight: 800; color: #f0f6fc; line-height: 1.2; }
.kpi-lab  { font-size: 11px; color: #6e7681; margin-top: 4px; font-weight: 500; }
.kpi-delta-up   { font-size: 11px; color: #56d364; margin-top: 2px; }
.kpi-delta-down { font-size: 11px; color: #ffa198; margin-top: 2px; }

/* Page title */
.page-title {
    font-size: 26px; font-weight: 800; color: #f0f6fc;
    padding: 6px 0 2px 0;
}
.page-sub { font-size: 13px; color: #6e7681; margin-bottom: 18px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #161b22;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #21262d;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #8b949e;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
}
.stTabs [aria-selected="true"] {
    background: #21262d !important;
    color: #f0f6fc !important;
}

/* Dataframe */
.stDataFrame { border: 1px solid #21262d !important; border-radius: 8px !important; }

/* Info/warning/error */
.stInfo, .stWarning, .stError { border-radius: 8px; }

/* Selectbox, multiselect */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #161b22;
    border-color: #30363d;
    border-radius: 8px;
    color: #c9d1d9;
}
</style>

“””, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════

# CONSTANTS

# ══════════════════════════════════════════════════════════════

NHOM_SP = [
(“Ống HDPE”,        r”HDPE”),
(“Ống PVC nước”,    r”PVC.*(?:nước|nong dài|nong trơn|thoát|cấp)”),
(“Ống PVC bơm cát”, r”PVC.*(?:cát|bơm cát)”),
(“Ống PPR”,         r”PPR”),
(“Lõi PVC”,         r”(?:Lơi|Lõi|lori)”),
(“Phụ kiện & Keo”,  r”(?:Nối|Co |Tê |Van |Keo |Măng|Bít|Y PVC|Y PPR|Giảm|Cút)”),
]

# Plotly theme

PLOTLY_LAYOUT = dict(
paper_bgcolor=”#0d1117”,
plot_bgcolor=”#0d1117”,
font=dict(family=“Be Vietnam Pro, sans-serif”, color=”#c9d1d9”, size=12),
title_font=dict(size=14, color=”#f0f6fc”, family=“Be Vietnam Pro, sans-serif”),
legend=dict(
bgcolor=”#161b22”,
bordercolor=”#21262d”,
borderwidth=1,
font=dict(size=11, color=”#c9d1d9”)
),
xaxis=dict(gridcolor=”#21262d”, linecolor=”#30363d”, tickfont=dict(size=11)),
yaxis=dict(gridcolor=”#21262d”, linecolor=”#30363d”, tickfont=dict(size=11)),
margin=dict(l=10, r=10, t=45, b=10),
colorway=[”#388bfd”,”#56d364”,”#e3b341”,”#ffa198”,”#79c0ff”,”#d2a8ff”,”#ffb800”,”#3fb950”],
)

COLOR_SEQ = [”#388bfd”,”#56d364”,”#e3b341”,”#ffa198”,”#79c0ff”,”#d2a8ff”,”#ffb800”,”#3fb950”,”#bc8cff”,”#ff7b72”]

# ══════════════════════════════════════════════════════════════

# HELPERS

# ══════════════════════════════════════════════════════════════

def fmt(v):
try:
f = float(v)
if abs(f) >= 1e9:
return f”{f/1e9:,.2f} tỷ”
if abs(f) >= 1e6:
return f”{f/1e6:,.1f} tr”
return f”{f:,.0f}”
except Exception:
return str(v)

def fmt_full(v):
try:
return f”{float(v):,.0f}”
except Exception:
return str(v)

def apply_layout(fig, **kwargs):
layout = {**PLOTLY_LAYOUT, **kwargs}
# Handle nested axis updates
xaxis_extra = kwargs.get(“xaxis_extra”, {})
yaxis_extra = kwargs.get(“yaxis_extra”, {})
layout.pop(“xaxis_extra”, None)
layout.pop(“yaxis_extra”, None)
fig.update_layout(**layout)
if xaxis_extra:
fig.update_xaxes(**xaxis_extra)
if yaxis_extra:
fig.update_yaxes(**yaxis_extra)
return fig

def get_col(df, col, default=0):
if col in df.columns:
return pd.to_numeric(df[col], errors=“coerce”).fillna(0)
return pd.Series(default, index=df.index)

# ══════════════════════════════════════════════════════════════

# DATA LOADING

# ══════════════════════════════════════════════════════════════

def find_header_row(fb):
try:
raw = pd.read_excel(io.BytesIO(fb), header=None, engine=“openpyxl”, nrows=40)
except Exception:
return 0
kws = [“số chứng từ”, “ngày chứng từ”, “mã nhóm kh”, “tên khách hàng”, “tên hàng”, “thành tiền bán”]
for i in range(raw.shape[0]):
vals = [str(v).strip().lower() for v in raw.iloc[i].tolist() if str(v).strip() not in (””, “nan”)]
row_text = “ “.join(vals)
if sum(1 for k in kws if k in row_text) >= 3:
return i
return 0

def load_all(file_data):
frames, errs = [], []
for name, fb in file_data:
try:
hr = find_header_row(fb)
df = pd.read_excel(io.BytesIO(fb), header=hr, engine=“openpyxl”)
df.columns = [str(c).strip().replace(”\n”, “ “).replace(”\r”, “”) for c in df.columns]
df = df.loc[:, ~df.columns.str.startswith(“Unnamed”)]
df.dropna(how=“all”, inplace=True)
df[“Nguon file”] = name
frames.append(df)
except Exception as e:
errs.append(f”`{name}`: {e}”)

```
for e in errs:
    st.warning(f"⚠️ {e}")

if not frames:
    return pd.DataFrame()

df = pd.concat(frames, ignore_index=True)

# Numeric columns
num_cols = ["Thành tiền bán", "Thành tiền vốn", "Lợi nhuận",
            "Khối lượng", "Số lượng", "Giá bán", "Giá vốn",
            "Đơn giá vận chuyển", "Đơn giá quy đổi"]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    else:
        df[c] = 0.0

# Date parsing
date_col = None
for c in ["Ngày chứng từ", "Ngay chung tu", "Ngay_CT"]:
    if c in df.columns:
        date_col = c
        break
if date_col is None:
    st.error("❌ Không tìm thấy cột ngày chứng từ.")
    return pd.DataFrame()
if date_col != "Ngày chứng từ":
    df.rename(columns={date_col: "Ngày chứng từ"}, inplace=True)

df["Ngày chứng từ"] = pd.to_datetime(df["Ngày chứng từ"], dayfirst=True, errors="coerce")
df = df[df["Ngày chứng từ"].notna()].copy()
df["Nam"]   = df["Ngày chứng từ"].dt.year.astype(str)
df["Quy"]   = df["Ngày chứng từ"].dt.to_period("Q").astype(str)
df["Thang"] = df["Ngày chứng từ"].dt.to_period("M").astype(str)
df["Thang_label"] = df["Ngày chứng từ"].dt.strftime("%m/%Y")
df["Ngay_trong_thang"] = df["Ngày chứng từ"].dt.day
df["Cuoi_thang"] = df["Ngay_trong_thang"] >= 28

# Transaction type
gc   = df["Ghi chú"].astype(str).str.upper() if "Ghi chú" in df.columns else pd.Series("", index=df.index)
loai = df["Loại đơn hàng"].astype(str).str.upper() if "Loại đơn hàng" in df.columns else pd.Series("", index=df.index)
df["Loai_GD"] = "Xuất bán"
df.loc[gc.str.contains(r"NHẬP TRẢ|TRẢ HÀNG", regex=True, na=False), "Loai_GD"] = "Trả hàng"
df.loc[loai.str.contains(r"TRA HANG|HUY HD", regex=True, na=False), "Loai_GD"] = "Trả hàng"
df.loc[gc.str.contains(r"BỔ SUNG|THAY THẾ", regex=True, na=False), "Loai_GD"] = "Xuất bổ sung"

# Product groups
ten = df["Tên hàng"].astype(str) if "Tên hàng" in df.columns else pd.Series("", index=df.index)
df["Nhom_SP"] = "Khác"
for label, pat in NHOM_SP:
    df.loc[ten.str.contains(pat, case=False, regex=True, na=False), "Nhom_SP"] = label

# Margin
df["Bien_LN"] = np.where(
    df["Thành tiền bán"] != 0,
    (df["Lợi nhuận"] / df["Thành tiền bán"] * 100).round(2),
    0.0
)

# Clean kho
if "Mã kho" in df.columns:
    df["Mã kho"] = df["Mã kho"].astype(str).str.replace(".0", "", regex=False).str.strip()

# Ensure customer name col
if "Tên khách hàng" not in df.columns:
    st.error("❌ Không tìm thấy cột 'Tên khách hàng'.")
    return pd.DataFrame()

return df
```

# ══════════════════════════════════════════════════════════════

# SIDEBAR & UPLOAD

# ══════════════════════════════════════════════════════════════

st.sidebar.markdown(”## 📂 Upload dữ liệu”)
uploaded = st.sidebar.file_uploader(
“File Excel báo cáo bán hàng (OM_RPT_055)”,
type=[“xlsx”],
accept_multiple_files=True
)

if not uploaded:
st.markdown(’<div class="page-title">📊 Phân tích Bán hàng - Hoa Sen</div>’, unsafe_allow_html=True)
st.markdown(’<div class="page-sub">Hệ thống phân tích dữ liệu & nhận diện rủi ro khách hàng</div>’, unsafe_allow_html=True)
st.info(“👈 Upload file Excel báo cáo OM_RPT_055 để bắt đầu phân tích.”)
col1, col2, col3 = st.columns(3)
for c, icon, title, desc in [
(col1, “📈”, “Phân tích doanh thu”, “Theo KH, Phòng KD, tháng, quý, năm”),
(col2, “📦”, “Cơ cấu sản phẩm”, “Nhóm SP, xu hướng, tần suất mua”),
(col3, “⚠️”, “Nhận diện rủi ro”, “12 nhóm rủi ro tự động, biên LN, trả hàng”),
]:
c.markdown(f”””
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:20px;text-align:center;height:110px;">
<div style="font-size:28px">{icon}</div>
<div style="font-weight:700;color:#f0f6fc;margin:4px 0">{title}</div>
<div style="font-size:12px;color:#6e7681">{desc}</div>
</div>
“””, unsafe_allow_html=True)
st.stop()

@st.cache_data(show_spinner=“⏳ Đang xử lý dữ liệu…”)
def cached_load(file_data):
return load_all(file_data)

file_data = [(u.name, u.read()) for u in uploaded]
df_all = cached_load(tuple(file_data))

if df_all.empty:
st.error(“Không có dữ liệu hợp lệ.”)
st.stop()

# ══════════════════════════════════════════════════════════════

# SIDEBAR FILTERS

# ══════════════════════════════════════════════════════════════

st.sidebar.markdown(”—”)
st.sidebar.markdown(”## 🔍 Bộ lọc”)

# — Filter: Phòng KD —

pkd_col_exists = “Mã nhóm KH” in df_all.columns and “Tên nhóm KH” in df_all.columns
if pkd_col_exists:
pkd_opts = sorted(df_all[“Tên nhóm KH”].dropna().astype(str).unique().tolist())
pkd_chon = st.sidebar.multiselect(“🏢 Phòng Kinh doanh”, pkd_opts, default=pkd_opts,
help=“Chọn một hoặc nhiều Phòng KD”)
if pkd_chon:
df_filtered = df_all[df_all[“Tên nhóm KH”].astype(str).isin(pkd_chon)].copy()
else:
df_filtered = df_all.copy()
else:
df_filtered = df_all.copy()
pkd_chon = []

# — Filter: Tháng —

thang_opts = sorted(df_filtered[“Thang”].dropna().unique().tolist())
thang_labels = sorted(df_filtered[“Thang_label”].dropna().unique().tolist())
thang_map    = dict(zip(thang_labels, [t for t in thang_opts]))

thang_chon_labels = st.sidebar.multiselect(
“📅 Tháng”, thang_labels, default=thang_labels,
help=“Chọn tháng để lọc dữ liệu”
)
thang_chon = [thang_map[l] for l in thang_chon_labels if l in thang_map]
if thang_chon:
df_filtered = df_filtered[df_filtered[“Thang”].isin(thang_chon)].copy()

# — Filter: Chế độ xem —

st.sidebar.markdown(”—”)
view_mode = st.sidebar.radio(“📌 Chế độ xem”, [“Tổng quan”, “Theo Phòng KD”, “Theo Khách hàng”])

single_kh   = False
scope_label = “Tất cả”

if view_mode == “Theo Khách hàng”:
kh_list = sorted(df_filtered[“Tên khách hàng”].dropna().astype(str).unique())
if not kh_list:
st.warning(“Không có khách hàng phù hợp với bộ lọc.”)
st.stop()
kh = st.sidebar.selectbox(“👤 Khách hàng”, kh_list)
df_scope   = df_filtered[df_filtered[“Tên khách hàng”].astype(str) == kh].copy()
scope_label = kh
single_kh   = True

elif view_mode == “Theo Phòng KD”:
if pkd_col_exists and pkd_opts:
pkd_view = st.sidebar.selectbox(“🏢 Xem chi tiết Phòng KD”, pkd_opts)
df_scope   = df_filtered[df_filtered[“Tên nhóm KH”].astype(str) == pkd_view].copy()
scope_label = pkd_view
else:
df_scope   = df_filtered.copy()
scope_label = “Tổng hợp”
else:
df_scope   = df_filtered.copy()
scope_label = “Tổng quan”

# Time grouping

time_col_map   = {“Năm”: “Nam”, “Quý”: “Quy”, “Tháng”: “Thang”}
time_level_lbl = st.sidebar.radio(“⏱ Cụm thời gian”, [“Tháng”, “Quý”, “Năm”], index=0)
time_col       = time_col_map[time_level_lbl]

df_ban = df_scope[df_scope[“Loai_GD”] == “Xuất bán”].copy()

# ══════════════════════════════════════════════════════════════

# HEADER

# ══════════════════════════════════════════════════════════════

ngay_min = df_scope[“Ngày chứng từ”].min()
ngay_max = df_scope[“Ngày chứng từ”].max()
date_str = (
f”{ngay_min.strftime(’%d/%m/%Y’) if pd.notna(ngay_min) else ‘?’} → “
f”{ngay_max.strftime(’%d/%m/%Y’) if pd.notna(ngay_max) else ‘?’}”
)

st.markdown(f’<div class="page-title">📊 {scope_label}</div>’, unsafe_allow_html=True)
st.markdown(f’<div class="page-sub">📅 {date_str}  |  🗓 {time_level_lbl}  |  🏢 {”, “.join(pkd_chon[:3]) + (”…” if len(pkd_chon)>3 else “”) if pkd_chon else “Tất cả PKD”}  |  📆 {”, “.join(thang_chon_labels[:4]) + (”…” if len(thang_chon_labels)>4 else “”) if thang_chon_labels else “Tất cả tháng”}</div>’, unsafe_allow_html=True)

if df_ban.empty:
st.warning(“⚠️ Không có dữ liệu xuất bán cho bộ lọc đã chọn.”)
st.stop()

# KPIs

tong_dt  = df_ban[“Thành tiền bán”].sum()
tong_ln  = df_ban[“Lợi nhuận”].sum()
tong_kl  = df_ban[“Khối lượng”].sum() / 1000
bien_ln  = (tong_ln / tong_dt * 100) if tong_dt else 0
n_ct     = df_ban[“Số chứng từ”].nunique() if “Số chứng từ” in df_ban.columns else len(df_ban)
n_kh     = df_ban[“Tên khách hàng”].nunique()
n_sp     = df_ban[“Tên hàng”].nunique() if “Tên hàng” in df_ban.columns else 0

kpis = [
(“💰 Doanh thu”, fmt(tong_dt) + “ đ”, None),
(“💹 Lợi nhuận”, fmt(tong_ln) + “ đ”, None),
(“📊 Biên LN”, f”{bien_ln:.1f}%”, “up” if bien_ln >= 15 else (“down” if bien_ln < 5 else None)),
(“⚖️ Khối lượng”, f”{tong_kl:,.1f} tấn”, None),
(“📋 Chứng từ”, f”{n_ct:,}”, None),
(“👥 Khách hàng”, f”{n_kh:,}”, None),
(“📦 Sản phẩm”, f”{n_sp:,}”, None),
]

cols = st.columns(len(kpis))
for col, (lab, val, delta) in zip(cols, kpis):
delta_html = “”
if delta == “up”:
delta_html = ‘<div class="kpi-delta-up">▲ Tốt</div>’
elif delta == “down”:
delta_html = ‘<div class="kpi-delta-down">▼ Thấp</div>’
col.markdown(
f’<div class="kpi-card"><div class="kpi-val">{val}</div>’
f’<div class="kpi-lab">{lab}</div>{delta_html}</div>’,
unsafe_allow_html=True
)

st.markdown(””)

# ══════════════════════════════════════════════════════════════

# TABS

# ══════════════════════════════════════════════════════════════

tabs = st.tabs([
“🏢 Phòng KD & KH”,
“📅 Thời gian”,
“📦 Sản phẩm”,
“💹 Lợi nhuận”,
“🚚 Giao hàng”,
“🔁 Tần suất”,
“⚠️ Rủi ro”,
])
tab_pkd, tab_time, tab_sp, tab_ln, tab_giao, tab_freq, tab_risk = tabs

# ══════════════════════════════════════════════════════════════

# TAB 1 - PHÒNG KD & KH

# ══════════════════════════════════════════════════════════════

with tab_pkd:
has_pkd = “Mã nhóm KH” in df_ban.columns and “Tên nhóm KH” in df_ban.columns

```
if has_pkd:
    st.markdown('<div class="section-title">🏢 Cơ cấu Doanh thu: Phòng KD → Khách hàng</div>', unsafe_allow_html=True)

    # Sunburst
    df_sun = (df_ban.groupby(["Tên nhóm KH", "Tên khách hàng"])
              .agg(DT=("Thành tiền bán", "sum")).reset_index())
    df_sun = df_sun[df_sun["DT"] > 0]
    if not df_sun.empty:
        fig_sun = px.sunburst(
            df_sun, path=["Tên nhóm KH", "Tên khách hàng"],
            values="DT", title="Sunburst: Phòng KD → Khách hàng",
            color="DT", color_continuous_scale="Blues"
        )
        fig_sun.update_layout(**{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis")})
        fig_sun.update_layout(height=500)
        st.plotly_chart(fig_sun, use_container_width=True)

    # PKD summary table
    st.markdown('<div class="section-title">📋 Tổng hợp Phòng Kinh Doanh</div>', unsafe_allow_html=True)
    df_pkd = (df_ban.groupby(["Mã nhóm KH", "Tên nhóm KH"])
              .agg(
                  DT=("Thành tiền bán", "sum"),
                  LN=("Lợi nhuận", "sum"),
                  KL=("Khối lượng", lambda x: round(x.sum() / 1000, 2)),
                  N_KH=("Tên khách hàng", "nunique"),
                  N_CT=("Số chứng từ", "nunique") if "Số chứng từ" in df_ban.columns else ("Thành tiền bán", "count")
              ).reset_index().sort_values("DT", ascending=False))
    df_pkd["Biên (%)"] = (df_pkd["LN"] / df_pkd["DT"].replace(0, np.nan) * 100).round(1).fillna(0)
    df_pkd_d = df_pkd.copy()
    df_pkd_d["DT"] = df_pkd_d["DT"].map(fmt_full)
    df_pkd_d["LN"] = df_pkd_d["LN"].map(fmt_full)
    df_pkd_d.columns = ["Mã PKD", "Tên Phòng KD", "Doanh thu (VNĐ)", "Lợi nhuận (VNĐ)", "KL (tấn)", "Số KH", "Số CT", "Biên (%)"]
    st.dataframe(df_pkd_d, use_container_width=True, hide_index=True)

    # Bar PKD
    fig_pkd_bar = go.Figure()
    fig_pkd_bar.add_trace(go.Bar(
        x=df_pkd["Tên nhóm KH"], y=df_pkd["DT"],
        name="Doanh thu", marker_color="#388bfd",
        text=[fmt(v) for v in df_pkd["DT"]], textposition="outside",
        opacity=0.9
    ))
    fig_pkd_bar.add_trace(go.Bar(
        x=df_pkd["Tên nhóm KH"], y=df_pkd["LN"],
        name="Lợi nhuận", marker_color="#56d364",
        text=[fmt(v) for v in df_pkd["LN"]], textposition="outside",
        opacity=0.9
    ))
    fig_pkd_bar.update_layout(**PLOTLY_LAYOUT,
                               title="Doanh thu & Lợi nhuận theo Phòng KD",
                               barmode="group", height=380,
                               xaxis_tickangle=-20)
    st.plotly_chart(fig_pkd_bar, use_container_width=True)

# KH table
st.markdown('<div class="section-title">👥 Hiệu quả kinh doanh theo Khách hàng</div>', unsafe_allow_html=True)
grp_cols = (["Mã nhóm KH", "Tên nhóm KH", "Tên khách hàng"]
            if has_pkd else ["Tên khách hàng"])
df_kh_tbl = (df_ban.groupby(grp_cols)
             .agg(
                 DT=("Thành tiền bán", "sum"),
                 LN=("Lợi nhuận", "sum"),
                 KL=("Khối lượng", lambda x: round(x.sum() / 1000, 2)),
                 N_CT=("Số chứng từ", "nunique") if "Số chứng từ" in df_ban.columns else ("Thành tiền bán", "count"),
                 N_SP=("Tên hàng", "nunique") if "Tên hàng" in df_ban.columns else ("Thành tiền bán", "count")
             ).reset_index().sort_values("DT", ascending=False))
df_kh_tbl["Biên (%)"] = (df_kh_tbl["LN"] / df_kh_tbl["DT"].replace(0, np.nan) * 100).round(1).fillna(0)
df_kh_d = df_kh_tbl.copy()
df_kh_d["DT"] = df_kh_d["DT"].map(fmt_full)
df_kh_d["LN"] = df_kh_d["LN"].map(fmt_full)
st.dataframe(df_kh_d, use_container_width=True, hide_index=True)

# Top KH bar (horizontal, màu = biên LN)
df_top_kh = (df_ban.groupby("Tên khách hàng")
             .agg(DT=("Thành tiền bán", "sum"), LN=("Lợi nhuận", "sum"))
             .reset_index().sort_values("DT", ascending=False).head(15))
df_top_kh["Bien"] = (df_top_kh["LN"] / df_top_kh["DT"].replace(0, np.nan) * 100).round(1).fillna(0)
df_top_kh = df_top_kh.sort_values("DT", ascending=True)

fig_kh = go.Figure()
fig_kh.add_trace(go.Bar(
    y=df_top_kh["Tên khách hàng"],
    x=df_top_kh["DT"],
    orientation="h",
    marker=dict(
        color=df_top_kh["Bien"],
        colorscale=[[0, "#ffa198"], [0.3, "#e3b341"], [0.6, "#3fb950"], [1, "#56d364"]],
        colorbar=dict(title="Biên LN %", tickfont=dict(color="#c9d1d9"), titlefont=dict(color="#c9d1d9")),
        showscale=True
    ),
    text=[fmt(v) for v in df_top_kh["DT"]],
    textposition="outside",
    textfont=dict(size=11, color="#c9d1d9")
))
fig_kh.update_layout(**{**PLOTLY_LAYOUT,
                         "title": "Top 15 Khách hàng - Doanh thu (màu = Biên LN%)",
                         "height": 480,
                         "xaxis": dict(gridcolor="#21262d", tickfont=dict(size=10)),
                         "yaxis": dict(tickfont=dict(size=10), gridcolor="#21262d")})
st.plotly_chart(fig_kh, use_container_width=True)

# Khu vực
if "Khu vực" in df_ban.columns:
    st.markdown('<div class="section-title">🗺️ Doanh thu theo Khu vực</div>', unsafe_allow_html=True)
    df_kv = (df_ban.groupby("Khu vực")
             .agg(DT=("Thành tiền bán", "sum"), LN=("Lợi nhuận", "sum"),
                  N_KH=("Tên khách hàng", "nunique"))
             .reset_index().sort_values("DT", ascending=False))
    df_kv["Biên (%)"] = (df_kv["LN"] / df_kv["DT"].replace(0, np.nan) * 100).round(1).fillna(0)

    c1, c2 = st.columns([1, 1])
    with c1:
        fig_kv_pie = go.Figure(go.Pie(
            labels=df_kv["Khu vực"], values=df_kv["DT"],
            hole=0.55,
            marker=dict(colors=COLOR_SEQ[:len(df_kv)]),
            textfont=dict(size=12, color="#f0f6fc"),
            textinfo="label+percent"
        ))
        fig_kv_pie.update_layout(**{**PLOTLY_LAYOUT,
                                    "title": "Cơ cấu DT theo Khu vực", "height": 360,
                                    "showlegend": False})
        st.plotly_chart(fig_kv_pie, use_container_width=True)
    with c2:
        df_kv_d = df_kv.copy()
        df_kv_d["DT"] = df_kv_d["DT"].map(fmt_full)
        df_kv_d["LN"] = df_kv_d["LN"].map(fmt_full)
        st.dataframe(df_kv_d, use_container_width=True, hide_index=True)
```

# ══════════════════════════════════════════════════════════════

# TAB 2 - THỜI GIAN

# ══════════════════════════════════════════════════════════════

with tab_time:
st.markdown(f’<div class="section-title">📅 Xu hướng theo: {time_level_lbl}</div>’, unsafe_allow_html=True)

```
df_t = (df_ban.groupby(time_col)
        .agg(
            DT=("Thành tiền bán", "sum"),
            LN=("Lợi nhuận", "sum"),
            KL=("Khối lượng", lambda x: round(x.sum() / 1000, 3)),
            SL=("Số lượng", "sum"),
            N_CT=("Số chứng từ", "nunique") if "Số chứng từ" in df_ban.columns else ("Thành tiền bán", "count"),
            N_KH=("Tên khách hàng", "nunique")
        ).reset_index().sort_values(time_col))
df_t["Bien"] = (df_t["LN"] / df_t["DT"].replace(0, np.nan) * 100).round(2).fillna(0)
df_t["Tang_truong"] = (df_t["DT"].pct_change() * 100).round(1)

# Combined chart
fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True,
    subplot_titles=["Doanh thu & Lợi nhuận (VNĐ)",
                     f"Khối lượng (tấn)",
                     "Biên LN (%) & Tăng trưởng (%)"],
    vertical_spacing=0.1,
    row_heights=[0.45, 0.25, 0.3]
)

# Row 1
fig.add_trace(go.Bar(
    x=df_t[time_col], y=df_t["DT"], name="Doanh thu",
    marker_color="#388bfd", opacity=0.85
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=df_t[time_col], y=df_t["LN"], name="Lợi nhuận",
    mode="lines+markers", line=dict(color="#56d364", width=2.5),
    marker=dict(size=7, color="#56d364")
), row=1, col=1)

# Row 2
fig.add_trace(go.Bar(
    x=df_t[time_col], y=df_t["KL"], name="KL (tấn)",
    marker_color="#79c0ff", opacity=0.75
), row=2, col=1)

# Row 3
fig.add_trace(go.Scatter(
    x=df_t[time_col], y=df_t["Bien"], name="Biên LN (%)",
    mode="lines+markers+text",
    text=[f"{v:.1f}%" for v in df_t["Bien"]],
    textposition="top center",
    textfont=dict(size=10, color="#e3b341"),
    line=dict(color="#e3b341", width=2.5),
    marker=dict(size=7)
), row=3, col=1)
fig.add_trace(go.Bar(
    x=df_t[time_col], y=df_t["Tang_truong"],
    name="Tăng trưởng (%)",
    marker=dict(color=[
        "#56d364" if v >= 0 else "#ffa198"
        for v in df_t["Tang_truong"].fillna(0)
    ]),
    opacity=0.6
), row=3, col=1)

fig.update_layout(
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="Be Vietnam Pro", color="#c9d1d9", size=11),
    height=620, showlegend=True,
    legend=dict(bgcolor="#161b22", bordercolor="#21262d", borderwidth=1,
                orientation="h", y=-0.05, font=dict(size=11)),
    margin=dict(l=10, r=10, t=40, b=10)
)
fig.update_xaxes(gridcolor="#21262d", linecolor="#30363d")
fig.update_yaxes(gridcolor="#21262d", linecolor="#30363d")
for ann in fig.layout.annotations:
    ann.font.color = "#8b949e"
    ann.font.size  = 12
st.plotly_chart(fig, use_container_width=True)

# Table
df_t_d = df_t.copy()
df_t_d["DT"] = df_t_d["DT"].map(fmt_full)
df_t_d["LN"] = df_t_d["LN"].map(fmt_full)
cols_show = [time_col, "DT", "LN", "KL", "SL", "N_CT", "N_KH", "Bien"]
df_t_show = df_t_d[[c for c in cols_show if c in df_t_d.columns]].copy()
df_t_show.columns = [time_level_lbl, "DT (VNĐ)", "LN (VNĐ)", "KL (tấn)", "SL (cái)", "Số CT", "Số KH", "Biên (%)"][:len(df_t_show.columns)]
st.dataframe(df_t_show, use_container_width=True, hide_index=True)

# Heatmap KH × Tháng
if not single_kh and len(df_ban["Tên khách hàng"].unique()) > 1:
    st.markdown('<div class="section-title">🗓️ Heatmap DT: Khách hàng × Tháng</div>', unsafe_allow_html=True)
    df_hm = (df_ban.groupby(["Tên khách hàng", "Thang"])["Thành tiền bán"]
             .sum().reset_index())
    df_piv_hm = df_hm.pivot(index="Tên khách hàng", columns="Thang",
                              values="Thành tiền bán").fillna(0)
    top_kh = df_piv_hm.sum(axis=1).nlargest(min(20, len(df_piv_hm))).index
    fig_hm = px.imshow(
        df_piv_hm.loc[top_kh],
        color_continuous_scale=[[0, "#0d1117"], [0.3, "#1f3058"], [0.7, "#2d5ea8"], [1, "#388bfd"]],
        aspect="auto", title="Heatmap Doanh thu: Khách hàng × Tháng",
        labels=dict(color="DT (VNĐ)")
    )
    fig_hm.update_layout(**{**PLOTLY_LAYOUT,
                             "height": max(350, len(top_kh) * 26)})
    st.plotly_chart(fig_hm, use_container_width=True)
```

# ══════════════════════════════════════════════════════════════

# TAB 3 - SẢN PHẨM

# ══════════════════════════════════════════════════════════════

with tab_sp:
st.markdown(’<div class="section-title">📦 Cơ cấu Sản phẩm</div>’, unsafe_allow_html=True)

```
df_nhom = (df_ban.groupby("Nhom_SP")
           .agg(N=("Nhom_SP", "count"),
                KL=("Khối lượng", lambda x: round(x.sum() / 1000, 2)),
                DT=("Thành tiền bán", "sum"))
           .reset_index().sort_values("DT", ascending=False))

c1, c2 = st.columns(2)
with c1:
    fig_nhom_bar = go.Figure(go.Bar(
        x=df_nhom["Nhom_SP"], y=df_nhom["DT"],
        marker=dict(color=COLOR_SEQ[:len(df_nhom)]),
        text=[fmt(v) for v in df_nhom["DT"]],
        textposition="outside",
        textfont=dict(size=11, color="#c9d1d9")
    ))
    fig_nhom_bar.update_layout(**{**PLOTLY_LAYOUT,
                                   "title": "Doanh thu theo Nhóm SP", "height": 360,
                                   "showlegend": False, "xaxis_tickangle": -15})
    st.plotly_chart(fig_nhom_bar, use_container_width=True)

with c2:
    fig_nhom_pie = go.Figure(go.Pie(
        labels=df_nhom["Nhom_SP"], values=df_nhom["DT"],
        hole=0.55,
        marker=dict(colors=COLOR_SEQ[:len(df_nhom)],
                    line=dict(color="#0d1117", width=2)),
        textfont=dict(size=11, color="#f0f6fc"),
        textinfo="label+percent"
    ))
    fig_nhom_pie.update_layout(**{**PLOTLY_LAYOUT,
                                   "title": "Tỷ trọng DT theo Nhóm SP", "height": 360,
                                   "showlegend": True})
    st.plotly_chart(fig_nhom_pie, use_container_width=True)

# Top 15 SP
if "Tên hàng" in df_ban.columns:
    st.markdown('<div class="section-title">🏆 Top 15 Sản phẩm & Xu hướng</div>', unsafe_allow_html=True)
    df_top_sp = (df_ban.groupby("Tên hàng")
                 .agg(N=("Tên hàng", "count"),
                      KL=("Khối lượng", lambda x: round(x.sum() / 1000, 2)),
                      DT=("Thành tiền bán", "sum"),
                      LN=("Lợi nhuận", "sum"))
                 .reset_index().sort_values("DT", ascending=False).head(15))
    df_top_sp["Bien"] = (df_top_sp["LN"] / df_top_sp["DT"].replace(0, np.nan) * 100).round(1).fillna(0)
    df_top_sp_sorted = df_top_sp.sort_values("DT", ascending=True)

    fig_sp = go.Figure(go.Bar(
        y=df_top_sp_sorted["Tên hàng"],
        x=df_top_sp_sorted["DT"],
        orientation="h",
        marker=dict(
            color=df_top_sp_sorted["Bien"],
            colorscale=[[0, "#ffa198"], [0.3, "#e3b341"], [0.7, "#3fb950"], [1, "#56d364"]],
            colorbar=dict(title="Biên LN %", tickfont=dict(color="#c9d1d9"), titlefont=dict(color="#c9d1d9")),
            showscale=True
        ),
        text=[fmt(v) for v in df_top_sp_sorted["DT"]],
        textposition="outside",
        textfont=dict(size=10, color="#c9d1d9")
    ))
    fig_sp.update_layout(**{**PLOTLY_LAYOUT,
                              "title": "Top 15 Sản phẩm - Doanh thu (màu = Biên LN%)",
                              "height": 520,
                              "xaxis": dict(gridcolor="#21262d"),
                              "yaxis": dict(tickfont=dict(size=10), gridcolor="#21262d")})
    st.plotly_chart(fig_sp, use_container_width=True)

    # Trend top 5
    top5 = df_top_sp["Tên hàng"].head(5).tolist()
    df_tr = (df_ban[df_ban["Tên hàng"].isin(top5)]
             .groupby(["Tên hàng", time_col])["Thành tiền bán"].sum().reset_index())
    if not df_tr.empty:
        fig_tr = px.line(
            df_tr, x=time_col, y="Thành tiền bán", color="Tên hàng",
            markers=True,
            title=f"Xu hướng Top 5 SP theo {time_level_lbl}",
            labels={"Thành tiền bán": "DT (VNĐ)", time_col: time_level_lbl},
            color_discrete_sequence=COLOR_SEQ
        )
        fig_tr.update_traces(line=dict(width=2.5), marker=dict(size=8))
        fig_tr.update_layout(**{**PLOTLY_LAYOUT, "height": 380})
        st.plotly_chart(fig_tr, use_container_width=True)

# Nhận định mục đích
st.markdown('<div class="section-title">🎯 Nhận định mục đích sử dụng</div>', unsafe_allow_html=True)
nhom_set = set(df_nhom["Nhom_SP"].tolist())
nhom_info = {
    "Ống HDPE":        ("info",   "🔵 <b>Ống HDPE</b>: Dự án hạ tầng cấp thoát nước, thuỷ lợi công trình lớn."),
    "Ống PVC nước":    ("low",    "🟢 <b>Ống PVC nước</b>: Xây dựng dân dụng, công nghiệp, khu công nghiệp."),
    "Ống PVC bơm cát": ("low",    "🟡 <b>Ống PVC bơm cát</b>: Thuỷ lợi, nông nghiệp, nuôi trồng thuỷ sản."),
    "Ống PPR":         ("info",   "🟠 <b>Ống PPR</b>: Hệ thống nước nóng/lạnh nội thất."),
    "Lõi PVC":         ("medium", "⚪ <b>Lõi PVC</b>: Có thể là đại lý hoặc nhà SX thứ cấp."),
    "Phụ kiện & Keo":  ("low",    "🔴 <b>Phụ kiện & Keo</b>: Tự thi công hoặc bán lại trọn gói."),
}
for k, (lvl, msg) in nhom_info.items():
    if k in nhom_set:
        st.markdown(f'<div class="risk-{lvl}">{msg}</div>', unsafe_allow_html=True)
```

# ══════════════════════════════════════════════════════════════

# TAB 4 - LỢI NHUẬN

# ══════════════════════════════════════════════════════════════

with tab_ln:
st.markdown(’<div class="section-title">💹 Lợi nhuận & Phát hiện Chính sách</div>’, unsafe_allow_html=True)

```
df_ln_t = (df_ban.groupby(time_col)
           .agg(DT=("Thành tiền bán", "sum"),
                Von=("Thành tiền vốn", "sum"),
                LN=("Lợi nhuận", "sum"))
           .reset_index().sort_values(time_col))
df_ln_t["Bien"] = (df_ln_t["LN"] / df_ln_t["DT"].replace(0, np.nan) * 100).round(2).fillna(0)

fig_ln = make_subplots(
    rows=2, cols=1, shared_xaxes=True,
    subplot_titles=["DT / Vốn / LN (VNĐ)", f"Biên LN (%) theo {time_level_lbl}"],
    vertical_spacing=0.14,
    row_heights=[0.6, 0.4]
)
fig_ln.add_trace(go.Bar(
    x=df_ln_t[time_col], y=df_ln_t["DT"], name="Doanh thu",
    marker_color="#388bfd", opacity=0.8
), row=1, col=1)
fig_ln.add_trace(go.Bar(
    x=df_ln_t[time_col], y=df_ln_t["Von"], name="Giá vốn",
    marker_color="#e05c5c", opacity=0.7
), row=1, col=1)
fig_ln.add_trace(go.Scatter(
    x=df_ln_t[time_col], y=df_ln_t["LN"], name="Lợi nhuận",
    mode="lines+markers", line=dict(color="#56d364", width=2.5),
    marker=dict(size=8)
), row=1, col=1)
fig_ln.add_trace(go.Scatter(
    x=df_ln_t[time_col], y=df_ln_t["Bien"], name="Biên LN (%)",
    mode="lines+markers+text",
    text=[f"{v:.1f}%" for v in df_ln_t["Bien"]],
    textposition="top center",
    textfont=dict(size=10, color="#e3b341"),
    line=dict(color="#e3b341", width=2.5),
    marker=dict(size=8),
    fill="tozeroy", fillcolor="rgba(227,179,65,0.08)"
), row=2, col=1)

fig_ln.update_layout(
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="Be Vietnam Pro", color="#c9d1d9", size=11),
    height=520, barmode="group",
    legend=dict(bgcolor="#161b22", bordercolor="#21262d", orientation="h", y=-0.05),
    margin=dict(l=10, r=10, t=40, b=10)
)
fig_ln.update_xaxes(gridcolor="#21262d", linecolor="#30363d")
fig_ln.update_yaxes(gridcolor="#21262d", linecolor="#30363d")
for ann in fig_ln.layout.annotations:
    ann.font.color = "#8b949e"
    ann.font.size  = 12
st.plotly_chart(fig_ln, use_container_width=True)

# Kỳ bất thường
if len(df_ln_t) >= 2:
    mb = df_ln_t["Bien"].mean()
    sb = df_ln_t["Bien"].std() or 1
    anom = df_ln_t[df_ln_t["Bien"] < mb - sb * 1.5]
    if not anom.empty:
        st.markdown('<div class="section-title">🔍 Kỳ nghi có Chiết khấu / Chính sách đặc biệt</div>', unsafe_allow_html=True)
        for _, r in anom.iterrows():
            st.markdown(
                f'<div class="risk-high">🔴 <b>{r[time_col]}</b>: Biên LN = {r["Bien"]:.1f}% '
                f'(TB: {mb:.1f}%) → Nghi chiết khấu lớn hoặc giá đặc biệt</div>',
                unsafe_allow_html=True
            )

# Giá bán < Giá vốn
st.markdown('<div class="section-title">❗ Dòng Giá bán < Giá vốn (Bán lỗ)</div>', unsafe_allow_html=True)
if "Giá bán" in df_ban.columns and "Giá vốn" in df_ban.columns:
    df_lo = df_ban[
        (df_ban["Giá bán"] > 0) &
        (df_ban["Giá vốn"] > 0) &
        (df_ban["Giá bán"] < df_ban["Giá vốn"])
    ]
    if not df_lo.empty:
        st.error(f"⚠️ {len(df_lo)} dòng có giá bán < giá vốn")
        cols_lo = [c for c in ["Ngày chứng từ", "Tên khách hàng", "Tên hàng",
                                "Giá bán", "Giá vốn", "Lợi nhuận", "Ghi chú"] if c in df_lo.columns]
        st.dataframe(df_lo[cols_lo], use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="risk-low">✅ Không có dòng nào giá bán thấp hơn giá vốn.</div>', unsafe_allow_html=True)

# Trả hàng
df_tra = df_scope[df_scope["Loai_GD"] == "Trả hàng"]
if not df_tra.empty:
    st.markdown('<div class="section-title">↩️ Hàng trả lại</div>', unsafe_allow_html=True)
    tong_tra_val = abs(df_tra["Thành tiền bán"].sum())
    st.error(f"Tổng giá trị trả hàng: {fmt_full(tong_tra_val)} VNĐ ({len(df_tra)} dòng)")
    cols_tr = [c for c in ["Số chứng từ", "Ngày chứng từ", "Tên khách hàng",
                            "Tên hàng", "Thành tiền bán", "Ghi chú"] if c in df_tra.columns]
    df_tra_d = df_tra[cols_tr].copy()
    if "Thành tiền bán" in df_tra_d.columns:
        df_tra_d["Thành tiền bán"] = df_tra_d["Thành tiền bán"].map(fmt_full)
    st.dataframe(df_tra_d, use_container_width=True, hide_index=True)
```

# ══════════════════════════════════════════════════════════════

# TAB 5 - GIAO HÀNG

# ══════════════════════════════════════════════════════════════

with tab_giao:
st.markdown(’<div class="section-title">🚚 Hình thức & Địa điểm giao hàng</div>’, unsafe_allow_html=True)

```
c1, c2 = st.columns(2)
with c1:
    if "Freight Terms" in df_ban.columns:
        ft = df_ban["Freight Terms"].dropna().value_counts().reset_index()
        ft.columns = ["Hình thức", "Số lần"]
        if not ft.empty:
            fig_ft = go.Figure(go.Pie(
                labels=ft["Hình thức"], values=ft["Số lần"],
                hole=0.55,
                marker=dict(colors=COLOR_SEQ[:len(ft)], line=dict(color="#0d1117", width=2)),
                textfont=dict(size=11), textinfo="label+percent"
            ))
            fig_ft.update_layout(**{**PLOTLY_LAYOUT,
                                     "title": "Điều kiện giao hàng", "height": 360, "showlegend": False})
            st.plotly_chart(fig_ft, use_container_width=True)
with c2:
    if "Shipping method" in df_ban.columns:
        sm = df_ban["Shipping method"].dropna().value_counts().reset_index()
        sm.columns = ["Phương tiện", "Số lần"]
        if not sm.empty:
            fig_sm = go.Figure(go.Pie(
                labels=sm["Phương tiện"], values=sm["Số lần"],
                hole=0.55,
                marker=dict(colors=COLOR_SEQ[:len(sm)], line=dict(color="#0d1117", width=2)),
                textfont=dict(size=11), textinfo="label+percent"
            ))
            fig_sm.update_layout(**{**PLOTLY_LAYOUT,
                                     "title": "Phương tiện vận chuyển", "height": 360, "showlegend": False})
            st.plotly_chart(fig_sm, use_container_width=True)

if "Nơi giao hàng" in df_ban.columns:
    st.markdown('<div class="section-title">📍 Địa điểm giao hàng</div>', unsafe_allow_html=True)
    df_noi = (df_ban.groupby("Nơi giao hàng")
              .agg(N=("Nơi giao hàng", "count"),
                   KL=("Khối lượng", lambda x: round(x.sum() / 1000, 2)),
                   DT=("Thành tiền bán", "sum"))
              .reset_index().sort_values("DT", ascending=False).head(20))
    df_noi_sorted = df_noi.sort_values("DT", ascending=True)
    fig_noi = go.Figure(go.Bar(
        y=df_noi_sorted["Nơi giao hàng"],
        x=df_noi_sorted["DT"],
        orientation="h",
        marker=dict(color="#79c0ff", opacity=0.85),
        text=[fmt(v) for v in df_noi_sorted["DT"]],
        textposition="outside",
        textfont=dict(size=10)
    ))
    fig_noi.update_layout(**{**PLOTLY_LAYOUT,
                               "title": "Top 20 Địa điểm giao hàng theo DT", "height": max(380, len(df_noi_sorted)*30)})
    st.plotly_chart(fig_noi, use_container_width=True)

if "Mã kho" in df_ban.columns:
    st.markdown('<div class="section-title">🏭 Kho xuất hàng</div>', unsafe_allow_html=True)
    df_kho = (df_ban.groupby("Mã kho")
              .agg(N=("Mã kho", "count"),
                   DT=("Thành tiền bán", "sum"),
                   KL=("Khối lượng", lambda x: round(x.sum() / 1000, 2)))
              .reset_index().sort_values("DT", ascending=False))
    df_kho_d = df_kho.copy()
    df_kho_d["DT"] = df_kho_d["DT"].map(fmt_full)
    st.dataframe(df_kho_d, use_container_width=True, hide_index=True)
    if df_ban["Mã kho"].nunique() >= 2:
        st.markdown('<div class="risk-medium">🟡 KH nhận hàng từ nhiều kho - kiểm tra giá xuất kho & tính nhất quán.</div>', unsafe_allow_html=True)

with st.expander("🚛 Danh sách xe & tài xế"):
    xe_cols = [c for c in ["Số xe", "Tài Xế", "Tên ĐVVC", "Shipping method",
                            "Ngày chứng từ", "Nơi giao hàng"] if c in df_ban.columns]
    if xe_cols:
        st.dataframe(df_ban[xe_cols].drop_duplicates().sort_values("Ngày chứng từ"),
                     use_container_width=True, hide_index=True)
```

# ══════════════════════════════════════════════════════════════

# TAB 6 - TẦN SUẤT

# ══════════════════════════════════════════════════════════════

with tab_freq:
if “Tên hàng” in df_ban.columns:
st.markdown(’<div class="section-title">🔁 Heatmap tần suất: Sản phẩm × Tháng</div>’, unsafe_allow_html=True)
df_fr  = df_ban.groupby([“Tên hàng”, “Thang”]).size().reset_index(name=“N”)
df_piv = df_fr.pivot(index=“Tên hàng”, columns=“Thang”, values=“N”).fillna(0)
top_n  = df_piv.sum(axis=1).nlargest(min(25, len(df_piv))).index

```
    fig_freq = px.imshow(
        df_piv.loc[top_n],
        labels=dict(x="Tháng", y="Sản phẩm", color="Số lần"),
        title="Heatmap tần suất - Top SP × Tháng",
        color_continuous_scale=[[0,"#0d1117"],[0.3,"#1f3058"],[0.7,"#2d5ea8"],[1,"#388bfd"]],
        aspect="auto"
    )
    fig_freq.update_layout(**{**PLOTLY_LAYOUT,
                                "height": max(400, len(top_n) * 22)})
    st.plotly_chart(fig_freq, use_container_width=True)

    st.markdown('<div class="section-title">📋 Chi tiết theo Quý</div>', unsafe_allow_html=True)
    for q in sorted(df_ban["Quy"].dropna().unique()):
        df_q   = df_ban[df_ban["Quy"] == q]
        months = sorted(df_q["Thang"].dropna().unique())
        with st.expander(f"📅 {q}  |  {', '.join(months)}"):
            agg = (df_q.groupby(["Tên hàng", "Thang"])
                   .agg(N=("Tên hàng", "count"),
                        KL=("Khối lượng", lambda x: round(x.sum() / 1000, 2)),
                        DT=("Thành tiền bán", "sum"))
                   .reset_index().sort_values("DT", ascending=False))
            agg_d = agg.copy()
            agg_d["DT"] = agg_d["DT"].map(fmt_full)
            agg_d.columns = ["Sản phẩm", "Tháng", "Số lần", "KL (tấn)", "DT (VNĐ)"]
            st.dataframe(agg_d, use_container_width=True, hide_index=True)
else:
    st.info("Không có cột 'Tên hàng' trong dữ liệu.")
```

# ══════════════════════════════════════════════════════════════

# TAB 7 - RỦI RO

# ══════════════════════════════════════════════════════════════

with tab_risk:
st.markdown(’<div class="section-title">⚠️ Nhận diện Rủi ro & Bất thường (12 nhóm)</div>’, unsafe_allow_html=True)

```
risks = []
score = 0
tong_dt_ban = df_ban["Thành tiền bán"].sum()
tong_ln_ban = df_ban["Lợi nhuận"].sum()
bien_tb     = (tong_ln_ban / tong_dt_ban * 100) if tong_dt_ban else 0

# R1 - Trả hàng
df_tra_r = df_scope[df_scope["Loai_GD"] == "Trả hàng"]
tong_tra_r = abs(df_tra_r["Thành tiền bán"].sum())
tl_tra_r   = (tong_tra_r / tong_dt_ban * 100) if tong_dt_ban else 0
if tl_tra_r > 10:
    score += 30
    risks.append(("high", "↩️ Trả hàng",
                   f"Tỷ lệ trả hàng <b>{tl_tra_r:.1f}%</b> ({fmt_full(tong_tra_r)} VNĐ) -- Rủi ro tranh chấp cao",
                   df_tra_r))
elif tl_tra_r > 3:
    score += 15
    risks.append(("medium", "↩️ Trả hàng",
                   f"Tỷ lệ trả hàng <b>{tl_tra_r:.1f}%</b> -- Cần theo dõi", df_tra_r))
else:
    risks.append(("low", "↩️ Trả hàng",
                   f"Tỷ lệ trả hàng thấp: {tl_tra_r:.1f}% ✓", None))

# R2 - Bán lỗ
if "Giá bán" in df_ban.columns and "Giá vốn" in df_ban.columns:
    df_lo_r = df_ban[
        (df_ban["Giá bán"] > 0) & (df_ban["Giá vốn"] > 0) &
        (df_ban["Giá bán"] < df_ban["Giá vốn"])
    ]
    if not df_lo_r.empty:
        score += 25
        risks.append(("high", "💸 Bán lỗ trực tiếp",
                       f"<b>{len(df_lo_r)}</b> dòng giá bán < giá vốn -- bán lỗ hoặc sai dữ liệu", df_lo_r))
    else:
        risks.append(("low", "💸 Giá bán vs Giá vốn", "Không có dòng nào giá bán < giá vốn ✓", None))

# R3 - LN âm
df_ln_am_r = df_ban[df_ban["Lợi nhuận"] < 0]
if not df_ln_am_r.empty:
    score += 20
    risks.append(("high", "📉 Lợi nhuận âm",
                   f"<b>{len(df_ln_am_r)}</b> dòng xuất bán có LN âm (tổng: -{fmt_full(abs(df_ln_am_r['Lợi nhuận'].sum()))} VNĐ)",
                   df_ln_am_r))
else:
    risks.append(("low", "📉 Lợi nhuận âm", "Không có dòng xuất bán nào bị lỗ ✓", None))

# R4 - Biên LN bất thường
if len(df_ln_t) >= 2:
    mb2 = df_ln_t["Bien"].mean()
    sb2 = df_ln_t["Bien"].std() or 1
    anom_k = df_ln_t[df_ln_t["Bien"] < mb2 - sb2 * 1.5]
    if not anom_k.empty:
        ky_str = ", ".join(anom_k[time_col].tolist())
        score += 10
        risks.append(("medium", "📊 Biên LN bất thường",
                       f"Kỳ <b>{ky_str}</b> biên LN thấp bất thường → nghi chiết khấu đặc biệt", None))
    else:
        risks.append(("low", "📊 Biên LN", "Biên LN ổn định ✓", None))

# R5 - Tập trung cuối tháng
dt_cuoi   = df_ban[df_ban["Cuoi_thang"] == True]["Thành tiền bán"].sum()
tl_cuoi   = (dt_cuoi / tong_dt_ban * 100) if tong_dt_ban else 0
if tl_cuoi > 40:
    score += 15
    risks.append(("high", "📅 Tập trung cuối tháng",
                   f"<b>{tl_cuoi:.1f}%</b> DT tập trung ngày 28-31 -- nghi đẩy doanh số ảo", None))
elif tl_cuoi > 25:
    score += 8
    risks.append(("medium", "📅 Tập trung cuối tháng",
                   f"{tl_cuoi:.1f}% DT cuối tháng -- cần kiểm tra thực chất", None))
else:
    risks.append(("low", "📅 Phân bổ thời gian", f"Đơn hàng phân bổ đều ✓ (cuối tháng: {tl_cuoi:.1f}%)", None))

# R6 - Outlier
q1v = df_ban["Thành tiền bán"].quantile(0.25)
q3v = df_ban["Thành tiền bán"].quantile(0.75)
iqr = q3v - q1v
if iqr > 0:
    df_out_r = df_ban[df_ban["Thành tiền bán"] > q3v + 3 * iqr]
    if not df_out_r.empty:
        score += 10
        risks.append(("medium", "📦 Đơn giá trị lớn bất thường",
                       f"<b>{len(df_out_r)}</b> đơn vượt 3×IQR -- kiểm soát hạn mức tín dụng", df_out_r))
    else:
        risks.append(("low", "📦 Quy mô đơn hàng", "Không có đơn bất thường về giá trị ✓", None))

# R7 - Bổ sung
df_bs_r = df_scope[df_scope["Loai_GD"] == "Xuất bổ sung"]
if not df_bs_r.empty:
    score += 12
    risks.append(("medium", "🔄 Xuất bổ sung/thay thế",
                   f"<b>{len(df_bs_r)}</b> dòng xuất bổ sung -- giao nhầm, thiếu hoặc hàng lỗi", df_bs_r))
else:
    risks.append(("low", "🔄 Xuất bổ sung", "Không có đơn bổ sung ✓", None))

# R8 - Giao phân tán
if "Nơi giao hàng" in df_ban.columns:
    n_noi = df_ban["Nơi giao hàng"].nunique()
    if n_noi >= 6:
        score += 10
        risks.append(("medium", "📍 Giao hàng phân tán",
                       f"Giao tới <b>{n_noi}</b> địa điểm -- rủi ro phân tán công nợ", None))
    else:
        risks.append(("low", "📍 Địa điểm giao hàng", f"{n_noi} địa điểm -- bình thường ✓", None))

# R9 - Nhiều kho
if "Mã kho" in df_ban.columns and df_ban["Mã kho"].nunique() >= 2:
    score += 5
    risks.append(("medium", "🏭 Nhiều kho xuất hàng",
                   f"KH nhận từ <b>{df_ban['Mã kho'].nunique()}</b> kho -- kiểm tra giá & nhất quán", None))
else:
    risks.append(("low", "🏭 Kho xuất hàng", "Xuất từ 1 kho ✓", None))

# R10 - Tần suất không đều
n_thang_mua = df_ban["Thang"].nunique()
delta_days  = (df_ban["Ngày chứng từ"].max() - df_ban["Ngày chứng từ"].min()).days
n_thang_rng = max(delta_days // 30, 1)
if n_thang_mua / n_thang_rng < 0.5:
    score += 10
    risks.append(("medium", "🔁 Mua hàng không đều",
                   f"Chỉ mua <b>{n_thang_mua}/{n_thang_rng}</b> tháng -- phụ thuộc dự án", None))
else:
    risks.append(("low", "🔁 Tần suất mua", f"Mua đều: {n_thang_mua} tháng có GD ✓", None))

# R11 - Biên LN thấp
if bien_tb < 5:
    score += 20
    risks.append(("high", "💹 Biên LN tổng thấp",
                   f"Biên LN = <b>{bien_tb:.1f}%</b> -- nguy cơ bán phá giá hoặc chiết khấu quá mức", None))
elif bien_tb < 15:
    score += 8
    risks.append(("medium", "💹 Biên LN tổng",
                   f"Biên LN = <b>{bien_tb:.1f}%</b> -- mức thấp, cần theo dõi", None))
else:
    risks.append(("low", "💹 Biên LN tổng", f"Biên LN = {bien_tb:.1f}% ✓", None))

# R12 - PO/Dự án
if "Ghi chú" in df_scope.columns:
    gc2   = df_scope["Ghi chú"].astype(str).str.upper()
    df_po = df_scope[gc2.str.contains(r"PO|B[0-9]{3}|HỢP ĐỒNG", regex=True, na=False)]
    if not df_po.empty:
        score += 8
        n_po  = df_po["Số chứng từ"].nunique() if "Số chứng từ" in df_po.columns else len(df_po)
        risks.append(("medium", "📄 Đơn PO/Dự án",
                       f"<b>{n_po}</b> CT có PO/HĐ ({fmt_full(abs(df_po['Thành tiền bán'].sum()))} VNĐ) -- thanh toán chậm NET 30-90 ngày",
                       df_po))

# Score display
n_high   = sum(1 for l, _, _, _ in risks if l == "high")
n_medium = sum(1 for l, _, _, _ in risks if l == "medium")
n_low    = sum(1 for l, _, _, _ in risks if l == "low")

if score >= 60:
    color, label = "#ffa198", "🔴 RỦI RO CAO"
    bg_color = "rgba(218,54,51,0.1)"
elif score >= 30:
    color, label = "#e3b341", "🟡 RỦI RO TRUNG BÌNH"
    bg_color = "rgba(187,128,9,0.1)"
else:
    color, label = "#56d364", "🟢 RỦI RO THẤP"
    bg_color = "rgba(35,134,54,0.1)"

st.markdown(f"""
<div style='background:{bg_color};border:1px solid {color};border-radius:12px;
            padding:24px;text-align:center;margin:10px 0 20px 0;'>
    <div style='font-size:28px;font-weight:900;color:{color};letter-spacing:0.03em;'>{label}</div>
    <div style='font-size:15px;color:#8b949e;margin-top:10px;'>
        Điểm rủi ro tổng hợp: <b style='color:{color};font-size:18px;'>{score} / 130</b>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        🔴 {n_high} cao &nbsp; 🟡 {n_medium} trung bình &nbsp; 🟢 {n_low} thấp
    </div>
</div>
""", unsafe_allow_html=True)

# Score bar visual
pct = min(score / 130 * 100, 100)
bar_color = "#ffa198" if score >= 60 else ("#e3b341" if score >= 30 else "#56d364")
st.markdown(f"""
<div style='background:#161b22;border-radius:6px;height:8px;margin:-10px 0 20px 0;overflow:hidden;'>
    <div style='background:{bar_color};width:{pct:.0f}%;height:100%;border-radius:6px;
                transition:width 0.5s ease;'></div>
</div>
""", unsafe_allow_html=True)

# Risk list
for lvl, cat, msg, detail in risks:
    st.markdown(f'<div class="risk-{lvl}"><b>[{cat}]</b>&nbsp; {msg}</div>', unsafe_allow_html=True)
    if detail is not None and not detail.empty and lvl in ["high", "medium"]:
        show_c = [c for c in ["Số chứng từ", "Ngày chứng từ", "Tên khách hàng", "Tên hàng",
                               "Thành tiền bán", "Lợi nhuận", "Giá bán", "Giá vốn", "Ghi chú"]
                  if c in detail.columns]
        with st.expander(f"📋 Chi tiết - {cat} ({len(detail)} dòng)"):
            d2 = detail[show_c].head(50).copy()
            for c in ["Thành tiền bán", "Lợi nhuận", "Giá bán", "Giá vốn"]:
                if c in d2.columns:
                    d2[c] = d2[c].map(fmt_full)
            st.dataframe(d2, use_container_width=True, hide_index=True)

# BCCN note
st.markdown("---")
st.markdown('<div class="section-title">📄 BCCN - Lưu ý Thanh toán & Công nợ</div>', unsafe_allow_html=True)
st.markdown("""
<div class="risk-info">
⚠️ File OM_RPT_055 <b>không chứa ngày thanh toán thực tế</b>. Để phân tích BCCN đầy đủ cần bổ sung:<br>
&nbsp;&nbsp;• <b>Sổ AR Aging</b> → số ngày tồn đọng, quá hạn, hạn mức tín dụng<br>
&nbsp;&nbsp;• <b>Lịch sử thanh toán</b> → thói quen NET 30/60/90<br><br>
<b>Dấu hiệu từ dữ liệu hiện có:</b><br>
&nbsp;&nbsp;• Ghi chú <b>B-xxx / PO</b> → đơn dự án → thanh toán chậm, phụ thuộc chủ đầu tư<br>
&nbsp;&nbsp;• <b>Trả hàng</b> → tranh chấp → kéo dài công nợ<br>
&nbsp;&nbsp;• <b>Nhiều địa điểm giao</b> → công nợ phân tán nhiều công trình<br>
&nbsp;&nbsp;• <b>Đơn cuối tháng giá trị lớn</b> → kiểm tra giao nhận trước khi ghi nhận DT
</div>
""", unsafe_allow_html=True)
```