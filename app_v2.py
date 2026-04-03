import io
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Phân tích KH – Hoa Sen", layout="wide", page_icon="📊")

# CSS Styling để hiển thị cảnh báo rủi ro chuyên nghiệp
st.markdown("""
<style>
.risk-high { background:#4a1010; border-left:4px solid #e74c3c; padding:10px 14px; border-radius:6px; margin:6px 0; color:#fff; }
.risk-medium { background:#3d2e10; border-left:4px solid #f39c12; padding:10px 14px; border-radius:6px; margin:6px 0; color:#fff; }
.section-title { font-size:18px; font-weight:700; color:#e0e0e0; margin-top:20px; border-bottom:1px solid #2e3350; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  CHẨN HÓA CỘT DỮ LIỆU
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
    "Tên hàng":,
    "Giá vốn": ["Giá vốn", "Cost Price"],
    "Giá bán": ["Giá bán", "Unit Price"]
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

def find_header_row(file_bytes):
    """Tìm dòng header thật sự (dòng chứa 'Số chứng từ')"""
    try:
        df_raw = pd.read_excel(io.BytesIO(file_bytes), header=None, engine="openpyxl", nrows=30)
        for i in range(df_raw.shape):
            row_vals = [str(v).lower() for v in df_raw.iloc[i].tolist()]
            if "số chứng từ" in row_vals or "ngày chứng từ" in row_vals:
                return i
    except: return 0
    return 0

@st.cache_data
def load_data(uploaded_files):
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
    full_df["Ngày chứng từ"] = pd.to_datetime(full_df["Ngày chứng từ"], dayfirst=True, errors='coerce')
    full_df = full_df[full_df["Ngày chứng từ"].notna()].copy()
    full_df = full_df["Ngày chứng từ"].dt.to_period("M").astype(str)
    
    # Ép kiểu số cho các cột tài chính
    for c in:
        if c in full_df.columns:
            full_df[c] = pd.to_numeric(full_df[c], errors="coerce").fillna(0)
    return full_df

# ══════════════════════════════════════════════════════════════
#  BỘ LỌC SIDEBAR
# ══════════════════════════════════════════════════════════════
st.sidebar.markdown("## 📂 Dữ liệu đầu vào")
uploaded_files = st.sidebar.file_uploader("Upload báo cáo OM_RPT_055", type=["xlsx"], accept_multiple_files=True)

if not uploaded_files:
    st.info("👈 Vui lòng tải file Excel lên để bắt đầu.")
    st.stop()

df_all = load_data(uploaded_files)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 Bộ lọc phân tích")

# 1. Bộ lọc Phòng kinh doanh (Mới)
pkd_list = + sorted(df_all["Phòng kinh doanh"].dropna().unique().tolist())
pkd_selected = st.sidebar.selectbox("🏢 Phòng kinh doanh", pkd_list)

df_pkd = df_all.copy()
if pkd_selected!= "Tất cả":
    df_pkd = df_pkd[df_pkd["Phòng kinh doanh"] == pkd_selected]

# 2. Bộ lọc Khách hàng (Đã fix lỗi Syntax)
kh_list = sorted(df_pkd.dropna().unique().tolist())
kh = st.sidebar.selectbox("👤 Khách hàng", kh_list)

# FIX: Cấu trúc lọc đúng df_filtered[df_filtered["Cột"] == giá_trị]
df_filtered = df_pkd == kh].copy()

# ══════════════════════════════════════════════════════════════
#  HIỂN THỊ KẾT QUẢ
# ══════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs()

with tab1:
    st.markdown(f"### Phân tích khách hàng: {kh}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Doanh thu (VNĐ)", f"{df_filtered.sum():,.0f}")
    c2.metric("Lợi nhuận (VNĐ)", f"{df_filtered['Lợi nhuận'].sum():,.0f}")
    
    # Line chart doanh thu
    dt_thang = df_filtered.groupby("Tháng").sum().reset_index()
    st.plotly_chart(px.line(dt_thang, x="Tháng", y="Thành tiền bán", title="Xu hướng Doanh thu"), use_container_width=True)

with tab2:
    st.markdown('<div class="section-title">🔍 Phỏng đoán các dấu hiệu bất thường</div>', unsafe_allow_html=True)
    
    # 1. Phát hiện Lợi nhuận âm (Dữ liệu thực tế PPR hay bị lỗi này)
    ln_am = df_filtered[df_filtered["Lợi nhuận"] < 0]
    if not ln_am.empty:
        st.markdown('<div class="risk-high">⚠️ <b>Cảnh báo:</b> Phát hiện các chứng từ bán lỗ (Giá vốn > Giá bán)</div>', unsafe_allow_html=True)
        st.dataframe(ln_am], hide_index=True)
    
    # 2. Phát hiện mâu thuẫn Khu vực & Nơi giao hàng
    # Phỏng đoán: Miền Bắc nhưng giao hàng ở Miền Nam (Đồng Nai/HCM)
    mismatch = df_filtered[
        (df_filtered["Khu vực"] == "Miền Bắc") & 
        (df_filtered["Nơi giao hàng"].str.contains("Đồng Nai|Long Thành|Hồ Chí Minh", na=False))
    ]
    if not mismatch.empty:
        st.markdown('<div class="risk-medium">📍 <b>Dấu hiệu:</b> Sai lệch vùng miền quản lý và địa điểm giao hàng thực tế.</div>', unsafe_allow_html=True)
        st.write("Khách hàng thuộc khu vực Miền Bắc nhưng đang thi công dự án tại Miền Nam.")
        st.dataframe(mismatch].drop_duplicates(), hide_index=True)

    # 3. Phỏng đoán rủi ro công nợ dự án
    po_check = df_filtered.astype(str).str.contains("PO|B-", na=False)]
    if not po_check.empty:
        st.info(f"💡 Hệ thống phát hiện {len(po_check)} chứng từ có ký hiệu dự án (PO). Cần đối soát biên bản giải quyết khiếu nại để tránh đọng vốn.")