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
st.set_page_config(page_title="Phan tich KH - Hoa Sen", layout="wide", page_icon="U+1F4CA")
st.markdown("""
<style>
.risk-high { background:#4a1010; border-left:4px solid #e74c3c; padding:10px 14px; border-r
.risk-medium { background:#3d2e10; border-left:4px solid #f39c12; padding:10px 14px; border-r
.risk-low { background:#0f3020; border-left:4px solid #26c281; padding:10px 14px; border-r
.section-title { font-size:17px; font-weight:700; color:#e0e0e0; margin:20px 0 10px 0;
padding-bottom:6px; border-bottom:1px solid #2e3350; }
.info-box { background:#1a2035; border-radius:8px; padding:14px; margin:8px 0; color:#ccc; }
.filter-label { font-size:12px; color:#9aa0b0; margin-bottom:2px; }
.risk-badge-cao { display:inline-block; background:#4a1010; color:#e74c3c; border:1px solid
padding:1px 8px; border-radius:10px; font-size:11px; font-weight:700; }
.risk-badge-tb { display:inline-block; background:#3d2e10; color:#f39c12; border:1px solid
padding:1px 8px; border-radius:10px; font-size:11px; font-weight:700; }
.risk-badge-thap { display:inline-block; background:#0f3020; color:#26c281; border:1px solid
padding:1px 8px; border-radius:10px; font-size:11px; font-weight:700; }
</style>
""", unsafe_allow_html=True)
# ======================================================
# UTILITIES
# ======================================================
def strip_acc(s):
s = unicodedata.normalize("NFD", str(s))
return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().strip()
COL_ALIASES = {
"Ten khach hang": "Ngay chung tu": "So chung tu": "Ten hang": ["Ten khach hang", "Ten KH", "Khach hang", "Ten khach", "customer_nam
["Ngay chung tu", "Ngay CT", "date"],
["So chung tu", "So CT", "voucher_no"],
["Ten hang", "Ten ma hang", "Ten SP", "product_name"],
"Ma hang": "Khoi luong": ["Ma hang", "Ma SP", "product_code"],
["Khoi luong", "KL", "weight"],
"So luong": ["So luong", "SL", "qty", "quantity"],
"Thanh tien ban": ["Thanh tien ban", "Doanh thu", "revenue", "amount"],
"Thanh tien von": ["Thanh tien von", "Gia von hang ban", "cost"],
"Loi nhuan": ["Loi nhuan", "Profit", "profit"],
"Gia ban": ["Gia ban", "Don gia", "unit_price"],
"Gia von": ["Gia von", "cost_price"],
"Noi giao hang": ["Noi giao hang", "Dia chi giao hang", "delivery_address"],
"Freight Terms": ["Freight Terms", "Dieu kien giao hang", "freight"],
"Shipping method": ["Shipping method", "Phuong tien", "shipping"],
"Bien so xe": "Tai Xe": ["So xe", "Bien so xe", "plate_no"],
["Tai Xe", "Tai xe", "Driver", "driver"],
"Ten DVVC": ["Ten DVVC", "Don vi van chuyen", "carrier"],
"Ghi chu": ["Ghi chu", "Note", "notes"],
"Khu vuc": ["Khu vuc", "Region", "region"],
"Ten nhom KH": ["Ten nhom KH", "Nhom KH", "sales_group_name"],
"Ma nhom KH": ["Ma nhom KH", "ma_nhom_kh"],
"Ma nhom hang": ["Ma nhom hang", "Nhom hang", "product_group"],
"Don gia van chuyen": ["Don gia van chuyen", "freight_cost"],
"Don gia quy doi": ["Don gia quy doi", "converted_price"],
}
# Map from stripped alias -> standard name (built once)
def _build_alias_map():
m = {}
for std, aliases in COL_ALIASES.items():
for a in aliases:
m[strip_acc(a)] = std
return m
ALIAS_MAP = _build_alias_map()
def normalize_columns(df):
rename = {}
for c in df.columns:
sc = strip_acc(c)
if sc in ALIAS_MAP and c != ALIAS_MAP[sc]:
rename[c] = ALIAS_MAP[sc]
# Only rename if target not already present
final = {}
for old, new in rename.items():
if new not in df.columns:
final[old] = new
df.rename(columns=final, inplace=True)
return df
def safe_num(df, col):
if col in df.columns:
return pd.to_numeric(df[col], errors="coerce").fillna(0)
return pd.Series(0.0, index=df.index)
def find_header_row(file_bytes):
try:
df_raw = pd.read_excel(io.BytesIO(file_bytes), header=None, engine="openpyxl", except Exception:
return 0
kws = ["so chung tu", "ngay chung tu", "ten khach hang",
"ten hang", "thanh tien ban", "loi nhuan", "ten nhom kh", "khu vuc"]
for i in range(df_raw.shape[0]):
row_vals = [str(v).strip() for v in df_raw.iloc[i].tolist()
if str(v).strip() not in ("", "nan", "none")]
if len(row_vals) < 5:
continue
row_text = strip_acc(" ".join(row_vals))
hits = sum(1 for k in kws if k in row_text)
if hits >= 3:
return i
nrows=
return 0
# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data(show_spinner="Dang xu ly du lieu...")
def load_all(file_data):
frames = []
for name, fb in file_data:
try:
hr = find_header_row(fb)
df = pd.read_excel(io.BytesIO(fb), header=hr, engine="openpyxl")
df.columns = [str(c).strip().replace("\n", " ").replace("\r", "") for c in df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
df.dropna(how="all", inplace=True)
normalize_columns(df)
df["Nguon file"] = name
frames.append(df)
except Exception as e:
st.warning("Loi doc file {}: {}".format(name, e))
df.col
if not frames:
return pd.DataFrame()
df = pd.concat(frames, ignore_index=True)
# Check required
date_col = "Ngay chung tu"
kh_col = "Ten khach hang"
if date_col not in df.columns:
st.error("Khong tim thay cot ngay chung tu.")
return pd.DataFrame()
if kh_col not in df.columns:
st.error("Khong tim thay cot ten khach hang.")
return pd.DataFrame()
df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
df = df[df[date_col].notna()].copy()
df["Thang"] = df[date_col].dt.to_period("M").astype(str)
df["Quy"] = df[date_col].dt.to_period("Q").astype(str)
df["_day"] = df[date_col].dt.day
num_cols = ["Thanh tien ban", "Thanh tien von", "Loi nhuan",
"Khoi luong", "So luong", "Gia ban", "Gia von",
"Don gia van chuyen", "Don gia quy doi"]
for col in num_cols:
df[col] = safe_num(df, col)
# Loai GD
gc = df["Ghi chu"].astype(str).str.upper() if "Ghi chu" in df.columns else pd.Series("",
loai = df["Ma nhom KH"].astype(str).str.upper() if "Ma nhom KH" in df.columns else df["Loai GD"] = "Xuat ban"
tra_mask = (gc.str.contains("NHAP TRA|TRA HANG", regex=True, na=False) |
loai.str.contains("TRA HANG|HUY HD", regex=True, na=False))
bs_mask = gc.str.contains("BO SUNG|THAY THE|BS PKTM|BS ", regex=True, na=False)
df.loc[tra_mask, "Loai GD"] = "Tra hang"
df.loc[bs_mask & ~tra_mask, "Loai GD"] = "Xuat bo sung"
pd.Ser
# Nhom SP
ten = df["Ten hang"].astype(str) if "Ten hang" in df.columns else pd.Series("", index=df.
df["Nhom SP"] = "Khac"
sp_map = [
("Ong HDPE", "hdpe"),
("Ong PVC nuoc", r"pvc.*(nuoc|nong dai|nong tron|thoat|cap)"),
("Ong PVC bom cat", r"pvc.*(cat|bom cat)"),
("Ong PPR", "ppr"),
("Loi PVC", r"(loi |lori)"),
("Phu kien & Keo", r"(noi |co |te |van |keo |mang|bit |y pvc|y ppr|giam|cut)"),
]
ten_s = ten.apply(strip_acc)
for label, pat in sp_map:
try:
df.loc[ten_s.str.contains(pat, regex=True, na=False), "Nhom SP"] = label
except Exception:
pass
# Clean text cols
for c in ["Ten khach hang", "Ten nhom KH", "Ma nhom KH", "Khu vuc"]:
if c in df.columns:
df[c] = df[c].fillna("").astype(str).str.strip().replace({"nan":"","None":"","NaN
return df
# ======================================================
# RISK SCORE (pre-compute for all customers)
# ======================================================
def compute_risk(df_kh_all):
"""Compute risk score for a single customer slice (all Loai GD)."""
df_b = df_kh_all[df_kh_all["Loai GD"] == "Xuat ban"]
df_t = df_kh_all[df_kh_all["Loai GD"] == "Tra hang"]
df_s = df_kh_all[df_kh_all["Loai GD"] == "Xuat bo sung"]
if df_b.empty:
return 0
tong_ban = df_b["Thanh tien ban"].sum()
tong_tra = abs(df_t["Thanh tien ban"].sum()) if not df_t.empty else 0
tong_ln = df_b["Loi nhuan"].sum()
tl_tra = (tong_tra / tong_ban * 100) if tong_ban > 0 else 0
bien = (tong_ln / tong_ban * 100) if tong_ban > 0 else 0
sc = 0
if tl_tra > 10: sc += 30
elif tl_tra > 3: sc += 15
if bien < 5: sc += 25
elif bien < 15: sc += 10
if not df_s.empty: sc += 15
if len(df_b) > 4:
q75 = df_b["Thanh tien ban"].quantile(0.75)
q25 = df_b["Thanh tien ban"].quantile(0.25)
iqr = q75 - q25
if iqr > 0 and len(df_b[df_b["Thanh tien ban"] > q75 + 3*iqr]) > 0:
sc += 10
if "Noi giao hang" in df_b.columns and df_b["Noi giao hang"].nunique() >= 5:
sc += 10
n_thang = df_b["Thang"].nunique()
delta_d = (df_b["Ngay chung tu"].max() - df_b["Ngay chung tu"].min()).days
n_range = max(delta_d // 30, 1)
if n_thang / n_range < 0.5:
sc += 10
return sc
def risk_label_short(sc):
if sc >= 50: return "Cao"
if sc >= 25: return "Trung binh"
return "Thap"
def risk_color(sc):
if sc >= 50: return "#e74c3c"
if sc >= 25: return "#f39c12"
return "#26c281"
# ======================================================
# SIDEBAR UPLOAD
# ======================================================
st.sidebar.markdown("## Upload du lieu")
uploaded_files = st.sidebar.file_uploader(
"File Excel bao cao ban hang (OM_RPT_055)",
type=["xlsx"],
accept_multiple_files=True
)
if not uploaded_files:
st.markdown("## Upload file Excel de bat dau phan tich")
st.info("Ho tro bao cao OM_RPT_055 - Hoa Sen. Header tu dong nhan dien.")
st.stop()
file_data = tuple((u.name, u.read()) for u in uploaded_files)
df_all = load_all(file_data)
if df_all.empty:
st.error("Khong co du lieu hop le. Vui long kiem tra file.")
st.stop()
# Pre-compute risk scores for ALL customers (once, before filters)
@st.cache_data(show_spinner=False)
def build_risk_table(file_data):
df = load_all(file_data)
if df.empty or "Ten khach hang" not in df.columns:
return pd.DataFrame()
rows = []
for kh_name, grp in df.groupby("Ten khach hang"):
if not kh_name or str(kh_name) in ("", "nan"):
continue
sc = compute_risk(grp)
nhom = grp["Ten nhom KH"].mode()[0] if "Ten nhom KH" in grp.columns and not grp["Ten
kv = grp["Khu vuc"].mode()[0] if "Khu vuc" in grp.columns and not grp["Khu vuc"].eq
rows.append({
"Ten KH": str(kh_name),
"Ten nhom KH": str(nhom),
"Khu vuc": str(kv),
"Diem rui ro": sc,
"Muc rui ro": risk_label_short(sc),
})
if not rows:
return pd.DataFrame()
return pd.DataFrame(rows)
risk_table = build_risk_table(file_data)
# ======================================================
# SIDEBAR FILTERS (hierarchy: Phong KD -> Khu vuc -> KH sorted by risk)
# ======================================================
st.sidebar.markdown("---")
st.sidebar.markdown("## Bo loc")
# ── Level 1: Phong KD (Ten nhom KH) ──
has_nhom = "Ten nhom KH" in df_all.columns
if has_nhom:
nhom_opts = sorted([x for x in df_all["Ten nhom KH"].unique() if x not in ("", "nan", "No
else:
nhom_opts = []
if nhom_opts:
nhom_chon = st.sidebar.multiselect(
"1. Phong Kinh Doanh",
nhom_opts,
default=nhom_opts,
help="Chon Phong KD de loc Khu vuc va Khach hang"
)
if nhom_chon:
df_after_nhom = df_all[df_all["Ten nhom KH"].isin(nhom_chon)].copy()
else:
df_after_nhom = df_all.copy()
nhom_chon = nhom_opts
else:
nhom_chon = []
df_after_nhom = df_all.copy()
# ── Level 2: Khu vuc (filtered by Phong KD) ──
has_kv = "Khu vuc" in df_after_nhom.columns
if has_kv:
kv_opts = sorted([x for x in df_after_nhom["Khu vuc"].unique() if x not in ("", "nan", "N
else:
kv_opts = []
if kv_opts:
kv_chon = st.sidebar.multiselect(
"2. Khu vuc",
kv_opts,
default=kv_opts,
help="Loc theo khu vuc dia ly"
)
if kv_chon:
df_after_kv = df_after_nhom[df_after_nhom["Khu vuc"].isin(kv_chon)].copy()
else:
df_after_kv = df_after_nhom.copy()
kv_chon = kv_opts
else:
kv_chon = []
df_after_kv = df_after_nhom.copy()
# ── Level 3: Ten KH sorted by risk score asc (thap den cao) ──
kh_in_scope = sorted([x for x in df_after_kv["Ten khach hang"].unique()
if x not in ("", "nan", "None")])
if not kh_in_scope:
st.error("Khong co khach hang sau khi ap bo loc. Hay mo rong bo loc.")
st.stop()
# Build display list: "KH Name [score - level]"
if not risk_table.empty:
rt_lookup = risk_table.set_index("Ten KH")[["Diem rui ro","Muc rui ro"]].to_dict("index")
kh_sorted = sorted(
kh_in_scope,
key=lambda k: rt_lookup.get(k, {}).get("Diem rui ro", 0)
)
kh_display = []
for k in kh_sorted:
info = rt_lookup.get(k, {})
sc_v = info.get("Diem rui ro", 0)
lv = info.get("Muc rui ro", "?")
kh_display.append("{} [{}pt - {}]".format(k, sc_v, lv))
display_to_name = {d: n for d, n in zip(kh_display, kh_sorted)}
else:
kh_sorted = kh_in_scope
kh_display = kh_in_scope
display_to_name = {k: k for k in kh_in_scope}
selected_display = st.sidebar.selectbox(
"3. Ten Khach hang (sap xep theo diem rui ro tang dan)",
kh_display,
help="Khach hang duoc sap xep tu rui ro THAP nhat den CAO nhat"
)
kh = display_to_name.get(selected_display, kh_sorted[0] if kh_sorted else "")
# ── Level 4: Quy ──
quy_opts = sorted(df_after_kv["Quy"].dropna().unique().tolist())
quy_chon = st.sidebar.multiselect("4. Quy", quy_opts, default=quy_opts)
if not quy_chon:
quy_chon = quy_opts
# Apply final filter
df = df_all[
(df_all["Ten khach hang"].astype(str) == kh) &
(df_all["Quy"].isin(quy_chon))
].copy()
df_ban = df[df["Loai GD"] == "Xuat ban"].copy()
# ======================================================
# PAGE HEADER
# ======================================================
kh_info = risk_table[risk_table["Ten KH"] == kh].iloc[0] if not risk_table.empty and kh in ri
sc_kh lv_kh = int(kh_info["Diem rui ro"]) if kh_info is not None else 0
= kh_info["Muc rui ro"] if kh_info is not None else "?"
col_kh = risk_color(sc_kh)
ngay_min = df["Ngay chung tu"].min() if "Ngay chung tu" in df.columns else None
ngay_max = df["Ngay chung tu"].max() if "Ngay chung tu" in df.columns else None
date_str = "{} - {}".format(
ngay_min.strftime("%d/%m/%Y") if pd.notna(ngay_min) else "?",
ngay_max.strftime("%d/%m/%Y") if pd.notna(ngay_max) else "?"
)
nhom_disp = kh_info["Ten nhom KH"] if kh_info is not None else ""
kv_disp = kh_info["Khu vuc"] if kh_info is not None else ""
st.markdown(
'<h2 style="margin-bottom:4px;">Phan tich: {}</h2>'.format(kh),
unsafe_allow_html=True
)
st.markdown(
'<p style="color:#9aa0b0;margin-bottom:6px;">'
'{} | PKD: {} | KV: {} | {} dong'
' &nbsp;<span style="background:{};color:#fff;padding:2px 10px;border-radius:10px;font-we
'{}pt - {}</span></p>'.format(
date_str, nhom_disp or "?", kv_disp or "?",
len(df), col_kh, sc_kh, lv_kh
),
unsafe_allow_html=True
)
if df_ban.empty:
st.warning("Khong co du lieu xuat ban cho bo loc da chon.")
st.stop()
# ======================================================
# TABS
# ======================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
"San pham",
"Doanh thu",
"Loi nhuan",
"Giao hang",
"Tan suat",
"Rui ro & BCCN",
"Bang xep hang rui ro",
])
# ======================================================
# TAB 1 - SAN PHAM
# ======================================================
with tab1:
st.markdown('<div class="section-title">Co cau san pham theo nhom</div>', unsafe_allow_ht
df_nhom = (df_ban.groupby("Nhom SP")
.agg(So_lan=("Nhom SP","count"),
KL_tan=("Khoi luong", lambda x: round(x.sum()/1000,2)),
DT=("Thanh tien ban","sum"))
.reset_index().sort_values("DT", ascending=False))
df_nhom = df_nhom[df_nhom["DT"] > 0]
if not df_nhom.empty:
c1, c2 = st.columns(2)
with c1:
fig = px.bar(df_nhom, x="Nhom SP", y="DT", color="Nhom SP", text_auto=".3s",
title="DT theo nhom SP", labels={"DT":"DT (VND)","Nhom SP":""})
fig.update_layout(showlegend=False, height=360)
st.plotly_chart(fig, use_container_width=True)
with c2:
fig2 = px.pie(df_nhom, names="Nhom SP", values="So_lan",
title="Ty trong so lan mua", hole=0.45)
fig2.update_layout(height=360)
st.plotly_chart(fig2, use_container_width=True)
st.markdown('<div class="section-title">Top 15 san pham theo DT</div>', unsafe_allow_html
df_top = (df_ban.groupby("Ten hang")
.agg(So_lan=("Ten hang","count"),
KL_tan=("Khoi luong", lambda x: round(x.sum()/1000,2)),
SL=("So luong","sum"),
DT=("Thanh tien ban","sum"))
.reset_index().sort_values("DT", ascending=False).head(15))
df_top_s = df_top.copy()
df_top_s["DT"] = df_top_s["DT"].map("{:,.0f}".format)
df_top_s.columns = ["San pham","So lan","KL (tan)","SL","DT (VND)"]
st.dataframe(df_top_s, use_container_width=True, hide_index=True)
st.markdown('<div class="section-title">Nhan dinh muc dich su dung</div>', unsafe_allow_h
nhom_set = set(df_nhom["Nhom SP"].tolist()) if not df_nhom.empty else set()
notes = {
"Ong HDPE": "Ong HDPE (lon): Du an ha tang, cap thoat nuoc cong trinh lon.",
"Ong PVC nuoc": "Ong PVC nuoc: Xay dung dan dung, cong nghiep, nong nghiep.",
"Ong PVC bom cat": "Ong PVC bom cat: Thuy loi, nong nghiep, nuoi trong thuy san.",
"Ong PPR": "Ong PPR: He thong nuoc nong/lanh noi that, dan dung.",
"Loi PVC": "Loi PVC: KH co the la dai ly hoac nha SX thu cap.",
"Phu kien & Keo": "Phu kien & Keo: Tu thi cong hoac ban lai tron goi.",
}
shown = False
for k, v in notes.items():
if k in nhom_set:
shown = True
st.markdown('<div class="risk-low">{}</div>'.format(v), unsafe_allow_html=True)
if not shown:
st.info("Khong du du lieu de nhan dinh.")
# ======================================================
# TAB 2 - DOANH THU
# ======================================================
with tab2:
st.markdown('<div class="section-title">Bien dong DT, KL, SL theo thang</div>', unsafe_al
ct_col = "So chung tu" if "So chung tu" in df_ban.columns else "Thanh tien ban"
df_m = (df_ban.groupby("Thang")
.agg(DT=("Thanh tien ban","sum"),
KL=("Khoi luong", lambda x: round(x.sum()/1000,3)),
SL=("So luong","sum"),
So_CT=(ct_col,"nunique"))
.reset_index().sort_values("Thang"))
fig_t = make_subplots(rows=2, cols=1, shared_xaxes=True,
subplot_titles=["DT (VND) & KL (tan)", "SL & So chung tu"],
vertical_spacing=0.14)
fig_t.add_trace(go.Bar(x=df_m["Thang"], y=df_m["DT"], name="DT",
marker_color="#4e79d4", opacity=0.85), row=1, col=1)
fig_t.add_trace(go.Scatter(x=df_m["Thang"], y=df_m["KL"], name="KL (tan)",
mode="lines+markers", line=dict(color="#f0a500",width=2),
marker=dict(size=7)), row=1, col=1)
fig_t.add_trace(go.Bar(x=df_m["Thang"], y=df_m["SL"], name="SL",
marker_color="#26c281", opacity=0.85), row=2, col=1)
fig_t.add_trace(go.Scatter(x=df_m["Thang"], y=df_m["So_CT"], name="So CT",
mode="lines+markers", line=dict(color="#e74c3c",width=2),
marker=dict(size=7)), row=2, col=1)
fig_t.update_layout(height=520, legend=dict(orientation="h", y=-0.12))
st.plotly_chart(fig_t, use_container_width=True)
df_ms = df_m.copy()
df_ms["DT"] = df_ms["DT"].map("{:,.0f}".format)
df_ms.columns = ["Thang","DT (VND)","KL (tan)","SL","So CT"]
st.dataframe(df_ms, use_container_width=True, hide_index=True)
st.markdown('<div class="section-title">Tong hop theo Quy</div>', unsafe_allow_html=True)
df_q = (df_ban.groupby("Quy")
.agg(DT=("Thanh tien ban","sum"),
KL=("Khoi luong", lambda x: round(x.sum()/1000,2)),
LN=("Loi nhuan","sum"),
So_CT=(ct_col,"nunique"))
.reset_index())
df_q["Bien (%)"] = (df_q["LN"] / df_q["DT"].replace(0, float("nan")) * 100).round(1).fill
df_qs = df_q.copy()
df_qs["DT"] = df_qs["DT"].map("{:,.0f}".format)
df_qs["LN"] = df_qs["LN"].map("{:,.0f}".format)
df_qs.columns = ["Quy","DT (VND)","KL (tan)","LN (VND)","So CT","Bien LN (%)"]
st.dataframe(df_qs, use_container_width=True, hide_index=True)
# ======================================================
# TAB 3 - LOI NHUAN
# ======================================================
with tab3:
st.markdown('<div class="section-title">Bien dong loi nhuan & phat hien chinh sach</div>'
df_ln = (df_ban.groupby("Thang")
.agg(DT=("Thanh tien ban","sum"),
Von=("Thanh tien von","sum"),
LN=("Loi nhuan","sum"))
.reset_index().sort_values("Thang"))
df_ln["Bien"] = (df_ln["LN"] / df_ln["DT"].replace(0, float("nan")) * 100).round(2).filln
fig_ln = make_subplots(rows=2, cols=1, shared_xaxes=True,
subplot_titles=["DT / Von / LN (VND)", "Bien loi nhuan (%)"],
vertical_spacing=0.14)
fig_ln.add_trace(go.Bar(x=df_ln["Thang"], y=df_ln["DT"], name="DT", marker_color="#4e79d4
fig_ln.add_trace(go.Bar(x=df_ln["Thang"], y=df_ln["Von"], name="Von", marker_color="#e05c
fig_ln.add_trace(go.Scatter(x=df_ln["Thang"], y=df_ln["LN"], name="LN",
mode="lines+markers", line=dict(color="#26c281",width=2),
marker=dict(size=7)), row=1, col=1)
fig_ln.add_trace(go.Scatter(x=df_ln["Thang"], y=df_ln["Bien"], name="Bien LN",
mode="lines+markers+text",
text=["{:.1f}%".format(v) for v in df_ln["Bien"]],
textposition="top center",
line=dict(color="#f0a500",width=2),
marker=dict(size=7)), row=2, col=1)
fig_ln.update_layout(height=520, barmode="group")
st.plotly_chart(fig_ln, use_container_width=True)
if len(df_ln) >= 2:
mean_b = df_ln["Bien"].mean()
std_b = max(float(df_ln["Bien"].std()), 1.0)
anom = df_ln[df_ln["Bien"] < mean_b - std_b]
st.markdown('<div class="section-title">Thang nghi co chiet khau bat thuong</div>', u
if not anom.empty:
for _, r in anom.iterrows():
st.markdown(
'<div class="risk-medium">Thang <b>{}</b>: Bien LN = <b>{:.1f}%</b> (TB={
r["Thang"], r["Bien"], mean_b),
unsafe_allow_html=True
)
else:
st.markdown('<div class="risk-low">Khong phat hien thang bat thuong ve bien LN.</
df_tra = df[df["Loai GD"] == "Tra hang"]
if not df_tra.empty:
st.markdown('<div class="section-title">Don hang tra lai</div>', unsafe_allow_html=Tr
show_cols = [c for c in ["So chung tu","Ngay chung tu","Ten hang","Khoi luong","Thanh
df_tra_s = df_tra[show_cols].copy()
if "Thanh tien ban" in df_tra_s.columns:
df_tra_s["Thanh tien ban"] = df_tra_s["Thanh tien ban"].map("{:,.0f}".format)
st.dataframe(df_tra_s, use_container_width=True, hide_index=True)
st.error("Tong GT tra hang: {:,.0f} VND".format(abs(df_tra["Thanh tien ban"].sum())))
with st.expander("Chi tiet gia ban tung giao dich"):
show2 = [c for c in ["So chung tu","Ngay chung tu","Ten hang","Gia ban","Don gia quy
"Thanh tien ban","Loi nhuan","Ghi chu"] if c in df_ban.columns
st.dataframe(df_ban[show2].sort_values("Ngay chung tu"), use_container_width=True, hi
# ======================================================
# TAB 4 - GIAO HANG
# ======================================================
with tab4:
st.markdown('<div class="section-title">Hinh thuc & dia diem giao hang</div>', unsafe_all
c1, c2 = st.columns(2)
with c1:
if "Freight Terms" in df_ban.columns:
df_ft = df_ban["Freight Terms"].value_counts().reset_index()
df_ft.columns = ["Hinh thuc","So lan"]
fig_ft = px.pie(df_ft, names="Hinh thuc", values="So lan",
title="Dieu kien giao hang", hole=0.4)
st.plotly_chart(fig_ft, use_container_width=True)
else:
st.info("Khong co du lieu Freight Terms.")
with c2:
if "Shipping method" in df_ban.columns:
df_sm = df_ban["Shipping method"].value_counts().reset_index()
df_sm.columns = ["Phuong tien","So lan"]
fig_sm = px.pie(df_sm, names="Phuong tien", values="So lan",
title="Phuong tien van chuyen", hole=0.4)
st.plotly_chart(fig_sm, use_container_width=True)
else:
st.info("Khong co du lieu Shipping method.")
st.markdown('<div class="section-title">Dia diem giao hang</div>', unsafe_allow_html=True
if "Noi giao hang" in df_ban.columns:
df_noi = (df_ban.groupby("Noi giao hang")
.agg(So_lan=("Noi giao hang","count"),
KL=("Khoi luong", lambda x: round(x.sum()/1000,2)),
DT=("Thanh tien ban","sum"))
.reset_index().sort_values("DT", ascending=False))
df_noi["DT"] = df_noi["DT"].map("{:,.0f}".format)
df_noi.columns = ["Dia diem","So lan","KL (tan)","DT (VND)"]
st.dataframe(df_noi, use_container_width=True, hide_index=True)
else:
st.info("Khong co du lieu Noi giao hang.")
with st.expander("Danh sach xe & tai xe"):
xe_cols = [c for c in ["Bien so xe","Tai Xe","Ten DVVC","Shipping method",
"Ngay chung tu","Noi giao hang"] if c in df_ban.columns]
if xe_cols:
st.dataframe(df_ban[xe_cols].drop_duplicates().sort_values(xe_cols[0]),
use_container_width=True, hide_index=True)
else:
st.info("Khong co du lieu xe/tai xe.")
# ======================================================
# TAB 5 - TAN SUAT
# ======================================================
with tab5:
st.markdown('<div class="section-title">Heatmap tan suat: San pham x Thang</div>', unsafe
if "Ten hang" in df_ban.columns:
df_freq = df_ban.groupby(["Ten hang","Thang"]).size().reset_index(name="So lan")
df_piv = df_freq.pivot(index="Ten hang", columns="Thang", values="So lan").fillna(0)
top_n = df_piv.sum(axis=1).nlargest(min(20, len(df_piv))).index
if len(top_n) > 0:
fig_h = px.imshow(df_piv.loc[top_n],
labels=dict(x="Thang", y="San pham", color="So lan"),
title="Top SP mua nhieu nhat x Thang",
color_continuous_scale="Blues", aspect="auto")
fig_h.update_layout(height=max(380, len(top_n)*24))
st.plotly_chart(fig_h, use_container_width=True)
st.markdown('<div class="section-title">Chi tiet theo Quy</div>', unsafe_allow_html=T
for qv in sorted(df_ban["Quy"].dropna().unique()):
dq = df_ban[df_ban["Quy"] == qv]
months_str = ", ".join(sorted(dq["Thang"].dropna().unique()))
with st.expander("{} | {}".format(qv, months_str)):
ag = (dq.groupby(["Ten hang","Thang"])
.agg(So_lan=("Ten hang","count"),
KL=("Khoi luong", lambda x: round(x.sum()/1000,2)),
DT=("Thanh tien ban","sum"))
.reset_index().sort_values("DT", ascending=False))
ag["DT"] = ag["DT"].map("{:,.0f}".format)
ag.columns = ["San pham","Thang","So lan","KL (tan)","DT (VND)"]
st.dataframe(ag, use_container_width=True, hide_index=True)
else:
st.info("Khong co du lieu Ten hang.")
# ======================================================
# TAB 6 - RUI RO & BCCN
# ======================================================
with tab6:
st.markdown('<div class="section-title">BCCN - Phan tich thanh toan & cong no</div>', uns
gc_s = df["Ghi chu"].astype(str).str.upper() if "Ghi chu" in df.columns else pd.Series
df_po = df[gc_s.str.contains(r"PO|B[0-9]{3}|HOP DONG", regex=True, na=False)]
df_tra2 = df[df["Loai GD"] == "Tra hang"]
df_bs2 = df[df["Loai GD"] == "Xuat bo sung"]
ct_col2 = "So chung tu" if "So chung tu" in df.columns else "Thanh tien ban"
mc = st.columns(4)
mc[0].metric("Don PO/HD", df_po[ct_col2].nunique() if not df_po.empty else 0)
mc[1].metric("Phieu tra hang", df_tra2[ct_col2].nunique() if not df_tra2.empty else 0)
mc[2].metric("Xuat bo sung", df_bs2[ct_col2].nunique() if not df_bs2.empty else 0)
mc[3].metric("GT tra hang (VND)", "{:,.0f}".format(abs(df_tra2["Thanh tien ban"].sum()) i
st.markdown("""
<div class="info-box">
<b>File OM_RPT_055 khong co ngay thanh toan thuc te.</b><br>
Can bo sung: So cong no phai thu (AR Aging), Lich su thanh toan.<br>
Dau hieu: Ghi chu B-xxx/PO = don du an = TT cham NET30-90 |
Tra hang = tranh chap | Nhieu dia diem giao = cong no phan tan.
</div>""", unsafe_allow_html=True)
if not df_po.empty:
with st.expander("{} don co PO / ma du an".format(len(df_po))):
show_po = [c for c in ["So chung tu","Ngay chung tu","Ten hang","Thanh tien ban",
df_po_s = df_po[show_po].drop_duplicates().copy()
if "Thanh tien ban" in df_po_s.columns:
df_po_s["Thanh tien ban"] = df_po_s["Thanh tien ban"].map("{:,.0f}".format)
st.dataframe(df_po_s, use_container_width=True, hide_index=True)
st.markdown('<div class="section-title">Danh gia rui ro tong hop</div>', unsafe_allow_htm
risks = []
score = 0
tong_ban = df_ban["Thanh tien ban"].sum()
tong_tra = abs(df_tra2["Thanh tien ban"].sum()) if not df_tra2.empty else 0
tl_tra = (tong_tra / tong_ban * 100) if tong_ban > 0 else 0
if tl_tra > 10:
score += 30
risks.append(("high", elif tl_tra > 3:
score += 15
"Ty le hang tra: <b>{:.1f}%</b> ({:,.0f} VND) - rui ro cao".f
risks.append(("medium", "Ty le hang tra: <b>{:.1f}%</b> - can theo doi".format(tl_tra
else:
risks.append(("low", "Ty le tra hang thap: {:.1f}%".format(tl_tra)))
tong_ln = df_ban["Loi nhuan"].sum()
= (tong_ln / tong_ban * 100) if tong_ban > 0 else 0
bien if bien < 5:
score += 25
risks.append(("high", elif bien < 15:
"Bien LN rat thap: <b>{:.1f}%</b> - ban duoi gia hoac chiet k
score += 10
risks.append(("medium", "Bien LN o muc thap: <b>{:.1f}%</b>".format(bien)))
else:
risks.append(("low", "Bien LN binh thuong: {:.1f}%".format(bien)))
if not df_bs2.empty:
score += 15
risks.append(("medium", "Co <b>{}</b> dong xuat bo sung/thay the".format(len(df_bs2))
else:
risks.append(("low", "Khong co don xuat bo sung."))
if len(df_ban) > 4:
q75 = df_ban["Thanh tien ban"].quantile(0.75)
q25 = df_ban["Thanh tien ban"].quantile(0.25)
iqr = q75 - q25
if iqr > 0:
outs = df_ban[df_ban["Thanh tien ban"] > q75 + 3*iqr]
if not outs.empty:
score += 10
risks.append(("medium", "Co <b>{}</b> don hang gia tri rat lon - kiem soat ha
else:
risks.append(("low", "Khong co don hang gia tri bat thuong."))
if "Noi giao hang" in df_ban.columns:
n_noi = df_ban["Noi giao hang"].nunique()
if n_noi >= 5:
score += 10
risks.append(("medium", "Giao hang toi <b>{}</b> dia diem - cong no phan tan".for
else:
risks.append(("low", "So dia diem: {} (binh thuong)".format(n_noi)))
n_thang_mua = df_ban["Thang"].nunique()
delta_days = (df_ban["Ngay chung tu"].max() - df_ban["Ngay chung tu"].min()).days
n_range = max(delta_days // 30, 1)
if n_thang_mua / n_range < 0.5:
score += 10
risks.append(("medium", "Mua chi <b>{}/{}</b> thang - khong deu, phu thuoc du an".for
else:
risks.append(("low", "Mua deu: {}/{} thang co GD".format(n_thang_mua, n_range)))
sc_col2 = risk_color(score)
if score >= 50: sc_lbl2 = "RUI RO CAO"
elif score >= 25: sc_lbl2 = "RUI RO TRUNG BINH"
else: sc_lbl2 = "RUI RO THAP"
pct_b = min(score, 100)
st.markdown(
'<div style="background:#1a2035;border-radius:10px;padding:20px;text-align:center;mar
'<div style="font-size:32px;font-weight:900;color:{};">{}</div>'
'<div style="font-size:16px;color:#9aa0b0;margin-top:6px;">'
'Diem rui ro: <b style="color:{}">{}/100</b></div>'
'</div>'.format(sc_col2, sc_lbl2, sc_col2, score),
unsafe_allow_html=True
)
st.markdown(
'<div style="background:#21262d;border-radius:6px;height:8px;margin:-8px 0 18px 0;ove
'<div style="background:{};width:{}%;height:100%;border-radius:6px;"></div></div>'.fo
unsafe_allow_html=True
)
for lvl, msg in risks:
st.markdown('<div class="risk-{}">{}</div>'.format(lvl, msg), unsafe_allow_html=True)
# ======================================================
# TAB 7 - BANG XEP HANG RUI RO
# ======================================================
with tab7:
st.markdown('<div class="section-title">Bang xep hang rui ro tat ca khach hang (thap den
if not risk_table.empty:
# Filter by current Phong KD and Khu vuc selection
rt_filtered = risk_table.copy()
if nhom_chon:
rt_filtered = rt_filtered[rt_filtered["Ten nhom KH"].isin(nhom_chon)]
if kv_chon:
rt_filtered = rt_filtered[rt_filtered["Khu vuc"].isin(kv_chon)]
rt_display = rt_filtered.sort_values("Diem rui ro", ascending=True).copy()
rt_display.index = range(1, len(rt_display)+1)
# Add color column
def make_badge(row):
sc2 = row["Diem rui ro"]
lv2 = row["Muc rui ro"]
if sc2 >= 50: return '<span class="risk-badge-cao">{} - {}pt</span>'.format(lv2
elif sc2 >= 25: return '<span class="risk-badge-tb">{} - {}pt</span>'.format(lv2,
else: return '<span class="risk-badge-thap">{} - {}pt</span>'.format(lv
rt_display["Muc rui ro HTML"] = rt_display.apply(make_badge, axis=1)
# Show bar chart
fig_rank = go.Figure()
colors_bar = [risk_color(sc2) for sc2 in rt_display["Diem rui ro"]]
fig_rank.add_trace(go.Bar(
y=rt_display["Ten KH"],
x=rt_display["Diem rui ro"],
orientation="h",
marker=dict(color=colors_bar),
text=rt_display["Diem rui ro"].astype(str),
textposition="outside",
textfont=dict(color="#c9d1d9", size=11)
))
fig_rank.update_layout(
paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
font=dict(color="#c9d1d9", size=11),
title="Diem rui ro KH (thap den cao)",
height=max(400, len(rt_display)*32),
margin=dict(l=10, r=10, t=45, b=10),
xaxis=dict(gridcolor="#21262d", range=[0, 105])
)
fig_rank.update_yaxes(gridcolor="#21262d", tickfont=dict(size=10))
st.plotly_chart(fig_rank, use_container_width=True)
# Summary by Phong KD
if "Ten nhom KH" in rt_display.columns and rt_display["Ten nhom KH"].replace("","nan"
st.markdown('<div class="section-title">Tong hop rui ro theo Phong KD</div>', uns
df_grp_nhom = (rt_display.groupby("Ten nhom KH")
.agg(So_KH=("Ten KH","count"),
Diem_TB=("Diem rui ro","mean"),
Diem_Max=("Diem rui ro","max"))
.reset_index().sort_values("Diem_Max", ascending=False))
df_grp_nhom["Diem_TB"] = df_grp_nhom["Diem_TB"].round(1)
df_grp_nhom.columns = ["Phong KD","So KH","Diem TB","Diem Max"]
st.dataframe(df_grp_nhom, use_container_width=True, hide_index=True)
# Summary by Khu vuc
if "Khu vuc" in rt_display.columns and rt_display["Khu vuc"].replace("","nan").nuniqu
st.markdown('<div class="section-title">Tong hop rui ro theo Khu vuc</div>', unsa
df_grp_kv = (rt_display.groupby("Khu vuc")
.agg(So_KH=("Ten KH","count"),
Diem_TB=("Diem rui ro","mean"),
Diem_Max=("Diem rui ro","max"))
.reset_index().sort_values("Diem_Max", ascending=False))
df_grp_kv["Diem_TB"] = df_grp_kv["Diem_TB"].round(1)
df_grp_kv.columns = ["Khu vuc","So KH","Diem TB","Diem Max"]
st.dataframe(df_grp_kv, use_container_width=True, hide_index=True)
# Full table (without HTML col)
st.markdown('<div class="section-title">Chi tiet toan bo khach hang</div>', unsafe_al
rt_show = rt_display[["Ten KH","Ten nhom KH","Khu vuc","Diem rui ro","Muc rui ro"]].c
st.dataframe(rt_show, use_container_width=True)
else:
st.info("Chua co du lieu rui ro.")