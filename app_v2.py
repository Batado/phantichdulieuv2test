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

# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Phan tich KH - Hoa Sen",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

st.markdown("""
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
""", unsafe_allow_html=True)
