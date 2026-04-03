import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Phân tích KH – Hoa Sen", layout="wide", page_icon="📊")

# CSS Styling
st.markdown("""
<style>
.risk-high { background:#4a1010; border-left:4px solid #e74c3c; padding:10px 14px; border-radius:6px; margin:6px 0; color:#fff; }
.risk-medium { background:#3d2e10; border-left:4px solid #f39c12; padding:10px 14px; border-radius:6px; margin:6px 0; color:#fff; }
.risk-low { background:#0f3020; border-left:4px solid #26c281; padding:10px 14px; border-radius:6px; margin:6px 0; color:#fff; }
.section-title { font-size:17px; font-weight:700; color:#e0e0e0; margin:20px 0 10px 0; padding-bottom:6px; border-bottom:1px solid #2e3350; }
.info-box { background:#1a2035; border-radius:8px; padding:14px; margin:8px 0; color:#ccc; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  CẤU HÌNH CỘT DỮ LIỆU
# ══════════════════════════════════════════════════════════════
COL_ALIASES = {
    "Tên khách hàng":,
    "Phòng kinh doanh":,
    "Ngày chứng từ":,
    "Số chứng từ":,
    "Tên hàng":,
    "Khối lượng": ["Khối lượng", "KL", "weight"],
    "Thành tiền bán":,
    "Thành tiền vốn":,
    "Lợi nhuận": ["Lợi nhuận", "Profit", "profit"],
    "Giá bán": ["Giá bán", "Đơn giá", "unit_price"],
    "Nơi giao hàng": ["Nơi giao hàng", "Địa chỉ giao hàng", "delivery_address"],
    "Khu vực":,
    "Ghi chú": ["Ghi chú", "Note", "notes"],
    "Đơn giá vận chuyển": ["Đơn giá vận chuyển", "Chi phí vận chuyển", "freight_cost"],
}

def normalize_columns(df):
    rename_map = {}
    cols_lower = {c.strip().lower(): c for c in df.columns}
    for standard, aliases in COL_ALIASES.items():
        for alias in aliases:
            if alias.strip().lower() in cols_lower:
                rename_map[cols_lower[alias.strip().lower()]] = standard
                break
    df.rename(columns=rename_map, inplace=True)
    return df

def find_header_row(fb):
    try:
        # Đọc 40 dòng đầu để tìm header dựa trên mật độ từ khóa
        df_raw = pd.read_excel(io.BytesIO(fb), header=None, engine="openpyxl", nrows=40)
        kws = ["số chứng từ", "ngày chứng từ", "khách hàng", "tên hàng", "lợi nhuận"]
        for i in range(df_raw.shape):
            row_text = " ".join([str(v) for v in df_raw.iloc[i].tolist()]).lower()
            if sum(1 for kw in kws if kw in row_text) >= 2:
                return i
    except: return 0
    return 0

# ══════════════════════════════════════════════════════════════
#  XỬ LÝ DỮ LIỆU
# ══════════════════════════════════════════════════════════════
@st.cache_data
def load_all(uploaded_files):
    frames =
    for uf in uploaded_files:
        fb = uf.read()
        hr = find_header_row(fb)
        df = pd.read_excel(io.BytesIO(fb), header=hr, engine="openpyxl")
        df.columns = [str(c).strip().replace("\n", " ") for c in df.columns]
        df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
        df = normalize_columns(df)
        df.dropna(subset=, inplace=True)
        frames.append(df)
    
    if not frames: return pd.DataFrame()
    full_df = pd.concat(frames, ignore_index=True)
    full_df["Ngày chứng từ"] = pd.to_datetime(full_df["Ngày chứng từ"], dayfirst=True, errors="coerce")
    full_df = full_df[full_df["Ngày chứng từ"].notna()].copy()
    full_df = full_df["Ngày chứng từ"].dt.to_period("M").astype(str)
    
    # Ép kiểu số
    num_cols =
    for c in num_cols:
        if c in full_df.columns:
            full_df[c] = pd.to_numeric(full_df[c], errors="coerce").fillna(0)
            
    return full_df

# ══════════════════════════════════════════════════════════════
#  GIAO DIỆN & BỘ LỌC
# ══════════════════════════════════════════════════════════════
st.sidebar.markdown("## 📂 Upload dữ liệu")
uploaded_files = st.sidebar.file_uploader("Upload file Excel (OM_RPT_055)", type=["xlsx"], accept_multiple_files=True)

if not uploaded_files:
    st.info("Vui lòng upload file để bắt đầu.")
    st.stop()

df_all = load_all(uploaded_files)

# BỘ LỌC PHÒNG KINH DOANH (MỚI)
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 Bộ lọc")

pkd_list = + sorted(df_all["Phòng kinh doanh"].dropna().unique().tolist())
pkd_selected = st.sidebar.selectbox("🏢 Phòng kinh doanh", pkd_list)

df_filtered = df_all.copy()
if pkd_selected!= "Tất cả":
    df_filtered = df_filtered[df_filtered["Phòng kinh doanh"] == pkd_selected]

kh_list = sorted(df_filtered.dropna().unique().tolist())
kh = st.sidebar.selectbox("👤 Khách hàng", kh_list)

df = df_filtered == kh].copy()
df_ban = df >= 0].copy()

# Tabs hiển thị
t1, t2, t3 = st.tabs()

with t1:
    st.markdown(f"### Phân tích: {kh}")
    st.metric("Tổng doanh thu", f"{df_ban.sum():,.0f} VNĐ")
    fig = px.line(df_ban.groupby("Tháng").sum().reset_index(), x="Tháng", y="Thành tiền bán", title="Biến động doanh thu")
    st.plotly_chart(fig, use_container_width=True)

with t3:
    st.markdown('<div class="section-title">🔍 Phát hiện bất thường từ dữ liệu</div>', unsafe_allow_html=True)
    
    # 1. Bất thường Lợi nhuận âm
    ln_am = df[df["Lợi nhuận"] < 0]
    if not ln_am.empty:
        st.markdown(f'<div class="risk-high">⚠️ Phát hiện {len(ln_am)} dòng hàng có <b>lợi nhuận âm</b>.</div>', unsafe_allow_html=True)
        st.dataframe(ln_am], hide_index=True)
        st.info("Dấu hiệu: Giá vốn cao hơn giá bán. Thường gặp ở các mặt hàng phụ kiện (PPR) hoặc do sai sót hệ số quy đổi đơn vị tính.")
    
    # 2. Bất thường Khu vực & Địa điểm giao hàng
    # Ví dụ: Khu vực Miền Bắc nhưng giao tại Đồng Nai (Phía Nam)
    mismatch = df[(df["Khu vực"] == "Miền Bắc") & (df["Nơi giao hàng"].str.contains("Đồng Nai|Hồ Chí Minh|Vũng Tàu", na=False))]
    if not mismatch.empty:
        st.markdown(f'<div class="risk-medium">⚠️ Phát hiện {len(mismatch)} chứng từ có <b>sai lệch địa giới hành chính</b>.</div>', unsafe_allow_html=True)
        st.write("Khu vực quản lý: Miền Bắc | Địa điểm giao thực tế: Phía Nam.")
        st.dataframe(mismatch], hide_index=True)
        st.info("Phỏng đoán: Khách hàng dự án có trụ sở tại Miền Bắc nhưng thi công công trình tại Miền Nam.")

    # 3. Bất thường Chi phí vận chuyển (Z-Score)
    if len(df_ban) > 2:
        mean_v = df_ban["Đơn giá vận chuyển"].mean()
        std_v = df_ban["Đơn giá vận chuyển"].std()
        if std_v > 0:
            outlier_v = df_ban[df_ban["Đơn giá vận chuyển"] > mean_v + 2*std_v]
            if not outlier_v.empty:
                st.markdown(f'<div class="risk-medium">⚠️ Đơn giá vận chuyển cao bất thường tại {len(outlier_v)} dòng.</div>', unsafe_allow_html=True)
                st.write(f"Đơn giá trung bình: {mean_v:,.0f} | Các dòng vượt ngưỡng: > {(mean_v + 2*std_v):,.0f}")