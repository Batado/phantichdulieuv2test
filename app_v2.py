import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Cấu hình Streamlit
st.set_page_config(page_title="Phân tích KH - Hoa Sen", layout="wide", page_icon="📊")

# Các hàm và tiện ích đã tồn tại như cũ
# ...

# Load file Excel (tương tự mã code trước đó)

# --- Bổ sung thêm bộ lọc theo Tên nhóm KH, Khu vực và Điểm rủi ro ---
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 Bộ lọc nâng cao")

# 1. Lọc theo Tên nhóm khách hàng
if "Tên nhóm KH" in df_all.columns:
    group_list = sorted(df_all["Tên nhóm KH"].dropna().unique())
    selected_group = st.sidebar.multiselect("✅ Tên nhóm KH", group_list, default=group_list)
    df_all = df_all[df_all["Tên nhóm KH"].isin(selected_group)]

# 2. Lọc theo Khu vực
if "Khu vực" in df_all.columns:
    region_list = sorted(df_all["Khu vực"].dropna().unique())
    selected_region = st.sidebar.multiselect("📍 Khu vực", region_list, default=region_list)
    df_all = df_all[df_all["Khu vực"].isin(selected_region)]

# 3. Lọc theo Điểm rủi ro từ cao đến thấp
sort_risk = st.sidebar.checkbox("🔽 Sắp xếp theo điểm rủi ro (Cao → Thấp)", value=False)

# Áp dụng sắp xếp theo điểm rủi ro nếu cần
if sort_risk and "Điểm rủi ro" in df_all.columns:
    df_all = df_all.sort_values(by="Điểm rủi ro", ascending=False)

# Tiếp tục hiển thị dữ liệu đã lọc
df = df_all[
    (df_all["Tên khách hàng"].astype(str) == kh) &
    (df_all["Quý"].isin(quy_chon))
].copy()