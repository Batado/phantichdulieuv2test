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
page_icon=“📊”,
initial_sidebar_state=“expanded”
)

CSS = “””

<style>
@import url("https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800&display=swap");
html,body,[class*="css"]{font-family:"Be Vietnam Pro",sans-serif;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1117 0%,#161b22 100%);border-right:1px solid #21262d;}
section[data-testid="stSidebar"] *{color:#c9d1d9 !important;}
.stApp{background:#0d1117;}
.risk-high{background:rgba(218,54,51,0.12);border-left:3px solid #da3633;padding:10px 16px;border-radius:6px;margin:5px 0;color:#ffa198;}
.risk-medium{background:rgba(187,128,9,0.12);border-left:3px solid #bb8009;padding:10px 16px;border-radius:6px;margin:5px 0;color:#e3b341;}
.risk-low{background:rgba(35,134,54,0.12);border-left:3px solid #238636;padding:10px 16px;border-radius:6px;margin:5px 0;color:#56d364;}
.risk-info{background:rgba(31,111,235,0.12);border-left:3px solid #1f6feb;padding:10px 16px;border-radius:6px;margin:5px 0;color:#79c0ff;}
.section-title{font-size:13px;font-weight:700;color:#8b949e;margin:20px 0 10px 0;padding-bottom:6px;border-bottom:1px solid #21262d;text-transform:uppercase;letter-spacing:0.05em;}
.kpi-card{background:linear-gradient(135deg,#161b22 0%,#1c2128 100%);border:1px solid #21262d;border-radius:10px;padding:16px 20px;}
.kpi-val{font-size:20px;font-weight:800;color:#f0f6fc;line-height:1.2;}
.kpi-lab{font-size:11px;color:#6e7681;margin-top:4px;font-weight:500;}
.page-title{font-size:24px;font-weight:800;color:#f0f6fc;padding:6px 0 2px 0;}
.page-sub{font-size:13px;color:#6e7681;margin-bottom:18px;}
.stTabs [data-baseweb="tab-list"]{background:#161b22;border-radius:8px;padding:4px;gap:4px;border:1px solid #21262d;}
.stTabs [data-baseweb="tab"]{background:transparent;color:#8b949e;border-radius:6px;font-weight:600;font-size:13px;}
.stTabs [aria-selected="true"]{background:#21262d !important;color:#f0f6fc !important;}
</style>

“””
st.markdown(CSS, unsafe_allow_html=True)

NHOM_SP = [
(“Ong HDPE”,        “HDPE”),
(“Ong PVC nuoc”,    r”PVC.*(?:nuoc|nong dai|nong tron|thoat|cap)”),
(“Ong PVC bom cat”, r”PVC.*(?:cat|bom cat)”),
(“Ong PPR”,         “PPR”),
(“Loi PVC”,         r”(?:Loi|loi|lori)”),
(“Phu kien & Keo”,  r”(?:Noi|Co |Te |Van |Keo |Mang|Bit|Y PVC|Y PPR|Giam|Cut)”),
]

COLOR_SEQ = [”#388bfd”,”#56d364”,”#e3b341”,”#ffa198”,”#79c0ff”,”#d2a8ff”,”#ffb800”,”#3fb950”,”#bc8cff”,”#ff7b72”]

PLOTLY_BASE = dict(
paper_bgcolor=”#0d1117”,
plot_bgcolor=”#0d1117”,
font=dict(family=“Be Vietnam Pro, sans-serif”, color=”#c9d1d9”, size=12),
title_font=dict(size=14, color=”#f0f6fc”),
legend=dict(bgcolor=”#161b22”, bordercolor=”#21262d”, borderwidth=1, font=dict(size=11, color=”#c9d1d9”)),
margin=dict(l=10, r=10, t=45, b=10),
colorway=COLOR_SEQ,
)

def pl(fig, **kw):
d = {**PLOTLY_BASE, **kw}
fig.update_layout(**d)
fig.update_xaxes(gridcolor=”#21262d”, linecolor=”#30363d”)
fig.update_yaxes(gridcolor=”#21262d”, linecolor=”#30363d”)
return fig

def fmt(v):
try:
f = float(v)
if abs(f) >= 1e9: return “{:.2f} ty”.format(f/1e9)
if abs(f) >= 1e6: return “{:.1f} tr”.format(f/1e6)
return “{:,.0f}”.format(f)
except Exception:
return str(v)

def fmt_full(v):
try: return “{:,.0f}”.format(float(v))
except Exception: return str(v)

def find_col(df, keywords):
for c in df.columns:
cn = str(c).lower()
if any(k.lower() in cn for k in keywords):
return c
return None

def find_header_row(fb):
try:
raw = pd.read_excel(io.BytesIO(fb), header=None, engine=“openpyxl”, nrows=40)
except Exception:
return 0
for i in range(raw.shape[0]):
vals = [str(v) for v in raw.iloc[i].tolist() if str(v).strip() not in (””, “nan”)]
row_text = “ “.join(vals).lower()
hits = 0
for kw in [“chung tu”, “khach hang”, “ten hang”, “thanh tien”, “loi nhuan”, “nhom kh”]:
if kw in row_text:
hits += 1
if hits >= 3 and len(vals) >= 5:
return i
return 0

def load_all(file_data):
frames = []
for name, fb in file_data:
try:
hr = find_header_row(fb)
df = pd.read_excel(io.BytesIO(fb), header=hr, engine=“openpyxl”)
df.columns = [str(c).strip().replace(”\n”, “ “).replace(”\r”, “”) for c in df.columns]
df = df.loc[:, ~df.columns.str.startswith(“Unnamed”)]
df.dropna(how=“all”, inplace=True)
df[”_file”] = name
frames.append(df)
except Exception as e:
st.warning(“File loi {}: {}”.format(name, e))

```
if not frames:
    return pd.DataFrame()

df = pd.concat(frames, ignore_index=True)

# Numeric cols
for c in df.columns:
    cn = str(c).lower()
    if any(k in cn for k in ["thanh tien", "loi nhuan", "khoi luong", "so luong", "gia ban", "gia von", "don gia"]):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# Date
date_col = find_col(df, ["ngay chung tu", "Ngay chung tu", "chung tu"])
if date_col is None:
    st.error("Khong tim thay cot ngay chung tu.")
    return pd.DataFrame()

df["_date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
df = df[df["_date"].notna()].copy()
df["Nam"]        = df["_date"].dt.year.astype(str)
df["Quy"]        = df["_date"].dt.to_period("Q").astype(str)
df["Thang"]      = df["_date"].dt.to_period("M").astype(str)
df["Thang_lbl"]  = df["_date"].dt.strftime("%m/%Y")
df["Cuoi_thang"] = df["_date"].dt.day >= 28

# Map columns
col_dt   = find_col(df, ["thanh tien ban"])
col_ln   = find_col(df, ["loi nhuan"])
col_kl   = find_col(df, ["khoi luong"])
col_von  = find_col(df, ["thanh tien von"])
col_gban = find_col(df, ["gia ban"])
col_gvon = find_col(df, ["gia von"])
col_sl   = find_col(df, ["so luong"])
col_kh   = find_col(df, ["ten khach hang", "khach hang"])
col_ct   = find_col(df, ["so chung tu"])
col_hang = find_col(df, ["ten hang"])
col_gc   = find_col(df, ["ghi chu"])
col_loai = find_col(df, ["loai don hang"])
col_nhom = find_col(df, ["ma nhom kh"])
col_tnhom= find_col(df, ["ten nhom kh"])
col_kv   = find_col(df, ["khu vuc"])
col_noi  = find_col(df, ["noi giao hang"])
col_kho  = find_col(df, ["ma kho"])
col_frt  = find_col(df, ["freight terms"])
col_ship = find_col(df, ["shipping method"])
col_xe   = find_col(df, ["so xe", "bien so"])
col_tx   = find_col(df, ["tai xe", "tai x"])
col_dvvc = find_col(df, ["ten dvvc"])

def gc(c):
    return df[c] if c else pd.Series(0, index=df.index)

def gs(c, default=""):
    return df[c].astype(str) if c else pd.Series(default, index=df.index)

df["_col_dt"]   = pd.to_numeric(gc(col_dt),   errors="coerce").fillna(0)
df["_col_ln"]   = pd.to_numeric(gc(col_ln),   errors="coerce").fillna(0)
df["_col_kl"]   = pd.to_numeric(gc(col_kl),   errors="coerce").fillna(0)
df["_col_von"]  = pd.to_numeric(gc(col_von),  errors="coerce").fillna(0)
df["_col_gban"] = pd.to_numeric(gc(col_gban), errors="coerce").fillna(0)
df["_col_gvon"] = pd.to_numeric(gc(col_gvon), errors="coerce").fillna(0)
df["_col_sl"]   = pd.to_numeric(gc(col_sl),   errors="coerce").fillna(0)

df["_kh"]    = gs(col_kh)
df["_ct"]    = gs(col_ct)
df["_hang"]  = gs(col_hang)
df["_gc"]    = gs(col_gc).str.upper()
df["_loai"]  = gs(col_loai).str.upper()
df["_nhom"]  = gs(col_nhom)
df["_tnhom"] = gs(col_tnhom)
df["_kv"]    = gs(col_kv)
df["_noi"]   = gs(col_noi)
df["_kho"]   = gs(col_kho).str.replace(".0", "", regex=False).str.strip()
df["_frt"]   = gs(col_frt)
df["_ship"]  = gs(col_ship)
df["_xe"]    = gs(col_xe)
df["_tx"]    = gs(col_tx)
df["_dvvc"]  = gs(col_dvvc)

# Clean nan strings
for c in ["_kh","_ct","_hang","_nhom","_tnhom","_kv","_noi","_kho","_frt","_ship","_xe","_tx","_dvvc"]:
    df[c] = df[c].replace("nan", "").replace("None", "")

# Transaction type
df["Loai_GD"] = "Xuat ban"
mask_tra  = df["_gc"].str.contains(r"NHAP TRA|TRA HANG|TR[AÀ] H[AÀ]NG", regex=True, na=False)
mask_tra2 = df["_loai"].str.contains(r"TRA HANG|HUY HD", regex=True, na=False)
mask_bs   = df["_gc"].str.contains(r"BO SUNG|THAY THE", regex=True, na=False)
df.loc[mask_tra | mask_tra2, "Loai_GD"] = "Tra hang"
df.loc[mask_bs, "Loai_GD"] = "Xuat bo sung"

# Product group
df["Nhom_SP"] = "Khac"
for label, pat in NHOM_SP:
    df.loc[df["_hang"].str.contains(pat, case=False, regex=True, na=False), "Nhom_SP"] = label

df["Bien_LN"] = np.where(df["_col_dt"] != 0, (df["_col_ln"] / df["_col_dt"] * 100).round(2), 0.0)
return df
```

# ── SIDEBAR ───────────────────────────────────────────────────

st.sidebar.markdown(”## Upload du lieu”)
uploaded = st.sidebar.file_uploader(
“File Excel OM_RPT_055”, type=[“xlsx”], accept_multiple_files=True
)

if not uploaded:
st.markdown(’<div class="page-title">Phan tich Ban hang - Hoa Sen</div>’, unsafe_allow_html=True)
st.info(“Upload file Excel bao cao OM_RPT_055 de bat dau.”)
st.stop()

@st.cache_data(show_spinner=“Dang xu ly du lieu…”)
def cached_load(file_data):
return load_all(list(file_data))

file_tuples = tuple((u.name, u.read()) for u in uploaded)
df_all = cached_load(file_tuples)

if df_all.empty:
st.error(“Khong co du lieu hop le.”)
st.stop()

# ── FILTERS ───────────────────────────────────────────────────

st.sidebar.markdown(”—”)
st.sidebar.markdown(”## Bo loc”)

pkd_opts = sorted([x for x in df_all[”_tnhom”].unique() if x not in (””, “nan”, “None”)])
if pkd_opts:
pkd_chon = st.sidebar.multiselect(“Phong Kinh doanh”, pkd_opts, default=pkd_opts)
df_f = df_all[df_all[”_tnhom”].isin(pkd_chon)].copy() if pkd_chon else df_all.copy()
else:
df_f = df_all.copy()
pkd_chon = []

thang_opts = sorted(df_f[“Thang_lbl”].unique().tolist())
thang_chon = st.sidebar.multiselect(“Thang”, thang_opts, default=thang_opts)
if thang_chon:
df_f = df_f[df_f[“Thang_lbl”].isin(thang_chon)].copy()

st.sidebar.markdown(”—”)
view_mode = st.sidebar.radio(“Che do xem”, [“Tong quan”, “Theo Phong KD”, “Theo Khach hang”])

single_kh   = False
scope_label = “Tong quan”

if view_mode == “Theo Khach hang”:
kh_list = sorted([x for x in df_f[”_kh”].unique() if x not in (””, “nan”)])
if not kh_list:
st.warning(“Khong co khach hang phu hop.”)
st.stop()
kh = st.sidebar.selectbox(“Khach hang”, kh_list)
df_scope    = df_f[df_f[”_kh”] == kh].copy()
scope_label = kh
single_kh   = True
elif view_mode == “Theo Phong KD” and pkd_opts:
pv_opts = sorted([x for x in df_f[”_tnhom”].unique() if x not in (””,“nan”)])
pv = st.sidebar.selectbox(“Xem Phong KD”, pv_opts) if pv_opts else None
df_scope    = df_f[df_f[”_tnhom”] == pv].copy() if pv else df_f.copy()
scope_label = pv or “Tong hop”
else:
df_scope = df_f.copy()

time_lbl_map = {“Thang”: “Thang”, “Quy”: “Quy”, “Nam”: “Nam”}
time_lbl = st.sidebar.radio(“Cum thoi gian”, [“Thang”, “Quy”, “Nam”], index=0)
time_col = time_lbl_map[time_lbl]

df_ban = df_scope[df_scope[“Loai_GD”] == “Xuat ban”].copy()

# ── HEADER ────────────────────────────────────────────────────

dmin = df_scope[”_date”].min()
dmax = df_scope[”_date”].max()
ds = “{} - {}”.format(
dmin.strftime(”%d/%m/%Y”) if pd.notna(dmin) else “?”,
dmax.strftime(”%d/%m/%Y”) if pd.notna(dmax) else “?”
)
st.markdown(’<div class="page-title">📊 {}</div>’.format(scope_label), unsafe_allow_html=True)
st.markdown(’<div class="page-sub">{} | {} | PKD: {} | Thang: {}</div>’.format(
ds, time_lbl, len(pkd_chon) if pkd_chon else “Tat ca”,
len(thang_chon) if thang_chon else “Tat ca”
), unsafe_allow_html=True)

if df_ban.empty:
st.warning(“Khong co du lieu xuat ban cho bo loc da chon.”)
st.stop()

tong_dt = df_ban[”_col_dt”].sum()
tong_ln = df_ban[”_col_ln”].sum()
tong_kl = df_ban[”_col_kl”].sum() / 1000
bien_ln = (tong_ln / tong_dt * 100) if tong_dt else 0
n_ct    = df_ban[”_ct”].nunique()
n_kh    = df_ban[”_kh”].nunique()
n_sp    = df_ban[”_hang”].nunique()

kpis = [
(“Doanh thu”,  fmt(tong_dt) + “ d”),
(“Loi nhuan”,  fmt(tong_ln) + “ d”),
(“Bien LN”,    “{:.1f}%”.format(bien_ln)),
(“Khoi luong”, “{:,.1f} tan”.format(tong_kl)),
(“Chung tu”,   “{:,}”.format(n_ct)),
(“Khach hang”, “{:,}”.format(n_kh)),
(“San pham”,   “{:,}”.format(n_sp)),
]
cols_kpi = st.columns(len(kpis))
for col, (lab, val) in zip(cols_kpi, kpis):
col.markdown(
‘<div class="kpi-card"><div class="kpi-val">{}</div><div class="kpi-lab">{}</div></div>’.format(val, lab),
unsafe_allow_html=True
)
st.markdown(””)

# ── TABS ──────────────────────────────────────────────────────

tab_pkd, tab_time, tab_sp, tab_ln, tab_giao, tab_freq, tab_risk = st.tabs([
“🏢 Phong KD & KH”, “📅 Thoi gian”, “📦 San pham”,
“💹 Loi nhuan”, “🚚 Giao hang”, “🔁 Tan suat”, “⚠️ Rui ro”
])

# ── TAB 1: PHONG KD & KH ──────────────────────────────────────

with tab_pkd:
has_pkd = df_ban[”_tnhom”].replace(””, “nan”).nunique() > 1

```
if has_pkd:
    st.markdown('<div class="section-title">Co cau DT: Phong KD → Khach hang</div>', unsafe_allow_html=True)
    df_sun = df_ban.groupby(["_tnhom","_kh"]).agg(DT=("_col_dt","sum")).reset_index()
    df_sun = df_sun[df_sun["DT"] > 0]
    if not df_sun.empty:
        fig_sun = px.sunburst(df_sun, path=["_tnhom","_kh"], values="DT",
                               title="Sunburst: Phong KD → Khach hang",
                               color="DT", color_continuous_scale="Blues")
        pl(fig_sun, height=480, showlegend=False)
        st.plotly_chart(fig_sun, use_container_width=True)

    df_pkd2 = df_ban.groupby("_tnhom").agg(
        DT=("_col_dt","sum"), LN=("_col_ln","sum"),
        KL=("_col_kl", lambda x: round(x.sum()/1000,2)),
        N_KH=("_kh","nunique"), N_CT=("_ct","nunique")
    ).reset_index().sort_values("DT", ascending=False)
    df_pkd2["Bien"] = (df_pkd2["LN"] / df_pkd2["DT"].replace(0, np.nan) * 100).round(1).fillna(0)

    fig_pb = go.Figure()
    fig_pb.add_trace(go.Bar(x=df_pkd2["_tnhom"], y=df_pkd2["DT"], name="DT",
                             marker_color="#388bfd",
                             text=[fmt(v) for v in df_pkd2["DT"]], textposition="outside"))
    fig_pb.add_trace(go.Bar(x=df_pkd2["_tnhom"], y=df_pkd2["LN"], name="LN",
                             marker_color="#56d364",
                             text=[fmt(v) for v in df_pkd2["LN"]], textposition="outside"))
    pl(fig_pb, title="DT & LN theo Phong KD", barmode="group", height=360, xaxis_tickangle=-20)
    st.plotly_chart(fig_pb, use_container_width=True)

    df_pkd_show = df_pkd2.copy()
    df_pkd_show["DT"] = df_pkd_show["DT"].map(fmt_full)
    df_pkd_show["LN"] = df_pkd_show["LN"].map(fmt_full)
    df_pkd_show.columns = ["Phong KD","DT (VND)","LN (VND)","KL (tan)","So KH","So CT","Bien (%)"]
    st.dataframe(df_pkd_show, use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">Top 15 Khach hang theo DT</div>', unsafe_allow_html=True)
df_kh2 = df_ban.groupby("_kh").agg(
    DT=("_col_dt","sum"), LN=("_col_ln","sum"),
    KL=("_col_kl", lambda x: round(x.sum()/1000,2)),
    N_CT=("_ct","nunique"), N_SP=("_hang","nunique")
).reset_index().sort_values("DT", ascending=False)
df_kh2["Bien"] = (df_kh2["LN"] / df_kh2["DT"].replace(0, np.nan) * 100).round(1).fillna(0)
df_top15 = df_kh2.head(15).sort_values("DT", ascending=True)

fig_kh = go.Figure(go.Bar(
    y=df_top15["_kh"], x=df_top15["DT"], orientation="h",
    marker=dict(
        color=df_top15["Bien"],
        colorscale=[[0,"#ffa198"],[0.3,"#e3b341"],[0.7,"#3fb950"],[1,"#56d364"]],
        colorbar=dict(title="Bien LN%", tickfont=dict(color="#c9d1d9"), titlefont=dict(color="#c9d1d9")),
        showscale=True
    ),
    text=[fmt(v) for v in df_top15["DT"]], textposition="outside",
    textfont=dict(size=10, color="#c9d1d9")
))
pl(fig_kh, title="Top 15 KH - DT (mau = Bien LN%)", height=480)
st.plotly_chart(fig_kh, use_container_width=True)

df_kh_show = df_kh2.copy()
df_kh_show["DT"] = df_kh_show["DT"].map(fmt_full)
df_kh_show["LN"] = df_kh_show["LN"].map(fmt_full)
df_kh_show.columns = ["Khach hang","DT (VND)","LN (VND)","KL (tan)","So CT","So SP","Bien (%)"]
st.dataframe(df_kh_show, use_container_width=True, hide_index=True)
```

# ── TAB 2: THOI GIAN ─────────────────────────────────────────

with tab_time:
st.markdown(’<div class="section-title">Xu huong theo {}</div>’.format(time_lbl), unsafe_allow_html=True)
df_t = df_ban.groupby(time_col).agg(
DT=(”_col_dt”,“sum”), LN=(”_col_ln”,“sum”),
KL=(”_col_kl”, lambda x: round(x.sum()/1000,3)),
N_CT=(”_ct”,“nunique”), N_KH=(”_kh”,“nunique”)
).reset_index().sort_values(time_col)
df_t[“Bien”] = (df_t[“LN”] / df_t[“DT”].replace(0,np.nan) * 100).round(2).fillna(0)
df_t[“Tang”] = (df_t[“DT”].pct_change() * 100).round(1)

```
fig_t = make_subplots(rows=3, cols=1, shared_xaxes=True,
                       subplot_titles=["DT & LN (VND)", "KL (tan)", "Bien LN (%) & Tang truong (%)"],
                       vertical_spacing=0.1, row_heights=[0.45,0.2,0.35])
fig_t.add_trace(go.Bar(x=df_t[time_col], y=df_t["DT"], name="DT",
                        marker_color="#388bfd", opacity=0.85), row=1, col=1)
fig_t.add_trace(go.Scatter(x=df_t[time_col], y=df_t["LN"], name="LN",
                            mode="lines+markers", line=dict(color="#56d364",width=2.5),
                            marker=dict(size=7)), row=1, col=1)
fig_t.add_trace(go.Bar(x=df_t[time_col], y=df_t["KL"], name="KL (tan)",
                        marker_color="#79c0ff", opacity=0.75), row=2, col=1)
colors_tang = ["#56d364" if v >= 0 else "#ffa198" for v in df_t["Tang"].fillna(0)]
fig_t.add_trace(go.Scatter(x=df_t[time_col], y=df_t["Bien"], name="Bien LN",
                            mode="lines+markers+text",
                            text=["{:.1f}%".format(v) for v in df_t["Bien"]],
                            textposition="top center",
                            textfont=dict(size=10, color="#e3b341"),
                            line=dict(color="#e3b341",width=2.5),
                            marker=dict(size=7)), row=3, col=1)
fig_t.add_trace(go.Bar(x=df_t[time_col], y=df_t["Tang"], name="Tang truong",
                        marker=dict(color=colors_tang), opacity=0.5), row=3, col=1)
fig_t.update_layout(
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="Be Vietnam Pro", color="#c9d1d9", size=11),
    height=620, showlegend=True,
    legend=dict(bgcolor="#161b22", bordercolor="#21262d", orientation="h", y=-0.05),
    margin=dict(l=10, r=10, t=40, b=10)
)
fig_t.update_xaxes(gridcolor="#21262d", linecolor="#30363d")
fig_t.update_yaxes(gridcolor="#21262d", linecolor="#30363d")
for ann in fig_t.layout.annotations:
    ann.font.color = "#8b949e"
    ann.font.size  = 12
st.plotly_chart(fig_t, use_container_width=True)

df_td = df_t.copy()
df_td["DT"] = df_td["DT"].map(fmt_full)
df_td["LN"] = df_td["LN"].map(fmt_full)
st.dataframe(df_td[[time_col,"DT","LN","KL","N_CT","N_KH","Bien"]], use_container_width=True, hide_index=True)

if not single_kh:
    st.markdown('<div class="section-title">Heatmap DT: Khach hang x Thang</div>', unsafe_allow_html=True)
    df_hm = df_ban.groupby(["_kh","Thang"])["_col_dt"].sum().reset_index()
    df_piv = df_hm.pivot(index="_kh", columns="Thang", values="_col_dt").fillna(0)
    top_kh = df_piv.sum(axis=1).nlargest(min(20, len(df_piv))).index
    fig_hm = px.imshow(
        df_piv.loc[top_kh],
        color_continuous_scale=[[0,"#0d1117"],[0.3,"#1f3058"],[0.7,"#2d5ea8"],[1,"#388bfd"]],
        aspect="auto", title="Heatmap DT: KH x Thang"
    )
    pl(fig_hm, height=max(350, len(top_kh)*26))
    st.plotly_chart(fig_hm, use_container_width=True)
```

# ── TAB 3: SAN PHAM ──────────────────────────────────────────

with tab_sp:
st.markdown(’<div class="section-title">Co cau San pham</div>’, unsafe_allow_html=True)
df_nhom = df_ban.groupby(“Nhom_SP”).agg(
N=(“Nhom_SP”,“count”),
KL=(”_col_kl”, lambda x: round(x.sum()/1000,2)),
DT=(”_col_dt”,“sum”)
).reset_index().sort_values(“DT”, ascending=False)

```
c1, c2 = st.columns(2)
with c1:
    fig_n1 = go.Figure(go.Bar(
        x=df_nhom["Nhom_SP"], y=df_nhom["DT"],
        marker=dict(color=COLOR_SEQ[:len(df_nhom)]),
        text=[fmt(v) for v in df_nhom["DT"]], textposition="outside",
        textfont=dict(size=11, color="#c9d1d9")
    ))
    pl(fig_n1, title="DT theo Nhom SP", height=360, showlegend=False, xaxis_tickangle=-15)
    st.plotly_chart(fig_n1, use_container_width=True)
with c2:
    fig_n2 = go.Figure(go.Pie(
        labels=df_nhom["Nhom_SP"], values=df_nhom["DT"], hole=0.55,
        marker=dict(colors=COLOR_SEQ[:len(df_nhom)], line=dict(color="#0d1117",width=2)),
        textfont=dict(size=11, color="#f0f6fc"), textinfo="label+percent"
    ))
    pl(fig_n2, title="Ty trong DT theo Nhom SP", height=360)
    st.plotly_chart(fig_n2, use_container_width=True)

df_top_sp = df_ban.groupby("_hang").agg(
    N=("_hang","count"),
    KL=("_col_kl", lambda x: round(x.sum()/1000,2)),
    DT=("_col_dt","sum"), LN=("_col_ln","sum")
).reset_index().sort_values("DT", ascending=False).head(15)
df_top_sp["Bien"] = (df_top_sp["LN"] / df_top_sp["DT"].replace(0,np.nan) * 100).round(1).fillna(0)
df_tops = df_top_sp.sort_values("DT", ascending=True)

fig_sp2 = go.Figure(go.Bar(
    y=df_tops["_hang"], x=df_tops["DT"], orientation="h",
    marker=dict(
        color=df_tops["Bien"],
        colorscale=[[0,"#ffa198"],[0.3,"#e3b341"],[0.7,"#3fb950"],[1,"#56d364"]],
        colorbar=dict(title="Bien LN%", tickfont=dict(color="#c9d1d9"), titlefont=dict(color="#c9d1d9")),
        showscale=True
    ),
    text=[fmt(v) for v in df_tops["DT"]], textposition="outside",
    textfont=dict(size=10, color="#c9d1d9")
))
pl(fig_sp2, title="Top 15 SP - DT (mau = Bien LN%)", height=520)
st.plotly_chart(fig_sp2, use_container_width=True)

top5 = df_top_sp["_hang"].head(5).tolist()
df_tr2 = df_ban[df_ban["_hang"].isin(top5)].groupby(["_hang",time_col])["_col_dt"].sum().reset_index()
if not df_tr2.empty:
    fig_tr2 = px.line(df_tr2, x=time_col, y="_col_dt", color="_hang", markers=True,
                       title="Xu huong Top 5 SP theo {}".format(time_lbl),
                       labels={"_col_dt":"DT (VND)", time_col: time_lbl},
                       color_discrete_sequence=COLOR_SEQ)
    fig_tr2.update_traces(line=dict(width=2.5), marker=dict(size=8))
    pl(fig_tr2, height=360)
    st.plotly_chart(fig_tr2, use_container_width=True)
```

# ── TAB 4: LOI NHUAN ─────────────────────────────────────────

with tab_ln:
st.markdown(’<div class="section-title">Loi nhuan & Phat hien Chinh sach</div>’, unsafe_allow_html=True)
df_lnt = df_ban.groupby(time_col).agg(
DT=(”_col_dt”,“sum”), Von=(”_col_von”,“sum”), LN=(”_col_ln”,“sum”)
).reset_index().sort_values(time_col)
df_lnt[“Bien”] = (df_lnt[“LN”] / df_lnt[“DT”].replace(0,np.nan) * 100).round(2).fillna(0)

```
fig_ln2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                         subplot_titles=["DT / Von / LN (VND)", "Bien LN (%) theo {}".format(time_lbl)],
                         vertical_spacing=0.14, row_heights=[0.6,0.4])
fig_ln2.add_trace(go.Bar(x=df_lnt[time_col], y=df_lnt["DT"], name="DT",
                          marker_color="#388bfd", opacity=0.8), row=1, col=1)
fig_ln2.add_trace(go.Bar(x=df_lnt[time_col], y=df_lnt["Von"], name="Von",
                          marker_color="#e05c5c", opacity=0.7), row=1, col=1)
fig_ln2.add_trace(go.Scatter(x=df_lnt[time_col], y=df_lnt["LN"], name="LN",
                              mode="lines+markers", line=dict(color="#56d364",width=2.5),
                              marker=dict(size=8)), row=1, col=1)
fig_ln2.add_trace(go.Scatter(x=df_lnt[time_col], y=df_lnt["Bien"], name="Bien LN",
                              mode="lines+markers+text",
                              text=["{:.1f}%".format(v) for v in df_lnt["Bien"]],
                              textposition="top center",
                              textfont=dict(size=10, color="#e3b341"),
                              line=dict(color="#e3b341",width=2.5), marker=dict(size=8),
                              fill="tozeroy", fillcolor="rgba(227,179,65,0.08)"), row=2, col=1)
fig_ln2.update_layout(
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(family="Be Vietnam Pro", color="#c9d1d9", size=11),
    height=520, barmode="group",
    legend=dict(bgcolor="#161b22", bordercolor="#21262d", orientation="h", y=-0.05),
    margin=dict(l=10, r=10, t=40, b=10)
)
fig_ln2.update_xaxes(gridcolor="#21262d", linecolor="#30363d")
fig_ln2.update_yaxes(gridcolor="#21262d", linecolor="#30363d")
for ann in fig_ln2.layout.annotations:
    ann.font.color = "#8b949e"
    ann.font.size  = 12
st.plotly_chart(fig_ln2, use_container_width=True)

if len(df_lnt) >= 2:
    mb = df_lnt["Bien"].mean()
    sb = df_lnt["Bien"].std() or 1
    anom = df_lnt[df_lnt["Bien"] < mb - sb*1.5]
    if not anom.empty:
        st.markdown('<div class="section-title">Ky nghi co Chiet khau bat thuong</div>', unsafe_allow_html=True)
        for _, r in anom.iterrows():
            bien_val = r["Bien"]
            ky_val   = r[time_col]
            st.markdown(
                '<div class="risk-high"><b>{}</b>: Bien LN = {:.1f}% (TB: {:.1f}%) - Nghi chiet khau lon</div>'.format(ky_val, bien_val, mb),
                unsafe_allow_html=True
            )

st.markdown('<div class="section-title">Gia ban vs Gia von</div>', unsafe_allow_html=True)
if df_ban["_col_gban"].sum() > 0 and df_ban["_col_gvon"].sum() > 0:
    df_lo2 = df_ban[
        (df_ban["_col_gban"] > 0) &
        (df_ban["_col_gvon"] > 0) &
        (df_ban["_col_gban"] < df_ban["_col_gvon"])
    ]
    if not df_lo2.empty:
        st.error("{} dong gia ban < gia von".format(len(df_lo2)))
        st.dataframe(df_lo2[["_date","_kh","_hang","_col_gban","_col_gvon","_col_ln"]].head(50),
                     use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="risk-low">Khong co dong nao gia ban thap hon gia von.</div>', unsafe_allow_html=True)

df_tra2 = df_scope[df_scope["Loai_GD"] == "Tra hang"]
if not df_tra2.empty:
    st.markdown('<div class="section-title">Hang tra lai</div>', unsafe_allow_html=True)
    tong_tra_val = abs(df_tra2["_col_dt"].sum())
    st.error("Tong GT tra hang: {} VND ({} dong)".format(fmt_full(tong_tra_val), len(df_tra2)))
    st.dataframe(df_tra2[["_date","_kh","_hang","_col_dt","_gc"]].head(50),
                 use_container_width=True, hide_index=True)
```

# ── TAB 5: GIAO HANG ─────────────────────────────────────────

with tab_giao:
st.markdown(’<div class="section-title">Hinh thuc & Dia diem giao hang</div>’, unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
ft_v = df_ban[df_ban[”_frt”] != “”].groupby(”_frt”).size().reset_index(name=“N”)
if not ft_v.empty:
fig_ft2 = go.Figure(go.Pie(
labels=ft_v[”_frt”], values=ft_v[“N”], hole=0.55,
marker=dict(colors=COLOR_SEQ[:len(ft_v)], line=dict(color=”#0d1117”,width=2)),
textfont=dict(size=11), textinfo=“label+percent”
))
pl(fig_ft2, title=“Dieu kien giao hang”, height=340, showlegend=False)
st.plotly_chart(fig_ft2, use_container_width=True)
with c2:
sm_v = df_ban[df_ban[”_ship”] != “”].groupby(”_ship”).size().reset_index(name=“N”)
if not sm_v.empty:
fig_sm2 = go.Figure(go.Pie(
labels=sm_v[”_ship”], values=sm_v[“N”], hole=0.55,
marker=dict(colors=COLOR_SEQ[:len(sm_v)], line=dict(color=”#0d1117”,width=2)),
textfont=dict(size=11), textinfo=“label+percent”
))
pl(fig_sm2, title=“Phuong tien van chuyen”, height=340, showlegend=False)
st.plotly_chart(fig_sm2, use_container_width=True)

```
df_noi_f = df_ban[df_ban["_noi"] != ""]
if not df_noi_f.empty:
    st.markdown('<div class="section-title">Dia diem giao hang</div>', unsafe_allow_html=True)
    df_noi2 = df_noi_f.groupby("_noi").agg(
        N=("_noi","count"),
        KL=("_col_kl", lambda x: round(x.sum()/1000,2)),
        DT=("_col_dt","sum")
    ).reset_index().sort_values("DT", ascending=False).head(20)
    df_noi_s = df_noi2.sort_values("DT", ascending=True)
    fig_noi2 = go.Figure(go.Bar(
        y=df_noi_s["_noi"], x=df_noi_s["DT"], orientation="h",
        marker=dict(color="#79c0ff", opacity=0.85),
        text=[fmt(v) for v in df_noi_s["DT"]], textposition="outside",
        textfont=dict(size=10)
    ))
    pl(fig_noi2, title="Top 20 Dia diem giao hang", height=max(380, len(df_noi_s)*30))
    st.plotly_chart(fig_noi2, use_container_width=True)

df_kho_f = df_ban[df_ban["_kho"] != ""]
if not df_kho_f.empty and df_kho_f["_kho"].nunique() >= 1:
    st.markdown('<div class="section-title">Kho xuat hang</div>', unsafe_allow_html=True)
    df_kho2 = df_kho_f.groupby("_kho").agg(
        N=("_kho","count"), DT=("_col_dt","sum")
    ).reset_index().sort_values("DT", ascending=False)
    df_kho2["DT"] = df_kho2["DT"].map(fmt_full)
    st.dataframe(df_kho2, use_container_width=True, hide_index=True)
```

# ── TAB 6: TAN SUAT ──────────────────────────────────────────

with tab_freq:
st.markdown(’<div class="section-title">Heatmap tan suat: San pham x Thang</div>’, unsafe_allow_html=True)
df_fr2 = df_ban[df_ban[”_hang”] != “”].groupby([”_hang”,“Thang”]).size().reset_index(name=“N”)
if not df_fr2.empty:
df_piv2 = df_fr2.pivot(index=”_hang”, columns=“Thang”, values=“N”).fillna(0)
top_nn  = df_piv2.sum(axis=1).nlargest(min(25, len(df_piv2))).index
fig_fq2 = px.imshow(
df_piv2.loc[top_nn],
color_continuous_scale=[[0,”#0d1117”],[0.3,”#1f3058”],[0.7,”#2d5ea8”],[1,”#388bfd”]],
aspect=“auto”, title=“Heatmap tan suat SP x Thang”
)
pl(fig_fq2, height=max(400, len(top_nn)*22))
st.plotly_chart(fig_fq2, use_container_width=True)

```
for q in sorted(df_ban["Quy"].dropna().unique()):
    df_q2   = df_ban[df_ban["Quy"] == q]
    months2 = sorted(df_q2["Thang"].dropna().unique())
    with st.expander("{} | {}".format(q, ", ".join(months2))):
        agg2 = df_q2.groupby(["_hang","Thang"]).agg(
            N=("_hang","count"),
            KL=("_col_kl", lambda x: round(x.sum()/1000,2)),
            DT=("_col_dt","sum")
        ).reset_index().sort_values("DT", ascending=False)
        agg2["DT"] = agg2["DT"].map(fmt_full)
        agg2.columns = ["San pham","Thang","So lan","KL (tan)","DT (VND)"]
        st.dataframe(agg2, use_container_width=True, hide_index=True)
```

# ── TAB 7: RUI RO ─────────────────────────────────────────────

with tab_risk:
st.markdown(’<div class="section-title">Nhan dien Rui ro & Bat thuong (12 nhom)</div>’, unsafe_allow_html=True)
risks  = []
score  = 0
tdtb   = df_ban[”_col_dt”].sum()
tlnb   = df_ban[”_col_ln”].sum()
bien_tb2 = (tlnb / tdtb * 100) if tdtb else 0

```
# R1
df_tra3 = df_scope[df_scope["Loai_GD"] == "Tra hang"]
tl_tra3 = (abs(df_tra3["_col_dt"].sum()) / tdtb * 100) if tdtb else 0
if tl_tra3 > 10:
    score += 30
    risks.append(("high","Tra hang","Ty le tra hang <b>{:.1f}%</b> - Rui ro cao".format(tl_tra3), df_tra3))
elif tl_tra3 > 3:
    score += 15
    risks.append(("medium","Tra hang","Ty le tra hang <b>{:.1f}%</b> - Can theo doi".format(tl_tra3), df_tra3))
else:
    risks.append(("low","Tra hang","Ty le tra hang thap: {:.1f}%".format(tl_tra3), None))

# R2
df_lo3 = df_ban[(df_ban["_col_gban"]>0)&(df_ban["_col_gvon"]>0)&(df_ban["_col_gban"]<df_ban["_col_gvon"])]
if not df_lo3.empty:
    score += 25
    risks.append(("high","Ban lo","<b>{}</b> dong gia ban < gia von".format(len(df_lo3)), df_lo3))
else:
    risks.append(("low","Ban lo","Khong co dong gia ban < gia von", None))

# R3
df_lnam = df_ban[df_ban["_col_ln"] < 0]
if not df_lnam.empty:
    score += 20
    risks.append(("high","LN am","<b>{}</b> dong xuat ban co LN am".format(len(df_lnam)), df_lnam))
else:
    risks.append(("low","LN am","Khong co dong xuat ban nao bi lo", None))

# R4
if len(df_lnt) >= 2:
    mb2 = df_lnt["Bien"].mean()
    sb2 = df_lnt["Bien"].std() or 1
    anom2 = df_lnt[df_lnt["Bien"] < mb2 - sb2*1.5]
    if not anom2.empty:
        score += 10
        risks.append(("medium","Bien LN bat thuong",
                       "Ky {} bien LN thap bat thuong".format(", ".join(anom2[time_col].tolist())), None))
    else:
        risks.append(("low","Bien LN","Bien LN on dinh", None))

# R5
dt_c  = df_ban[df_ban["Cuoi_thang"]==True]["_col_dt"].sum()
tl_c  = (dt_c / tdtb * 100) if tdtb else 0
if tl_c > 40:
    score += 15
    risks.append(("high","Tap trung cuoi thang","<b>{:.1f}%</b> DT ngay 28-31 - Nghi day doanh so ao".format(tl_c), None))
elif tl_c > 25:
    score += 8
    risks.append(("medium","Tap trung cuoi thang","{:.1f}% DT cuoi thang - Can kiem tra".format(tl_c), None))
else:
    risks.append(("low","Phan bo thoi gian","Don hang phan bo deu (cuoi thang: {:.1f}%)".format(tl_c), None))

# R6
q1v = df_ban["_col_dt"].quantile(0.25)
q3v = df_ban["_col_dt"].quantile(0.75)
iqr = q3v - q1v
if iqr > 0:
    df_out2 = df_ban[df_ban["_col_dt"] > q3v + 3*iqr]
    if not df_out2.empty:
        score += 10
        risks.append(("medium","Don hang lon bat thuong","<b>{}</b> don vuot 3xIQR".format(len(df_out2)), df_out2))
    else:
        risks.append(("low","Quy mo don hang","Khong co don bat thuong ve gia tri", None))

# R7
df_bs2 = df_scope[df_scope["Loai_GD"] == "Xuat bo sung"]
if not df_bs2.empty:
    score += 12
    risks.append(("medium","Xuat bo sung","<b>{}</b> dong xuat bo sung/thay the".format(len(df_bs2)), df_bs2))
else:
    risks.append(("low","Xuat bo sung","Khong co don bo sung", None))

# R8
n_noi2 = df_ban[df_ban["_noi"] != ""]["_noi"].nunique()
if n_noi2 >= 6:
    score += 10
    risks.append(("medium","Giao hang phan tan","Giao toi <b>{}</b> dia diem - Rui ro phan tan cong no".format(n_noi2), None))
else:
    risks.append(("low","Dia diem giao hang","{} dia diem - Binh thuong".format(n_noi2), None))

# R9
n_kho2 = df_ban[df_ban["_kho"] != ""]["_kho"].nunique()
if n_kho2 >= 2:
    score += 5
    risks.append(("medium","Nhieu kho","KH nhan tu <b>{}</b> kho - Kiem tra nhat quan".format(n_kho2), None))
else:
    risks.append(("low","Kho xuat hang","Xuat tu {} kho - Nhat quan".format(n_kho2 or 1), None))

# R10
n_thang3 = df_ban["Thang"].nunique()
delta3   = (df_ban["_date"].max() - df_ban["_date"].min()).days
n_rng    = max(delta3 // 30, 1)
if n_thang3 / n_rng < 0.5:
    score += 10
    risks.append(("medium","Mua khong deu","Chi mua <b>{}/{}</b> thang - Phu thuoc du an".format(n_thang3, n_rng), None))
else:
    risks.append(("low","Tan suat mua","Mua deu: {} thang co GD".format(n_thang3), None))

# R11
if bien_tb2 < 5:
    score += 20
    risks.append(("high","Bien LN thap","Bien LN = <b>{:.1f}%</b> - Nguy co ban pha gia".format(bien_tb2), None))
elif bien_tb2 < 15:
    score += 8
    risks.append(("medium","Bien LN tong","Bien LN = <b>{:.1f}%</b> - Muc thap".format(bien_tb2), None))
else:
    risks.append(("low","Bien LN tong","Bien LN = {:.1f}% - OK".format(bien_tb2), None))

# R12
df_po2 = df_scope[df_scope["_gc"].str.contains(r"PO|HOP DONG", regex=True, na=False)]
if not df_po2.empty:
    score += 8
    risks.append(("medium","Don PO/Du an",
                   "<b>{}</b> CT co PO/HD - Thanh toan cham NET30-90".format(df_po2["_ct"].nunique()), df_po2))

# Score display
n_hi = sum(1 for l,_,_,_ in risks if l=="high")
n_md = sum(1 for l,_,_,_ in risks if l=="medium")
n_lo = sum(1 for l,_,_,_ in risks if l=="low")

if score >= 60:
    color3, label3, bg3 = "#ffa198", "RUI RO CAO", "rgba(218,54,51,0.1)"
elif score >= 30:
    color3, label3, bg3 = "#e3b341", "RUI RO TRUNG BINH", "rgba(187,128,9,0.1)"
else:
    color3, label3, bg3 = "#56d364", "RUI RO THAP", "rgba(35,134,54,0.1)"

st.markdown(
    '<div style="background:{};border:1px solid {};border-radius:12px;padding:24px;text-align:center;margin:10px 0 20px 0;">'
    '<div style="font-size:26px;font-weight:900;color:{};">{}</div>'
    '<div style="font-size:15px;color:#8b949e;margin-top:10px;">'
    'Diem rui ro: <b style="color:{};font-size:18px;">{} / 130</b>'
    '&nbsp;|&nbsp; Cao: {} &nbsp; TB: {} &nbsp; Thap: {}'
    '</div></div>'.format(bg3,color3,color3,label3,color3,score,n_hi,n_md,n_lo),
    unsafe_allow_html=True
)
pct3 = min(score/130*100, 100)
st.markdown(
    '<div style="background:#161b22;border-radius:6px;height:8px;margin:-10px 0 20px 0;overflow:hidden;">'
    '<div style="background:{};width:{:.0f}%;height:100%;border-radius:6px;"></div></div>'.format(color3, pct3),
    unsafe_allow_html=True
)

for lvl, cat, msg, detail in risks:
    st.markdown('<div class="risk-{}"><b>[{}]</b> {}</div>'.format(lvl, cat, msg), unsafe_allow_html=True)
    if detail is not None and not detail.empty and lvl in ["high","medium"]:
        with st.expander("Chi tiet - {} ({} dong)".format(cat, len(detail))):
            show_c2 = [c for c in ["_date","_kh","_hang","_col_dt","_col_ln","_col_gban","_col_gvon","_gc"] if c in detail.columns]
            d3 = detail[show_c2].head(50).copy()
            for c2 in ["_col_dt","_col_ln","_col_gban","_col_gvon"]:
                if c2 in d3.columns:
                    d3[c2] = d3[c2].map(fmt_full)
            st.dataframe(d3, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    '<div class="risk-info">File OM_RPT_055 khong chua ngay thanh toan thuc te.<br>'
    'Can bo sung: So AR Aging, Lich su thanh toan.<br>'
    'Dau hieu tu du lieu: Ghi chu PO = TT cham | Tra hang = tranh chap | Nhieu dia diem giao = cong no phan tan.</div>',
    unsafe_allow_html=True
)
```