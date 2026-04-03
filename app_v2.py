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
        # Đọc file Excel
        data = pd.read_excel(io.BytesIO(file.read()), engine="openpyxl")
        return data
    except Exception as e:
        st.error(f"Lỗi khi đọc file Excel: {e}")
        return pd.DataFrame()

# Sidebar: Tải file Excel
st.sidebar.title("🗂 Tải File Dữ Liệu")
uploaded_file = st.sidebar.file_uploader("Chọn file Excel (*.xlsx)", type=["xlsx"])

# Kiểm tra file được tải lên
if uploaded_file:
    # Đọc dữ liệu
    data = load_excel(uploaded_file)

    # Kiểm tra dữ liệu hợp lệ không
    if data.empty:
        st.error("❌ File Excel không hợp lệ hoặc không có dữ liệu.")
        st.stop()

    # -> Thêm bước: In ra danh sách các cột trong file để kiểm tra tên
    st.write("### 📋 Tên các cột trong dữ liệu:")
    st.write(data.columns.tolist())

    # Kiểm tra sự tồn tại của cột "Ngày chứng từ"
    if "Ngày chứng từ" in data.columns:
        # Làm sạch dữ liệu "Ngày chứng từ"
        data["Ngày chứng từ"] = pd.to_datetime(data["Ngày chứng từ"], errors="coerce")
        data["Tháng"] = data["Ngày chứng từ"].dt.to_period("M")  # Tạo cột để phân tích theo tháng
    else:
        st.error("❌ Cột 'Ngày chứng từ' không tồn tại. Vui lòng kiểm tra lại file Excel.")
        st.stop()

    # Làm sạch các cột khác
    if "Thành tiền bán" in data.columns:
        data["Thành tiền bán"] = pd.to_numeric(data["Thành tiền bán"], errors="coerce").fillna(0)
    else:
        st.error("❌ Cột 'Thành tiền bán' không tồn tại. Vui lòng kiểm tra lại file.")
        st.stop()

    if "Lợi nhuận" in data.columns:
        data["Lợi nhuận"] = pd.to_numeric(data["Lợi nhuận"], errors="coerce").fillna(0)
    else:
        st.warning("⚠️ Dữ liệu 'Lợi nhuận' không tồn tại. Một số phân tích lợi nhuận sẽ không có.")

    # Hiển thị dữ liệu sau khi làm sạch
    st.title("📊 Phân Tích Dữ Liệu Bán Hàng")
    st.write("### Dữ Liệu Gốc (Sau Khi Làm Sạch)")
    st.dataframe(data.head(10))  # Hiển thị 10 dòng đầu tiên

    # Tổng Quan Dữ Liệu
    st.write("### 🌟 Tổng Quan Dữ Liệu")
    total_revenue = data["Thành tiền bán"].sum()
    total_profit = data["Lợi nhuận"].sum()
    total_orders