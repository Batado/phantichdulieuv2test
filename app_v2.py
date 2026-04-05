import io
import warnings
warnings.filterwarnings(‘ignore’)
import unicodedata

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title=‘Phan tich KH - Hoa Sen’, layout=‘wide’)

st.markdown(’’’

<style>
.risk-high   { background:#4a1010; border-left:4px solid #e74c3c; padding:10px 14px; border-radius:6px; margin:6px 0; color:#fff; }
.risk-medium { background:#3d2e10; border-left:4px solid #f39c12; padding:10px 14px; border-radius:6px; margin:6px 0; color:#fff; }
.risk-low    { background:#0f3020; border-left:4px solid #26c281; padding:10px 14px; border-radius:6px; margin:6px 0; color:#fff; }
.section-title { font-size:17px; font-weight:700; color:#e0e0e0; margin:20px 0 10px 0; padding-bottom:6px; border-bottom:1px solid #2e3350; }
.info-box { background:#1a2035; border-radius:8px; padding:14px; margin:8px 0; color:#ccc; }
</style>

‘’’, unsafe_allow_html=True)

def strip_acc(s):
s = unicodedata.normalize(‘NFD’, str(s))
return ‘’.join(c for c in s if unicodedata.category(c) != ‘Mn’).lower().strip()

def find_header_row(file_bytes):
try:
df_raw = pd.read_excel(io.BytesIO(file_bytes), header=None, engine=‘openpyxl’, nrows=40)
except Exception:
return 0
kws = [‘so chung tu’, ‘ngay chung tu’, ‘ten khach hang’,
‘ten hang’, ‘thanh tien ban’, ‘loi nhuan’, ‘ten nhom kh’, ‘khu vuc’]
for i in range(df_raw.shape[0]):
vals = [str(v).strip() for v in df_raw.iloc[i].tolist()
if str(v).strip() not in (’’, ‘nan’, ‘none’, ‘None’)]
if len(vals) < 5:
continue
txt = strip_acc(’ ’.join(vals))
if sum(1 for k in kws if k in txt) >= 3:
return i
return 0

_ALIAS_PAIRS = [
(‘Ten khach hang’, [‘Ten khach hang’, ‘Ten KH’, ‘Khach hang’, ‘customer_name’]),
(‘Ngay chung tu’,  [‘Ngay chung tu’, ‘Ngay CT’, ‘date’]),
(‘So chung tu’,    [‘So chung tu’, ‘So CT’, ‘voucher_no’]),
(‘Ten hang’,       [‘Ten hang’, ‘Ten ma hang’, ‘Ten SP’, ‘product_name’]),
(‘Ma hang’,        [‘Ma hang’, ‘Ma SP’, ‘product_code’]),
(‘Khoi luong’,     [‘Khoi luong’, ‘KL’, ‘weight’]),
(‘So luong’,       [‘So luong’, ‘SL’, ‘qty’, ‘quantity’]),
(‘Thanh tien ban’, [‘Thanh tien ban’, ‘Doanh thu’, ‘revenue’, ‘amount’]),
(‘Thanh tien von’, [‘Thanh tien von’, ‘Gia von hang ban’, ‘cost’]),
(‘Loi nhuan’,      [‘Loi nhuan’, ‘Profit’, ‘profit’]),
(‘Gia ban’,        [‘Gia ban’, ‘Don gia’, ‘unit_price’]),
(‘Gia von’,        [‘Gia von’, ‘cost_price’]),
(‘Noi giao hang’,  [‘Noi giao hang’, ‘Dia chi giao hang’, ‘delivery_address’]),
(‘Freight Terms’,  [‘Freight Terms’, ‘Dieu kien giao hang’, ‘freight’]),
(‘Shipping method’,[‘Shipping method’, ‘Phuong tien’, ‘shipping’]),
(‘Bien so xe’,     [‘So xe’, ‘Bien so xe’, ‘Bien xe’, ‘plate_no’]),
(‘Tai Xe’,         [‘Tai Xe’, ‘Tai xe’, ‘Driver’, ‘driver’]),
(‘Ten DVVC’,       [‘Ten DVVC’, ‘Don vi van chuyen’, ‘carrier’]),
(‘Ghi chu’,        [‘Ghi chu’, ‘Note’, ‘Ghi Chu’, ‘notes’]),
(‘Khu vuc’,        [‘Khu vuc’, ‘Region’, ‘region’]),
(‘Ten nhom KH’,    [‘Ten nhom KH’, ‘Nhom KH’, ‘sales_group_name’]),
(‘Ma nhom KH’,     [‘Ma nhom KH’, ‘ma_nhom_kh’]),
(‘Ma nhom hang’,   [‘Ma nhom hang’, ‘Nhom hang’, ‘product_group’]),
(‘Don gia vc’,     [‘Don gia van chuyen’, ‘freight_cost’]),
(‘Don gia qd’,     [‘Don gia quy doi’, ‘converted_price’]),
]

_ALIAS_MAP = {}
for _std, _aliases in _ALIAS_PAIRS:
for _a in _aliases:
_ALIAS_MAP[strip_acc(_a)] = _aliases[0]

def normalize_columns(df):
rename = {}
for col in df.columns:
key = strip_acc(col)
if key in _ALIAS_MAP:
canonical = _ALIAS_MAP[key]
if col != canonical and canonical not in df.columns:
rename[col] = canonical
if rename:
df.rename(columns=rename, inplace=True)
return df

def safe_num(df, col):
if col in df.columns:
return pd.to_numeric(df[col], errors=‘coerce’).fillna(0)
return pd.Series(0.0, index=df.index)

@st.cache_data(show_spinner=‘Dang xu ly du lieu…’)
def load_all(file_data):
frames = []
for name, fb in file_data:
try:
hr  = find_header_row(fb)
tmp = pd.read_excel(io.BytesIO(fb), header=hr, engine=‘openpyxl’)
tmp.columns = [str(c).strip().replace(’\n’, ’ ‘).replace(’\r’, ‘’) for c in tmp.columns]
tmp = tmp.loc[:, ~tmp.columns.str.startswith(‘Unnamed’)]
tmp.dropna(how=‘all’, inplace=True)
normalize_columns(tmp)
tmp[’_file’] = name
frames.append(tmp)
except Exception as exc:
st.warning(‘Loi doc file {}: {}’.format(name, exc))
if not frames:
return pd.DataFrame()

```
data = pd.concat(frames, ignore_index=True)

if 'Ngay chung tu' not in data.columns:
    st.error('Khong tim thay cot Ngay chung tu.')
    return pd.DataFrame()
if 'Ten khach hang' not in data.columns:
    st.error('Khong tim thay cot Ten khach hang.')
    return pd.DataFrame()

data['Ngay chung tu'] = pd.to_datetime(data['Ngay chung tu'], dayfirst=True, errors='coerce')
data = data[data['Ngay chung tu'].notna()].copy()
data['Thang'] = data['Ngay chung tu'].dt.to_period('M').astype(str)
data['Quy']   = data['Ngay chung tu'].dt.to_period('Q').astype(str)

NUM = ['Thanh tien ban', 'Thanh tien von', 'Loi nhuan',
       'Khoi luong', 'So luong', 'Gia ban', 'Gia von', 'Don gia vc', 'Don gia qd']
for c in NUM:
    data[c] = safe_num(data, c)

gc   = data['Ghi chu'].astype(str).str.upper() if 'Ghi chu' in data.columns else pd.Series('', index=data.index)
loai = data['Loai don hang'].astype(str).str.upper() if 'Loai don hang' in data.columns else pd.Series('', index=data.index)
data['Loai_GD'] = 'Xuat ban'
tra = gc.str.contains('NHAP TRA|TRA HANG', regex=True, na=False) | loai.str.contains('TRA HANG|HUY HD', regex=True, na=False)
bos = gc.str.contains('BO SUNG|THAY THE', regex=True, na=False)
data.loc[tra, 'Loai_GD'] = 'Tra hang'
data.loc[bos & ~tra, 'Loai_GD'] = 'Xuat bo sung'

ten_s = data['Ten hang'].astype(str).apply(strip_acc) if 'Ten hang' in data.columns else pd.Series('', index=data.index)
data['Nhom_SP'] = 'Khac'
SP = [
    ('Ong HDPE',        'hdpe'),
    ('Ong PVC nuoc',    r'pvc.*(nuoc|nong dai|nong tron|thoat|cap)'),
    ('Ong PVC bom cat', r'pvc.*(cat|bom cat)'),
    ('Ong PPR',         'ppr'),
    ('Loi PVC',         r'(loi |lori)'),
    ('Phu kien & Keo',  r'(noi |co |te |van |keo |mang|bit |y pvc|y ppr)'),
]
for lbl, pat in SP:
    try:
        data.loc[ten_s.str.contains(pat, regex=True, na=False), 'Nhom_SP'] = lbl
    except Exception:
        pass

for c in ['Ten khach hang', 'Ten nhom KH', 'Ma nhom KH', 'Khu vuc']:
    if c in data.columns:
        data[c] = data[c].fillna('').astype(str).str.strip().replace({'nan':'','None':'','NaN':''})

return data
```

def compute_risk(grp):
db = grp[grp[‘Loai_GD’] == ‘Xuat ban’]
dt = grp[grp[‘Loai_GD’] == ‘Tra hang’]
bs = grp[grp[‘Loai_GD’] == ‘Xuat bo sung’]
if db.empty:
return 0
tb  = db[‘Thanh tien ban’].sum()
tt  = abs(dt[‘Thanh tien ban’].sum()) if not dt.empty else 0
ln  = db[‘Loi nhuan’].sum()
tl  = (tt / tb * 100) if tb > 0 else 0
bln = (ln / tb * 100) if tb > 0 else 0
sc  = 0
if tl  > 10: sc += 30
elif tl > 3: sc += 15
if bln < 5:  sc += 25
elif bln < 15: sc += 10
if not bs.empty: sc += 15
if len(db) > 4:
q75 = db[‘Thanh tien ban’].quantile(0.75)
q25 = db[‘Thanh tien ban’].quantile(0.25)
iqr = q75 - q25
if iqr > 0 and (db[‘Thanh tien ban’] > q75 + 3*iqr).any():
sc += 10
if ‘Noi giao hang’ in db.columns and db[‘Noi giao hang’].nunique() >= 5:
sc += 10
nm = db[‘Thang’].nunique()
dd = (db[‘Ngay chung tu’].max() - db[‘Ngay chung tu’].min()).days
nr = max(dd // 30, 1)
if nm / nr < 0.5:
sc += 10
return sc

def risk_level(sc):
if sc >= 50: return ‘Cao’
if sc >= 25: return ‘Trung binh’
return ‘Thap’

def risk_color(sc):
if sc >= 50: return ‘#e74c3c’
if sc >= 25: return ‘#f39c12’
return ‘#26c281’

@st.cache_data(show_spinner=False)
def build_risk_table(file_data):
data = load_all(file_data)
if data.empty or ‘Ten khach hang’ not in data.columns:
return pd.DataFrame()
rows = []
for kh_name, grp in data.groupby(‘Ten khach hang’):
if not kh_name or str(kh_name) in (’’, ‘nan’, ‘None’):
continue
sc   = compute_risk(grp)
nhom = grp[‘Ten nhom KH’].mode()[0] if (‘Ten nhom KH’ in grp.columns and grp[‘Ten nhom KH’].ne(’’).any()) else ‘’
kv   = grp[‘Khu vuc’].mode()[0]     if (‘Khu vuc’    in grp.columns and grp[‘Khu vuc’].ne(’’).any())    else ‘’
rows.append({‘Ten_KH’: str(kh_name), ‘Ten_nhom_KH’: str(nhom),
‘Khu_vuc’: str(kv), ‘Diem’: sc, ‘Muc’: risk_level(sc)})
return pd.DataFrame(rows) if rows else pd.DataFrame()

st.sidebar.markdown(’## Upload du lieu’)
uploaded_files = st.sidebar.file_uploader(
‘File Excel bao cao ban hang (OM_RPT_055)’,
type=[‘xlsx’], accept_multiple_files=True
)
if not uploaded_files:
st.markdown(’## Upload file Excel de bat dau phan tich’)
st.info(‘Ho tro bao cao OM_RPT_055 - Hoa Sen.’)
st.stop()

file_data  = tuple((u.name, u.read()) for u in uploaded_files)
df_all     = load_all(file_data)
risk_table = build_risk_table(file_data)

if df_all.empty:
st.error(‘Khong co du lieu hop le.’)
st.stop()

st.sidebar.markdown(’—’)
st.sidebar.markdown(’## Bo loc’)

nhom_opts = []
if ‘Ten nhom KH’ in df_all.columns:
nhom_opts = sorted([x for x in df_all[‘Ten nhom KH’].unique() if x not in (’’, ‘nan’, ‘None’)])
if nhom_opts:
nhom_chon = st.sidebar.multiselect(‘1. Phong Kinh Doanh’, nhom_opts, default=nhom_opts)
df_f1 = df_all[df_all[‘Ten nhom KH’].isin(nhom_chon)].copy() if nhom_chon else df_all.copy()
nhom_chon = nhom_chon or nhom_opts
else:
nhom_chon = []
df_f1 = df_all.copy()

kv_opts = []
if ‘Khu vuc’ in df_f1.columns:
kv_opts = sorted([x for x in df_f1[‘Khu vuc’].unique() if x not in (’’, ‘nan’, ‘None’)])
if kv_opts:
kv_chon = st.sidebar.multiselect(‘2. Khu vuc’, kv_opts, default=kv_opts)
df_f2 = df_f1[df_f1[‘Khu vuc’].isin(kv_chon)].copy() if kv_chon else df_f1.copy()
kv_chon = kv_chon or kv_opts
else:
kv_chon = []
df_f2 = df_f1.copy()

kh_pool = sorted([x for x in df_f2[‘Ten khach hang’].unique() if x not in (’’, ‘nan’, ‘None’)])
if not kh_pool:
st.error(‘Khong co khach hang. Mo rong bo loc.’)
st.stop()

if not risk_table.empty:
rt = risk_table.set_index(‘Ten_KH’)[[‘Diem’,‘Muc’]].to_dict(‘index’)
kh_sorted  = sorted(kh_pool, key=lambda k: rt.get(k, {}).get(‘Diem’, 0))
kh_display = [’[{}pt-{}] {}’.format(rt.get(k,{}).get(‘Diem’,0), rt.get(k,{}).get(‘Muc’,’?’), k) for k in kh_sorted]
else:
kh_sorted  = kh_pool
kh_display = kh_pool

d2n    = dict(zip(kh_display, kh_sorted))
sel    = st.sidebar.selectbox(‘3. Khach hang (rui ro: thap -> cao)’, kh_display)
kh_sel = d2n.get(sel, kh_sorted[0])

quy_all  = sorted(df_f2[‘Quy’].dropna().unique().tolist())
quy_chon = st.sidebar.multiselect(‘4. Quy’, quy_all, default=quy_all)
quy_chon = quy_chon or quy_all

df_kh  = df_all[(df_all[‘Ten khach hang’] == kh_sel) & (df_all[‘Quy’].isin(quy_chon))].copy()
df_ban = df_kh[df_kh[‘Loai_GD’] == ‘Xuat ban’].copy()
df_tra = df_kh[df_kh[‘Loai_GD’] == ‘Tra hang’].copy()
df_bs  = df_kh[df_kh[‘Loai_GD’] == ‘Xuat bo sung’].copy()

sc_kh = 0
lv_kh = ‘?’
cl_kh = ‘#26c281’
if not risk_table.empty and kh_sel in risk_table[‘Ten_KH’].values:
row_kh = risk_table[risk_table[‘Ten_KH’] == kh_sel].iloc[0]
sc_kh  = int(row_kh[‘Diem’])
lv_kh  = row_kh[‘Muc’]
cl_kh  = risk_color(sc_kh)

d_min  = df_kh[‘Ngay chung tu’].min() if not df_kh.empty else None
d_max  = df_kh[‘Ngay chung tu’].max() if not df_kh.empty else None
ds     = ‘{} - {}’.format(
d_min.strftime(’%d/%m/%Y’) if pd.notna(d_min) else ‘?’,
d_max.strftime(’%d/%m/%Y’) if pd.notna(d_max) else ‘?’
)
nhom_h = risk_table[risk_table[‘Ten_KH’]==kh_sel][‘Ten_nhom_KH’].values[0] if (not risk_table.empty and kh_sel in risk_table[‘Ten_KH’].values) else ‘’
kv_h   = risk_table[risk_table[‘Ten_KH’]==kh_sel][‘Khu_vuc’].values[0]    if (not risk_table.empty and kh_sel in risk_table[‘Ten_KH’].values) else ‘’
n_ct   = df_kh[‘So chung tu’].nunique() if ‘So chung tu’ in df_kh.columns else len(df_kh)

st.markdown(’<h2>{}</h2>’.format(kh_sel), unsafe_allow_html=True)
st.markdown(
‘<p style="color:#9aa0b0">{} | PKD: {} | KV: {} | {} dong’
’ <span style="background:{};color:#fff;padding:2px 10px;border-radius:10px;font-weight:700;">’
‘{}pt - {}</span></p>’.format(ds, nhom_h or ‘?’, kv_h or ‘?’, len(df_kh), cl_kh, sc_kh, lv_kh),
unsafe_allow_html=True
)

if df_ban.empty:
st.warning(‘Khong co du lieu xuat ban.’)
st.stop()

tb_dt = df_ban[‘Thanh tien ban’].sum()
tb_ln = df_ban[‘Loi nhuan’].sum()
tb_kl = df_ban[‘Khoi luong’].sum() / 1000
bien  = (tb_ln / tb_dt * 100) if tb_dt else 0
kpi_c = st.columns(5)
kpi_c[0].metric(‘DT (VND)’,   ‘{:,.0f}’.format(tb_dt))
kpi_c[1].metric(‘Loi nhuan’, ‘{:,.0f}’.format(tb_ln))
kpi_c[2].metric(‘Bien LN’,   ‘{:.1f}%’.format(bien))
kpi_c[3].metric(‘KL (tan)’,  ‘{:,.1f}’.format(tb_kl))
kpi_c[4].metric(‘CT / SP’,   ‘{} / {}’.format(n_ct, df_ban[‘Ten hang’].nunique() if ‘Ten hang’ in df_ban.columns else 0))

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
‘San pham’, ‘Doanh thu’, ‘Loi nhuan’, ‘Giao hang’,
‘Tan suat’, ‘Rui ro & BCCN’, ‘Xep hang rui ro’
])

with tab1:
st.markdown(’<div class="section-title">Co cau san pham</div>’, unsafe_allow_html=True)
df_nhom = (
df_ban.groupby(‘Nhom_SP’)
.agg(So_lan=(‘Nhom_SP’,‘count’),
KL_tan=(‘Khoi luong’, lambda x: round(x.sum()/1000, 2)),
DT=(‘Thanh tien ban’,‘sum’))
.reset_index().sort_values(‘DT’, ascending=False)
)
df_nhom = df_nhom[df_nhom[‘DT’] > 0]
if not df_nhom.empty:
c1, c2 = st.columns(2)
with c1:
fig = px.bar(df_nhom, x=‘Nhom_SP’, y=‘DT’, color=‘Nhom_SP’, text_auto=’.3s’,
title=‘DT theo nhom SP’, labels={‘DT’:‘DT (VND)’,‘Nhom_SP’:’’})
fig.update_layout(showlegend=False, height=360)
st.plotly_chart(fig, use_container_width=True)
with c2:
fig2 = px.pie(df_nhom, names=‘Nhom_SP’, values=‘So_lan’,
title=‘Ty trong so lan mua’, hole=0.45)
fig2.update_layout(height=360)
st.plotly_chart(fig2, use_container_width=True)
if ‘Ten hang’ in df_ban.columns:
st.markdown(’<div class="section-title">Top 15 san pham</div>’, unsafe_allow_html=True)
df_top = (
df_ban.groupby(‘Ten hang’)
.agg(So_lan=(‘Ten hang’,‘count’),
KL_tan=(‘Khoi luong’, lambda x: round(x.sum()/1000, 2)),
SL=(‘So luong’,‘sum’), DT=(‘Thanh tien ban’,‘sum’))
.reset_index().sort_values(‘DT’, ascending=False).head(15)
)
df_top[‘DT’] = df_top[‘DT’].map(’{:,.0f}’.format)
df_top.columns = [‘San pham’,‘So lan’,‘KL (tan)’,‘SL’,‘DT (VND)’]
st.dataframe(df_top, use_container_width=True, hide_index=True)
nhom_set = set(df_nhom[‘Nhom_SP’].tolist()) if not df_nhom.empty else set()
notes = {
‘Ong HDPE’:        ‘Ong HDPE (lon): Du an ha tang, cap thoat nuoc.’,
‘Ong PVC nuoc’:    ‘Ong PVC nuoc: Xay dung dan dung, cong nghiep.’,
‘Ong PVC bom cat’: ‘Ong PVC bom cat: Thuy loi, nong nghiep.’,
‘Ong PPR’:         ‘Ong PPR: He thong nuoc nong/lanh noi that.’,
‘Loi PVC’:         ‘Loi PVC: KH co the la dai ly hoac nha SX thu cap.’,
‘Phu kien & Keo’:  ‘Phu kien & Keo: Tu thi cong hoac ban lai tron goi.’,
}
shown = False
for k, v in notes.items():
if k in nhom_set:
st.markdown(’<div class="risk-low">{}</div>’.format(v), unsafe_allow_html=True)
shown = True
if not shown:
st.info(‘Khong du du lieu.’)

with tab2:
st.markdown(’<div class="section-title">Bien dong DT theo thang</div>’, unsafe_allow_html=True)
ct_c = ‘So chung tu’ if ‘So chung tu’ in df_ban.columns else ‘Thanh tien ban’
df_m = (
df_ban.groupby(‘Thang’)
.agg(DT=(‘Thanh tien ban’,‘sum’),
KL=(‘Khoi luong’, lambda x: round(x.sum()/1000, 3)),
SL=(‘So luong’,‘sum’), So_CT=(ct_c,‘nunique’))
.reset_index().sort_values(‘Thang’)
)
fig_t = make_subplots(rows=2, cols=1, shared_xaxes=True,
subplot_titles=[‘DT (VND) & KL (tan)’, ‘SL & So chung tu’],
vertical_spacing=0.14)
fig_t.add_trace(go.Bar(x=df_m[‘Thang’], y=df_m[‘DT’], name=‘DT’,
marker_color=’#4e79d4’, opacity=0.85), row=1, col=1)
fig_t.add_trace(go.Scatter(x=df_m[‘Thang’], y=df_m[‘KL’], name=‘KL’,
mode=‘lines+markers’, line=dict(color=’#f0a500’,width=2),
marker=dict(size=7)), row=1, col=1)
fig_t.add_trace(go.Bar(x=df_m[‘Thang’], y=df_m[‘SL’], name=‘SL’,
marker_color=’#26c281’, opacity=0.85), row=2, col=1)
fig_t.add_trace(go.Scatter(x=df_m[‘Thang’], y=df_m[‘So_CT’], name=‘So CT’,
mode=‘lines+markers’, line=dict(color=’#e74c3c’,width=2),
marker=dict(size=7)), row=2, col=1)
fig_t.update_layout(height=520, legend=dict(orientation=‘h’, y=-0.12))
st.plotly_chart(fig_t, use_container_width=True)
df_ms = df_m.copy()
df_ms[‘DT’] = df_ms[‘DT’].map(’{:,.0f}’.format)
df_ms.columns = [‘Thang’,‘DT (VND)’,‘KL (tan)’,‘SL’,‘So CT’]
st.dataframe(df_ms, use_container_width=True, hide_index=True)
st.markdown(’<div class="section-title">Tong hop theo Quy</div>’, unsafe_allow_html=True)
df_q = (
df_ban.groupby(‘Quy’)
.agg(DT=(‘Thanh tien ban’,‘sum’),
KL=(‘Khoi luong’, lambda x: round(x.sum()/1000, 2)),
LN=(‘Loi nhuan’,‘sum’), So_CT=(ct_c,‘nunique’))
.reset_index()
)
df_q[‘Bien (%)’] = (df_q[‘LN’] / df_q[‘DT’].replace(0, float(‘nan’)) * 100).round(1).fillna(0)
df_qs = df_q.copy()
df_qs[‘DT’] = df_qs[‘DT’].map(’{:,.0f}’.format)
df_qs[‘LN’] = df_qs[‘LN’].map(’{:,.0f}’.format)
df_qs.columns = [‘Quy’,‘DT (VND)’,‘KL (tan)’,‘LN (VND)’,‘So CT’,‘Bien LN (%)’]
st.dataframe(df_qs, use_container_width=True, hide_index=True)

with tab3:
st.markdown(’<div class="section-title">Bien dong loi nhuan & phat hien chinh sach</div>’, unsafe_allow_html=True)
df_ln = (
df_ban.groupby(‘Thang’)
.agg(DT=(‘Thanh tien ban’,‘sum’), Von=(‘Thanh tien von’,‘sum’), LN=(‘Loi nhuan’,‘sum’))
.reset_index().sort_values(‘Thang’)
)
df_ln[‘Bien’] = (df_ln[‘LN’] / df_ln[‘DT’].replace(0, float(‘nan’)) * 100).round(2).fillna(0)
fig_ln = make_subplots(rows=2, cols=1, shared_xaxes=True,
subplot_titles=[‘DT / Von / LN (VND)’, ‘Bien loi nhuan (%)’],
vertical_spacing=0.14)
fig_ln.add_trace(go.Bar(x=df_ln[‘Thang’], y=df_ln[‘DT’], name=‘DT’, marker_color=’#4e79d4’), row=1, col=1)
fig_ln.add_trace(go.Bar(x=df_ln[‘Thang’], y=df_ln[‘Von’], name=‘Von’, marker_color=’#e05c5c’), row=1, col=1)
fig_ln.add_trace(go.Scatter(x=df_ln[‘Thang’], y=df_ln[‘LN’], name=‘LN’,
mode=‘lines+markers’, line=dict(color=’#26c281’,width=2),
marker=dict(size=7)), row=1, col=1)
fig_ln.add_trace(go.Scatter(x=df_ln[‘Thang’], y=df_ln[‘Bien’], name=‘Bien LN’,
mode=‘lines+markers+text’,
text=[’{:.1f}%’.format(v) for v in df_ln[‘Bien’]],
textposition=‘top center’,
line=dict(color=’#f0a500’,width=2), marker=dict(size=7)), row=2, col=1)
fig_ln.update_layout(height=520, barmode=‘group’)
st.plotly_chart(fig_ln, use_container_width=True)
if len(df_ln) >= 2:
mb  = df_ln[‘Bien’].mean()
sdb = max(float(df_ln[‘Bien’].std()), 1.0)
an  = df_ln[df_ln[‘Bien’] < mb - sdb]
st.markdown(’<div class="section-title">Thang nghi co chiet khau bat thuong</div>’, unsafe_allow_html=True)
if not an.empty:
for _, r in an.iterrows():
st.markdown(
‘<div class="risk-medium">Thang <b>{}</b>: Bien LN=<b>{:.1f}%</b> (TB={:.1f}%)</div>’.format(
r[‘Thang’], r[‘Bien’], mb), unsafe_allow_html=True)
else:
st.markdown(’<div class="risk-low">Khong phat hien bat thuong.</div>’, unsafe_allow_html=True)
if not df_tra.empty:
st.markdown(’<div class="section-title">Don hang tra lai</div>’, unsafe_allow_html=True)
tra_c = [c for c in [‘So chung tu’,‘Ngay chung tu’,‘Ten hang’,‘Khoi luong’,‘Thanh tien ban’,‘Ghi chu’] if c in df_tra.columns]
df_tra_s = df_tra[tra_c].copy()
if ‘Thanh tien ban’ in df_tra_s.columns:
df_tra_s[‘Thanh tien ban’] = df_tra_s[‘Thanh tien ban’].map(’{:,.0f}’.format)
st.dataframe(df_tra_s, use_container_width=True, hide_index=True)
st.error(‘Tong GT tra hang: {:,.0f} VND’.format(abs(df_tra[‘Thanh tien ban’].sum())))
with st.expander(‘Chi tiet gia ban’):
sh2 = [c for c in [‘So chung tu’,‘Ngay chung tu’,‘Ten hang’,‘Gia ban’,‘Thanh tien ban’,‘Loi nhuan’,‘Ghi chu’] if c in df_ban.columns]
st.dataframe(df_ban[sh2].sort_values(‘Ngay chung tu’), use_container_width=True, hide_index=True)

with tab4:
st.markdown(’<div class="section-title">Hinh thuc & dia diem giao hang</div>’, unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
if ‘Freight Terms’ in df_ban.columns:
ft = df_ban[‘Freight Terms’].value_counts().reset_index()
ft.columns = [‘Hinh thuc’,‘So lan’]
st.plotly_chart(px.pie(ft, names=‘Hinh thuc’, values=‘So lan’, title=‘Dieu kien giao hang’, hole=0.4), use_container_width=True)
else:
st.info(‘Khong co du lieu Freight Terms.’)
with c2:
if ‘Shipping method’ in df_ban.columns:
sm = df_ban[‘Shipping method’].value_counts().reset_index()
sm.columns = [‘Phuong tien’,‘So lan’]
st.plotly_chart(px.pie(sm, names=‘Phuong tien’, values=‘So lan’, title=‘Phuong tien van chuyen’, hole=0.4), use_container_width=True)
else:
st.info(‘Khong co du lieu Shipping method.’)
if ‘Noi giao hang’ in df_ban.columns:
st.markdown(’<div class="section-title">Dia diem giao hang</div>’, unsafe_allow_html=True)
df_noi = (
df_ban.groupby(‘Noi giao hang’)
.agg(So_lan=(‘Noi giao hang’,‘count’),
KL=(‘Khoi luong’, lambda x: round(x.sum()/1000, 2)),
DT=(‘Thanh tien ban’,‘sum’))
.reset_index().sort_values(‘DT’, ascending=False)
)
df_noi[‘DT’] = df_noi[‘DT’].map(’{:,.0f}’.format)
df_noi.columns = [‘Dia diem’,‘So lan’,‘KL (tan)’,‘DT (VND)’]
st.dataframe(df_noi, use_container_width=True, hide_index=True)
with st.expander(‘Danh sach xe & tai xe’):
xe_c = [c for c in [‘Bien so xe’,‘Tai Xe’,‘Ten DVVC’,‘Shipping method’,‘Ngay chung tu’,‘Noi giao hang’] if c in df_ban.columns]
if xe_c:
st.dataframe(df_ban[xe_c].drop_duplicates(), use_container_width=True, hide_index=True)
else:
st.info(‘Khong co du lieu xe/tai xe.’)

with tab5:
st.markdown(’<div class="section-title">Heatmap tan suat: San pham x Thang</div>’, unsafe_allow_html=True)
if ‘Ten hang’ in df_ban.columns:
df_freq = df_ban.groupby([‘Ten hang’,‘Thang’]).size().reset_index(name=‘So_lan’)
if not df_freq.empty:
df_piv = df_freq.pivot(index=‘Ten hang’, columns=‘Thang’, values=‘So_lan’).fillna(0)
top_n  = df_piv.sum(axis=1).nlargest(min(20, len(df_piv))).index
fig_hm = px.imshow(df_piv.loc[top_n],
labels=dict(x=‘Thang’, y=‘San pham’, color=‘So lan’),
title=‘Top SP x Thang’, color_continuous_scale=‘Blues’, aspect=‘auto’)
fig_hm.update_layout(height=max(380, len(top_n)*24))
st.plotly_chart(fig_hm, use_container_width=True)
for qv in sorted(df_ban[‘Quy’].dropna().unique()):
dq = df_ban[df_ban[‘Quy’] == qv]
ms = ‘, ‘.join(sorted(dq[‘Thang’].dropna().unique()))
with st.expander(’{} | {}’.format(qv, ms)):
ag = (
dq.groupby([‘Ten hang’,‘Thang’])
.agg(So_lan=(‘Ten hang’,‘count’),
KL=(‘Khoi luong’, lambda x: round(x.sum()/1000,2)),
DT=(‘Thanh tien ban’,‘sum’))
.reset_index().sort_values(‘DT’, ascending=False)
)
ag[‘DT’] = ag[‘DT’].map(’{:,.0f}’.format)
ag.columns = [‘San pham’,‘Thang’,‘So lan’,‘KL (tan)’,‘DT (VND)’]
st.dataframe(ag, use_container_width=True, hide_index=True)
else:
st.info(‘Khong co du lieu Ten hang.’)

with tab6:
st.markdown(’<div class="section-title">BCCN - Phan tich thanh toan & cong no</div>’, unsafe_allow_html=True)
gc_s  = df_kh[‘Ghi chu’].astype(str).str.upper() if ‘Ghi chu’ in df_kh.columns else pd.Series(’’, index=df_kh.index)
df_po = df_kh[gc_s.str.contains(r’PO|B[0-9]{3}|HOP DONG’, regex=True, na=False)]
ct_c2 = ‘So chung tu’ if ‘So chung tu’ in df_kh.columns else ‘Thanh tien ban’
mc = st.columns(4)
mc[0].metric(‘Don PO/HD’,      df_po[ct_c2].nunique()  if not df_po.empty  else 0)
mc[1].metric(‘Phieu tra hang’, df_tra[ct_c2].nunique() if not df_tra.empty else 0)
mc[2].metric(‘Xuat bo sung’,   df_bs[ct_c2].nunique()  if not df_bs.empty  else 0)
mc[3].metric(‘GT tra hang VND’,’{:,.0f}’.format(abs(df_tra[‘Thanh tien ban’].sum()) if not df_tra.empty else 0))
st.markdown(’’’

<div class="info-box">
<b>File OM_RPT_055 khong co ngay thanh toan thuc te.</b><br>
Can bo sung: So AR Aging, Lich su thanh toan.<br>
Dau hieu: Ghi chu B-xxx/PO = don du an = TT cham NET30-90 | Tra hang = tranh chap.
</div>''', unsafe_allow_html=True)
    if not df_po.empty:
        with st.expander('{} don co PO'.format(len(df_po))):
            po_c = [c for c in ['So chung tu','Ngay chung tu','Ten hang','Thanh tien ban','Ghi chu'] if c in df_po.columns]
            df_po_s = df_po[po_c].drop_duplicates().copy()
            if 'Thanh tien ban' in df_po_s.columns:
                df_po_s['Thanh tien ban'] = df_po_s['Thanh tien ban'].map('{:,.0f}'.format)
            st.dataframe(df_po_s, use_container_width=True, hide_index=True)
    st.markdown('<div class="section-title">Danh gia rui ro</div>', unsafe_allow_html=True)
    risks  = []
    score  = sc_kh
    tt_ban = df_ban['Thanh tien ban'].sum()
    tt_tra = abs(df_tra['Thanh tien ban'].sum()) if not df_tra.empty else 0
    tl_tra = (tt_tra / tt_ban * 100) if tt_ban > 0 else 0
    tt_ln  = df_ban['Loi nhuan'].sum()
    bien   = (tt_ln  / tt_ban * 100) if tt_ban > 0 else 0
    if tl_tra > 10:
        risks.append(('high',   'Ty le hang tra: <b>{:.1f}%</b> ({:,.0f} VND) - rui ro cao'.format(tl_tra, tt_tra)))
    elif tl_tra > 3:
        risks.append(('medium', 'Ty le hang tra: <b>{:.1f}%</b> - can theo doi'.format(tl_tra)))
    else:
        risks.append(('low',    'Ty le tra hang thap: {:.1f}%'.format(tl_tra)))
    if bien < 5:
        risks.append(('high',   'Bien LN rat thap: <b>{:.1f}%</b>'.format(bien)))
    elif bien < 15:
        risks.append(('medium', 'Bien LN o muc thap: <b>{:.1f}%</b>'.format(bien)))
    else:
        risks.append(('low',    'Bien LN binh thuong: {:.1f}%'.format(bien)))
    if not df_bs.empty:
        risks.append(('medium', 'Co <b>{}</b> dong xuat bo sung'.format(len(df_bs))))
    else:
        risks.append(('low', 'Khong co don xuat bo sung.'))
    if len(df_ban) > 4:
        q75 = df_ban['Thanh tien ban'].quantile(0.75)
        q25 = df_ban['Thanh tien ban'].quantile(0.25)
        iqr = q75 - q25
        if iqr > 0:
            outs = df_ban[df_ban['Thanh tien ban'] > q75 + 3*iqr]
            if not outs.empty:
                risks.append(('medium', 'Co <b>{}</b> don hang gia tri rat lon'.format(len(outs))))
            else:
                risks.append(('low', 'Khong co don hang gia tri bat thuong.'))
    if 'Noi giao hang' in df_ban.columns:
        n_noi = df_ban['Noi giao hang'].nunique()
        if n_noi >= 5:
            risks.append(('medium', 'Giao hang toi <b>{}</b> dia diem'.format(n_noi)))
        else:
            risks.append(('low', 'So dia diem: {} (binh thuong)'.format(n_noi)))
    n_thang = df_ban['Thang'].nunique()
    dd_d    = (df_ban['Ngay chung tu'].max() - df_ban['Ngay chung tu'].min()).days
    n_range = max(dd_d // 30, 1)
    if n_thang / n_range < 0.5:
        risks.append(('medium', 'Mua chi <b>{}/{}</b> thang - khong deu'.format(n_thang, n_range)))
    else:
        risks.append(('low', 'Mua deu: {}/{} thang co GD'.format(n_thang, n_range)))
    sc2 = risk_color(score)
    sl2 = 'RUI RO CAO' if score >= 50 else ('RUI RO TRUNG BINH' if score >= 25 else 'RUI RO THAP')
    st.markdown(
        '<div style="background:#1a2035;border-radius:10px;padding:20px;text-align:center;margin:12px 0;">'
        '<div style="font-size:32px;font-weight:900;color:{};"> {}</div>'
        '<div style="font-size:16px;color:#9aa0b0;margin-top:6px;">'
        'Diem rui ro: <b style="color:{}">{}/100</b></div></div>'.format(sc2, sl2, sc2, score),
        unsafe_allow_html=True
    )
    pct = min(score, 100)
    st.markdown(
        '<div style="background:#21262d;border-radius:6px;height:8px;margin:-8px 0 18px 0;overflow:hidden;">'
        '<div style="background:{};width:{}%;height:100%;border-radius:6px;"></div></div>'.format(sc2, pct),
        unsafe_allow_html=True
    )
    for lvl, msg in risks:
        st.markdown('<div class="risk-{}">{}</div>'.format(lvl, msg), unsafe_allow_html=True)

with tab7:
st.markdown(’<div class="section-title">Bang xep hang rui ro (thap -> cao)</div>’, unsafe_allow_html=True)
if risk_table.empty:
st.info(‘Chua co du lieu.’)
else:
rt_f = risk_table.copy()
if nhom_chon:
rt_f = rt_f[rt_f[‘Ten_nhom_KH’].isin(nhom_chon)]
if kv_chon:
rt_f = rt_f[rt_f[‘Khu_vuc’].isin(kv_chon)]
rt_s = rt_f.sort_values(‘Diem’, ascending=True).reset_index(drop=True)
rt_s.index += 1
colors_b = [risk_color(s) for s in rt_s[‘Diem’]]
fig_r = go.Figure(go.Bar(
y=rt_s[‘Ten_KH’], x=rt_s[‘Diem’], orientation=‘h’,
marker=dict(color=colors_b),
text=rt_s[‘Diem’].astype(str), textposition=‘outside’,
textfont=dict(color=’#c9d1d9’, size=11)
))
fig_r.update_layout(
paper_bgcolor=’#0d1117’, plot_bgcolor=’#0d1117’,
font=dict(color=’#c9d1d9’, size=11), title=‘Diem rui ro KH (thap den cao)’,
height=max(400, len(rt_s)*32), margin=dict(l=10, r=10, t=45, b=10),
xaxis=dict(gridcolor=’#21262d’, range=[0, 110]),
)
fig_r.update_yaxes(gridcolor=’#21262d’, tickfont=dict(size=10))
st.plotly_chart(fig_r, use_container_width=True)
if rt_s[‘Ten_nhom_KH’].ne(’’).any():
st.markdown(’<div class="section-title">Tong hop theo Phong KD</div>’, unsafe_allow_html=True)
g1 = (
rt_s.groupby(‘Ten_nhom_KH’)
.agg(So_KH=(‘Ten_KH’,‘count’), Diem_TB=(‘Diem’,‘mean’), Diem_Max=(‘Diem’,‘max’))
.reset_index().sort_values(‘Diem_Max’, ascending=False)
)
g1[‘Diem_TB’] = g1[‘Diem_TB’].round(1)
g1.columns = [‘Phong KD’,‘So KH’,‘Diem TB’,‘Diem Max’]
st.dataframe(g1, use_container_width=True, hide_index=True)
if rt_s[‘Khu_vuc’].ne(’’).any():
st.markdown(’<div class="section-title">Tong hop theo Khu vuc</div>’, unsafe_allow_html=True)
g2 = (
rt_s.groupby(‘Khu_vuc’)
.agg(So_KH=(‘Ten_KH’,‘count’), Diem_TB=(‘Diem’,‘mean’), Diem_Max=(‘Diem’,‘max’))
.reset_index().sort_values(‘Diem_Max’, ascending=False)
)
g2[‘Diem_TB’] = g2[‘Diem_TB’].round(1)
g2.columns = [‘Khu vuc’,‘So KH’,‘Diem TB’,‘Diem Max’]
st.dataframe(g2, use_container_width=True, hide_index=True)
st.dataframe(
rt_s[[‘Ten_KH’,‘Ten_nhom_KH’,‘Khu_vuc’,‘Diem’,‘Muc’]],
use_container_width=True
)