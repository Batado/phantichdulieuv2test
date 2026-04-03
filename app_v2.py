import io
import warnings
warnings.filterwarnings(“ignore”)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
page_title=“Phan tich KH - Hoa Sen”,
layout=“wide”,
page_icon=”=”,
initial_sidebar_state=“expanded”
)

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#0d1117 0%,#161b22 100%); border-right:1px solid #21262d; }
section[data-testid="stSidebar"] * { color:#c9d1d9 !important; }
.stApp { background:#0d1117; }
.risk-high   { background:rgba(218,54,51,0.12);  border-left:3px solid #da3633; padding:10px 16px; border-radius:6px; margin:5px 0; color:#ffa198; }
.risk-medium { background:rgba(187,128,9,0.12);  border-left:3px solid #bb8009; padding:10px 16px; border-radius:6px; margin:5px 0; color:#e3b341; }
.risk-low    { background:rgba(35,134,54,0.12);  border-left:3px solid #238636; padding:10px 16px; border-radius:6px; margin:5px 0; color:#56d364; }
.risk-info   { background:rgba(31,111,235,0.12); border-left:3px solid #1f6feb; padding:10px 16px; border-radius:6px; margin:5px 0; color:#79c0ff; }
.section-title { font-size:14px; font-weight:700; color:#8b949e; margin:22px 0 10px 0; padding-bottom:6px; border-bottom:1px solid #21262d; text-transform:uppercase; letter-spacing:0.05em; }
.kpi-card { background:linear-gradient(135deg,#161b22 0%,#1c2128 100%); border:1px solid #21262d; border-radius:10px; padding:16px 20px; }
.kpi-val  { font-size:20px; font-weight:800; color:#f0f6fc; line-height:1.2; }
.kpi-lab  { font-size:11px; color:#6e7681; margin-top:4px; font-weight:500; }
.page-title { font-size:26px; font-weight:800; color:#f0f6fc; padding:6px 0 2px 0; }
.page-sub   { font-size:13px; color:#6e7681; margin-bottom:18px; }
.stTabs [data-baseweb="tab-list"] { background:#161b22; border-radius:8px; padding:4px; gap:4px; border:1px solid #21262d; }
.stTabs [data-baseweb="tab"]      { background:transparent; color:#8b949e; border-radius:6px; font-weight:600; font-size:13px; }
.stTabs [aria-selected="true"]    { background:#21262d !important; color:#f0f6fc !important; }
</style>

“””, unsafe_allow_html=True)

NHOM_SP = [
(“Ong HDPE”,        r”HDPE”),
(“Ong PVC nuoc”,    r”PVC.*(?:nuoc|nong dai|nong tron|thoat|cap)”),
(“Ong PVC bom cat”, r”PVC.*(?:cat|bom cat)”),
(“Ong PPR”,         r”PPR”),
(“Loi PVC”,         r”(?:Loi|lori)”),
(“Phu kien & Keo”,  r”(?:Noi|Co |Te |Van |Keo |Mang|Bit|Y PVC|Y PPR|Giam|Cut)”),
]

COLORS = [”#388bfd”,”#56d364”,”#e3b341”,”#ffa198”,”#79c0ff”,”#d2a8ff”,”#ffb800”,”#3fb950”]

BASE_LAYOUT = dict(
paper_bgcolor=”#0d1117”,
plot_bgcolor=”#0d1117”,
font=dict(family=“Be Vietnam Pro, sans-serif”, color=”#c9d1d9”, size=12),
title_font=dict(size=14, color=”#f0f6fc”),
legend=dict(bgcolor=”#161b22”, bordercolor=”#21262d”, borderwidth=1, font=dict(size=11, color=”#c9d1d9”)),
margin=dict(l=10, r=10, t=45, b=10),
xaxis=dict(gridcolor=”#21262d”, linecolor=”#30363d”, tickfont=dict(size=11)),
yaxis=dict(gridcolor=”#21262d”, linecolor=”#30363d”, tickfont=dict(size=11)),
)

def fmt(v):
try:
f = float(v)
if abs(f) >= 1e9: return f”{f/1e9:,.2f} ty”
if abs(f) >= 1e6: return f”{f/1e6:,.1f} tr”
return f”{f:,.0f}”
except Exception:
return str(v)

def fmt_full(v):
try: return f”{float(v):,.0f}”
except Exception: return str(v)

def get_num(df, col):
if col in df.columns:
return pd.to_numeric(df[col], errors=“coerce”).fillna(0)
return pd.Series(0.0, index=df.index)

def find_header_row(fb):
try:
raw = pd.read_excel(io.BytesIO(fb), header=None, engine=“openpyxl”, nrows=40)
except Exception:
return 0
kws = [“so chung tu”, “ngay chung tu”, “ma nhom kh”, “ten khach hang”, “thanh tien ban”]
for i in range(raw.shape[0]):
vals = [str(v).strip().lower() for v in raw.iloc[i].tolist() if str(v).strip() not in (””, “nan”)]
row_text = “ “.join(vals)
hits = sum(1 for k in kws if k in row_text)
if hits >= 2:
return i
return 0

def normalize_str(s):
import unicodedata
s = unicodedata.normalize(“NFC”, str(s))
s = s.lower().strip()
replacements = [
(“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”,“a”),
]
vmap = {
“à”:  “a”, “á”:  “a”, “â”:  “a”, “ã”:  “a”,
“ä”:  “a”, “å”:  “a”, “ă”:  “a”, “ǎ”:  “a”,
“ạ”:  “a”, “ả”:  “a”, “ấ”:  “a”, “ầ”:  “a”,
“ẩ”:  “a”, “ẫ”:  “a”, “ậ”:  “a”, “ắ”:  “a”,
“ằ”:  “a”, “ẳ”:  “a”, “ẵ”:  “a”, “ặ”:  “a”,
“è”:  “e”, “é”:  “e”, “ê”:  “e”, “ẹ”:  “e”,
“ẻ”:  “e”, “ẽ”:  “e”, “ế”:  “e”, “ề”:  “e”,
“ể”:  “e”, “ễ”:  “e”, “ệ”:  “e”,
“ì”:  “i”, “í”:  “i”, “ĩ”:  “i”, “ỉ”:  “i”, “ị”:  “i”,
“ò”:  “o”, “ó”:  “o”, “ô”:  “o”, “õ”:  “o”,
“ơ”:  “o”, “ọ”:  “o”, “ỏ”:  “o”, “ố”:  “o”,
“ồ”:  “o”, “ổ”:  “o”, “ỗ”:  “o”, “ộ”:  “o”,
“ớ”:  “o”, “ờ”:  “o”, “ở”:  “o”, “ỡ”:  “o”,
“ợ”:  “o”,
“ù”:  “u”, “ú”:  “u”, “ũ”:  “u”, “ư”:  “u”,
“ụ”:  “u”, “ủ”:  “u”, “ứ”:  “u”, “ừ”:  “u”,
“ử”:  “u”, “ữ”:  “u”, “ự”:  “u”,
“ỳ”:  “y”, “ý”:  “y”, “ỵ”:  “y”, “ỷ”:  “y”, “ỹ”:  “y”,
“đ”:  “d”, “ự”:  “u”,
}
result = “”
for c in s:
result += vmap.get(c, c)
return result

COL_MAP = {
“so chung tu”:     “So chung tu”,
“ngay chung tu”:   “Ngay chung tu”,
“loai don hang”:   “Loai don hang”,
“khu vuc”:         “Khu vuc”,
“ma nhom kh”:      “Ma nhom KH”,
“ten nhom kh”:     “Ten nhom KH”,
“ma khach hang”:   “Ma khach hang”,
“ten khach hang”:  “Ten khach hang”,
“noi giao hang”:   “Noi giao hang”,
“ma kho”:          “Ma kho”,
“ma nhom hang”:    “Ma nhom hang”,
“ma hang”:         “Ma hang”,
“ten hang”:        “Ten hang”,
“khoi luong”:      “Khoi luong”,
“so luong”:        “So luong”,
“gia von”:         “Gia von”,
“thanh tien von”:  “Thanh tien von”,
“gia ban”:         “Gia ban”,
“don gia quy doi”: “Don gia quy doi”,
“don gia van chuyen”: “Don gia van chuyen”,
“thanh tien ban”:  “Thanh tien ban”,
“loi nhuan”:       “Loi nhuan”,
“freight terms”:   “Freight Terms”,
“shipping method”: “Shipping method”,
“so xe”:           “So xe”,
“tai xe”:          “Tai xe”,
“ghi chu”:         “Ghi chu”,
}

def map_columns(df):
rename = {}
for col in df.columns:
norm = normalize_str(col)
if norm in COL_MAP:
rename[col] = COL_MAP[norm]
if rename:
df = df.rename(columns=rename)
return df

def load_all(file_data):
frames, errs = [], []
for name, fb in file_data:
try:
hr = find_header_row(fb)
df = pd.read_excel(io.BytesIO(fb), header=hr, engine=“openpyxl”)
df.columns = [str(c).strip().replace(”\n”, “ “).replace(”\r”, “”) for c in df.columns]
df = df.loc[:, ~df.columns.str.startswith(“Unnamed”)]
df.dropna(how=“all”, inplace=True)
df = map_columns(df)
df[“Nguon file”] = name
frames.append(df)
except Exception as e:
errs.append(f”{name}: {e}”)
for e in errs:
st.warning(f”File loi: {e}”)
if not frames:
return pd.DataFrame()

```
df = pd.concat(frames, ignore_index=True)

num_cols = [
    "Thanh tien ban", "Thanh tien von", "Loi nhuan",
    "Khoi luong", "So luong", "Gia ban", "Gia von",
    "Don gia van chuyen", "Don gia quy doi"
]
for c in num_cols:
    df[c] = get_num(df, c)

date_col = next((c for c in ["Ngay chung tu"] if c in df.columns), None)
if date_col is None:
    st.error("Khong tim thay cot ngay chung tu.")
    return pd.DataFrame()

df["Ngay chung tu"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
df = df[df["Ngay chung tu"].notna()].copy()
df["Nam"]          = df["Ngay chung tu"].dt.year.astype(str)
df["Quy"]          = df["Ngay chung tu"].dt.to_period("Q").astype(str)
df["Thang"]        = df["Ngay chung tu"].dt.to_period("M").astype(str)
df["Thang_label"]  = df["Ngay chung tu"].dt.strftime("%m/%Y")
df["Ngay_trongthang"] = df["Ngay chung tu"].dt.day
df["Cuoi_thang"]   = df["Ngay_trongthang"] >= 28

gc   = df["Ghi chu"].astype(str).str.upper() if "Ghi chu" in df.columns else pd.Series("", index=df.index)
loai = df["Loai don hang"].astype(str).str.upper() if "Loai don hang" in df.columns else pd.Series("", index=df.index)
df["Loai_GD"] = "Xuat ban"
df.loc[gc.str.contains(r"NHAP TRA|TRA HANG", regex=True, na=False), "Loai_GD"] = "Tra hang"
df.loc[loai.str.contains(r"TRA HANG|HUY HD", regex=True, na=False), "Loai_GD"] = "Tra hang"
df.loc[gc.str.contains(r"BO SUNG|THAY THE", regex=True, na=False), "Loai_GD"] = "Xuat bo sung"

ten = df["Ten hang"].astype(str) if "Ten hang" in df.columns else pd.Series("", index=df.index)
df["Nhom_SP"] = "Khac"
for label, pat in NHOM_SP:
    df.loc[ten.str.contains(pat, case=False, regex=True, na=False), "Nhom_SP"] = label

df["Bien_LN"] = np.where(
    df["Thanh tien ban"] != 0,
    (df["Loi nhuan"] / df["Thanh tien ban"] * 100).round(2),
    0.0
)
if "Ma kho" in df.columns:
    df["Ma kho"] = df["Ma kho"].astype(str).str.replace(".0", "", regex=False).str.strip()

if "Ten khach hang" not in df.columns:
    st.error("Khong tim thay cot Ten khach hang.")
    return pd.DataFrame()

return df
```

# –– SIDEBAR ––

st.sidebar.markdown(”## Upload du lieu”)
uploaded = st.sidebar.file_uploader(
“File Excel bao cao ban hang (OM_RPT_055)”,
type=[“xlsx”],
accept_multiple_files=True
)

if not uploaded:
st.markdown(’<div class="page-title">Phan tich Ban hang - Hoa Sen</div>’, unsafe_allow_html=True)
st.info(“Upload file Excel bao cao OM_RPT_055 de bat dau phan tich.”)
st.stop()

@st.cache_data(show_spinner=“Dang xu ly du lieu…”)
def cached_load(file_data):
return load_all(list(file_data))

file_data = tuple((u.name, u.read()) for u in uploaded)
df_all = cached_load(file_data)

if df_all.empty:
st.error(“Khong co du lieu hop le.”)
st.stop()

# –– FILTERS ––

st.sidebar.markdown(”—”)
st.sidebar.markdown(”## Bo loc”)

pkd_exists = “Ten nhom KH” in df_all.columns
if pkd_exists:
pkd_opts = sorted(df_all[“Ten nhom KH”].dropna().astype(str).unique().tolist())
pkd_chon = st.sidebar.multiselect(“Phong Kinh doanh”, pkd_opts, default=pkd_opts)
df_f = df_all[df_all[“Ten nhom KH”].astype(str).isin(pkd_chon)].copy() if pkd_chon else df_all.copy()
else:
df_f = df_all.copy()
pkd_chon = []

thang_labels = sorted(df_f[“Thang_label”].dropna().unique().tolist())
thang_map    = {row[“Thang_label”]: row[“Thang”]
for _, row in df_f[[“Thang_label”,“Thang”]].drop_duplicates().iterrows()}
t_chon_labels = st.sidebar.multiselect(“Thang”, thang_labels, default=thang_labels)
t_chon = [thang_map[l] for l in t_chon_labels if l in thang_map]
if t_chon:
df_f = df_f[df_f[“Thang”].isin(t_chon)].copy()

st.sidebar.markdown(”—”)
view_mode = st.sidebar.radio(“Che do xem”, [“Tong quan”, “Theo Phong KD”, “Theo Khach hang”])

single_kh   = False
scope_label = “Tong quan”

if view_mode == “Theo Khach hang”:
kh_list = sorted(df_f[“Ten khach hang”].dropna().astype(str).unique())
if not kh_list:
st.warning(“Khong co khach hang phu hop.”)
st.stop()
kh = st.sidebar.selectbox(“Khach hang”, kh_list)
df_scope   = df_f[df_f[“Ten khach hang”].astype(str) == kh].copy()
scope_label = kh
single_kh   = True
elif view_mode == “Theo Phong KD” and pkd_exists and pkd_opts:
pkd_view   = st.sidebar.selectbox(“Xem Phong KD”, pkd_opts)
df_scope   = df_f[df_f[“Ten nhom KH”].astype(str) == pkd_view].copy()
scope_label = pkd_view
else:
df_scope   = df_f.copy()
scope_label = “Tong hop”

time_map = {“Thang”: “Thang”, “Quy”: “Quy”, “Nam”: “Nam”}
time_lbl = st.sidebar.radio(“Cum thoi gian”, [“Thang”, “Quy”, “Nam”], index=0)
time_col = time_map[time_lbl]

df_ban = df_scope[df_scope[“Loai_GD”] == “Xuat ban”].copy()

# –– HEADER ––

ngay_min = df_scope[“Ngay chung tu”].min()
ngay_max = df_scope[“Ngay chung tu”].max()
d_str = f”{ngay_min.strftime(’%d/%m/%Y’) if pd.notna(ngay_min) else ‘?’} -> {ngay_max.strftime(’%d/%m/%Y’) if pd.notna(ngay_max) else ‘?’}”

st.markdown(f’<div class="page-title">= {scope_label}</div>’, unsafe_allow_html=True)
pkd_str = “, “.join(pkd_chon[:3]) + (”…” if len(pkd_chon) > 3 else “”) if pkd_chon else “Tat ca PKD”
t_str   = “, “.join(t_chon_labels[:4]) + (”…” if len(t_chon_labels) > 4 else “”) if t_chon_labels else “Tat ca thang”
st.markdown(f’<div class="page-sub"> {d_str} | {time_lbl} | {pkd_str} | {t_str}</div>’, unsafe_allow_html=True)

if df_ban.empty:
st.warning(“Khong co du lieu xuat ban cho bo loc da chon.”)
st.stop()

tong_dt  = df_ban[“Thanh tien ban”].sum()
tong_ln  = df_ban[“Loi nhuan”].sum()
tong_kl  = df_ban[“Khoi luong”].sum() / 1000
bien_ln  = (tong_ln / tong_dt * 100) if tong_dt else 0
n_ct     = df_ban[“So chung tu”].nunique() if “So chung tu” in df_ban.columns else len(df_ban)
n_kh     = df_ban[“Ten khach hang”].nunique()
n_sp     = df_ban[“Ten hang”].nunique() if “Ten hang” in df_ban.columns else 0

kpis = [
(“Doanh thu”, fmt(tong_dt) + “ d”),
(“Loi nhuan”,  fmt(tong_ln) + “ d”),
(“Bien LN”,   f”{bien_ln:.1f}%”),
(“Khoi luong”, f”{tong_kl:,.1f} tan”),
(“Chung tu”,  f”{n_ct:,}”),
(“Khach hang”, f”{n_kh:,}”),
(“San pham”,  f”{n_sp:,}”),
]
cols = st.columns(len(kpis))
for col, (lab, val) in zip(cols, kpis):
col.markdown(
f’<div class="kpi-card"><div class="kpi-val">{val}</div><div class="kpi-lab">{lab}</div></div>’,
unsafe_allow_html=True
)
st.markdown(””)

# –– TABS ––

tab_pkd, tab_time, tab_sp, tab_ln, tab_giao, tab_freq, tab_risk = st.tabs([
“Phong KD & KH”, “Thoi gian”, “San pham”, “Loi nhuan”, “Giao hang”, “Tan suat”, “Rui ro”
])

# ============================================================

# TAB 1 - PHONG KD & KH

# ============================================================

with tab_pkd:
has_pkd = “Ma nhom KH” in df_ban.columns and “Ten nhom KH” in df_ban.columns

```
if has_pkd:
    st.markdown('<div class="section-title">Co cau Doanh thu: Phong KD -> Khach hang</div>', unsafe_allow_html=True)
    df_sun = (df_ban.groupby(["Ten nhom KH", "Ten khach hang"])
              .agg(DT=("Thanh tien ban", "sum")).reset_index())
    df_sun = df_sun[df_sun["DT"] > 0]
    if not df_sun.empty:
        fig_sun = px.sunburst(df_sun, path=["Ten nhom KH", "Ten khach hang"],
                              values="DT", title="Phong KD -> Khach hang",
                              color="DT", color_continuous_scale="Blues")
        fig_sun.update_layout(**{k: v for k, v in BASE_LAYOUT.items() if k not in ("xaxis","yaxis")})
        fig_sun.update_layout(height=480)
        st.plotly_chart(fig_sun, use_container_width=True)

    df_pkd = (df_ban.groupby(["Ma nhom KH","Ten nhom KH"])
              .agg(DT=("Thanh tien ban","sum"), LN=("Loi nhuan","sum"),
                   KL=("Khoi luong", lambda x: round(x.sum()/1000,2)),
                   N_KH=("Ten khach hang","nunique"))
              .reset_index().sort_values("DT", ascending=False))
    df_pkd["Bien"] = (df_pkd["LN"] / df_pkd["DT"].replace(0, np.nan) * 100).round(1).fillna(0)

    fig_pkd = go.Figure()
    fig_pkd.add_trace(go.Bar(x=df_pkd["Ten nhom KH"], y=df_pkd["DT"], name="Doanh thu",
                              marker_color="#388bfd", opacity=0.85,
                              text=[fmt(v) for v in df_pkd["DT"]], textposition="outside"))
    fig_pkd.add_trace(go.Bar(x=df_pkd["Ten nhom KH"], y=df_pkd["LN"], name="Loi nhuan",
                              marker_color="#56d364", opacity=0.85,
                              text=[fmt(v) for v in df_pkd["LN"]], textposition="outside"))
    fig_pkd.update_layout(**BASE_LAYOUT, title="DT & LN theo Phong KD",
                           barmode="group", height=360, xaxis_tickangle=-15)
    st.plotly_chart(fig_pkd, use_container_width=True)

st.markdown('<div class="section-title">Top Khach hang</div>', unsafe_allow_html=True)
df_kh = (df_ban.groupby("Ten khach hang")
         .agg(DT=("Thanh tien ban","sum"), LN=("Loi nhuan","sum"),
              KL=("Khoi luong", lambda x: round(x.sum()/1000,2)),
              N_CT=("So chung tu","nunique") if "So chung tu" in df_ban.columns else ("Thanh tien ban","count"))
         .reset_index().sort_values("DT", ascending=False))
df_kh["Bien"] = (df_kh["LN"] / df_kh["DT"].replace(0, np.nan) * 100).round(1).fillna(0)

df_top15 = df_kh.head(15).sort_values("DT", ascending=True)
fig_kh = go.Figure(go.Bar(
    y=df_top15["Ten khach hang"], x=df_top15["DT"], orientation="h",
    marker=dict(
        color=df_top15["Bien"],
        colorscale=[[0,"#ffa198"],[0.3,"#e3b341"],[0.7,"#3fb950"],[1,"#56d364"]],
        colorbar=dict(title="Bien LN%", tickfont=dict(color="#c9d1d9"), titlefont=dict(color="#c9d1d9")),
        showscale=True
    ),
    text=[fmt(v) for v in df_top15["DT"]], textposition="outside",
    textfont=dict(size=10, color="#c9d1d9")
))
fig_kh.update_layout(**BASE_LAYOUT, title="Top 15 Khach hang - DT (mau = Bien LN%)", height=480)
st.plotly_chart(fig_kh, use_container_width=True)

df_kh_d = df_kh.copy()
df_kh_d["DT"] = df_kh_d["DT"].map(fmt_full)
df_kh_d["LN"] = df_kh_d["LN"].map(fmt_full)
st.dataframe(df_kh_d, use_container_width=True, hide_index=True)

if "Khu vuc" in df_ban.columns:
    st.markdown('<div class="section-title">DT theo Khu vuc</div>', unsafe_allow_html=True)
    df_kv = (df_ban.groupby("Khu vuc")
             .agg(DT=("Thanh tien ban","sum"), LN=("Loi nhuan","sum"),
                  N_KH=("Ten khach hang","nunique"))
             .reset_index().sort_values("DT", ascending=False))
    df_kv["Bien"] = (df_kv["LN"] / df_kv["DT"].replace(0, np.nan) * 100).round(1).fillna(0)
    c1, c2 = st.columns(2)
    with c1:
        fig_kv = go.Figure(go.Pie(
            labels=df_kv["Khu vuc"], values=df_kv["DT"], hole=0.55,
            marker=dict(colors=COLORS[:len(df_kv)], line=dict(color="#0d1117", width=2)),
            textfont=dict(size=11), textinfo="label+percent"
        ))
        fig_kv.update_layout(**{k: v for k, v in BASE_LAYOUT.items() if k not in ("xaxis","yaxis")},
                               title="Co cau DT theo Khu vuc", height=360, showlegend=False)
        st.plotly_chart(fig_kv, use_container_width=True)
    with c2:
        df_kv_d = df_kv.copy()
        df_kv_d["DT"] = df_kv_d["DT"].map(fmt_full)
        df_kv_d["LN"] = df_kv_d["LN"].map(fmt_full)
        st.dataframe(df_kv_d, use_container_width=True, hide_index=True)
```

# ============================================================

# TAB 2 - THOI GIAN

# ============================================================

with tab_time:
st.markdown(f’<div class="section-title">Xu huong theo: {time_lbl}</div>’, unsafe_allow_html=True)

```
df_t = (df_ban.groupby(time_col)
        .agg(DT=("Thanh tien ban","sum"), LN=("Loi nhuan","sum"),
             KL=("Khoi luong", lambda x: round(x.sum()/1000,3)),
             SL=("So luong","sum"),
             N_CT=("So chung tu","nunique") if "So chung tu" in df_ban.columns else ("Thanh tien ban","count"),
             N_KH=("Ten khach hang","nunique"))
        .reset_index().sort_values(time_col))
df_t["Bien"] = (df_t["LN"] / df_t["DT"].replace(0, np.nan) * 100).round(2).fillna(0)
df_t["Tang"] = (df_t["DT"].pct_change() * 100).round(1)

fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                    subplot_titles=["DT & LN (VND)", "Khoi luong (tan)", "Bien LN (%) & Tang truong (%)"],
                    vertical_spacing=0.1, row_heights=[0.45, 0.25, 0.3])
fig.add_trace(go.Bar(x=df_t[time_col], y=df_t["DT"], name="Doanh thu",
                      marker_color="#388bfd", opacity=0.85), row=1, col=1)
fig.add_trace(go.Scatter(x=df_t[time_col], y=df_t["LN"], name="Loi nhuan",
                          mode="lines+markers", line=dict(color="#56d364", width=2.5),
                          marker=dict(size=7)), row=1, col=1)
fig.add_trace(go.Bar(x=df_t[time_col], y=df_t["KL"], name="KL (tan)",
                      marker_color="#79c0ff", opacity=0.75), row=2, col=1)
fig.add_trace(go.Scatter(x=df_t[time_col], y=df_t["Bien"], name="Bien LN %",
                          mode="lines+markers+text",
                          text=[f"{v:.1f}%" for v in df_t["Bien"]],
                          textposition="top center", textfont=dict(size=10, color="#e3b341"),
                          line=dict(color="#e3b341", width=2.5), marker=dict(size=7),
                          fill="tozeroy", fillcolor="rgba(227,179,65,0.07)"), row=3, col=1)
fig.add_trace(go.Bar(x=df_t[time_col], y=df_t["Tang"], name="Tang truong %",
                      marker=dict(color=["#56d364" if (v >= 0) else "#ffa198"
                                         for v in df_t["Tang"].fillna(0)]),
                      opacity=0.55), row=3, col=1)
fig.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                  font=dict(family="Be Vietnam Pro", color="#c9d1d9", size=11),
                  height=620, showlegend=True,
                  legend=dict(bgcolor="#161b22", bordercolor="#21262d", orientation="h", y=-0.05),
                  margin=dict(l=10, r=10, t=40, b=10))
fig.update_xaxes(gridcolor="#21262d", linecolor="#30363d")
fig.update_yaxes(gridcolor="#21262d", linecolor="#30363d")
for ann in fig.layout.annotations:
    ann.font.color = "#8b949e"
    ann.font.size  = 12
st.plotly_chart(fig, use_container_width=True)

df_t_d = df_t.copy()
df_t_d["DT"] = df_t_d["DT"].map(fmt_full)
df_t_d["LN"] = df_t_d["LN"].map(fmt_full)
show_cols = [c for c in [time_col, "DT", "LN", "KL", "SL", "N_CT", "N_KH", "Bien"] if c in df_t_d.columns]
st.dataframe(df_t_d[show_cols], use_container_width=True, hide_index=True)

if not single_kh and df_ban["Ten khach hang"].nunique() > 1:
    st.markdown('<div class="section-title">Heatmap DT: Khach hang x Thang</div>', unsafe_allow_html=True)
    df_hm = df_ban.groupby(["Ten khach hang","Thang"])["Thanh tien ban"].sum().reset_index()
    df_piv = df_hm.pivot(index="Ten khach hang", columns="Thang", values="Thanh tien ban").fillna(0)
    top20 = df_piv.sum(axis=1).nlargest(min(20, len(df_piv))).index
    fig_hm = px.imshow(df_piv.loc[top20],
                        color_continuous_scale=[[0,"#0d1117"],[0.3,"#1f3058"],[0.7,"#2d5ea8"],[1,"#388bfd"]],
                        aspect="auto", title="Heatmap DT: Khach hang x Thang")
    fig_hm.update_layout(**{k: v for k, v in BASE_LAYOUT.items() if k not in ("xaxis","yaxis")},
                           height=max(350, len(top20)*26))
    st.plotly_chart(fig_hm, use_container_width=True)
```

# ============================================================

# TAB 3 - SAN PHAM

# ============================================================

with tab_sp:
st.markdown(’<div class="section-title">Co cau San pham</div>’, unsafe_allow_html=True)
df_nhom = (df_ban.groupby(“Nhom_SP”)
.agg(N=(“Nhom_SP”,“count”),
KL=(“Khoi luong”, lambda x: round(x.sum()/1000,2)),
DT=(“Thanh tien ban”,“sum”))
.reset_index().sort_values(“DT”, ascending=False))

```
c1, c2 = st.columns(2)
with c1:
    fig_nb = go.Figure(go.Bar(
        x=df_nhom["Nhom_SP"], y=df_nhom["DT"],
        marker=dict(color=COLORS[:len(df_nhom)]),
        text=[fmt(v) for v in df_nhom["DT"]], textposition="outside",
        textfont=dict(size=11, color="#c9d1d9")
    ))
    fig_nb.update_layout(**BASE_LAYOUT, title="DT theo Nhom SP", height=360, showlegend=False, xaxis_tickangle=-10)
    st.plotly_chart(fig_nb, use_container_width=True)
with c2:
    fig_np = go.Figure(go.Pie(
        labels=df_nhom["Nhom_SP"], values=df_nhom["DT"], hole=0.55,
        marker=dict(colors=COLORS[:len(df_nhom)], line=dict(color="#0d1117", width=2)),
        textfont=dict(size=11), textinfo="label+percent"
    ))
    fig_np.update_layout(**{k: v for k, v in BASE_LAYOUT.items() if k not in ("xaxis","yaxis")},
                           title="Ty trong DT Nhom SP", height=360)
    st.plotly_chart(fig_np, use_container_width=True)

if "Ten hang" in df_ban.columns:
    st.markdown('<div class="section-title">Top 15 San pham</div>', unsafe_allow_html=True)
    df_top = (df_ban.groupby("Ten hang")
              .agg(N=("Ten hang","count"),
                   KL=("Khoi luong", lambda x: round(x.sum()/1000,2)),
                   DT=("Thanh tien ban","sum"), LN=("Loi nhuan","sum"))
              .reset_index().sort_values("DT", ascending=False).head(15))
    df_top["Bien"] = (df_top["LN"] / df_top["DT"].replace(0, np.nan) * 100).round(1).fillna(0)
    df_tops = df_top.sort_values("DT", ascending=True)
    fig_sp = go.Figure(go.Bar(
        y=df_tops["Ten hang"], x=df_tops["DT"], orientation="h",
        marker=dict(color=df_tops["Bien"],
                    colorscale=[[0,"#ffa198"],[0.3,"#e3b341"],[0.7,"#3fb950"],[1,"#56d364"]],
                    colorbar=dict(title="Bien LN%", tickfont=dict(color="#c9d1d9"), titlefont=dict(color="#c9d1d9")),
                    showscale=True),
        text=[fmt(v) for v in df_tops["DT"]], textposition="outside",
        textfont=dict(size=10, color="#c9d1d9")
    ))
    fig_sp.update_layout(**BASE_LAYOUT, title="Top 15 SP - DT (mau = Bien LN%)", height=520)
    st.plotly_chart(fig_sp, use_container_width=True)

    top5 = df_top["Ten hang"].head(5).tolist()
    df_tr = (df_ban[df_ban["Ten hang"].isin(top5)]
             .groupby(["Ten hang", time_col])["Thanh tien ban"].sum().reset_index())
    if not df_tr.empty:
        fig_tr = px.line(df_tr, x=time_col, y="Thanh tien ban", color="Ten hang",
                          markers=True, title=f"Xu huong Top 5 SP theo {time_lbl}",
                          color_discrete_sequence=COLORS)
        fig_tr.update_traces(line=dict(width=2.5), marker=dict(size=8))
        fig_tr.update_layout(**BASE_LAYOUT, height=380)
        st.plotly_chart(fig_tr, use_container_width=True)
```

# ============================================================

# TAB 4 - LOI NHUAN

# ============================================================

with tab_ln:
df_lnt = (df_ban.groupby(time_col)
.agg(DT=(“Thanh tien ban”,“sum”), Von=(“Thanh tien von”,“sum”), LN=(“Loi nhuan”,“sum”))
.reset_index().sort_values(time_col))
df_lnt[“Bien”] = (df_lnt[“LN”] / df_lnt[“DT”].replace(0, np.nan) * 100).round(2).fillna(0)

```
fig_ln2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                         subplot_titles=["DT / Von / LN (VND)", f"Bien LN (%) theo {time_lbl}"],
                         vertical_spacing=0.14, row_heights=[0.6, 0.4])
fig_ln2.add_trace(go.Bar(x=df_lnt[time_col], y=df_lnt["DT"], name="Doanh thu",
                          marker_color="#388bfd", opacity=0.8), row=1, col=1)
fig_ln2.add_trace(go.Bar(x=df_lnt[time_col], y=df_lnt["Von"], name="Gia von",
                          marker_color="#e05c5c", opacity=0.7), row=1, col=1)
fig_ln2.add_trace(go.Scatter(x=df_lnt[time_col], y=df_lnt["LN"], name="Loi nhuan",
                              mode="lines+markers", line=dict(color="#56d364", width=2.5),
                              marker=dict(size=8)), row=1, col=1)
fig_ln2.add_trace(go.Scatter(x=df_lnt[time_col], y=df_lnt["Bien"], name="Bien LN %",
                              mode="lines+markers+text",
                              text=[f"{v:.1f}%" for v in df_lnt["Bien"]],
                              textposition="top center", textfont=dict(size=10, color="#e3b341"),
                              line=dict(color="#e3b341", width=2.5), marker=dict(size=8),
                              fill="tozeroy", fillcolor="rgba(227,179,65,0.08)"), row=2, col=1)
fig_ln2.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                       font=dict(family="Be Vietnam Pro", color="#c9d1d9", size=11),
                       height=520, barmode="group",
                       legend=dict(bgcolor="#161b22", bordercolor="#21262d", orientation="h", y=-0.05),
                       margin=dict(l=10, r=10, t=40, b=10))
fig_ln2.update_xaxes(gridcolor="#21262d", linecolor="#30363d")
fig_ln2.update_yaxes(gridcolor="#21262d", linecolor="#30363d")
for ann in fig_ln2.layout.annotations:
    ann.font.color = "#8b949e"
    ann.font.size  = 12
st.plotly_chart(fig_ln2, use_container_width=True)

if len(df_lnt) >= 2:
    mb = df_lnt["Bien"].mean()
    sb = df_lnt["Bien"].std() or 1
    anom = df_lnt[df_lnt["Bien"] < mb - sb * 1.5]
    if not anom.empty:
        st.markdown('<div class="section-title">Ky nghi co chiet khau / chinh sach dac biet</div>', unsafe_allow_html=True)
        for _, r in anom.iterrows():
            st.markdown(
                f'<div class="risk-high"><b>{r[time_col]}</b>: Bien LN = {r["Bien"]:.1f}% (TB: {mb:.1f}%) -> Nghi chiet khau lon</div>',
                unsafe_allow_html=True)

st.markdown('<div class="section-title">Gia ban < Gia von</div>', unsafe_allow_html=True)
if "Gia ban" in df_ban.columns and "Gia von" in df_ban.columns:
    df_lo = df_ban[(df_ban["Gia ban"] > 0) & (df_ban["Gia von"] > 0) & (df_ban["Gia ban"] < df_ban["Gia von"])]
    if not df_lo.empty:
        st.error(f"{len(df_lo)} dong co gia ban < gia von")
        show_lo = [c for c in ["Ngay chung tu","Ten khach hang","Ten hang","Gia ban","Gia von","Loi nhuan","Ghi chu"] if c in df_lo.columns]
        st.dataframe(df_lo[show_lo], use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="risk-low">Khong co dong nao gia ban thap hon gia von.</div>', unsafe_allow_html=True)

df_tra_ln = df_scope[df_scope["Loai_GD"] == "Tra hang"]
if not df_tra_ln.empty:
    st.markdown('<div class="section-title">Hang tra lai</div>', unsafe_allow_html=True)
    st.error(f"Tong GT tra hang: {fmt_full(abs(df_tra_ln['Thanh tien ban'].sum()))} VND ({len(df_tra_ln)} dong)")
    show_tr = [c for c in ["So chung tu","Ngay chung tu","Ten khach hang","Ten hang","Thanh tien ban","Ghi chu"] if c in df_tra_ln.columns]
    df_tr_d = df_tra_ln[show_tr].copy()
    if "Thanh tien ban" in df_tr_d.columns:
        df_tr_d["Thanh tien ban"] = df_tr_d["Thanh tien ban"].map(fmt_full)
    st.dataframe(df_tr_d, use_container_width=True, hide_index=True)
```

# ============================================================

# TAB 5 - GIAO HANG

# ============================================================

with tab_giao:
c1, c2 = st.columns(2)
with c1:
if “Freight Terms” in df_ban.columns:
ft = df_ban[“Freight Terms”].dropna().value_counts().reset_index()
ft.columns = [“Hinh thuc”, “So lan”]
if not ft.empty:
fig_ft = go.Figure(go.Pie(
labels=ft[“Hinh thuc”], values=ft[“So lan”], hole=0.55,
marker=dict(colors=COLORS[:len(ft)], line=dict(color=”#0d1117”, width=2)),
textfont=dict(size=11), textinfo=“label+percent”
))
fig_ft.update_layout(**{k: v for k, v in BASE_LAYOUT.items() if k not in (“xaxis”,“yaxis”)},
title=“Dieu kien giao hang”, height=360, showlegend=False)
st.plotly_chart(fig_ft, use_container_width=True)
with c2:
if “Shipping method” in df_ban.columns:
sm = df_ban[“Shipping method”].dropna().value_counts().reset_index()
sm.columns = [“Phuong tien”, “So lan”]
if not sm.empty:
fig_sm = go.Figure(go.Pie(
labels=sm[“Phuong tien”], values=sm[“So lan”], hole=0.55,
marker=dict(colors=COLORS[:len(sm)], line=dict(color=”#0d1117”, width=2)),
textfont=dict(size=11), textinfo=“label+percent”
))
fig_sm.update_layout(**{k: v for k, v in BASE_LAYOUT.items() if k not in (“xaxis”,“yaxis”)},
title=“Phuong tien van chuyen”, height=360, showlegend=False)
st.plotly_chart(fig_sm, use_container_width=True)

```
if "Noi giao hang" in df_ban.columns:
    st.markdown('<div class="section-title">Dia diem giao hang</div>', unsafe_allow_html=True)
    df_noi = (df_ban.groupby("Noi giao hang")
              .agg(N=("Noi giao hang","count"),
                   KL=("Khoi luong", lambda x: round(x.sum()/1000,2)),
                   DT=("Thanh tien ban","sum"))
              .reset_index().sort_values("DT", ascending=False).head(20))
    df_nois = df_noi.sort_values("DT", ascending=True)
    fig_noi = go.Figure(go.Bar(
        y=df_nois["Noi giao hang"], x=df_nois["DT"], orientation="h",
        marker=dict(color="#79c0ff", opacity=0.85),
        text=[fmt(v) for v in df_nois["DT"]], textposition="outside",
        textfont=dict(size=10)
    ))
    fig_noi.update_layout(**BASE_LAYOUT, title="Top 20 Dia diem giao hang", height=max(360, len(df_nois)*28))
    st.plotly_chart(fig_noi, use_container_width=True)

if "Ma kho" in df_ban.columns:
    st.markdown('<div class="section-title">Kho xuat hang</div>', unsafe_allow_html=True)
    df_kho = (df_ban.groupby("Ma kho")
              .agg(N=("Ma kho","count"), DT=("Thanh tien ban","sum"),
                   KL=("Khoi luong", lambda x: round(x.sum()/1000,2)))
              .reset_index().sort_values("DT", ascending=False))
    df_kho_d = df_kho.copy()
    df_kho_d["DT"] = df_kho_d["DT"].map(fmt_full)
    st.dataframe(df_kho_d, use_container_width=True, hide_index=True)

with st.expander("Danh sach xe & tai xe"):
    xe_cols = [c for c in ["So xe","Tai xe","Shipping method","Ngay chung tu","Noi giao hang"] if c in df_ban.columns]
    if xe_cols:
        st.dataframe(df_ban[xe_cols].drop_duplicates().sort_values("Ngay chung tu"),
                     use_container_width=True, hide_index=True)
```

# ============================================================

# TAB 6 - TAN SUAT

# ============================================================

with tab_freq:
if “Ten hang” in df_ban.columns:
st.markdown(’<div class="section-title">Heatmap tan suat: SP x Thang</div>’, unsafe_allow_html=True)
df_fr  = df_ban.groupby([“Ten hang”,“Thang”]).size().reset_index(name=“N”)
df_piv = df_fr.pivot(index=“Ten hang”, columns=“Thang”, values=“N”).fillna(0)
top_n  = df_piv.sum(axis=1).nlargest(min(25, len(df_piv))).index
fig_h  = px.imshow(df_piv.loc[top_n],
color_continuous_scale=[[0,”#0d1117”],[0.3,”#1f3058”],[0.7,”#2d5ea8”],[1,”#388bfd”]],
aspect=“auto”, title=“Heatmap tan suat - Top SP x Thang”)
fig_h.update_layout(**{k: v for k, v in BASE_LAYOUT.items() if k not in (“xaxis”,“yaxis”)},
height=max(400, len(top_n)*22))
st.plotly_chart(fig_h, use_container_width=True)

```
    for q in sorted(df_ban["Quy"].dropna().unique()):
        df_q   = df_ban[df_ban["Quy"] == q]
        months = sorted(df_q["Thang"].dropna().unique())
        with st.expander(f"{q} | {chr(44).join(months)}"):
            agg = (df_q.groupby(["Ten hang","Thang"])
                   .agg(N=("Ten hang","count"),
                        KL=("Khoi luong", lambda x: round(x.sum()/1000,2)),
                        DT=("Thanh tien ban","sum"))
                   .reset_index().sort_values("DT", ascending=False))
            agg_d = agg.copy()
            agg_d["DT"] = agg_d["DT"].map(fmt_full)
            agg_d.columns = ["San pham","Thang","So lan","KL (tan)","DT (VND)"]
            st.dataframe(agg_d, use_container_width=True, hide_index=True)
else:
    st.info("Khong co cot Ten hang.")
```

# ============================================================

# TAB 7 - RUI RO

# ============================================================

with tab_risk:
st.markdown(’<div class="section-title">Nhan dien Rui ro & Bat thuong (12 nhom)</div>’, unsafe_allow_html=True)

```
risks = []
score = 0
tdt = df_ban["Thanh tien ban"].sum()
tln = df_ban["Loi nhuan"].sum()
btb = (tln / tdt * 100) if tdt else 0

df_tra2 = df_scope[df_scope["Loai_GD"] == "Tra hang"]
t_tra   = abs(df_tra2["Thanh tien ban"].sum())
tl_tra  = (t_tra / tdt * 100) if tdt else 0
if tl_tra > 10:
    score += 30
    risks.append(("high","Tra hang", f"Ty le tra hang <b>{tl_tra:.1f}%</b> ({fmt_full(t_tra)} VND) - Rui ro cao", df_tra2))
elif tl_tra > 3:
    score += 15
    risks.append(("medium","Tra hang", f"Ty le tra hang <b>{tl_tra:.1f}%</b> - Can theo doi", df_tra2))
else:
    risks.append(("low","Tra hang", f"Ty le tra hang thap: {tl_tra:.1f}%", None))

if "Gia ban" in df_ban.columns and "Gia von" in df_ban.columns:
    df_lo2 = df_ban[(df_ban["Gia ban"] > 0) & (df_ban["Gia von"] > 0) & (df_ban["Gia ban"] < df_ban["Gia von"])]
    if not df_lo2.empty:
        score += 25
        risks.append(("high","Ban lo", f"<b>{len(df_lo2)}</b> dong gia ban < gia von", df_lo2))
    else:
        risks.append(("low","Gia ban vs Gia von", "Khong co dong nao gia ban < gia von", None))

df_lnam = df_ban[df_ban["Loi nhuan"] < 0]
if not df_lnam.empty:
    score += 20
    risks.append(("high","Loi nhuan am",
                   f"<b>{len(df_lnam)}</b> dong xuat ban co LN am (tong: -{fmt_full(abs(df_lnam['Loi nhuan'].sum()))} VND)",
                   df_lnam))
else:
    risks.append(("low","Loi nhuan am", "Khong co dong nao bi lo", None))

if len(df_lnt) >= 2:
    mb2 = df_lnt["Bien"].mean()
    sb2 = df_lnt["Bien"].std() or 1
    anom2 = df_lnt[df_lnt["Bien"] < mb2 - sb2 * 1.5]
    if not anom2.empty:
        ky_str = ", ".join(anom2[time_col].tolist())
        score += 10
        risks.append(("medium","Bien LN bat thuong", f"Ky <b>{ky_str}</b> bien LN thap bat thuong", None))
    else:
        risks.append(("low","Bien LN", "Bien LN on dinh qua cac ky", None))

dt_cuoi  = df_ban[df_ban["Cuoi_thang"] == True]["Thanh tien ban"].sum()
tl_cuoi  = (dt_cuoi / tdt * 100) if tdt else 0
if tl_cuoi > 40:
    score += 15
    risks.append(("high","Tap trung cuoi thang", f"<b>{tl_cuoi:.1f}%</b> DT tap trung ngay 28-31 - Nghi day doanh so", None))
elif tl_cuoi > 25:
    score += 8
    risks.append(("medium","Tap trung cuoi thang", f"{tl_cuoi:.1f}% DT cuoi thang - Can kiem tra", None))
else:
    risks.append(("low","Phan bo thoi gian", f"Don hang phan bo deu ({tl_cuoi:.1f}% cuoi thang)", None))

q1v = df_ban["Thanh tien ban"].quantile(0.25)
q3v = df_ban["Thanh tien ban"].quantile(0.75)
iqr = q3v - q1v
if iqr > 0:
    df_out2 = df_ban[df_ban["Thanh tien ban"] > q3v + 3 * iqr]
    if not df_out2.empty:
        score += 10
        risks.append(("medium","Don gia tri lon bat thuong", f"<b>{len(df_out2)}</b> don vuot 3xIQR", df_out2))
    else:
        risks.append(("low","Quy mo don hang", "Khong co don bat thuong", None))

df_bs2 = df_scope[df_scope["Loai_GD"] == "Xuat bo sung"]
if not df_bs2.empty:
    score += 12
    risks.append(("medium","Xuat bo sung", f"<b>{len(df_bs2)}</b> dong xuat bo sung - giao nham/thieu", df_bs2))
else:
    risks.append(("low","Xuat bo sung", "Khong co don bo sung", None))

if "Noi giao hang" in df_ban.columns:
    n_noi = df_ban["Noi giao hang"].nunique()
    if n_noi >= 6:
        score += 10
        risks.append(("medium","Giao hang phan tan", f"Giao toi <b>{n_noi}</b> dia diem - rui ro cong no phan tan", None))
    else:
        risks.append(("low","Dia diem giao hang", f"{n_noi} dia diem - binh thuong", None))

if "Ma kho" in df_ban.columns and df_ban["Ma kho"].nunique() >= 2:
    score += 5
    risks.append(("medium","Nhieu kho", f"Nhan hang tu <b>{df_ban['Ma kho'].nunique()}</b> kho", None))
else:
    risks.append(("low","Kho xuat hang", "Xuat tu 1 kho - nhat quan", None))

n_tm  = df_ban["Thang"].nunique()
n_rng = max((df_ban["Ngay chung tu"].max() - df_ban["Ngay chung tu"].min()).days // 30, 1)
if n_tm / n_rng < 0.5:
    score += 10
    risks.append(("medium","Mua hang khong deu", f"Chi mua <b>{n_tm}/{n_rng}</b> thang - phu thuoc du an", None))
else:
    risks.append(("low","Tan suat mua", f"Mua deu: {n_tm} thang co GD", None))

if btb < 5:
    score += 20
    risks.append(("high","Bien LN tong thap", f"Bien LN = <b>{btb:.1f}%</b> - nguy co ban pha gia", None))
elif btb < 15:
    score += 8
    risks.append(("medium","Bien LN tong", f"Bien LN = <b>{btb:.1f}%</b> - muc thap, can theo doi", None))
else:
    risks.append(("low","Bien LN tong", f"Bien LN = {btb:.1f}% - on dinh", None))

if "Ghi chu" in df_scope.columns:
    gc3   = df_scope["Ghi chu"].astype(str).str.upper()
    df_po = df_scope[gc3.str.contains(r"PO|B[0-9]{3}|HOP DONG", regex=True, na=False)]
    if not df_po.empty:
        score += 8
        n_po = df_po["So chung tu"].nunique() if "So chung tu" in df_po.columns else len(df_po)
        risks.append(("medium","Don PO/Du an",
                       f"<b>{n_po}</b> CT co PO/HD ({fmt_full(abs(df_po['Thanh tien ban'].sum()))} VND) - TT cham NET 30-90 ngay",
                       df_po))

n_high   = sum(1 for l,_,_,_ in risks if l == "high")
n_medium = sum(1 for l,_,_,_ in risks if l == "medium")
n_low    = sum(1 for l,_,_,_ in risks if l == "low")

if score >= 60:
    color, label, bg = "#ffa198", "RUI RO CAO", "rgba(218,54,51,0.1)"
elif score >= 30:
    color, label, bg = "#e3b341", "RUI RO TRUNG BINH", "rgba(187,128,9,0.1)"
else:
    color, label, bg = "#56d364", "RUI RO THAP", "rgba(35,134,54,0.1)"

pct = min(score / 130 * 100, 100)
st.markdown(f"""
```

<div style="background:{bg};border:1px solid {color};border-radius:12px;padding:24px;text-align:center;margin:10px 0 20px 0;">
  <div style="font-size:28px;font-weight:900;color:{color};">{label}</div>
  <div style="font-size:15px;color:#8b949e;margin-top:10px;">
    Diem rui ro: <b style="color:{color};font-size:18px;">{score}/130</b>
    &nbsp;|&nbsp; {n_high} cao &nbsp; {n_medium} trung binh &nbsp; {n_low} thap
  </div>
</div>
<div style="background:#161b22;border-radius:6px;height:8px;margin:-10px 0 20px 0;overflow:hidden;">
  <div style="background:{color};width:{pct:.0f}%;height:100%;border-radius:6px;"></div>
</div>
""", unsafe_allow_html=True)

```
for lvl, cat, msg, detail in risks:
    st.markdown(f'<div class="risk-{lvl}"><b>[{cat}]</b> {msg}</div>', unsafe_allow_html=True)
    if detail is not None and not detail.empty and lvl in ("high","medium"):
        show_c = [c for c in ["So chung tu","Ngay chung tu","Ten khach hang","Ten hang",
                               "Thanh tien ban","Loi nhuan","Gia ban","Gia von","Ghi chu"] if c in detail.columns]
        with st.expander(f"Chi tiet - {cat} ({len(detail)} dong)"):
            d2 = detail[show_c].head(50).copy()
            for c in ["Thanh tien ban","Loi nhuan","Gia ban","Gia von"]:
                if c in d2.columns:
                    d2[c] = d2[c].map(fmt_full)
            st.dataframe(d2, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown('<div class="section-title">BCCN - Luu y Thanh toan & Cong no</div>', unsafe_allow_html=True)
st.markdown("""
```

<div class="risk-info">
File OM_RPT_055 <b>khong chua ngay thanh toan thuc te</b>. Can bo sung:<br>
- <b>So AR Aging</b>: so ngay ton dong, han muc tin dung<br>
- <b>Lich su thanh toan</b>: NET 30/60/90<br><br>
<b>Dau hieu nhan biet:</b><br>
- Ghi chu <b>B-xxx / PO</b>: don du an, thanh toan cham<br>
- <b>Tra hang</b>: tranh chap, keo dai cong no<br>
- <b>Nhieu dia diem giao</b>: cong no phan tan nhieu cong trinh<br>
- <b>Don cuoi thang lon</b>: kiem tra giao nhan thuc te
</div>
""", unsafe_allow_html=True)