import io
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Phan tich KH - Hoa Sen",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

CSS = """
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
"""
st.markdown(CSS, unsafe_allow_html=True)

NHOM_SP = [
    ("Ong HDPE",        "HDPE"),
    ("Ong PVC nuoc",    r"PVC.*(?:nuoc|nong dai|nong tron|thoat|cap)"),
    ("Ong PVC bom cat", r"PVC.*(?:cat|bom cat)"),
    ("Ong PPR",         "PPR"),
    ("Loi PVC",         r"(?:Loi|loi|lori)"),
    ("Phu kien & Keo",  r"(?:Noi|Co |Te |Van |Keo |Mang|Bit|Y PVC|Y PPR|Giam|Cut)"),
]

COLOR_SEQ = ["#388bfd", "#56d364", "#e3b341", "#ffa198", "#79c0ff", "#d2a8ff", "#ffb800", "#3fb950", "#bc8cff", "#ff7b72"]

PLOTLY_BASE = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font=dict(family="Be Vietnam Pro, sans-serif", color="#c9d1d9", size=12),
    title_font=dict(size=14, color="#f0f6fc"),
    legend=dict(bgcolor="#161b22", bordercolor="#21262d", borderwidth=1, font=dict(size=11, color="#c9d1d9")),
    margin=dict(l=10, r=10, t=45, b=10),
    colorway=COLOR_SEQ,
)

def pl(fig, **kw):
    d = {**PLOTLY_BASE, **kw}
    fig.update_layout(**d)
    fig.update_xaxes(gridcolor="#21262d", linecolor="#30363d")
    fig.update_yaxes(gridcolor="#21262d", linecolor="#303