import io
import streamlit as st
import pandas as pd
import plotly.express as px

# Cấu hình ứng dụng với Streamlit
st.set_page_config(page_title="Phân Tích KH – Hoa Sen", layout="wide", page_icon="📊")

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

# Chuẩn hóa tên cột
COL_ALIASES = {
    "tên khách hàng": ["tên khách hàng", "tên kh", "khách hàng", "ten kh", "customer name"],
    "khu vực": ["khu vực", "khu vuc", "region"],
    "tên nhóm kh": ["tên nhóm kh", "mã nhóm kh", "nhom khach hang", "customer group"],
    "thành tiền bán": ["thành tiền bán", "doanh thu", "revenue", "amount"],
    "lợi nhuận": ["lợi nhuận", "profit", "ln"],
    "ngày chứng từ": ["ngày chứng từ", "ngày ct", "ngay", "date"]
}

def normalize_columns(df):
    """Chuẩn hóa cột dựa trên alias đã định nghĩa."""
    rename_map = {}
    df.columns = [str(c).strip().lower() for c in df.columns]  # Bỏ khoảng trắng, viết thường
    for std_name, aliases in COL_ALIASES.items():
        for alias in aliases:
            if alias in df.columns:
                rename_map[alias] = std_name
                break
    df.rename(columns=rename_map, inplace=True)
    return df

# Đọc file Excel
@st.cache_data(show_spinner="Đang xử lý dữ liệu tệp Excel...")
def load_data(file):
    """Hàm đọc và chuẩn hóa dữ liệu từ file Excel."""
    try:
        # Đọc dữ liệu từ file Excel
        data = pd.read_excel(file, engine="openpyxl")
        data.dropna(how="all", axis=1, inplace=True)  # Bỏ các cột toàn NaN
        data = normalize_columns(data)  # Chuẩn hóa tên cột
        return data
    except Exception as e:
        st.error(f"Lỗi khi đọc file Excel: {str(e)}")
        return pd.DataFrame()

df_all = load_data(uploaded_file)

# Nếu không có dữ liệu, báo lỗi
if df_all.empty:
    st.error("❌ File Excel không hợp lệ hoặc không có dữ liệu.")
    st.stop()

# Kiểm tra sự tồn tại của các cột cần thiết
required_columns = ["tên khách hàng", "khu vực", "tên nhóm kh", "thành tiền bán", "lợi nhuận", "ngày chứng từ"]
missing_columns = [col for col in required_columns if col not in df_all.columns]
if missing_columns:
    st.error(f"Các cột sau bị thiếu trong dữ liệu: {', '.join(missing_columns)}")
    st.stop()

# Chuẩn hóa dữ liệu
df_all["ngày chứng từ"] = pd.to_datetime(df_all["ngày chứng từ"], errors="coerce")
df_all["thành tiền bán"] = pd.to_numeric(df_all["thành tiền bán"], errors="coerce").fillna(0)
df_all["lợi nhuận"] = pd.to_numeric(df_all["lợi nhuận"], errors="coerce").fillna(0)
df_all["tháng"] = df_all["ngày chứng