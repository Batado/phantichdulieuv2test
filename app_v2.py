import io
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Ignore warnings
warnings.filterwarnings("ignore")

# Streamlit Configuration
st.set_page_config(
    page_title="Phân Tích KH - Hoa Sen",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# CSS styling for Streamlit page
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

# Pre-defined Constants
NHOM_SP = [
    ("Ống HDPE", "HDPE"),
    ("Ống PVC nước", r"PVC.*(?:nước|nong dài|nong tròn|thoát|cấp)"),
    ("Ống PVC bơm cát", r"PVC.*(?:cát|bơm cát)"),
    ("Ống PPR", "PPR"),
    ("Lõi PVC", r"(?:Lõi|loi|lori)"),
    ("Phụ kiện & Keo", r"(?:Nối|Co |Tê |Van |Keo |Măng|Bịt|Y PVC|Y PPR|Giảm|Cút)"),
]

COLOR_SEQ = ["#388bfd", "#56d364", "#e3b341", "#ffa198", "#79c0ff", "#d2a8ff", "#ffb800", "#3fb950", "#bc8cff", "#ff7b72"]

# Plotly Default Settings
PLOTLY_BASE = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font=dict(family="Be Vietnam Pro, sans-serif", color="#c9d1d9", size=12),
    title_font=dict(size=14, color="#f0f6fc"),
    legend=dict(bgcolor="#161b22", bordercolor="#21262d", borderwidth=1, font=dict(size=11, color="#c9d1d9")),
    margin=dict(l=10, r=10, t=45, b=10),
    colorway=COLOR_SEQ,
)

# Utility Functions
def pl(fig, **kw):
    """Apply default Plotly settings."""
    d = {**PLOTLY_BASE, **kw}
    fig.update_layout(**d)
    fig.update_xaxes(gridcolor="#21262d", linecolor="#30363d")
    fig.update_yaxes(gridcolor="#21262d", linecolor="#30363d")
    return fig

def fmt(v):
    """Format numeric values to readable format."""
    try:
        f = float(v)
        if abs(f) >= 1e9:
            return "{:.2f} tỷ".format(f / 1e9)
        elif abs(f) >= 1e6:
            return "{:.1f} triệu".format(f / 1e6)
        else:
            return "{:,.0f}".format(f)
    except Exception:
        return str(v)

def fmt_full(v):
    """Full numeric formatting."""
    try:
        return "{:,.0f}".format(float(v))
    except Exception:
        return str(v)

# Sidebar File Uploader
st.sidebar.markdown("## Upload File Dữ Liệu")
uploaded_files = st.sidebar.file_uploader("Chọn File Excel", type=["xlsx"], accept_multiple_files=True)

if not uploaded_files:
    st.markdown('<div class="page-title">Phân Tích Dữ Liệu - Hoa Sen</div>', unsafe_allow_html=True)
    st.info("Vui lòng tải lên file Excel để bắt đầu.")
    st.stop()

# Load data with caching for better efficiency
@st.cache_data(show_spinner="Đang xử lý dữ liệu...")
def load_files(files):
    """Load all Excel files into a single DataFrame."""
    all_data = []
    for file in files:
        try:
            data = pd.read_excel(io.BytesIO(file.read()), engine="openpyxl")
            data["_file"] = file.name
            all_data.append(data)
        except Exception as e:
            st.warning(f"Lỗi khi tải dữ liệu từ {file.name}: {e}")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

data = load_files(uploaded_files)

# Validate loaded data
if data.empty:
    st.error("Không có dữ liệu hợp lệ. Vui lòng kiểm tra file uploaded.")
    st.stop()

# Main Logic (Overview KPI)
st.markdown('<div class="page-title">📊 Tổng Quan</div>', unsafe_allow_html=True)
total_sales = data["DoanhThu"].sum()  # Example: replace this with actual column name
total_profit = data["LoiNhuan"].sum()  # Example
st.write(f"Tổng doanh thu: {fmt(total_sales)}")
st.write(f"Tổng lợi nhuận: {fmt(total_profit)}")