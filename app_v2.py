import io
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px


# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Phân Tích Dữ Liệu Bán Hàng",
    layout="wide",
    page_icon="📊"
)

# Hàm đọc dữ liệu Excel và lưu cache
@st.cache_data(show_spinner="Đang tải và xử lý dữ liệu...")
def load_excel(file):
    try:
        # Đọc file Excel với pandas
        data = pd.read_excel(io.BytesIO(file.read()), engine="openpyxl")
        return data
    except Exception as e:
        st.error(f"Lỗi khi đọc file Excel: {e}")
        return pd.DataFrame()


# Sidebar: Tải file Excel
st.sidebar.title("🗂 Tải File Dữ Liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel (*.xlsx)", type=["xlsx"])

# Kiểm tra file Excel được tải lên
if uploaded_file:
    # Đọc dữ liệu
    data = load_excel(uploaded_file)

    # Kiểm tra dữ liệu hợp lệ không
    if data.empty:
        st.error("❌ File Excel không hợp lệ hoặc không có dữ liệu.")
        st.stop()

    # Hiển thị dữ liệu ban đầu
    st.title("📊 Phân Tích Dữ Liệu Bán Hàng")
    st.write("### Dữ Liệu Gốc")
    st.dataframe(data.head(10))  # Hiển thị 10 dòng đầu tiên

    # Làm sạch dữ liệu
    data["Ngày chứng từ"] = pd.to_datetime(data["Ngày chứng từ"], errors="coerce")
    data["Tháng"] = data["Ngày chứng từ"].dt.to_period("M")  # Tạo cột để phân tích theo tháng
    data["Thành tiền bán"] = pd.to_numeric(data["Thành tiền bán"], errors="coerce").fillna(0)
    data["Lợi nhuận"] = pd.to_numeric(data["Lợi nhuận"], errors="coerce").fillna(0)

    # Sidebar: Bộ lọc thông tin
    st.sidebar.header("📌 Bộ Lọc Dữ Liệu")
    unique_customers = data["Tên khách hàng"].dropna().unique()
    unique_regions = data["Khu vực"].dropna().unique()

    # Bộ lọc Khách Hàng và Khu Vực
    selected_customer = st.sidebar.selectbox("Chọn Khách Hàng:", ["Tất cả"] + list(unique_customers))
    selected_region = st.sidebar.multiselect("Chọn Khu Vực:", unique_regions, default=unique_regions)

    # Áp dụng bộ lọc
    filtered_data = data[
        (data["Khu vực"].isin(selected_region))
    ]
    if selected_customer != "Tất cả":
        filtered_data = filtered_data[filtered_data["Tên khách hàng"] == selected_customer]

    # Tổng Quan Số Liệu
    st.write("### 🌟 Tổng Quan Dữ Liệu")
    total_revenue = filtered_data["Thành tiền bán"].sum()
    total_profit = filtered_data["Lợi nhuận"].sum()
    total_orders = filtered_data.shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Tổng Doanh Thu", f"{total_revenue:,.0f} VND")
    col2.metric("✅ Tổng Lợi Nhuận", f"{total_profit:,.0f} VND")
    col3.metric("✅ Số Đơn Hàng", f"{total_orders:,}")

    # Phân tích Doanh Thu Theo Tháng
    st.write("### 📅 Doanh Thu và Lợi Nhuận Theo Thời Gian")
    revenue_by_month = filtered_data.groupby("Tháng")[["Thành tiền bán", "Lợi nhuận"]].sum().reset_index()

    fig_revenue = px.bar(
        revenue_by_month,
        x="Tháng",
        y="Thành tiền bán",
        text="Thành tiền bán",
        title="Doanh Thu Theo Tháng",
        labels={"Tháng": "Thời Gian", "Thành tiền bán": "Doanh Thu (VND)"},
        color_discrete_sequence=["#636EFA"]
    )
    fig_revenue.update_traces(texttemplate="%{y:,.2f}", textposition="outside")
    fig_revenue.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")
    st.plotly_chart(fig_revenue, use_container_width=True)

    # Lợi Nhuận Theo Tháng (Biểu Đồ Đường)
    fig_profit = px.line(
        revenue_by_month,
        x="Tháng",
        y="Lợi nhuận",
        title="Lợi Nhuận Theo Tháng",
        labels={"Tháng": "Thời Gian", "Lợi nhuận": "Lợi Nhuận (VND)"},
        markers=True,
        line_shape="spline",
    )
    fig_profit.update_traces(line=dict(color="#EF553B", width=3))
    st.plotly_chart(fig_profit, use_container_width=True)

    # Phân Tích Sản Phẩm (Top 5 Sản Phẩm Theo Doanh Thu)
    st.write("### 🏆 Top 5 Sản Phẩm Theo Doanh Thu")
    top_products = (
        filtered_data.groupby("Tên hàng")[["Thành tiền bán", "Số lượng"]]
        .sum()
        .sort_values("Thành tiền bán", ascending=False)
        .head(5)
        .reset_index()
    )
    fig_top_products = px.pie(
        top_products,
        names="Tên hàng",
        values="Thành tiền bán",
        title="Tỷ Lệ Top 5 Sản Phẩm Theo Doanh Thu",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_top_products, use_container_width=True)

    # Phân tích giao hàng, khu vực
    shipment_data = filtered_data["Nơi giao hàng"].value_counts().reset_index()
    shipment_data.columns = ["Địa Điểm Giao", "Số Lượng Giao"]
    st.write("### 🚚 Phân Tích Giao Hàng Theo Địa Điểm")
    st.dataframe(shipment_data)
    
else:
    # Hiển thị thông báo khi chưa tải file
    st.title("📊 Phân Tích Dữ Liệu Bán Hàng")
    st.info("Hãy tải file Excel để bắt đầu phân tích.")