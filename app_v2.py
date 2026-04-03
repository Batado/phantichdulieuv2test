import io
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# Cấu hình ứng dụng với Streamlit
st.set_page_config(
    page_title="Phân Tích Dữ Liệu Excel",
    layout="wide",
    page_icon="📊",
)

# Hàm để đọc file được tải lên
@st.cache_data(show_spinner="Đang tải file...")
def load_excel(file):
    try:
        return pd.read_excel(io.BytesIO(file.read()), engine="openpyxl")
    except Exception as e:
        st.error(f"Lỗi khi tải file: {e}")
        return pd.DataFrame()

# Sidebar: Nơi để tải file
st.sidebar.title("🗂 Tải File Dữ Liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel (*.xlsx)", type=["xlsx"])

# Xử lý dữ liệu nếu người dùng tải file lên
if uploaded_file:
    # Đọc dữ liệu từ file Excel
    data = load_excel(uploaded_file)

    # Kiểm tra dữ liệu rỗng
    if data.empty:
        st.error("❌ File Excel không chứa dữ liệu hợp lệ. Vui lòng kiểm tra lại.")
        st.stop()

    # Hiển thị dữ liệu dòng đầu
    st.title("📊 Phân Tích Dữ Liệu")
    st.write("### Dữ Liệu Gốc:")
    st.dataframe(data.head(10))  # Hiển thị 10 dòng đầu tiên của dữ liệu

    # Sidebar: Bộ lọc dữ liệu
    st.sidebar.header("🔵 Bộ Lọc Dữ Liệu")
    unique_customers = data["Tên khách hàng"].unique()
    unique_groups = data["Mã nhóm KH"].unique()
    unique_regions = data["Khu vực"].unique()

    selected_customer = st.sidebar.selectbox("Chọn Khách Hàng:", ["Tất cả"] + list(unique_customers))
    selected_group = st.sidebar.multiselect("Chọn Mã Nhóm KH:", unique_groups, default=unique_groups)
    selected_region = st.sidebar.multiselect("Chọn Khu Vực:", unique_regions, default=unique_regions)

    # Lọc dữ liệu dựa trên bộ lọc
    filtered_data = data[
        (data["Khu vực"].isin(selected_region)) &
        (data["Mã nhóm KH"].isin(selected_group))
    ]
    if selected_customer != "Tất cả":
        filtered_data = filtered_data[filtered_data["Tên khách hàng"] == selected_customer]

    # Thói quen mua hàng theo sản phẩm
    st.header("👤 Thói Quen Mua Hàng - Phân Tích Theo Tên Hàng")
    product_data = filtered_data.groupby("Tên hàng")[["Thành tiền bán", "Số lượng", "Khối lượng"]].sum().reset_index()
    st.write("### Tổng Quan theo Sản Phẩm:")
    st.dataframe(product_data)

    # Biểu đồ Doanh Thu theo Tên Hàng
    st.write("### Biểu Đồ Doanh Thu Theo Tên Hàng")
    fig_product_revenue = px.bar(product_data, x="Tên hàng", y="Thành tiền bán", title="Doanh Thu Theo Sản Phẩm",
                                 labels={"Thành tiền bán": "Doanh Thu (VND)", "Tên hàng": "Tên Sản Phẩm"})
    st.plotly_chart(fig_product_revenue, use_container_width=True)

    # Doanh Thu và Lợi Nhuận theo thời gian
    st.header("📅 Doanh Thu và Lợi Nhuận Theo Thời Gian")
    filtered_data["Ngày chứng từ"] = pd.to_datetime(filtered_data["Ngày chứng từ"])
    filtered_data["Tháng"] = filtered_data["Ngày chứng từ"].dt.to_period("M")
    
    # Doanh thu theo tháng
    monthly_revenue = filtered_data.groupby("Tháng")[["Thành tiền bán", "Lợi nhuận"]].sum().reset_index()
    fig_revenue = px.bar(monthly_revenue, x="Tháng", y="Thành tiền bán", text="Lợi nhuận",
                         title="Doanh Thu và Lợi Nhuận Theo Tháng", labels={"Tháng": "Tháng", "Thành tiền bán": "Doanh Thu"})
    st.plotly_chart(fig_revenue, use_container_width=True)