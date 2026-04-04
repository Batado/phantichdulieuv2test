import io
import warnings
warnings.filterwarnings('ignore')
import unicodedata
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# ============================================================
st.set_page_config(
page_title='Phan tich KH - Hoa Sen',
layout='wide',
page_icon=None,
initial_sidebar_state='expanded'
)
st.markdown('''
<style>
.risk-high{background:#4a1010;border-left:4px solid #e74c3c;padding:10px 14px;border-radius:6
.risk-medium{background:#3d2e10;border-left:4px solid #f39c12;padding:10px 14px;border-radius
.risk-low{background:#0f3020;border-left:4px solid #26c281;padding:10px 14px;border-radius:6p
.section-title{font-size:16px;font-weight:700;color:#e0e0e0;margin:20px 0 10px 0;padding-bott
.info-box{background:#1a2035;border-radius:8px;padding:14px;margin:8px 0;color:#ccc;}
</style>
''', unsafe_allow_html=True)
# ============================================================
# UTILITIES
# ============================================================
def strip_acc(s):
s = unicodedata.normalize('NFD', str(s))
return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower().strip()
# Column alias map: stripped_alias -> standard_name
_RAW_ALIASES = [
('ten_khach_hang', ['Ten khach hang','Ten KH','Khach hang','customer_name']),
('ngay_chung_tu', ['Ngay chung tu','Ngay CT','date']),
('so_chung_tu', ['So chung tu','So CT','voucher_no']),
('ten_hang', ['Ten hang','Ten ma hang','Ten SP','product_name']),
('ma_hang', ['Ma hang','Ma SP','product_code']),
('khoi_luong', ['Khoi luong','KL','weight']),
('so_luong', ['So luong','SL','qty','quantity']),
('thanh_tien_ban', ['Thanh tien ban','Doanh thu','revenue','amount']),
('thanh_tien_von', ['Thanh tien von','Gia von hang ban','cost']),
('loi_nhuan', ['Loi nhuan','Profit','profit']),
('gia_ban', ['Gia ban','Don gia','unit_price']),
('gia_von', ['Gia von','cost_price']),
('noi_giao_hang', ['Noi giao hang','Dia chi giao hang','delivery_address']),
('freight_terms', ['Freight Terms','Dieu kien giao hang','freight']),
('shipping_method',['Shipping method','Phuong tien','shipping']),
('bien_so_xe', ['So xe','Bien so xe','plate_no']),
('tai_xe', ['Tai Xe','Tai xe','Driver','driver']),
('ten_dvvc', ['Ten DVVC','Don vi van chuyen','carrier']),
('ghi_chu', ['Ghi chu','Note','notes']),
('khu_vuc', ['Khu vuc','Region','region']),
('ten_nhom_kh', ['Ten nhom KH','Nhom KH','sales_group_name']),
('ma_nhom_kh', ['Ma nhom KH','ma_nhom_kh']),
('ma_nhom_hang', ['Ma nhom hang','Nhom hang','product_group']),
('don_gia_vc', ['Don gia van chuyen','freight_cost']),
('don_gia_qd', ['Don gia quy doi','converted_price']),
]
# Map from stripped-alias -> canonical column name (first alias in list)
ALIAS_TO_STD = {}
for _std, _aliases in _RAW_ALIASES:
for _a in _aliases:
ALIAS_TO_STD[strip_acc(_a)] = _aliases[0] # map to first alias as canonical
def normalize_columns(df):
rename = {}
for col in df.columns:
sc = strip_acc(col)
if sc in ALIAS_TO_STD:
canonical = ALIAS_TO_STD[sc]
if col != canonical and canonical not in df.columns:
rename[col] = canonical
df.rename(columns=rename, inplace=True)
return df
def safe_num(df, col):
if col in df.columns:
return pd.to_numeric(df[col], errors='coerce').fillna(0)
return pd.Series(0.0, index=df.index)
def find_header_row(file_bytes):
try:
df_raw = pd.read_excel(io.BytesIO(file_bytes), header=None, engine='openpyxl', except Exception:
return 0
kws = ['so chung tu','ngay chung tu','ten khach hang',
'ten hang','thanh tien ban','loi nhuan','ten nhom kh','khu vuc']
for i in range(df_raw.shape[0]):
row_vals = [str(v).strip() for v in df_raw.iloc[i].tolist()
if str(v).strip() not in ('','nan','none','None')]
if len(row_vals) < 5:
continue
row_text = strip_acc(' '.join(row_vals))
hits = sum(1 for k in kws if k in row_text)
if hits >= 3:
return i
nrows=
return 0
# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data(show_spinner='Dang xu ly du lieu...')
def load_all(file_data):
frames = []
for name, fb in file_data:
try:
hr = find_header_row(fb)
df = pd.read_excel(io.BytesIO(fb), header=hr, engine='openpyxl')
df.columns = [str(c).strip().replace('\n', ' ').replace('\r', '') for c in df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
df.dropna(how='all', inplace=True)
normalize_columns(df)
df['_file'] = name
frames.append(df)
except Exception as e:
st.warning('Loi doc file {}: {}'.format(name, e))
if not frames:
return pd.DataFrame()
df.col
df = pd.concat(frames, ignore_index=True)
date_col = 'Ngay chung tu'
kh_col = 'Ten khach hang'
if date_col not in df.columns:
st.error('Khong tim thay cot ngay chung tu. Kiem tra lai file.')
return pd.DataFrame()
if kh_col not in df.columns:
st.error('Khong tim thay cot ten khach hang. Kiem tra lai file.')
return pd.DataFrame()
df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
df = df[df[date_col].notna()].copy()
df['Thang'] = df[date_col].dt.to_period('M').astype(str)
df['Quy'] = df[date_col].dt.to_period('Q').astype(str)
df['_day'] = df[date_col].dt.day
NUM_COLS = ['Thanh tien ban','Thanh tien von','Loi nhuan',
'Khoi luong','So luong','Gia ban','Gia von',
'Don gia van chuyen','Don gia quy doi']
for col in NUM_COLS:
df[col] = safe_num(df, col)
# Loai GD
gc = df['Ghi chu'].astype(str).str.upper() if 'Ghi chu' in df.columns else pd.Series('
loai = df['Loai don hang'].astype(str).str.upper() if 'Loai don hang' in df.columns else
df['Loai_GD'] = 'Xuat ban'
tra = gc.str.contains('NHAP TRA|TRA HANG', regex=True, na=False) | loai.str.contains('TRA
bos = gc.str.contains('BO SUNG|THAY THE', regex=True, na=False)
df.loc[tra, 'Loai_GD'] = 'Tra hang'
df.loc[bos & ~tra, 'Loai_GD'] = 'Xuat bo sung'
# Nhom SP
ten = df['Ten hang'].astype(str) if 'Ten hang' in df.columns else pd.Series('', index=d
ten_s = ten.apply(strip_acc)
df['Nhom_SP'] = 'Khac'
SP_MAP = [
('Ong HDPE', 'hdpe'),
('Ong PVC nuoc', r'pvc.*(nuoc|nong dai|nong tron|thoat|cap)'),
('Ong PVC bom cat', r'pvc.*(cat|bom cat)'),
('Ong PPR', 'ppr'),
('Loi PVC', r'(loi |lori)'),
('Phu kien & Keo', r'(noi |co |te |van |keo |mang|bit |y pvc|y ppr)'),
]
for lbl, pat in SP_MAP:
try:
df.loc[ten_s.str.contains(pat, regex=True, na=False), 'Nhom_SP'] = lbl
except Exception:
pass
# Clean text
for c in ['Ten khach hang','Ten nhom KH','Ma nhom KH','Khu vuc']:
if c in df.columns:
df[c] = df[c].fillna('').astype(str).str.strip()
df[c] = df[c].replace({'nan':'','None':'','NaN':''})
return df
# ============================================================
# RISK SCORE
# ============================================================
def compute_risk(grp):
db = grp[grp['Loai_GD'] == 'Xuat ban']
dt = grp[grp['Loai_GD'] == 'Tra hang']
bs = grp[grp['Loai_GD'] == 'Xuat bo sung']
if db.empty:
return 0
tb = db['Thanh tien ban'].sum()
tt = abs(dt['Thanh tien ban'].sum()) if not dt.empty else 0
ln = db['Loi nhuan'].sum()
tl_tra = (tt / tb * 100) if tb > 0 else 0
bien = (ln / tb * 100) if tb > 0 else 0
sc = 0
if tl_tra > 10: sc += 30
elif tl_tra > 3: sc += 15
if bien < 5: sc += 25
elif bien < 15: sc += 10
if not bs.empty: sc += 15
if len(db) > 4:
q75 = db['Thanh tien ban'].quantile(0.75)
q25 = db['Thanh tien ban'].quantile(0.25)
iqr = q75 - q25
if iqr > 0 and (db['Thanh tien ban'] > q75 + 3 * iqr).any():
sc += 10
if 'Noi giao hang' in db.columns and db['Noi giao hang'].nunique() >= 5:
sc += 10
nm = db['Thang'].nunique()
dd = (db['Ngay chung tu'].max() - db['Ngay chung tu'].min()).days
nr = max(dd // 30, 1)
if nm / nr < 0.5:
sc += 10
return sc
def risk_level(sc):
if sc >= 50: if sc >= 25: return 'Thap'
return 'Cao'
return 'Trung binh'
def risk_color(sc):
if sc >= 50: if sc >= 25: return '#26c281'
return '#e74c3c'
return '#f39c12'
@st.cache_data(show_spinner=False)
def build_risk_table(file_data):
df = load_all(file_data)
if df.empty or 'Ten khach hang' not in df.columns:
return pd.DataFrame()
rows = []
for kh_name, grp in df.groupby('Ten khach hang'):
if not kh_name or str(kh_name) in ('','nan','None'):
continue
sc = compute_risk(grp)
nhom = grp['Ten nhom KH'].mode()[0] if 'Ten nhom KH' in grp.columns and grp['Ten nhom
kv = grp['Khu vuc'].mode()[0] if 'Khu vuc' in grp.columns and grp['Khu vuc']
rows.append({'Ten_KH': str(kh_name), 'Ten_nhom_KH': str(nhom), 'Khu_vuc': str(kv),
'Diem_rui_ro': sc, 'Muc_rui_ro': risk_level(sc)})
if not rows:
return pd.DataFrame()
return pd.DataFrame(rows)
# ============================================================
# UPLOAD
# ============================================================
st.sidebar.markdown('## Upload du lieu')
uploaded_files = st.sidebar.file_uploader(
'File Excel bao cao ban hang (OM_RPT_055)',
type=['xlsx'],
accept_multiple_files=True
)
if not uploaded_files:
st.markdown('## Upload file Excel de bat dau phan tich')
st.info('Ho tro bao cao OM_RPT_055 - Hoa Sen. Header tu dong nhan dien.')
st.stop()
file_data = tuple((u.name, u.read()) for u in uploaded_files)
df_all = load_all(file_data)
risk_table = build_risk_table(file_data)
if df_all.empty:
st.error('Khong co du lieu hop le. Vui long kiem tra file.')
st.stop()
# ============================================================
# SIDEBAR FILTERS (hierarchy: Phong KD -> Khu vuc -> KH -> Quy)
# ============================================================
st.sidebar.markdown('---')
st.sidebar.markdown('## Bo loc')
# 1. Phong KD
has_nhom = 'Ten nhom KH' in df_all.columns
nhom_opts = sorted([x for x in df_all['Ten nhom KH'].unique() if x not in ('','nan','None')])
if nhom_opts:
nhom_chon = st.sidebar.multiselect('1. Phong Kinh Doanh', nhom_opts, default=nhom_opts)
df_f1 = df_all[df_all['Ten nhom KH'].isin(nhom_chon)].copy() if nhom_chon else df_all.cop
if not nhom_chon:
nhom_chon = nhom_opts
else:
nhom_chon = []
df_f1 = df_all.copy()
# 2. Khu vuc (depends on Phong KD)
has_kv = 'Khu vuc' in df_f1.columns
kv_opts = sorted([x for x in df_f1['Khu vuc'].unique() if x not in ('','nan','None')]) if has
if kv_opts:
kv_chon = st.sidebar.multiselect('2. Khu vuc', kv_opts, default=kv_opts)
df_f2 = df_f1[df_f1['Khu vuc'].isin(kv_chon)].copy() if kv_chon else df_f1.copy()
if not kv_chon:
kv_chon = kv_opts
else:
kv_chon = []
df_f2 = df_f1.copy()
# 3. Ten KH sorted by risk (thap -> cao)
kh_opts = sorted([x for x in df_f2['Ten khach hang'].unique() if x not in ('','nan','None')])
if not kh_opts:
st.error('Khong co khach hang. Hay mo rong bo loc.')
st.stop()
if not risk_table.empty:
rt = risk_table.set_index('Ten_KH')[['Diem_rui_ro','Muc_rui_ro']].to_dict('index')
kh_sorted = sorted(kh_opts, key=lambda k: rt.get(k, {}).get('Diem_rui_ro', 0))
kh_display = ['[{}pt-{}] {}'.format(
rt.get(k,{}).get('Diem_rui_ro',0),
rt.get(k,{}).get('Muc_rui_ro','?'),
k) for k in kh_sorted]
else:
kh_sorted = kh_opts
kh_display = kh_opts
d2n = dict(zip(kh_display, kh_sorted))
sel_disp = st.sidebar.selectbox(
'3. Ten Khach hang (rui ro: thap -> cao)',
kh_display,
help='Sap xep tu rui ro THAP nhat den CAO nhat'
)
kh = d2n.get(sel_disp, kh_sorted[0])
# 4. Quy
quy_opts = sorted(df_f2['Quy'].dropna().unique().tolist())
quy_chon = st.sidebar.multiselect('4. Quy', quy_opts, default=quy_opts)
if not quy_chon:
quy_chon = quy_opts
# Apply
df = df_all[(df_all['Ten khach hang'] == kh) & (df_all['Quy'].isin(quy_chon))].copy()
df_ban = df[df['Loai_GD'] == 'Xuat ban'].copy()
df_tra = df[df['Loai_GD'] == 'Tra hang'].copy()
df_bs = df[df['Loai_GD'] == 'Xuat bo sung'].copy()
# ============================================================
# PAGE HEADER
# ============================================================
sc_kh = 0
lv_kh = '?'
cl_kh = '#26c281'
if not risk_table.empty and kh in risk_table['Ten_KH'].values:
row_kh = risk_table[risk_table['Ten_KH'] == kh].iloc[0]
sc_kh = int(row_kh['Diem_rui_ro'])
lv_kh = row_kh['Muc_rui_ro']
cl_kh = risk_color(sc_kh)
date_col = 'Ngay chung tu'
d_min = df[date_col].min() if date_col in df.columns else None
d_max = df[date_col].max() if date_col in df.columns else None
date_str = '{} - {}'.format(
d_min.strftime('%d/%m/%Y') if pd.notna(d_min) else '?',
d_max.strftime('%d/%m/%Y') if pd.notna(d_max) else '?'
)
nhom_h = risk_table[risk_table['Ten_KH']==kh]['Ten_nhom_KH'].values[0] if not risk_table.empt
kv_h = risk_table[risk_table['Ten_KH']==kh]['Khu_vuc'].values[0] if not risk_table.empty
st.markdown('<h2>{}</h2>'.format(kh), unsafe_allow_html=True)
st.markdown(
'<p style="color:#9aa0b0">{} | PKD: {} | KV: {} | {} dong'
' <span style="background:{};color:#fff;padding:2px 10px;border-radius:10px;font-weight:7
'{}pt - {}</span></p>'.format(date_str, nhom_h or '?', kv_h or '?', len(df), cl_kh, sc_kh
unsafe_allow_html=True
)
if df_ban.empty:
st.warning('Khong co du lieu xuat ban.')
st.stop()
# KPI row
tong_dt = df_ban['Thanh tien ban'].sum()
tong_ln = df_ban['Loi nhuan'].sum()
tong_kl = df_ban['Khoi luong'].sum() / 1000
bien_ln = (tong_ln / tong_dt * 100) if tong_dt else 0
n_ct = df_ban['So chung tu'].nunique() if 'So chung tu' in df_ban.columns else len(df_ban)
n_sp = df_ban['Ten hang'].nunique() if 'Ten hang' in df_ban.columns else 0
kpi_cols = st.columns(5)
kpi_data = [
('DT (VND)', '{:,.0f}'.format(tong_dt)),
('Loi nhuan','{:,.0f}'.format(tong_ln)),
('Bien LN', '{:.1f}%'.format(bien_ln)),
('KL (tan)', '{:,.1f}'.format(tong_kl)),
('CT / SP', '{} / {}'.format(n_ct, n_sp)),
]
for col, (lab, val) in zip(kpi_cols, kpi_data):
col.metric(lab, val)
# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
'San pham', 'Doanh thu', 'Loi nhuan', 'Giao hang',
'Tan suat', 'Rui ro & BCCN', 'Xep hang rui ro'
])
# ============================================================
# TAB 1 - SAN PHAM
# ============================================================
with tab1:
st.markdown('<div class="section-title">Co cau san pham</div>', unsafe_allow_html=True)
if 'Nhom_SP' in df_ban.columns:
df_nhom = (
df_ban.groupby('Nhom_SP')
.agg(So_lan=('Nhom_SP','count'),
KL_tan=('Khoi luong', lambda x: round(x.sum()/1000, 2)),
DT=('Thanh tien ban','sum'))
.reset_index().sort_values('DT', ascending=False)
)
df_nhom = df_nhom[df_nhom['DT'] > 0]
if not df_nhom.empty:
c1, c2 = st.columns(2)
with c1:
fig = px.bar(df_nhom, x='Nhom_SP', y='DT', color='Nhom_SP',
text_auto='.3s', title='DT theo nhom SP',
labels={'DT':'DT (VND)','Nhom_SP':''})
fig.update_layout(showlegend=False, height=360)
st.plotly_chart(fig, use_container_width=True)
with c2:
fig2 = px.pie(df_nhom, names='Nhom_SP', values='So_lan',
title='Ty trong so lan mua', hole=0.45)
fig2.update_layout(height=360)
st.plotly_chart(fig2, use_container_width=True)
if 'Ten hang' in df_ban.columns:
st.markdown('<div class="section-title">Top 15 san pham theo DT</div>', unsafe_allow_
df_top = (
df_ban.groupby('Ten hang')
.agg(So_lan=('Ten hang','count'),
KL_tan=('Khoi luong', lambda x: round(x.sum()/1000, 2)),
SL=('So luong','sum'),
DT=('Thanh tien ban','sum'))
.reset_index().sort_values('DT', ascending=False).head(15)
)
df_top_s = df_top.copy()
df_top_s['DT'] = df_top_s['DT'].map('{:,.0f}'.format)
df_top_s.columns = ['San pham','So lan','KL (tan)','SL','DT (VND)']
st.dataframe(df_top_s, use_container_width=True, hide_index=True)
df_nho
st.markdown('<div class="section-title">Nhan dinh muc dich su dung</div>', unsafe_allow_h
nhom_set = set(df_nhom['Nhom_SP'].tolist()) if 'Nhom_SP' in df_ban.columns and not notes = {
'Ong HDPE': 'Ong HDPE (lon): Du an ha tang, cap thoat nuoc cong trinh lon.',
'Ong PVC nuoc': 'Ong PVC nuoc: Xay dung dan dung, cong nghiep, nong nghiep.',
'Ong PVC bom cat': 'Ong PVC bom cat: Thuy loi, nong nghiep, nuoi trong thuy san.',
'Ong PPR': 'Ong PPR: He thong nuoc nong/lanh noi that, dan dung.',
'Loi PVC': 'Loi PVC: KH co the la dai ly hoac nha SX thu cap.',
'Phu kien & Keo': 'Phu kien & Keo: Tu thi cong hoac ban lai tron goi.',
}
shown = False
for k, v in notes.items():
if k in nhom_set:
shown = True
st.markdown('<div class="risk-low">{}</div>'.format(v), unsafe_allow_html=True)
if not shown:
st.info('Khong du du lieu de nhan dinh.')
# ============================================================
# TAB 2 - DOANH THU
# ============================================================
with tab2:
st.markdown('<div class="section-title">Bien dong DT theo thang</div>', unsafe_allow_html
ct_col = 'So chung tu' if 'So chung tu' in df_ban.columns else 'Thanh tien ban'
df_m = (
df_ban.groupby('Thang')
.agg(DT=('Thanh tien ban','sum'),
KL=('Khoi luong', lambda x: round(x.sum()/1000, 3)),
SL=('So luong','sum'),
So_CT=(ct_col,'nunique'))
.reset_index().sort_values('Thang')
)
fig_t = make_subplots(rows=2, cols=1, shared_xaxes=True,
subplot_titles=['DT (VND) & KL (tan)', 'SL & So chung tu'],
vertical_spacing=0.14)
fig_t.add_trace(go.Bar(x=df_m['Thang'], y=df_m['DT'], name='DT',
marker_color='#4e79d4', opacity=0.85), row=1, col=1)
fig_t.add_trace(go.Scatter(x=df_m['Thang'], y=df_m['KL'], name='KL (tan)',
mode='lines+markers', line=dict(color='#f0a500', width=2),
marker=dict(size=7)), row=1, col=1)
fig_t.add_trace(go.Bar(x=df_m['Thang'], y=df_m['SL'], name='SL',
marker_color='#26c281', opacity=0.85), row=2, col=1)
fig_t.add_trace(go.Scatter(x=df_m['Thang'], y=df_m['So_CT'], name='So CT',
mode='lines+markers', line=dict(color='#e74c3c', width=2),
marker=dict(size=7)), row=2, col=1)
fig_t.update_layout(height=520, legend=dict(orientation='h', y=-0.12))
st.plotly_chart(fig_t, use_container_width=True)
df_ms = df_m.copy()
df_ms['DT'] = df_ms['DT'].map('{:,.0f}'.format)
df_ms.columns = ['Thang','DT (VND)','KL (tan)','SL','So CT']
st.dataframe(df_ms, use_container_width=True, hide_index=True)
st.markdown('<div class="section-title">Tong hop theo Quy</div>', unsafe_allow_html=True)
df_q = (
df_ban.groupby('Quy')
.agg(DT=('Thanh tien ban','sum'),
KL=('Khoi luong', lambda x: round(x.sum()/1000, 2)),
LN=('Loi nhuan','sum'),
So_CT=(ct_col,'nunique'))
.reset_index()
)
df_q['Bien (%)'] = (df_q['LN'] / df_q['DT'].replace(0, float('nan')) * 100).round(1).fill
df_qs = df_q.copy()
df_qs['DT'] = df_qs['DT'].map('{:,.0f}'.format)
df_qs['LN'] = df_qs['LN'].map('{:,.0f}'.format)
df_qs.columns = ['Quy','DT (VND)','KL (tan)','LN (VND)','So CT','Bien LN (%)']
st.dataframe(df_qs, use_container_width=True, hide_index=True)
# ============================================================
# TAB 3 - LOI NHUAN
# ============================================================
with tab3:
st.markdown('<div class="section-title">Bien dong loi nhuan & phat hien chinh sach</div>'
df_ln = (
df_ban.groupby('Thang')
.agg(DT=('Thanh tien ban','sum'),
Von=('Thanh tien von','sum'),
LN=('Loi nhuan','sum'))
.reset_index().sort_values('Thang')
)
df_ln['Bien'] = (df_ln['LN'] / df_ln['DT'].replace(0, float('nan')) * 100).round(2).filln
fig_ln = make_subplots(rows=2, cols=1, shared_xaxes=True,
subplot_titles=['DT / Von / LN (VND)', 'Bien loi nhuan (%)'],
vertical_spacing=0.14)
fig_ln.add_trace(go.Bar(x=df_ln['Thang'], y=df_ln['DT'], name='DT', marker_color='#4e79d4
fig_ln.add_trace(go.Bar(x=df_ln['Thang'], y=df_ln['Von'], name='Von', marker_color='#e05c
fig_ln.add_trace(go.Scatter(x=df_ln['Thang'], y=df_ln['LN'], name='LN',
mode='lines+markers', line=dict(color='#26c281', width=2),
marker=dict(size=7)), row=1, col=1)
fig_ln.add_trace(go.Scatter(x=df_ln['Thang'], y=df_ln['Bien'], name='Bien LN',
mode='lines+markers+text',
text=['{:.1f}%'.format(v) for v in df_ln['Bien']],
textposition='top center',
line=dict(color='#f0a500', width=2),
marker=dict(size=7)), row=2, col=1)
fig_ln.update_layout(height=520, barmode='group')
st.plotly_chart(fig_ln, use_container_width=True)
if len(df_ln) >= 2:
mean_b = df_ln['Bien'].mean()
std_b = max(float(df_ln['Bien'].std()), 1.0)
anom = df_ln[df_ln['Bien'] < mean_b - std_b]
st.markdown('<div class="section-title">Thang nghi co chiet khau bat thuong</div>', u
if not anom.empty:
for _, r in anom.iterrows():
st.markdown(
'<div class="risk-medium">Thang <b>{}</b>: Bien LN = <b>{:.1f}%</b> (TB={
r['Thang'], r['Bien'], mean_b),
unsafe_allow_html=True
)
else:
st.markdown('<div class="risk-low">Khong phat hien thang bat thuong ve bien LN.</
if not df_tra.empty:
st.markdown('<div class="section-title">Don hang tra lai</div>', unsafe_allow_html=Tr
show_tra = [c for c in ['So chung tu','Ngay chung tu','Ten hang','Khoi luong','Thanh
if c in df_tra.columns]
df_tra_s = df_tra[show_tra].copy()
if 'Thanh tien ban' in df_tra_s.columns:
df_tra_s['Thanh tien ban'] = df_tra_s['Thanh tien ban'].map('{:,.0f}'.format)
st.dataframe(df_tra_s, use_container_width=True, hide_index=True)
st.error('Tong GT tra hang: {:,.0f} VND'.format(abs(df_tra['Thanh tien ban'].sum())))
with st.expander('Chi tiet gia ban tung giao dich'):
show2 = [c for c in ['So chung tu','Ngay chung tu','Ten hang',
'Gia ban','Don gia quy doi','Thanh tien ban','Loi nhuan','Ghi c
if c in df_ban.columns]
st.dataframe(df_ban[show2].sort_values('Ngay chung tu'), use_container_width=True, hi
# ============================================================
# TAB 4 - GIAO HANG
# ============================================================
with tab4:
st.markdown('<div class="section-title">Hinh thuc & dia diem giao hang</div>', unsafe_all
c1, c2 = st.columns(2)
with c1:
if 'Freight Terms' in df_ban.columns:
df_ft = df_ban['Freight Terms'].value_counts().reset_index()
df_ft.columns = ['Hinh thuc','So lan']
fig_ft = px.pie(df_ft, names='Hinh thuc', values='So lan',
title='Dieu kien giao hang', hole=0.4)
st.plotly_chart(fig_ft, use_container_width=True)
else:
st.info('Khong co du lieu Freight Terms.')
with c2:
if 'Shipping method' in df_ban.columns:
df_sm = df_ban['Shipping method'].value_counts().reset_index()
df_sm.columns = ['Phuong tien','So lan']
fig_sm = px.pie(df_sm, names='Phuong tien', values='So lan',
title='Phuong tien van chuyen', hole=0.4)
st.plotly_chart(fig_sm, use_container_width=True)
else:
st.info('Khong co du lieu Shipping method.')
if 'Noi giao hang' in df_ban.columns:
st.markdown('<div class="section-title">Dia diem giao hang</div>', unsafe_allow_html=
df_noi = (
df_ban.groupby('Noi giao hang')
.agg(So_lan=('Noi giao hang','count'),
KL=('Khoi luong', lambda x: round(x.sum()/1000, 2)),
DT=('Thanh tien ban','sum'))
.reset_index().sort_values('DT', ascending=False)
)
df_noi['DT'] = df_noi['DT'].map('{:,.0f}'.format)
df_noi.columns = ['Dia diem','So lan','KL (tan)','DT (VND)']
st.dataframe(df_noi, use_container_width=True, hide_index=True)
with st.expander('Danh sach xe & tai xe'):
xe_c = [c for c in ['Bien so xe','Tai Xe','Ten DVVC','Shipping method','Ngay chung tu
if c in df_ban.columns]
if xe_c:
st.dataframe(df_ban[xe_c].drop_duplicates(), use_container_width=True, hide_index
else:
st.info('Khong co du lieu xe/tai xe.')
# ============================================================
# TAB 5 - TAN SUAT
# ============================================================
with tab5:
st.markdown('<div class="section-title">Heatmap tan suat: San pham x Thang</div>', unsafe
if 'Ten hang' in df_ban.columns:
df_freq = df_ban.groupby(['Ten hang','Thang']).size().reset_index(name='So_lan')
if not df_freq.empty:
df_piv = df_freq.pivot(index='Ten hang', columns='Thang', values='So_lan').fillna
top_n = df_piv.sum(axis=1).nlargest(min(20, len(df_piv))).index
fig_hm = px.imshow(df_piv.loc[top_n],
labels=dict(x='Thang', y='San pham', color='So lan'),
title='Top SP x Thang',
color_continuous_scale='Blues', aspect='auto')
fig_hm.update_layout(height=max(380, len(top_n)*24))
st.plotly_chart(fig_hm, use_container_width=True)
for qv in sorted(df_ban['Quy'].dropna().unique()):
dq = df_ban[df_ban['Quy'] == qv]
months_s = ', '.join(sorted(dq['Thang'].dropna().unique()))
with st.expander('{} | {}'.format(qv, months_s)):
ag = (
dq.groupby(['Ten hang','Thang'])
.agg(So_lan=('Ten hang','count'),
KL=('Khoi luong', lambda x: round(x.sum()/1000, 2)),
DT=('Thanh tien ban','sum'))
.reset_index().sort_values('DT', ascending=False)
)
ag['DT'] = ag['DT'].map('{:,.0f}'.format)
ag.columns = ['San pham','Thang','So lan','KL (tan)','DT (VND)']
st.dataframe(ag, use_container_width=True, hide_index=True)
else:
st.info('Khong co du lieu Ten hang.')
# ============================================================
# TAB 6 - RUI RO & BCCN
# ============================================================
with tab6:
st.markdown('<div class="section-title">BCCN - Phan tich thanh toan & cong no</div>', uns
gc_s df_po ct_c = df['Ghi chu'].astype(str).str.upper() if 'Ghi chu' in df.columns else pd.Series
= df[gc_s.str.contains(r'PO|B[0-9]{3}|HOP DONG', regex=True, na=False)]
= 'So chung tu' if 'So chung tu' in df.columns else 'Thanh tien ban'
mc = st.columns(4)
mc[0].metric('Don PO/HD', df_po[ct_c].nunique() if not df_po.empty else 0)
mc[1].metric('Phieu tra hang', df_tra[ct_c].nunique() if not df_tra.empty else 0)
mc[2].metric('Xuat bo sung', df_bs[ct_c].nunique() if not df_bs.empty else 0)
mc[3].metric('GT tra hang VND', '{:,.0f}'.format(abs(df_tra['Thanh tien ban'].sum()) if n
st.markdown('''
<div class="info-box">
<b>File OM_RPT_055 khong co ngay thanh toan thuc te.</b><br>
Can bo sung: So AR Aging, Lich su thanh toan.<br>
Dau hieu: Ghi chu B-xxx/PO = don du an = TT cham NET30-90 |
Tra hang = tranh chap | Nhieu dia diem giao = cong no phan tan.
</div>''', unsafe_allow_html=True)
if not df_po.empty:
with st.expander('{} don co PO / ma du an'.format(len(df_po))):
show_po = [c for c in ['So chung tu','Ngay chung tu','Ten hang','Thanh tien ban',
if c in df_po.columns]
df_po_s = df_po[show_po].drop_duplicates().copy()
if 'Thanh tien ban' in df_po_s.columns:
df_po_s['Thanh tien ban'] = df_po_s['Thanh tien ban'].map('{:,.0f}'.format)
st.dataframe(df_po_s, use_container_width=True, hide_index=True)
st.markdown('<div class="section-title">Danh gia rui ro tong hop</div>', unsafe_allow_htm
risks = []
score = sc_kh
tong_ban = df_ban['Thanh tien ban'].sum()
tong_tra = abs(df_tra['Thanh tien ban'].sum()) if not df_tra.empty else 0
tl_tra = (tong_tra / tong_ban * 100) if tong_ban > 0 else 0
tong_ln = df_ban['Loi nhuan'].sum()
bien = (tong_ln / tong_ban * 100) if tong_ban > 0 else 0
cao'.f
if tl_tra > 10:
risks.append(('high', elif tl_tra > 3:
'Ty le hang tra: <b>{:.1f}%</b> ({:,.0f} VND) - rui ro risks.append(('medium', 'Ty le hang tra: <b>{:.1f}%</b> - can theo doi'.format(tl_tra
else:
risks.append(('low', 'Ty le tra hang thap: {:.1f}%'.format(tl_tra)))
if bien < 5:
risks.append(('high', elif bien < 15:
'Bien LN rat thap: <b>{:.1f}%</b> - ban duoi gia hoac chiet k
risks.append(('medium', 'Bien LN o muc thap: <b>{:.1f}%</b>'.format(bien)))
else:
risks.append(('low', 'Bien LN binh thuong: {:.1f}%'.format(bien)))
if not df_bs.empty:
risks.append(('medium', 'Co <b>{}</b> dong xuat bo sung/thay the'.format(len(df_bs)))
else:
risks.append(('low', 'Khong co don xuat bo sung.'))
if len(df_ban) > 4:
q75 = df_ban['Thanh tien ban'].quantile(0.75)
q25 = df_ban['Thanh tien ban'].quantile(0.25)
iqr = q75 - q25
if iqr > 0:
outs = df_ban[df_ban['Thanh tien ban'] > q75 + 3 * iqr]
if not outs.empty:
risks.append(('medium', 'Co <b>{}</b> don hang gia tri rat lon - kiem soat ha
else:
risks.append(('low', 'Khong co don hang gia tri bat thuong.'))
if 'Noi giao hang' in df_ban.columns:
n_noi = df_ban['Noi giao hang'].nunique()
if n_noi >= 5:
risks.append(('medium', 'Giao hang toi <b>{}</b> dia diem - cong no phan tan'.for
else:
risks.append(('low', 'So dia diem: {} (binh thuong)'.format(n_noi)))
n_thang = df_ban['Thang'].nunique()
dd_days = (df_ban['Ngay chung tu'].max() - df_ban['Ngay chung tu'].min()).days
n_range = max(dd_days // 30, 1)
if n_thang / n_range < 0.5:
risks.append(('medium', 'Mua chi <b>{}/{}</b> thang - khong deu, phu thuoc du an'.for
else:
risks.append(('low', 'Mua deu: {}/{} thang co GD'.format(n_thang, n_range)))
'RUI R
sc2 = risk_color(score)
sc_lbl = 'RUI RO CAO' if score >= 50 else ('RUI RO TRUNG BINH' if score >= 25 else st.markdown(
'<div style="background:#1a2035;border-radius:10px;padding:20px;text-align:center;mar
'<div style="font-size:32px;font-weight:900;color:{};"> {}</div>'
'<div style="font-size:16px;color:#9aa0b0;margin-top:6px;">'
'Diem rui ro: <b style="color:{}">{}/100</b></div>'
'</div>'.format(sc2, sc_lbl, sc2, score),
unsafe_allow_html=True
)
pct = min(score, 100)
st.markdown(
'<div style="background:#21262d;border-radius:6px;height:8px;margin:-8px 0 18px 0;ove
'<div style="background:{};width:{}%;height:100%;border-radius:6px;"></div></div>'.fo
unsafe_allow_html=True
)
for lvl, msg in risks:
st.markdown('<div class="risk-{}">{}</div>'.format(lvl, msg), unsafe_allow_html=True)
# ============================================================
# TAB 7 - XEP HANG RUI RO
# ============================================================
with tab7:
st.markdown('<div class="section-title">Bang xep hang rui ro tat ca KH (thap -> cao)</div
if risk_table.empty:
st.info('Chua co du lieu rui ro.')
else:
rt_f = risk_table.copy()
if nhom_chon:
if kv_chon:
rt_f = rt_f[rt_f['Ten_nhom_KH'].isin(nhom_chon)]
rt_f = rt_f[rt_f['Khu_vuc'].isin(kv_chon)]
rt_show = rt_f.sort_values('Diem_rui_ro', ascending=True).reset_index(drop=True)
rt_show.index = rt_show.index + 1
bar_colors = [risk_color(s) for s in rt_show['Diem_rui_ro']]
fig_rank = go.Figure(go.Bar(
y=rt_show['Ten_KH'],
x=rt_show['Diem_rui_ro'],
orientation='h',
marker=dict(color=bar_colors),
text=rt_show['Diem_rui_ro'].astype(str),
textposition='outside',
textfont=dict(color='#c9d1d9', size=11)
))
fig_rank.update_layout(
paper_bgcolor='#0d1117', plot_bgcolor='#0d1117',
font=dict(color='#c9d1d9', size=11),
title='Diem rui ro KH (thap den cao)',
height=max(400, len(rt_show)*32),
margin=dict(l=10, r=10, t=45, b=10),
xaxis=dict(gridcolor='#21262d', range=[0, 110]),
)
fig_rank.update_yaxes(gridcolor='#21262d', tickfont=dict(size=10))
st.plotly_chart(fig_rank, use_container_width=True)
if rt_show['Ten_nhom_KH'].ne('').any():
st.markdown('<div class="section-title">Tong hop rui ro theo Phong KD</div>', uns
grp_nhom = (
rt_show.groupby('Ten_nhom_KH')
.agg(So_KH=('Ten_KH','count'),
Diem_TB=('Diem_rui_ro','mean'),
Diem_Max=('Diem_rui_ro','max'))
.reset_index().sort_values('Diem_Max', ascending=False)
)
grp_nhom['Diem_TB'] = grp_nhom['Diem_TB'].round(1)
grp_nhom.columns = ['Phong KD','So KH','Diem TB','Diem Max']
st.dataframe(grp_nhom, use_container_width=True, hide_index=True)
if rt_show['Khu_vuc'].ne('').any():
st.markdown('<div class="section-title">Tong hop rui ro theo Khu vuc</div>', unsa
grp_kv = (
rt_show.groupby('Khu_vuc')
.agg(So_KH=('Ten_KH','count'),
Diem_TB=('Diem_rui_ro','mean'),
Diem_Max=('Diem_rui_ro','max'))
.reset_index().sort_values('Diem_Max', ascending=False)
)
grp_kv['Diem_TB'] = grp_kv['Diem_TB'].round(1)
grp_kv.columns = ['Khu vuc','So KH','Diem TB','Diem Max']
st.dataframe(grp_kv, use_container_width=True, hide_index=True)
st.markdown('<div class="section-title">Chi tiet tat ca KH</div>', unsafe_allow_html=
st.dataframe(
rt_show[['Ten_KH','Ten_nhom_KH','Khu_vuc','Diem_rui_ro','Muc_rui_ro']],
use_container_width=True
)