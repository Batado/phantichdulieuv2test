import io
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# Cấu hình Streamlit
st.set_page_config(
    page_title="Phân Tích Dữ Liệu Bán Hàng",
    layout="wide",
    page_icon="📊",
)

# Hàm tải tệp Excel
@st.cache_data(show_spinner="Đang tải dữ liệu...")
def load_excel(file):
    try:
        return pd.read_excel(io.BytesIO(file.read()), engine="openpyxl")
    except Exception as e:
        st.error(f"Lỗi khi đọc file Excel: {e}")
        return pd.DataFrame()

# Tải file Excel qua sidebar
st.sidebar.title("🗂 Tải File Dữ Liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel (*.xlsx)", type=["xlsx"])

# Xử lý file tải lên
if uploaded_file:
    # Đọc file
    data = load_excel(uploaded_file)

    # Kiểm tra file rỗng
    if data.empty:
        st.error("❌ File Excel không có dữ liệu hoặc định dạng không đúng.")
        st.stop()

    # Hiển thị dữ liệu
    st.title("📊 Phân Tích Dữ Liệu Bán Hàng")
    st.write("### 🔍 Dữ Liệu Gốc")
    st.dataframe(data.head(10))  # Hiển thị trước 10 dòng đầu

    # Các bộ lọc cơ bản
    st.sidebar.header("🔍 Bộ Lọc Dữ Liệu")
    unique_customers = data["Tên khách hàng"].dropna().unique()
    unique_regions = data["Khu vực"].dropna().unique()
    unique_groups = data["Mã Nhóm KH"].dropna().unique()

    selected_customer = st.sidebar.selectbox("Chọn Khách Hàng", options=["Tất cả"] + list(unique_customers))
    selected_region = st.sidebar.multiselect("Chọn Khu Vực", options=unique_regions, default=unique_regions)
    selected_group = st.sidebar.multiselect("Chọn Mã Nhóm KH", options=unique_groups, default=unique_groups)

    # Áp dụng bộ lọc
    data_filtered = data[
        (data["Khu vực"].isin(selected_region)) &
       