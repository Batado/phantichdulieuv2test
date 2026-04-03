import io
import streamlit as st
import pandas as pd
import plotly.express as px

# Cấu hình ứng dụng với Streamlit
st.set_page_config(page_title="Phân tích KH – Hoa Sen", layout="wide", page_icon="📊")

# Sidebar: Tải file
st.sidebar.markdown("## 📂 Tải file dữ liệu")
uploaded_file = st.sidebar.file_uploader(
    "Chọn file Excel báo cáo bán hàng (Định dạng: .xlsx)", type=["xlsx"]
)

# Nếu không có file, hiển thị thông báo
if not uploaded_file:
    st.markdown("### 👈 Vui lòng tải file dữ liệu để bắt đầu phân tích.")
    st.info("Ứng dụng hỗ trợ phân tích dữ liệu khách hàng của tập tin Excel.")
    st.stop()

# Đọc file Excel
@st.cache_data(show_spinner="Đang xử lý dữ liệu...")
def load_data(file):
    """Hàm xử lý và làm sạch dữ liệu từ file Excel."""
    try:
        # Đọc dữ liệu từ file Excel
        data = pd.read_excel(file, engine="openpyxl")
        data.columns = data.columns.str.strip()  # Bỏ khoảng trắng trong tên cột
        return data
    except Exception as e:
        st.error(f"Lỗi khi đọc file Excel: {e}")
        return pd.DataFrame()

df_all = load_data(uploaded_file)

# Thông báo nếu dữ liệu rỗng
if df_all.empty:
    st.error("❌ File Excel không hợp lệ hoặc không có dữ liệu.")
    st.stop()

# Chuẩn hóa và kiểm tra các cột cần thiết
required_columns = ["Tên khách hàng", "Khu vực", "Tên nhóm KH", "Thành tiền bán", "Lợi nhuận", "Ngày chứng từ"]
missing_columns = [col for col in required_columns if col not in df_all.columns]
if missing_columns:
    st.error(f"Các cột sau bị thiếu trong dữ liệu: {', '.join(missing_columns)}")
    st.stop()

# Xử lý dữ liệu - chuẩn hóa ngày và số liệu
df_all["Ngày chứng từ"] = pd.to_datetime(df_all["Ngày chứng từ"], errors="coerce")
df_all["Thành tiền bán"] = pd.to_numeric(df_all["Thành tiền bán"], errors="coerce").fillna(0)
df_all["Lợi nhuận"] = pd.to_numeric(df_all["Lợi nhuận"], errors="coerce").fillna(0)
df_all["Tháng"] = df_all["Ngày chứng từ"].dt.to_period("M")  # Thêm thông tin tháng
df_all["Quý"] = df_all["Ngày chứng từ"].dt.to_period("Q")    # Thêm thông tin quý

# Sidebar: Bộ lọc nâng