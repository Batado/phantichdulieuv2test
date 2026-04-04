import io
import warnings
warnings.filterwarnings(“ignore”)
import unicodedata

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────

st.set_page_config(
page_title=“Phan tich KH - Hoa Sen”,
layout=“wide”,
page_icon=“📊”,
initial_sidebar_state=“expanded”
)

st.markdown(”””

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

“””, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────

# UTILITIES

# ─────────────────────────────────────────────────────────────

def strip_acc(s):
“”“Remove Vietnamese diacritics, return lowercase ASCII-like string.”””
s = unicodedata.normalize(“NFD”, str(s))
return “”.join(c for c in s if unicodedata.category(c) != “Mn”).lower().strip()

def fmt_vnd(v):
try:
f = float(v)
if abs(f) >= 1e9: return “{:.2f} ty”.format(f / 1e9)
if abs(f) >= 1e6: return “{:.1f} tr”.format(f / 1e6)
return “{:,.0f}”.format(f)
except Exception:
return str(v)

def fmt_full(v):
try: return “{:,.0f}”.format(float(v))
except Exception: return str(v)

def safe_pct(a, b):
try:
if float(b) == 0: return 0.0
return round(float(a) / float(b) * 100, 2)
except Exception:
return 0.0

COLORS = [”#4e79d4”,”#26c281”,”#f0a500”,”#e74c3c”,”#9b59b6”,”#1abc9c”,”#e67e22”,”#3498db”]

DARK = dict(
paper_bgcolor=”#0d1117”, plot_bgcolor=”#0d1117”,
font=dict(color=”#c9d1d9”, size=12),
title_font=dict(size=14, color=”#f0f6fc”),
legend=dict(bgcolor=”#161b22”, bordercolor=”#30363d”, borderwidth=1),
margin=dict(l=10, r=10, t=45, b=10),
)

def dark(fig, h=420, **kw):
fig.update_layout(**{**DARK, “height”: h, **kw})
fig.update_xaxes(gridcolor=”#21262d”, linecolor=”#30363d”, tickfont=dict(color=”#8b949e”))
fig.update_yaxes(gridcolor=”#21262d”, linecolor=”#30363d”, tickfont=dict(color=”#8b949e”))
return fig

NHOM_SP_PAT = [
(“Ong HDPE”,       “hdpe”),
(“Ong PVC nuoc”,   r”pvc.*(nuoc|nong dai|nong tron|thoat|cap)”),
(“Ong PVC bom cat”,r”pvc.*(cat|bom cat)”),
(“Ong PPR”,        “ppr”),
(“Loi PVC”,        r”(loi |lori)”),
(“Phu kien & Keo”, r”(noi |co |te |van |keo |mang|bit |y pvc|y ppr|giam|cut)”),
]

# ─────────────────────────────────────────────────────────────

# HEADER ROW DETECTION

# ─────────────────────────────────────────────────────────────

def find_header_row(fb):
try:
raw = pd.read_excel(io.BytesIO(fb), header=None, engine=“openpyxl”, nrows=40)
except Exception:
return 0
kws = [“so chung tu”,“ngay chung tu”,“ten khach hang”,“ten hang”,
“thanh tien ban”,“loi nhuan”,“ten nhom kh”,“khu vuc”,“ma nhom kh”]
for i in range(raw.shape[0]):
row_vals = [str(v).strip() for v in raw.iloc[i].tolist()
if str(v).strip() not in (””,“nan”,“none”,“None”)]
if len(row_vals) < 5:
continue
row_text = strip_acc(” “.join(row_vals))
hits = sum(1 for k in kws if k in row_text)
if hits >= 3:
return i
return 0

# ─────────────────────────────────────────────────────────────

# COLUMN FINDER (uses stripped names)

# ─────────────────────────────────────────────────────────────

def find_col(df_cols_stripped, keyword):
“”“Return original col name whose stripped name contains keyword.”””
for orig, stripped in df_cols_stripped:
if keyword in stripped:
return orig
return None

# ─────────────────────────────────────────────────────────────

# LOAD DATA

# ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=“Dang xu ly du lieu…”)
def load_all(file_data):
frames = []
for name, fb in file_data:
try:
hr = find_header_row(fb)
df = pd.read_excel(io.BytesIO(fb), header=hr, engine=“openpyxl”)
df.columns = [str(c).strip().replace(”\n”,” “).replace(”\r”,””)
for c in df.columns]
df = df.loc[:, ~df.columns.str.startswith(“Unnamed”)]
df.dropna(how=“all”, inplace=True)
df[”_file”] = name
frames.append(df)
except Exception as e:
st.warning(“Loi doc file {}: {}”.format(name, str(e)))

```
if not frames:
    return pd.DataFrame()

df = pd.concat(frames, ignore_index=True)

# Build stripped col lookup: [(orig, stripped), ...]
cols_s = [(c, strip_acc(c)) for c in df.columns]

# ── Date ──
dc = find_col(cols_s, "ngay chung tu")
if dc is None:
    dc = find_col(cols_s, "ngay ct")
if dc is None:
    st.error("Khong tim thay cot ngay chung tu.")
    return pd.DataFrame()

df["_date"] = pd.to_datetime(df[dc], dayfirst=True, errors="coerce")
df = df[df["_date"].notna()].copy()
df["Thang"] = df["_date"].dt.to_period("M").astype(str)
df["Quy"]   = df["_date"].dt.to_period("Q").astype(str)
df["_day"]  = df["_date"].dt.day
df["_cuoi"] = df["_day"] >= 28

# ── Numeric ──
num_targets = {
    "_dt":   ["thanh tien ban"],
    "_von":  ["thanh tien von"],
    "_ln":   ["loi nhuan"],
    "_kl":   ["khoi luong"],
    "_sl":   ["so luong"],
    "_gban": ["gia ban"],
    "_gvon": ["gia von"],
}
for priv, kws_list in num_targets.items():
    found = False
    for kw in kws_list:
        c = find_col(cols_s, kw)
        if c and "gross" not in strip_acc(c) and "thuc te" not in strip_acc(c):
            df[priv] = pd.to_numeric(df[c], errors="coerce").fillna(0)
            found = True
            break
    if not found:
        df[priv] = 0.0

# ── Text ──
text_targets = {
    "_kh":      ["ten khach hang"],
    "_ct":      ["so chung tu"],
    "_hang":    ["ten hang"],
    "_nhom_kh": ["ten nhom kh"],
    "_ma_nhom": ["ma nhom kh"],
    "_kv":      ["khu vuc"],
    "_noi":     ["noi giao hang"],
    "_kho":     ["ma kho"],
    "_gc":      ["ghi chu"],
    "_loai":    ["loai don hang"],
    "_frt":     ["freight terms"],
    "_ship":    ["shipping method"],
    "_xe":      ["so xe"],
    "_tx":      ["tai xe"],
    "_dvvc":    ["ten dvvc"],
}
for priv, kws_list in text_targets.items():
    found = False
    for kw in kws_list:
        c = find_col(cols_s, kw)
        if c:
            df[priv] = df[c].fillna("").astype(str).str.strip()
            found = True
            break
    if not found:
        df[priv] = ""

# Clean spurious nan strings
str_privs = ["_kh","_ct","_hang","_nhom_kh","_ma_nhom","_kv","_noi",
             "_kho","_gc","_loai","_frt","_ship","_xe","_tx","_dvvc"]
for c in str_privs:
    df[c] = df[c].replace({"nan":"","none":"","None":"","NaN":"","<NA>":""}).str.strip()

# ── Loai GD ──
gc_up   = df["_gc"].str.upper()
loai_up = df["_loai"].str.upper()
df["Loai_GD"] = "Xuat ban"
tra_mask = (loai_up.str.contains("TRA HANG|HUY HD", regex=True, na=False) |
            gc_up.str.contains("NHAP TRA|TRA HANG", regex=True, na=False))
bs_mask  = gc_up.str.contains(r"BO SUNG|THAY THE|BS PKTM|BS ", regex=True, na=False)
df.loc[tra_mask, "Loai_GD"] = "Tra hang"
df.loc[bs_mask & ~tra_mask, "Loai_GD"] = "Xuat bo sung"

# ── Nhom SP (strip accents of product name for matching) ──
df["Nhom_SP"] = "Khac"
hang_stripped = df["_hang"].apply(strip_acc)
for label, pat in NHOM_SP_PAT:
    try:
        mask = hang_stripped.str.contains(pat, case=False, regex=True, na=False)
        df.loc[mask, "Nhom_SP"] = label
    except Exception:
        pass

return df
```

# ─────────────────────────────────────────────────────────────

# RISK SCORE HELPER

# ─────────────────────────────────────────────────────────────

def calc_risk(df_ban_sub, df_all_sub):
sc = 0
dt = df_ban_sub[”_dt”].sum()
ln = df_ban_sub[”_ln”].sum()
bien = safe_pct(ln, dt)
tra_dt = abs(df_all_sub[df_all_sub[“Loai_GD”]==“Tra hang”][”_dt”].sum())
tl_tra = safe_pct(tra_dt, dt)
n_bs = len(df_all_sub[df_all_sub[“Loai_GD”]==“Xuat bo sung”])

```
if tl_tra > 10: sc += 30
elif tl_tra > 3: sc += 15
if bien < 5: sc += 25
elif bien < 15: sc += 10
if n_bs > 0: sc += 10
return sc, bien, tl_tra
```

def risk_label(sc):
if sc >= 50: return “🔴 Cao”
if sc >= 25: return “🟡 Trung binh”
return “🟢 Thap”

# ─────────────────────────────────────────────────────────────

# SIDEBAR UPLOAD

# ─────────────────────────────────────────────────────────────

st.sidebar.markdown(”## 📂 Upload du lieu”)
uploaded_files = st.sidebar.file_uploader(
“File Excel bao cao ban hang (OM_RPT_055)”,
type=[“xlsx”],
accept_multiple_files=True
)

if not uploaded_files:
st.markdown(”## 👈 Upload file Excel de bat dau phan tich”)
st.info(“Ho tro bao cao OM_RPT_055 - Hoa Sen. Header tu dong nhan dien.”)
st.stop()

file_data = tuple((u.name, u.read()) for u in uploaded_files)
df_all = load_all(file_data)

if df_all.empty:
st.error(“Khong co du lieu hop le. Vui long kiem tra file.”)
st.stop()

# ─────────────────────────────────────────────────────────────

# SIDEBAR FILTERS

# ─────────────────────────────────────────────────────────────

st.sidebar.markdown(”—”)
st.sidebar.markdown(”## 🔍 Bo loc”)

# 1. Nhom KH (Phong KD)

nhom_opts = sorted([x for x in df_all[”_nhom_kh”].unique() if x != “”])
if nhom_opts:
nhom_chon = st.sidebar.multiselect(
“🏢 Phong Kinh Doanh”,
nhom_opts,
default=nhom_opts
)
df_f = df_all[df_all[”_nhom_kh”].isin(nhom_chon)].copy() if nhom_chon else df_all.copy()
else:
nhom_chon = []
df_f = df_all.copy()

# 2. Khu vuc

kv_opts = sorted([x for x in df_f[”_kv”].unique() if x != “”])
if kv_opts:
kv_chon = st.sidebar.multiselect(
“🗺️ Khu vuc”,
kv_opts,
default=kv_opts
)
if kv_chon:
df_f = df_f[df_f[”_kv”].isin(kv_chon)].copy()
else:
kv_chon = []

# 3. Khach hang

kh_opts = sorted([x for x in df_f[”_kh”].unique() if x != “”])
if not kh_opts:
st.error(“Khong co khach hang sau khi ap bo loc. Hay mo rong bo loc.”)
st.stop()
kh_sel = st.sidebar.selectbox(“👤 Khach hang”, kh_opts)

# 4. Quy

quy_opts = sorted(df_f[“Quy”].dropna().unique().tolist())
quy_chon = st.sidebar.multiselect(“📅 Quy”, quy_opts, default=quy_opts)
if not quy_chon:
quy_chon = quy_opts

# Apply

df = df_f[(df_f[”_kh”] == kh_sel) & (df_f[“Quy”].isin(quy_chon))].copy()
df_ban = df[df[“Loai_GD”] == “Xuat ban”].copy()
df_tra = df[df[“Loai_GD”] == “Tra hang”].copy()
df_bs  = df[df[“Loai_GD”] == “Xuat bo sung”].copy()

# ─────────────────────────────────────────────────────────────

# PAGE HEADER + KPI

# ─────────────────────────────────────────────────────────────

dmin = df[”_date”].min()
dmax = df[”_date”].max()
ds   = “{} - {}”.format(
dmin.strftime(”%d/%m/%Y”) if pd.notna(dmin) else “?”,
dmax.strftime(”%d/%m/%Y”) if pd.notna(dmax) else “?”
)

nhom_str = “, “.join(nhom_chon[:3]) + (”…” if len(nhom_chon) > 3 else “”) if nhom_chon else “Tat ca”
kv_str   = “, “.join(kv_chon[:3])  + (”…” if len(kv_chon)   > 3 else “”) if kv_chon   else “Tat ca”

st.markdown(”## 📊 Phan tich: {}”.format(kh_sel))
st.markdown(”*{} | PKD: {} | KV: {} | {} dong*”.format(ds, nhom_str, kv_str, len(df)))

if df_ban.empty:
st.warning(“Khong co du lieu xuat ban cho bo loc da chon.”)
st.stop()

tong_dt  = df_ban[”_dt”].sum()
tong_ln  = df_ban[”_ln”].sum()
tong_kl  = df_ban[”_kl”].sum() / 1000
bien_ln  = safe_pct(tong_ln, tong_dt)
n_ct     = df_ban[”_ct”].nunique()
n_sp     = df_ban[”_hang”].nunique()

ck = st.columns(5)
for col, lab, val in [
(ck[0], “Doanh thu”,   fmt_vnd(tong_dt) + “ d”),
(ck[1], “Loi nhuan”,   fmt_vnd(tong_ln) + “ d”),
(ck[2], “Bien LN”,     “{:.1f}%”.format(bien_ln)),
(ck[3], “Khoi luong”,  “{:,.1f} tan”.format(tong_kl)),
(ck[4], “CT / SP”,     “{} / {}”.format(n_ct, n_sp)),
]:
col.markdown(
‘<div class="kpi-card"><div class="kpi-val">{}</div><div class="kpi-lab">{}</div></div>’.format(val, lab),
unsafe_allow_html=True
)
st.markdown(””)

# ─────────────────────────────────────────────────────────────

# TABS

# ─────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
“📦 San pham”,
“📈 Doanh thu”,
“💹 Loi nhuan”,
“🚚 Giao hang”,
“🔁 Tan suat”,
“⚠️ Rui ro & BCCN”,
])

# ═══════════════════════════════════════════════════════════

# TAB 1 - SAN PHAM

# ═══════════════════════════════════════════════════════════

with tab1:
st.markdown(’<div class="section-title">📦 Co cau san pham theo nhom</div>’, unsafe_allow_html=True)

```
df_nhom = (df_ban.groupby("Nhom_SP")
           .agg(So_lan=("Nhom_SP","count"),
                KL_tan=("_kl", lambda x: round(x.sum()/1000,2)),
                DT=("_dt","sum"))
           .reset_index().sort_values("DT", ascending=False))
df_nhom = df_nhom[df_nhom["DT"] > 0]

if not df_nhom.empty:
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Bar(
            x=df_nhom["Nhom_SP"], y=df_nhom["DT"],
            marker=dict(color=COLORS[:len(df_nhom)]),
            text=[fmt_vnd(v) for v in df_nhom["DT"]],
            textposition="outside", textfont=dict(size=11, color="#c9d1d9")
        ))
        dark(fig, h=360, title="DT theo Nhom SP", showlegend=False,
             xaxis=dict(tickangle=-15, gridcolor="#21262d"),
             yaxis=dict(gridcolor="#21262d"))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = go.Figure(go.Pie(
            labels=df_nhom["Nhom_SP"], values=df_nhom["So_lan"], hole=0.45,
            marker=dict(colors=COLORS[:len(df_nhom)], line=dict(color="#0d1117",width=2)),
            textfont=dict(size=11), textinfo="label+percent"
        ))
        dark(fig2, h=360, title="Ty trong so lan mua")
        st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section-title">🏆 Top 15 san pham theo DT</div>', unsafe_allow_html=True)
df_top = (df_ban.groupby("_hang")
          .agg(So_lan=("_hang","count"),
               KL_tan=("_kl", lambda x: round(x.sum()/1000,2)),
               SL=("_sl","sum"),
               DT=("_dt","sum"))
          .reset_index().sort_values("DT", ascending=False).head(15))
if not df_top.empty:
    df_tops = df_top.sort_values("DT", ascending=True)
    fig3 = go.Figure(go.Bar(
        y=df_tops["_hang"], x=df_tops["DT"], orientation="h",
        marker=dict(color="#4e79d4", opacity=0.85),
        text=[fmt_vnd(v) for v in df_tops["DT"]],
        textposition="outside", textfont=dict(size=10, color="#c9d1d9")
    ))
    dark(fig3, h=max(380, len(df_tops)*32), title="Top 15 san pham - DT")
    st.plotly_chart(fig3, use_container_width=True)

    df_top_show = df_top.copy()
    df_top_show["DT"] = df_top_show["DT"].map(fmt_full)
    df_top_show.columns = ["San pham","So lan","KL (tan)","SL","DT (VND)"]
    st.dataframe(df_top_show, use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">🎯 Nhan dinh muc dich su dung</div>', unsafe_allow_html=True)
nhom_set = set(df_nhom["Nhom_SP"].tolist()) if not df_nhom.empty else set()
notes = {
    "Ong HDPE":       "🔵 Ong HDPE (lon): Du an ha tang, cap thoat nuoc cong trinh lon.",
    "Ong PVC nuoc":   "🟢 Ong PVC nuoc: Xay dung dan dung, cong nghiep, nong nghiep.",
    "Ong PVC bom cat":"🟡 Ong PVC bom cat: Thuy loi, nong nghiep, nuoi trong thuy san.",
    "Ong PPR":        "🟠 Ong PPR: He thong nuoc nong/lanh noi that, dan dung.",
    "Loi PVC":        "⚪ Loi PVC: KH co the la dai ly hoac nha SX thu cap.",
    "Phu kien & Keo": "🔴 Phu kien & Keo: Tu thi cong hoac ban lai tron goi.",
}
shown = False
for k, v in notes.items():
    if k in nhom_set:
        st.markdown('<div class="risk-low">{}</div>'.format(v), unsafe_allow_html=True)
        shown = True
if not shown:
    st.info("Khong du du lieu de nhan dinh.")
```

# ═══════════════════════════════════════════════════════════

# TAB 2 - DOANH THU

# ═══════════════════════════════════════════════════════════

with tab2:
st.markdown(’<div class="section-title">📈 Bien dong DT, KL, SL theo thang</div>’, unsafe_allow_html=True)

```
df_m = (df_ban.groupby("Thang")
        .agg(DT=("_dt","sum"),
             KL=("_kl", lambda x: round(x.sum()/1000,3)),
             SL=("_sl","sum"),
             So_CT=("_ct","nunique"))
        .reset_index().sort_values("Thang"))

if not df_m.empty:
    fig_t = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           subplot_titles=["DT (VND) & KL (tan)", "SL & So chung tu"],
                           vertical_spacing=0.14)
    fig_t.add_trace(go.Bar(x=df_m["Thang"], y=df_m["DT"], name="DT",
                            marker_color="#4e79d4", opacity=0.85), row=1, col=1)
    fig_t.add_trace(go.Scatter(x=df_m["Thang"], y=df_m["KL"], name="KL (tan)",
                                mode="lines+markers",
                                line=dict(color="#f0a500",width=2),
                                marker=dict(size=7)), row=1, col=1)
    fig_t.add_trace(go.Bar(x=df_m["Thang"], y=df_m["SL"], name="SL",
                            marker_color="#26c281", opacity=0.8), row=2, col=1)
    fig_t.add_trace(go.Scatter(x=df_m["Thang"], y=df_m["So_CT"], name="So CT",
                                mode="lines+markers",
                                line=dict(color="#e74c3c",width=2),
                                marker=dict(size=7)), row=2, col=1)
    fig_t.update_layout(
        **{k: v for k, v in DARK.items()},
        height=520, showlegend=True,
        legend=dict(bgcolor="#161b22", bordercolor="#30363d",
                    orientation="h", y=-0.09),
    )
    fig_t.update_xaxes(gridcolor="#21262d", linecolor="#30363d")
    fig_t.update_yaxes(gridcolor="#21262d", linecolor="#30363d")
    for ann in fig_t.layout.annotations:
        ann.font.color = "#8b949e"
    st.plotly_chart(fig_t, use_container_width=True)

    df_ms = df_m.copy()
    df_ms["DT"] = df_ms["DT"].map(fmt_full)
    df_ms.columns = ["Thang","DT (VND)","KL (tan)","SL","So CT"]
    st.dataframe(df_ms, use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">📊 Tong hop theo Quy</div>', unsafe_allow_html=True)
df_q = (df_ban.groupby("Quy")
        .agg(DT=("_dt","sum"), KL=("_kl", lambda x: round(x.sum()/1000,2)),
             LN=("_ln","sum"), So_CT=("_ct","nunique"))
        .reset_index())
df_q["Bien (%)"] = [round(safe_pct(row["LN"], row["DT"]),1) for _, row in df_q.iterrows()]
df_qs = df_q.copy()
df_qs["DT"] = df_qs["DT"].map(fmt_full)
df_qs["LN"] = df_qs["LN"].map(fmt_full)
df_qs.columns = ["Quy","DT (VND)","KL (tan)","LN (VND)","So CT","Bien LN (%)"]
st.dataframe(df_qs, use_container_width=True, hide_index=True)
```

# ═══════════════════════════════════════════════════════════

# TAB 3 - LOI NHUAN

# ═══════════════════════════════════════════════════════════

with tab3:
st.markdown(’<div class="section-title">💹 Bien dong loi nhuan & phat hien chinh sach</div>’, unsafe_allow_html=True)

```
df_ln = (df_ban.groupby("Thang")
         .agg(DT=("_dt","sum"), Von=("_von","sum"), LN=("_ln","sum"))
         .reset_index().sort_values("Thang"))
df_ln["Bien"] = [round(safe_pct(r["LN"], r["DT"]),2) for _, r in df_ln.iterrows()]

if not df_ln.empty:
    fig_ln = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=["DT / Von / LN (VND)", "Bien loi nhuan (%)"],
                            vertical_spacing=0.14)
    fig_ln.add_trace(go.Bar(x=df_ln["Thang"], y=df_ln["DT"], name="DT",
                             marker_color="#4e79d4"), row=1, col=1)
    fig_ln.add_trace(go.Bar(x=df_ln["Thang"], y=df_ln["Von"], name="Von",
                             marker_color="#e05c5c"), row=1, col=1)
    fig_ln.add_trace(go.Scatter(x=df_ln["Thang"], y=df_ln["LN"], name="LN",
                                 mode="lines+markers",
                                 line=dict(color="#26c281",width=2),
                                 marker=dict(size=7)), row=1, col=1)
    fig_ln.add_trace(go.Scatter(x=df_ln["Thang"], y=df_ln["Bien"], name="Bien LN",
                                 mode="lines+markers+text",
                                 text=["{:.1f}%".format(v) for v in df_ln["Bien"]],
                                 textposition="top center",
                                 textfont=dict(size=10, color="#f0a500"),
                                 line=dict(color="#f0a500",width=2),
                                 marker=dict(size=7)), row=2, col=1)
    fig_ln.update_layout(
        **{k: v for k, v in DARK.items()},
        height=520, barmode="group",
        legend=dict(bgcolor="#161b22", bordercolor="#30363d",
                    orientation="h", y=-0.09),
    )
    fig_ln.update_xaxes(gridcolor="#21262d", linecolor="#30363d")
    fig_ln.update_yaxes(gridcolor="#21262d", linecolor="#30363d")
    for ann in fig_ln.layout.annotations:
        ann.font.color = "#8b949e"
    st.plotly_chart(fig_ln, use_container_width=True)

    if len(df_ln) >= 2:
        mb  = df_ln["Bien"].mean()
        std = max(float(df_ln["Bien"].std()), 1.0)
        anom = df_ln[df_ln["Bien"] < mb - std]
        st.markdown('<div class="section-title">🔍 Thang nghi co chiet khau bat thuong</div>', unsafe_allow_html=True)
        if not anom.empty:
            for _, r in anom.iterrows():
                st.markdown(
                    '<div class="risk-medium">⚠️ Thang <b>{}</b>: Bien LN = <b>{:.1f}%</b> (TB={:.1f}%) - kha nang co chiet khau/chinh sach</div>'.format(
                        r["Thang"], r["Bien"], mb),
                    unsafe_allow_html=True
                )
        else:
            st.markdown('<div class="risk-low">✅ Khong phat hien thang bat thuong ve bien LN.</div>', unsafe_allow_html=True)

if not df_tra.empty:
    st.markdown('<div class="section-title">↩️ Don hang tra lai</div>', unsafe_allow_html=True)
    tra_cols = [c for c in ["_ct","_date","_hang","_kl","_dt","_gc"] if c in df_tra.columns]
    df_tra_s = df_tra[tra_cols].copy()
    lbl = {"_ct":"So CT","_date":"Ngay","_hang":"Hang","_kl":"KL","_dt":"DT (VND)","_gc":"Ghi chu"}
    if "_dt" in df_tra_s.columns:
        df_tra_s["_dt"] = df_tra_s["_dt"].map(fmt_full)
    df_tra_s.columns = [lbl.get(c,c) for c in tra_cols]
    st.dataframe(df_tra_s, use_container_width=True, hide_index=True)
    st.error("Tong GT tra hang: {} VND".format(fmt_full(abs(df_tra["_dt"].sum()))))

with st.expander("📋 Chi tiet gia ban tung giao dich"):
    gd_cols = [c for c in ["_ct","_date","_hang","_gban","_gvon","_dt","_ln","_gc"] if c in df_ban.columns]
    df_gd = df_ban[gd_cols].sort_values("_date").copy()
    lbl2  = {"_ct":"CT","_date":"Ngay","_hang":"Hang","_gban":"Gia ban","_gvon":"Gia von",
             "_dt":"DT (VND)","_ln":"LN (VND)","_gc":"Ghi chu"}
    for nc in ["_dt","_ln","_gban","_gvon"]:
        if nc in df_gd.columns:
            df_gd[nc] = df_gd[nc].map(fmt_full)
    df_gd.columns = [lbl2.get(c,c) for c in gd_cols]
    st.dataframe(df_gd, use_container_width=True, hide_index=True)
```

# ═══════════════════════════════════════════════════════════

# TAB 4 - GIAO HANG

# ═══════════════════════════════════════════════════════════

with tab4:
st.markdown(’<div class="section-title">🚚 Hinh thuc & dia diem giao hang</div>’, unsafe_allow_html=True)

```
c1, c2 = st.columns(2)
with c1:
    df_frt = df_ban[df_ban["_frt"] != ""].groupby("_frt").size().reset_index(name="N")
    if not df_frt.empty:
        fig_ft = go.Figure(go.Pie(
            labels=df_frt["_frt"], values=df_frt["N"], hole=0.4,
            marker=dict(colors=COLORS[:len(df_frt)], line=dict(color="#0d1117",width=2)),
            textfont=dict(size=11), textinfo="label+percent"
        ))
        dark(fig_ft, h=340, title="Dieu kien giao hang", showlegend=False)
        st.plotly_chart(fig_ft, use_container_width=True)
    else:
        st.info("Khong co du lieu Freight Terms.")

with c2:
    df_shp = df_ban[df_ban["_ship"] != ""].groupby("_ship").size().reset_index(name="N")
    if not df_shp.empty:
        fig_sm = go.Figure(go.Pie(
            labels=df_shp["_ship"], values=df_shp["N"], hole=0.4,
            marker=dict(colors=COLORS[:len(df_shp)], line=dict(color="#0d1117",width=2)),
            textfont=dict(size=11), textinfo="label+percent"
        ))
        dark(fig_sm, h=340, title="Phuong tien van chuyen", showlegend=False)
        st.plotly_chart(fig_sm, use_container_width=True)
    else:
        st.info("Khong co du lieu Shipping method.")

st.markdown('<div class="section-title">📍 Dia diem giao hang</div>', unsafe_allow_html=True)
df_noi_f = df_ban[df_ban["_noi"] != ""]
if not df_noi_f.empty:
    df_noi_g = (df_noi_f.groupby("_noi")
                .agg(So_lan=("_noi","count"),
                     KL=("_kl", lambda x: round(x.sum()/1000,2)),
                     DT=("_dt","sum"))
                .reset_index().sort_values("DT", ascending=False))
    df_noi_s = df_noi_g.copy()
    df_noi_s["DT"] = df_noi_s["DT"].map(fmt_full)
    df_noi_s.columns = ["Dia diem","So lan","KL (tan)","DT (VND)"]
    st.dataframe(df_noi_s, use_container_width=True, hide_index=True)

    top_noi = df_noi_g.sort_values("DT", ascending=True).tail(15)
    fig_noi = go.Figure(go.Bar(
        y=top_noi["_noi"], x=top_noi["DT"], orientation="h",
        marker=dict(color="#79c0ff", opacity=0.85),
        text=[fmt_vnd(v) for v in top_noi["DT"]],
        textposition="outside", textfont=dict(size=10, color="#c9d1d9")
    ))
    dark(fig_noi, h=max(340, len(top_noi)*34), title="Top dia diem giao hang")
    st.plotly_chart(fig_noi, use_container_width=True)
else:
    st.info("Khong co du lieu noi giao hang.")

with st.expander("🚛 Danh sach xe & tai xe"):
    xe_c = [c for c in ["_xe","_tx","_dvvc","_ship","_date","_noi"] if c in df_ban.columns]
    if xe_c:
        df_xe = df_ban[xe_c].drop_duplicates().sort_values("_date")
        lbl_xe = {"_xe":"So xe","_tx":"Tai xe","_dvvc":"DVVC","_ship":"Phuong tien",
                  "_date":"Ngay","_noi":"Noi giao"}
        df_xe.columns = [lbl_xe.get(c,c) for c in xe_c]
        st.dataframe(df_xe, use_container_width=True, hide_index=True)
    else:
        st.info("Khong co du lieu xe/tai xe.")
```

# ═══════════════════════════════════════════════════════════

# TAB 5 - TAN SUAT

# ═══════════════════════════════════════════════════════════

with tab5:
st.markdown(’<div class="section-title">🔁 Heatmap tan suat: San pham x Thang</div>’, unsafe_allow_html=True)

```
df_hk = df_ban[df_ban["_hang"] != ""]
if not df_hk.empty:
    df_freq = df_hk.groupby(["_hang","Thang"]).size().reset_index(name="So_lan")
    if not df_freq.empty:
        df_piv = df_freq.pivot(index="_hang", columns="Thang", values="So_lan").fillna(0)
        top_n  = df_piv.sum(axis=1).nlargest(min(20, len(df_piv))).index
        fig_hm = px.imshow(
            df_piv.loc[top_n],
            labels=dict(x="Thang", y="San pham", color="So lan"),
            title="Top SP mua nhieu nhat x Thang",
            color_continuous_scale="Blues", aspect="auto"
        )
        dark(fig_hm, h=max(380, len(top_n)*26))
        st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown('<div class="section-title">📋 Chi tiet theo Quy</div>', unsafe_allow_html=True)
    for qv in sorted(df_hk["Quy"].dropna().unique()):
        dq = df_hk[df_hk["Quy"] == qv]
        months_s = ", ".join(sorted(dq["Thang"].dropna().unique()))
        with st.expander("{} | {}".format(qv, months_s)):
            ag = (dq.groupby(["_hang","Thang"])
                  .agg(So_lan=("_hang","count"),
                       KL=("_kl", lambda x: round(x.sum()/1000,2)),
                       DT=("_dt","sum"))
                  .reset_index().sort_values("DT", ascending=False))
            ag["DT"] = ag["DT"].map(fmt_full)
            ag.columns = ["San pham","Thang","So lan","KL (tan)","DT (VND)"]
            st.dataframe(ag, use_container_width=True, hide_index=True)
else:
    st.info("Khong co du lieu ten hang.")
```

# ═══════════════════════════════════════════════════════════

# TAB 6 - RUI RO & BCCN

# ═══════════════════════════════════════════════════════════

with tab6:
st.markdown(’<div class="section-title">📄 BCCN - Phan tich thanh toan & cong no</div>’, unsafe_allow_html=True)

```
gc_up2 = df["_gc"].str.upper()
df_po  = df[gc_up2.str.contains(r"PO|B[0-9]{3}|HOP DONG", regex=True, na=False)]
n_po   = df_po["_ct"].nunique() if not df_po.empty else 0
n_tra  = df_tra["_ct"].nunique() if not df_tra.empty else 0
n_bs   = df_bs["_ct"].nunique() if not df_bs.empty else 0
gt_tra = abs(df_tra["_dt"].sum()) if not df_tra.empty else 0

mc = st.columns(4)
mc[0].metric("📋 Don PO/HD", n_po)
mc[1].metric("↩️ Phieu tra hang", n_tra)
mc[2].metric("🔄 Xuat bo sung", n_bs)
mc[3].metric("💰 GT tra hang (VND)", fmt_full(gt_tra))

st.markdown("""
```

<div class="info-box">
<b>⚠️ File OM_RPT_055 khong co ngay thanh toan thuc te.</b><br>
Can bo sung: So cong no phai thu (AR Aging), Lich su thanh toan.<br>
Dau hieu: Ghi chu B-xxx/PO = don du an = TT cham NET30-90 |
Tra hang = tranh chap | Nhieu dia diem giao = cong no phan tan.
</div>""", unsafe_allow_html=True)

```
if not df_po.empty:
    with st.expander("{} don co PO / ma du an".format(len(df_po))):
        po_c = [c for c in ["_ct","_date","_hang","_dt","_gc"] if c in df_po.columns]
        df_po_s = df_po[po_c].drop_duplicates().copy()
        if "_dt" in df_po_s.columns:
            df_po_s["_dt"] = df_po_s["_dt"].map(fmt_full)
        lbl_po = {"_ct":"CT","_date":"Ngay","_hang":"Hang","_dt":"DT (VND)","_gc":"Ghi chu"}
        df_po_s.columns = [lbl_po.get(c,c) for c in po_c]
        st.dataframe(df_po_s, use_container_width=True, hide_index=True)

# ── RISK: KH hien tai ──
st.markdown('<div class="section-title">⚠️ Danh gia rui ro: Khach hang hien tai</div>', unsafe_allow_html=True)

risks = []
score = 0
tong_ban = df_ban["_dt"].sum()

# R1 Tra hang
gt_tra_v = abs(df_tra["_dt"].sum()) if not df_tra.empty else 0
tl_tra_v = safe_pct(gt_tra_v, tong_ban)
if tl_tra_v > 10:
    score += 30
    risks.append(("high","↩️ Ty le tra hang <b>{:.1f}%</b> ({} VND) - rui ro cao".format(tl_tra_v, fmt_full(gt_tra_v))))
elif tl_tra_v > 3:
    score += 15
    risks.append(("medium","↩️ Ty le tra hang <b>{:.1f}%</b> - can theo doi".format(tl_tra_v)))
else:
    risks.append(("low","✅ Ty le tra hang thap: {:.1f}%".format(tl_tra_v)))

# R2 Bien LN
tl_ln_v = df_ban["_ln"].sum()
bien_v   = safe_pct(tl_ln_v, tong_ban)
if bien_v < 5:
    score += 25
    risks.append(("high","💹 Bien LN rat thap: <b>{:.1f}%</b> - ban duoi gia hoac chiet khau lon".format(bien_v)))
elif bien_v < 15:
    score += 10
    risks.append(("medium","💹 Bien LN o muc thap: <b>{:.1f}%</b>".format(bien_v)))
else:
    risks.append(("low","✅ Bien LN binh thuong: {:.1f}%".format(bien_v)))

# R3 Bo sung
if not df_bs.empty:
    score += 15
    risks.append(("medium","🔄 Co <b>{}</b> dong xuat bo sung/thay the".format(len(df_bs))))
else:
    risks.append(("low","✅ Khong co don xuat bo sung."))

# R4 Outlier
if len(df_ban) > 4:
    q75 = df_ban["_dt"].quantile(0.75)
    q25 = df_ban["_dt"].quantile(0.25)
    iqr = q75 - q25
    if iqr > 0:
        outs = df_ban[df_ban["_dt"] > q75 + 3*iqr]
        if not outs.empty:
            score += 10
            risks.append(("medium","📦 Co <b>{}</b> don hang gia tri rat lon - kiem soat han muc tin dung".format(len(outs))))
        else:
            risks.append(("low","✅ Khong co don hang gia tri bat thuong."))

# R5 Dia diem phan tan
n_noi3 = df_ban[df_ban["_noi"] != ""]["_noi"].nunique()
if n_noi3 >= 5:
    score += 10
    risks.append(("medium","📍 Giao hang toi <b>{}</b> dia diem - cong no phan tan".format(n_noi3)))
else:
    risks.append(("low","✅ So dia diem: {} (binh thuong)".format(n_noi3)))

# R6 Tan suat
n_thang_m  = df_ban["Thang"].nunique()
delta_d    = (df_ban["_date"].max() - df_ban["_date"].min()).days
n_thang_r  = max(delta_d // 30, 1)
if n_thang_m / n_thang_r < 0.5:
    score += 10
    risks.append(("medium","🔁 Mua chi <b>{}/{}</b> thang - phu thuoc du an".format(n_thang_m, n_thang_r)))
else:
    risks.append(("low","✅ Mua deu: {}/{} thang co GD".format(n_thang_m, n_thang_r)))

# R7 Cuoi thang
dt_cuoi = df_ban[df_ban["_cuoi"]==True]["_dt"].sum()
tl_cuoi = safe_pct(dt_cuoi, tong_ban)
if tl_cuoi > 40:
    score += 15
    risks.append(("high","📅 <b>{:.1f}%</b> DT tap trung ngay 28-31 - nghi day doanh so ao".format(tl_cuoi)))
elif tl_cuoi > 25:
    score += 8
    risks.append(("medium","📅 {:.1f}% DT cuoi thang - kiem tra thuc chat giao nhan".format(tl_cuoi)))
else:
    risks.append(("low","✅ Don hang phan bo deu trong thang (cuoi thang: {:.1f}%)".format(tl_cuoi)))

# Score bar
if score >= 50:
    sc_col, sc_lbl = "#e74c3c", "🔴 RUI RO CAO"
elif score >= 25:
    sc_col, sc_lbl = "#f39c12", "🟡 RUI RO TRUNG BINH"
else:
    sc_col, sc_lbl = "#26c281", "🟢 RUI RO THAP"

pct_b = min(score, 100)
st.markdown(
    '<div style="background:#1a2035;border-radius:10px;padding:20px;text-align:center;margin:12px 0;">'
    '<div style="font-size:32px;font-weight:900;color:{};">{}</div>'
    '<div style="font-size:15px;color:#9aa0b0;margin-top:6px;">'
    'Diem rui ro: <b style="color:{}">{}/100</b></div>'
    '</div>'.format(sc_col, sc_lbl, sc_col, score),
    unsafe_allow_html=True
)
st.markdown(
    '<div style="background:#21262d;border-radius:6px;height:8px;margin:-8px 0 18px 0;overflow:hidden;">'
    '<div style="background:{};width:{}%;height:100%;border-radius:6px;"></div></div>'.format(sc_col, pct_b),
    unsafe_allow_html=True
)
for lvl, msg in risks:
    st.markdown('<div class="risk-{}">{}</div>'.format(lvl, msg), unsafe_allow_html=True)

# ── RISK BY NHOM KH ──
st.markdown('<div class="section-title">🏢 Diem rui ro theo Phong Kinh Doanh (Nhom KH) - cao den thap</div>', unsafe_allow_html=True)

nhom_all = [x for x in df_all["_nhom_kh"].unique() if x != ""]
if nhom_all:
    rows_n = []
    for nh in nhom_all:
        sb = df_all[(df_all["_nhom_kh"]==nh) & (df_all["Loai_GD"]=="Xuat ban")]
        sa = df_all[df_all["_nhom_kh"]==nh]
        if sb.empty:
            continue
        sc_n, bien_n, tl_n = calc_risk(sb, sa)
        rows_n.append({
            "Phong KD":         nh,
            "DT (VND)":         fmt_full(sb["_dt"].sum()),
            "Bien LN (%)":      round(bien_n,1),
            "TL Tra hang (%)":  round(tl_n,1),
            "Diem rui ro":      sc_n,
            "Muc rui ro":       risk_label(sc_n),
        })
    if rows_n:
        df_rn = pd.DataFrame(rows_n).sort_values("Diem rui ro", ascending=False)
        st.dataframe(df_rn, use_container_width=True, hide_index=True)
        if len(df_rn) > 1:
            fig_rn = go.Figure(go.Bar(
                x=df_rn["Phong KD"],
                y=df_rn["Diem rui ro"],
                marker=dict(
                    color=df_rn["Diem rui ro"],
                    colorscale=[[0,"#26c281"],[0.5,"#f39c12"],[1,"#e74c3c"]],
                    showscale=False
                ),
                text=df_rn["Diem rui ro"].astype(str),
                textposition="outside",
                textfont=dict(color="#c9d1d9")
            ))
            dark(fig_rn, h=300, title="Diem rui ro theo Phong KD", showlegend=False)
            st.plotly_chart(fig_rn, use_container_width=True)
else:
    st.info("Khong co du lieu Nhom KH.")

# ── RISK BY KHU VUC ──
st.markdown('<div class="section-title">🗺️ Diem rui ro theo Khu vuc - cao den thap</div>', unsafe_allow_html=True)

kv_all2 = [x for x in df_all["_kv"].unique() if x != ""]
if kv_all2:
    rows_k = []
    for kv_i in kv_all2:
        sb = df_all[(df_all["_kv"]==kv_i) & (df_all["Loai_GD"]=="Xuat ban")]
        sa = df_all[df_all["_kv"]==kv_i]
        if sb.empty:
            continue
        sc_k, bien_k, tl_k = calc_risk(sb, sa)
        n_kh_k = sb["_kh"].nunique()
        if n_kh_k == 1:
            sc_k += 5
        rows_k.append({
            "Khu vuc":          kv_i,
            "So KH":            n_kh_k,
            "DT (VND)":         fmt_full(sb["_dt"].sum()),
            "Bien LN (%)":      round(bien_k,1),
            "TL Tra hang (%)":  round(tl_k,1),
            "Diem rui ro":      sc_k,
            "Muc rui ro":       risk_label(sc_k),
        })
    if rows_k:
        df_rk = pd.DataFrame(rows_k).sort_values("Diem rui ro", ascending=False)
        st.dataframe(df_rk, use_container_width=True, hide_index=True)
        fig_rk = go.Figure(go.Bar(
            x=df_rk["Khu vuc"],
            y=df_rk["Diem rui ro"],
            marker=dict(
                color=df_rk["Diem rui ro"],
                colorscale=[[0,"#26c281"],[0.5,"#f39c12"],[1,"#e74c3c"]],
                showscale=False
            ),
            text=df_rk["Diem rui ro"].astype(str),
            textposition="outside",
            textfont=dict(color="#c9d1d9")
        ))
        dark(fig_rk, h=320, title="Diem rui ro theo Khu vuc", showlegend=False)
        st.plotly_chart(fig_rk, use_container_width=True)
else:
    st.info("Khong co du lieu Khu vuc.")
```