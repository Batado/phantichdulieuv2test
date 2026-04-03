import io
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Phân tích KH – Hoa Sen", layout="wide", page_icon="📊")

# CSS Styling
st.markdown("""
<style>
.risk-high { background:#4a1010; border-left:4px solid #e74c3c; padding:10px 14px; border-radius:6px; margin:6px 0; color:#fff; }
.risk-medium { background:#3d2e10; border-left:4px solid #f39c12; padding:10px 14px; border-radius:6px; margin:6px 0; color:#fff; }
.section-title { font-size:18px; font-weight:700; color:#e0e0e0; margin-top:20px; border-bottom:1px solid #2e3350; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  CẤU HÌNH & CHUẨN HÓA CỘT
# ══════════════════════════════════════════════════════════════
COL_ALIASES = {
    "Tên khách hàng":,
    "Phòng kinh doanh":,
    "Ngày chứng từ":,
    "Số chứng từ":,
    "Lợi nhuận": ["Lợi nhuận", "Profit"],
    "Thành tiền bán":,
    "Khu vực":,
    "Nơi giao hàng": ["Nơi giao hàng", "Địa chỉ giao hàng"],
    "Khối lượng": ["Khối lượng", "KL"],
    "Đơn giá vận chuyển": ["Đơn giá vận chuyển", "Chi phí vận chuyển"]
}

def normalize_columns(df):
    rename_map = {}
    cols_lower = {c.strip().lower(): c for c in df.columns}
    for standard, aliases in COL_ALIASES.items():
        for alias in aliases:
            if alias.strip().lower() in cols_lower:
                rename_map[cols_lower[alias.strip().lower()]] = standard
                break
    return df.rename(columns=rename_map)

@st.cache_data
def load_data(uploaded_files):
    frames =
    for uf in uploaded_files:
        fb = uf.read()
        # Header báo cáo Hoa Sen thường nằm sau các dòng metadata (khoảng dòng 13)
        df = pd.read_excel(io.BytesIO(fb), header=12, engine="openpyxl")
        df.columns = [str(c).strip().replace("\n", " ") for c in df.columns]
        df = normalize_columns(df)
        df.dropna(subset=, inplace=True)
        frames.append(df)
    
    full_df = pd.concat(frames, ignore_index=True)
    full_df["Ngày chứng từ"] = pd.to_datetime(full_df["Ngày chứng từ"], dayfirst=True, errors='coerce')
    full_df = full_df[full_df["Ngày chứng từ"].notna()]
    full_df = full_df["Ngày chứng từ"].dt.to_period("M").astype(str)
    
    # Chuyển đổi số
    num_cols =
    for c in num_cols:
        if c in full_df.columns:
            full_df[c] = pd.to_numeric(full_df[c], errors="coerce").fillna(0)
    return full_df

# ══════════════════════════════════════════════════════════════
#  GIAO DIỆN & BỘ LỌC
# ══════════════════════════════════════════════════════════════
st.sidebar.markdown("## 📂 Dữ liệu đầu vào")
uploaded_files = st.sidebar.file_uploader("Upload báo cáo OM_RPT_055", type=["xlsx"], accept_multiple_files=True)

if not uploaded_files:
    st.info("👈 Vui lòng tải file Excel lên để bắt đầu.")
    st.stop()

df_all = load_data(uploaded_files)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 Bộ lọc phân tích")

# Bộ lọc Phòng kinh doanh (Mới)
pkd_list = + sorted(df_all["Phòng kinh doanh"].dropna().unique().tolist())
pkd_selected = st.sidebar.selectbox("🏢 Phòng kinh doanh", pkd_list)

df_filtered = df_all.copy()
if pkd_selected!= "Tất cả":
    df_filtered = df_filtered[df_filtered["Phòng kinh doanh"] == pkd_selected]

# Bộ lọc Khách hàng (Cập nhật theo PKD)
kh_list = sorted(df_filtered.dropna().unique().tolist())
kh = st.sidebar.selectbox("👤 Khách hàng", kh_list)

# FIX LỖI: Cấu trúc lọc DataFrame đúng (Line 120 sửa lỗi Syntax)
df = df_filtered == kh].copy()

# ══════════════════════════════════════════════════════════════
#  HIỂN THỊ KẾT QUẢ
# ══════════════════════════════════════════════════════════════
t1, t2 = st.tabs()

with t1:
    st.markdown(f"### Phân tích khách hàng: {kh}")
    c1, c2 = st.columns(2)
    c1.metric("Doanh thu (VNĐ)", f"{df.sum():,.0f}")
    c2.metric("Lợi nhuận (VNĐ)", f"{df['Lợi nhuận'].sum():,.0f}")
    
    fig = px.bar(df.groupby("Tháng").sum().reset_index(), x="Tháng", y="Thành tiền bán", title="Doanh thu theo tháng")
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.markdown('<div class="section-title">🔍 Phỏng đoán dấu hiệu bất thường</div>', unsafe_allow_html=True)
    
    # 1. Phát hiện Lợi nhuận âm
    ln_am = df[df["Lợi nhuận"] < 0]
    if not ln_am.empty:
        st.markdown(f'<div class="risk-high">⚠️ Phát hiện {len(ln_am)} dòng hàng bị <b>lỗ (Lợi nhuận < 0)</b>.</div>', unsafe_allow_html=True)
        st.dataframe(ln_am], hide_index=True)
    
    # 2. Phát hiện sai lệch vùng miền (Dự án xuyên vùng)
    # Ví dụ: PKD Miền Nam nhưng giao hàng Miền Bắc/Trung
    mismatch = df[(df["Khu vực"] == "Miền Bắc") & (df["Nơi giao hàng"].str.contains("Đồng Nai|Long Thành", na=False))]
    if not mismatch.empty:
        st.markdown(f'<div class="risk-medium">⚠️ <b>Sai lệch Khu vực & Logistics:</b> Phát hiện khách hàng thuộc Miền Bắc nhưng giao hàng tại miền Nam.</div>', unsafe_allow_html=True)
        st.dataframe(mismatch], hide_index=True)