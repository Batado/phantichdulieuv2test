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

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Phan tich KH - Hoa Sen", layout="wide", page_icon="📊")

st.markdown("""
<style>
.section-title { font-size:17px; font-weight:700; color:#e0e0e0; margin:20px 0 10px 0;
                 padding-bottom:6px; border-bottom:1px solid #2e3350; }
.risk-high   { background:#4a1010; color:#fff; padding:10px; border-radius:6px; }
.risk-medium { background:#3d2e10; color:#fff; padding:10px; border-radius:6px; }
.risk-low    { background:#0f3020; color:#fff; padding:10px; border-radius:6px; }
</style>
""", unsafe_allow_html=True)

# =========================
# UTILITIES
# =========================
def strip_acc(s):
    s = unicodedata.normalize("NFD", str(s))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().strip()

def safe_num(df, col):
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").fillna(0)
    return pd.Series(0.0, index=df.index)

def compute_risk(df_kh):
    df_b = df_kh[df_kh["Loai GD"] == "Xuat ban"]
    df_t = df_kh[df_kh["Loai GD"] == "Tra hang"]
    df_s = df_kh[df_kh["Loai GD"] == "Xuat bo sung"]

    if df_b.empty:
        return 0

    tong_ban = df_b["Thanh tien ban"].sum()
    tong_tra = abs(df_t["Thanh tien ban"].sum()) if not df_t.empty else 0
    tong_ln  = df_b["Loi nhuan"].sum()

    tl_tra = (tong_tra / tong_ban * 100) if tong_ban > 0 else 0
    bien   = (tong_ln  / tong_ban * 100) if tong_ban > 0 else 0

    sc = 0
    if tl_tra > 10: sc += 30
    elif tl_tra > 3: sc += 15
    if bien < 5: sc += 25
    elif bien < 15: sc += 10
    if not df_s.empty: sc += 15

    return sc

def risk_label(sc):
    if sc >= 50: return "Cao"
    if sc >= 25: return "Trung binh"
    return "Thap"

def risk_color(sc):
    if sc >= 50: return "#e74c3c"
    if sc >= 25: return "#f39c12"
    return "#26c281"

# =========================
# SIDEBAR UPLOAD
# =========================
st.sidebar.header("Upload du lieu")
uploaded_files = st.sidebar.file_uploader("Chon file Excel", type=["xlsx"], accept_multiple_files=True)

if not uploaded_files:
    st.info("Vui long upload file Excel OM_RPT_055 de bat dau.")
    st.stop()

frames = []
for f in uploaded_files:
    df = pd.read_excel(f)
    frames.append(df)

df_all = pd.concat(frames, ignore_index=True)

# =========================
# TIEN XU LY
# =========================
if "Ngay chung tu" in df_all.columns:
    df_all["Ngay chung tu"] = pd.to_datetime(df_all["Ngay chung tu"], dayfirst=True, errors="coerce")
    df_all = df_all[df_all["Ngay chung tu"].notna()].copy()
    df_all["Thang"] = df_all["Ngay chung tu"].dt.to_period("M").astype(str)
    df_all["Quy"]   = df_all["Ngay chung tu"].dt.to_period("Q").astype(str)

for col in ["Thanh tien ban", "Thanh tien von", "Loi nhuan"]:
    df_all[col] = safe_num(df_all, col)

# =========================
# RISK TABLE
# =========================
risk_rows = []
for kh, grp in df_all.groupby("Ten khach hang"):
    sc = compute_risk(grp)
    risk_rows.append({
        "Ten KH": kh,
        "Diem rui ro": sc,
        "Muc rui ro": risk_label(sc)
    })
risk_table = pd.DataFrame(risk_rows)

# =========================
# PAGE HEADER
# =========================
st.header("Phan tich khach hang")
st.dataframe(risk_table, use_container_width=True)

# =========================
# TABS
# =========================
tab1, tab2 = st.tabs(["Doanh thu", "Loi nhuan"])

with tab1:
    st.markdown('<div class="section-title">Doanh thu theo thang</div>', unsafe_allow_html=True)
    df_m = df_all.groupby("Thang").agg(DT=("Thanh tien ban","sum")).reset_index()
    fig = px.bar(df_m, x="Thang", y="DT", title="Doanh thu theo thang")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown('<div class="section-title">Loi nhuan theo thang</div>', unsafe_allow_html=True)
    df_ln = df_all.groupby("Thang").agg(LN=("Loi nhuan","sum")).reset_index()
    fig2 = px.line(df_ln, x="Thang", y="LN", title="Loi nhuan theo thang")
    st.plotly_chart(fig2, use_container_width=True)
