import io
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Ignore warnings
warnings.filterwarnings("ignore")

# Configure the Streamlit app page
st.set_page_config(
    page_title="Phân Tích Dữ Liệu Excel",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

# Streamlit style with CSS
st.markdown("""
    <style>
        body {font-family: "Be Vietnam Pro", sans-serif;}
        section[data-testid="stSidebar"] {
            background-color: #0d1117;
            color: #c9d1d9;
        }
    </style>
""", unsafe_allow_html=True)

# Function to load the Excel file
@st.cache_data(show_spinner="Đang xử lý dữ liệu...")
def load_excel_file(uploaded_file):
    try:
        return pd.read_excel(io.BytesIO(uploaded_file.read()), engine="openpyxl")
    except Exception as e:
        st.error(f"Lỗi khi tải tệp Excel: {e}")
        return pd.DataFrame()

# Sidebar for file upload
st.sidebar.title("Tải Dữ Liệu Excel")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel của bạn", type=["xlsx"])

# Execute the application when a file is uploaded
if uploaded_file:
    # Load Excel data
    data = load_excel_file(uploaded_file)

    # Verify if data is valid
    if data.empty:
        st.error("❌ File Excel không có dữ liệu hoặc không hợp lệ.")
    else:
        st.title("📊 Phân Tích Dữ Liệu")
        st.write("### 🚀 Xem nhanh 5 dòng đầu tiên trong dữ liệu:")
        st.dataframe(data.head())  # Display the first 5 rows

        # Check and handle specific columns
        if "DoanhThu" in data.columns and "LoiNhuan" in data.columns:
            # Safely convert columns to numeric and handle missing values
            data["DoanhThu"] = pd.to_numeric(data["DoanhThu"], errors="coerce").fillna(0)
            data["LoiNhuan"] = pd.to_numeric(data["LoiNhuan"], errors="coerce").fillna(0)

            # Calculate key metrics
            total_sales = data["DoanhThu"].sum()
            total_profit = data["LoiNhuan"].sum()
            num_rows = data.shape[0]  # Total number of rows
            num_columns = data.shape[1]  # Total number of columns

            # Display KPIs
            st.write("### ⭐ Các Khóa Chỉ Số Quan Trọng:")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Tổng Dòng", f"{num_rows:,}")
            col2.metric("Tổng Cột", f"{num_columns:,}")
            col3.metric("Doanh thu (Tổng)", f"{total_sales:,.0f} VND")
            col4.metric("Lợi nhuận (Tổng)", f"{total_profit:,.0f} VND")

            # Visualize Data
            st.write("### 📈 Biểu Đồ Phân Tích:")
            scatter_fig = px.scatter(
                data,
                x="DoanhThu",
                y="LoiNhuan",
                title="Quan hệ giữa Doanh thu và Lợi nhuận",
                labels={"DoanhThu": "Doanh Thu (VND)", "LoiNhuan": "Lợi Nhuận (VND)"},
                color="DoanhThu",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(scatter_fig, use_container_width=True)
        else:
            st.error("❌ File Excel của bạn thiếu cột 'DoanhThu' hoặc 'LoiNhuan'. Vui lòng kiểm tra lại.")
else:
    st.title("📊 Phân Tích Dữ Liệu Excel")
    st.info("👐 Vui lòng tải một file Excel định dạng `.xlsx` để bắt đầu phân tích.")