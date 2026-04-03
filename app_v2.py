import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Streamlit Cấu hình trang
st.set_page_config(page_title="Phân tích KH - Hoa Sen", layout="wide", page_icon="📊")

st.sidebar.markdown("## 📂 Upload dữ liệu")
uploaded_files = st.sidebar.file_uploader(
    "Upload file Excel báo cáo bán hàng",
    type=["xlsx"], accept_multiple_files=True
)

# Kiểm tra nếu chưa có file nào được tải lên
if not uploaded_files:
    st.markdown("## 👈 Upload file Excel để bắt đầu phân tích")
    st.info("Hỗ trợ định dạng báo cáo OM_RPT_055 (Hoa Sen). Header tự động nhận diện.")
    st.stop()


# Load dữ liệu từ file đã tải
@st.cache_data(show_spinner="Đang xử lý dữ liệu…")
def load_all(file_data):
    """Load tất cả các file Excel đã tải."""
    frames = []
    errors = []

    for name, fb in file_data:
        try:
            # Đọc file Excel
            df = pd.read_excel(io.BytesIO(fb), engine="openpyxl")

            # Chuẩn hóa và làm sạch tên cột
            df.columns = [str(c).strip().replace("\n", " ") for c in df.columns]
            df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
            df.dropna(how="all", inplace=True)

            df["Nguồn file"] = name  # Để gắn tên file làm tham chiếu
            frames.append(df)

        except Exception as e:
            errors.append(f"`{name}`: {e}")

    if errors:
        for err in errors:
            st.warning(f"⚠️ Lỗi đọc file: {err}")

    # Trả về kết quả hợp nhất của các file Excel
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# Đọc file tải lên
file_data = [(uf.name, uf.read()) for uf in uploaded_files]
df_all = load_all(file_data)

# Kiểm tra 'df_all' có dữ liệu hay không trước khi tiếp tục
if df_all.empty:
    st.error("Không có dữ liệu hợp lệ. Vui lòng kiểm tra file và thử lại.")
    st.stop()

# ---- Kiểm tra cột "Tên nhóm KH" tồn tại trước khi sử dụng ----
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 Bộ lọc nâng cao")

# Lọc theo Tên nhóm khách hàng
if "Tên nhóm KH" in df_all.columns:
    group_list = sorted(df_all["Tên nhóm KH"].dropna().unique())
    selected_group = st.sidebar.multiselect("✅ Tên nhóm KH", group_list, default=group_list)
    df_all = df_all[df_all["Tên nhóm KH"].isin(selected_group)]
else:
    st.warning("⚠️ Cột 'Tên nhóm KH' không tồn tại trong dữ liệu.")

# Lọc theo Khu vực
if "Khu vực" in df_all.columns:
    region_list = sorted(df_all["Khu vực"].dropna().unique())
    selected_region = st.sidebar.multiselect("📍 Khu vực", region_list, default=region_list)
    df_all = df_all[df_all["Khu vực"].isin(selected_region)]
else:
    st.warning("⚠️ Cột 'Khu vực' không tồn tại trong dữ liệu