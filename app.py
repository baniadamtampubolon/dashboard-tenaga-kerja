import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data, get_geo_structure, filter_data

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Ketenagakerjaan | Kemnaker RI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Sidebar: Logo + Config ─────────────────────────────────────────────────────
with st.sidebar:
    st.image("kemnaker-logo.png", use_container_width=True)
    st.markdown("### ⚙️ Konfigurasi Dashboard")
    dataset_choice = st.radio(
        "Pilih Dataset",
        ["Ringkasan Eksekutif (Semua Data)",
         "Penduduk Usia Kerja (PUK)",
         "Angkatan Kerja (AK)",
         "Pengangguran Terbuka (PT)",
         "Penduduk yang Bekerja (PYB)"],
    )
    theme_choice = st.radio("Mode Tampilan", ["Terang ☀️", "Gelap 🌙"], horizontal=True)

# ─── Data Source Setup ───────────────────────────────────────────────────────────
is_main = "Ringkasan" in dataset_choice
is_puk  = "PUK" in dataset_choice
is_ak   = "AK"  in dataset_choice
is_pt   = "PT"  in dataset_choice
is_pyb  = "PYB" in dataset_choice

if is_main:
    df_puk = load_data("Database/PUK-2018-2025-ver2.xlsx")
    df_ak  = load_data("Database/AK-2018-2025.xlsx")
    df_pt  = load_data("Database/PT-2018-2025.xlsx")
    df_pyb = load_data("Database/PYB-2018-2025.xlsx")
    df = df_puk
else:
    if is_puk:   DATA_FILE = "Database/PUK-2018-2025-ver2.xlsx"
    elif is_ak:  DATA_FILE = "Database/AK-2018-2025.xlsx"
    elif is_pt:  DATA_FILE = "Database/PT-2018-2025.xlsx"
    else:        DATA_FILE = "Database/PYB-2018-2025.xlsx"
    df = load_data(DATA_FILE)

geo_structure = get_geo_structure(df)

# ─── Theme Palette ───────────────────────────────────────────────────────────────
is_dark = "Gelap" in theme_choice

if not is_dark:
    main_bg        = "#F0F4F8"
    card_bg        = "#FFFFFF"
    card_border    = "rgba(0, 74, 139, 0.08)"
    sidebar_bg     = "linear-gradient(180deg, #003D73 0%, #005BAB 100%)"
    header_color   = "#003D73"
    subtext_color  = "#64748B"
    text_color     = "#1E293B"
    divider_color  = "rgba(0, 74, 139, 0.12)"
    plotly_tpl     = "plotly_white"
    chart_bg       = "rgba(0,0,0,0)"
    grid_color     = "rgba(0,0,0,0.06)"
    font_color     = "#1E293B"
else:
    main_bg        = "#0F172A"
    card_bg        = "#1E293B"
    card_border    = "rgba(139, 181, 232, 0.12)"
    sidebar_bg     = "linear-gradient(180deg, #0B1628 0%, #132744 100%)"
    header_color   = "#93C5FD"
    subtext_color  = "#94A3B8"
    text_color     = "#E2E8F0"
    divider_color  = "rgba(139, 181, 232, 0.15)"
    plotly_tpl     = "plotly_dark"
    chart_bg       = "rgba(0,0,0,0)"
    grid_color     = "rgba(255,255,255,0.06)"
    font_color     = "#E2E8F0"

# ─── Kemnaker Blue Palette (reusable) ────────────────────────────────────────────
BLUE_SEQ     = ['#002B55', '#003D73', '#005BAB', '#2E86DE', '#5DADE2', '#85C1E9', '#AED6F1']
ACCENT_RED   = '#E74C3C'
ACCENT_AMBER = '#F39C12'

# ─── Global Chart Config ────────────────────────────────────────────────────────
BAR_RADIUS = 8  # Rounded corner radius for bar charts

CHART_LAYOUT = dict(
    template       = plotly_tpl,
    paper_bgcolor  = chart_bg,
    plot_bgcolor   = chart_bg,
    font           = dict(family="Inter, sans-serif", color=font_color, size=12),
    margin         = dict(l=20, r=20, t=50, b=20),
    hoverlabel     = dict(bgcolor=card_bg, font_size=12, font_family="Inter, sans-serif"),
    xaxis          = dict(gridcolor=grid_color, showline=False),
    yaxis          = dict(gridcolor=grid_color, showline=False),
    legend         = dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5,
                          bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    barcornerradius = BAR_RADIUS,
)

def apply_chart(fig, height=None):
    """Apply global layout to any figure."""
    kw = dict(CHART_LAYOUT)
    if height:
        kw['height'] = height
    fig.update_layout(**kw)
    return fig

# ─── Inject CSS ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
/* ── Base ────────────────────────── */
.stApp {{
    background-color: {main_bg};
    font-family: 'Inter', sans-serif;
}}
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {text_color};
}}

/* ── Sidebar ─────────────────────── */
div[data-testid="stSidebar"] {{
    background: {sidebar_bg};
}}
div[data-testid="stSidebar"] * {{
    color: #FFFFFF !important;
}}
div[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.15) !important;
}}

/* ── Metric Cards ────────────────── */
div[data-testid="stMetric"] {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 12px;
    padding: 20px 16px 16px;
    border-left: 4px solid #005BAB;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
div[data-testid="stMetric"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,74,139,0.12);
}}
div[data-testid="stMetric"] label {{
    color: {subtext_color} !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {text_color} !important;
    font-weight: 700 !important;
    font-size: 1.5rem !important;
}}

/* ── Section Headers ─────────────── */
.section-header {{
    font-size: 1.35rem;
    font-weight: 700;
    color: {header_color};
    margin: 32px 0 8px 0;
    padding: 0;
    letter-spacing: -0.3px;
}}
.section-sub {{
    font-size: 0.85rem;
    color: {subtext_color};
    margin: 0 0 24px 0;
    font-weight: 400;
}}
.section-divider {{
    border: none;
    border-top: 1px solid {divider_color};
    margin: 28px 0;
}}

/* ── General text ────────────────── */
p, span, div {{
    color: {text_color};
}}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar: Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🗺️ Filter Wilayah")
    selected_year = st.selectbox("Pilih Tahun", sorted(df['thn'].unique(), reverse=True))
    level_options = ["Nasional", "Provinsi", "Kabupaten/Kota"]
    selected_level = st.radio("Tingkat Wilayah", level_options)
    selected_prov = None
    selected_kabkot = None
    if selected_level in ["Provinsi", "Kabupaten/Kota"]:
        selected_prov = st.selectbox("Pilih Provinsi", sorted(geo_structure.keys()))
        if selected_level == "Kabupaten/Kota":
            selected_kabkot = st.selectbox("Pilih Kabupaten/Kota", geo_structure[selected_prov])

# ─── Resolve Location Name ──────────────────────────────────────────────────────
loc_name = "Indonesia"
if selected_level == "Provinsi": loc_name = selected_prov
if selected_level == "Kabupaten/Kota": loc_name = selected_kabkot

# ─── Apply Filters ───────────────────────────────────────────────────────────────
if is_main:
    data_puk = filter_data(df_puk, selected_year, selected_level, selected_prov, selected_kabkot)
    data_ak  = filter_data(df_ak,  selected_year, selected_level, selected_prov, selected_kabkot)
    data_pt  = filter_data(df_pt,  selected_year, selected_level, selected_prov, selected_kabkot)
    data_pyb = filter_data(df_pyb, selected_year, selected_level, selected_prov, selected_kabkot)
    data = data_puk
else:
    data = filter_data(df, selected_year, selected_level, selected_prov, selected_kabkot)

if data.empty:
    st.warning("⚠️ Data tidak ditemukan untuk filter yang dipilih.")
    st.stop()

# ─── Header ──────────────────────────────────────────────────────────────────────
dataset_labels = {
    "main": "Ringkasan Data Ketenagakerjaan",
    "puk":  "Penduduk Usia Kerja (PUK)",
    "ak":   "Angkatan Kerja (AK)",
    "pt":   "Pengangguran Terbuka (PT)",
    "pyb":  "Penduduk yang Bekerja (PYB)",
}
active_label = "main" if is_main else ("puk" if is_puk else ("ak" if is_ak else ("pt" if is_pt else "pyb")))

st.markdown(f"<div class='section-header'>{dataset_labels[active_label]}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-sub'>📍 {loc_name} &nbsp;·&nbsp; 📅 Tahun {selected_year}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD (Ringkasan Eksekutif)
# ═══════════════════════════════════════════════════════════════════════════════════
if is_main:
    # ── KPI Cards ────────────────────────────────────────────────────────────────
    v_puk = data_puk['total'].sum()
    v_ak  = data_ak['total'].sum()
    v_pyb = data_pyb['total'].sum()
    v_pt  = data_pt['total'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Penduduk Usia Kerja", f"{v_puk:,.0f}")
    col2.metric("Angkatan Kerja", f"{v_ak:,.0f}")
    col3.metric("Penduduk Bekerja", f"{v_pyb:,.0f}")
    col4.metric("Pengangguran Terbuka", f"{v_pt:,.0f}")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Composition Funnels ──────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        bak = max(0, v_puk - v_ak)
        fig = px.pie(
            pd.DataFrame({'Kategori': ['Angkatan Kerja', 'Bukan Angkatan Kerja'], 'Jumlah': [v_ak, bak]}),
            values='Jumlah', names='Kategori', hole=0.55,
            color_discrete_sequence=['#005BAB', '#AED6F1'],
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12,
                          hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<br>Proporsi: %{percent}<extra></extra>')
        apply_chart(fig)
        fig.update_layout(title=dict(text="Komposisi Penduduk Usia Kerja", font=dict(size=15)), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.pie(
            pd.DataFrame({'Kategori': ['Bekerja (PYB)', 'Menganggur (PT)'], 'Jumlah': [v_pyb, v_pt]}),
            values='Jumlah', names='Kategori', hole=0.55,
            color_discrete_sequence=['#2E86DE', ACCENT_RED],
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12,
                          hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<br>Proporsi: %{percent}<extra></extra>')
        apply_chart(fig)
        fig.update_layout(title=dict(text="Komposisi Angkatan Kerja", font=dict(size=15)), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Strength vs Challenge ────────────────────────────────────────────────────
    c3, c4 = st.columns(2)
    with c3:
        lapus_map = {
            'lapus_A': 'Pertanian & Perikanan', 'lapus_B': 'Pertambangan', 'lapus_C': 'Industri Pengolahan',
            'lapus_D': 'Listrik & Gas', 'lapus_E': 'Air & Limbah', 'lapus_F': 'Konstruksi',
            'lapus_G': 'Perdagangan', 'lapus_H': 'Transportasi', 'lapus_I': 'Akomodasi & F&B',
            'lapus_J': 'IT & Komunikasi', 'lapus_K': 'Keuangan', 'lapus_L': 'Real Estat',
            'lapus_MN': 'Jasa Profesional', 'lapus_O': 'Administrasi', 'lapus_P': 'Pendidikan',
            'lapus_Q': 'Kesehatan', 'lapus_RSTU': 'Jasa Lainnya',
        }
        vals = [data_pyb[c].sum() if c in data_pyb.columns else 0 for c in lapus_map.keys()]
        ldf = pd.DataFrame({'Sektor': list(lapus_map.values()), 'Jumlah': vals}).sort_values('Jumlah').tail(5)

        fig = px.bar(ldf, x='Jumlah', y='Sektor', orientation='h', text='Jumlah',
                     color_discrete_sequence=['#005BAB'])
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=11,
                          hovertemplate='<b>%{y}</b><br>Jumlah: %{x:,.0f}<extra></extra>')
        apply_chart(fig)
        fig.update_layout(title=dict(text="🏭 Top 5 Sektor Penyerap Tenaga Kerja", font=dict(size=14)),
                          xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        pt_map = {'kat_mp': 'Mencari Pekerjaan', 'kat_mu': 'Mempersiapkan Usaha',
                  'kat_pa': 'Putus Asa', 'kat_bmb': 'Diterima Belum Bekerja'}
        pt_vals = [data_pt[c].sum() if c in data_pt.columns else 0 for c in pt_map.keys()]
        ptdf = pd.DataFrame({'Kategori': list(pt_map.values()), 'Jumlah': pt_vals}).sort_values('Jumlah')

        fig = px.bar(ptdf, x='Jumlah', y='Kategori', orientation='h', text='Jumlah',
                     color_discrete_sequence=[ACCENT_RED])
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=11,
                          hovertemplate='<b>%{y}</b><br>Jumlah: %{x:,.0f}<extra></extra>')
        apply_chart(fig)
        fig.update_layout(title=dict(text="⚠️ Distribusi Kategori Pengangguran", font=dict(size=14)),
                          xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Master Trend ─────────────────────────────────────────────────────────────
    def _trend(d):
        if selected_level == "Nasional": return d[d['lvl_wil'] == 'nasional']
        elif selected_level == "Provinsi": return d[(d['lvl_wil'] == 'provinsi') & (d['nm_prov'] == selected_prov)]
        elif selected_level == "Kabupaten/Kota": return d[(d['lvl_wil'].isin(['kabupaten', 'kota'])) & (d['nm_kabkot'] == selected_kabkot)]
        return d

    t_puk = _trend(df_puk).groupby('thn')['total'].sum().reset_index()
    t_ak  = _trend(df_ak).groupby('thn')['total'].sum().reset_index()
    t_pyb = _trend(df_pyb).groupby('thn')['total'].sum().reset_index()
    t_pt  = _trend(df_pt).groupby('thn')['total'].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t_puk['thn'], y=t_puk['total'], name="PUK", line=dict(color='#AED6F1', width=2, dash='dot', shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=t_ak['thn'],  y=t_ak['total'],  name="AK",  line=dict(color='#5DADE2', width=2, dash='dot', shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=t_pyb['thn'], y=t_pyb['total'], name="Bekerja (PYB)", line=dict(color='#005BAB', width=3, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=6),
                             fill='tozeroy', fillcolor='rgba(0,91,171,0.08)'))
    fig.add_trace(go.Scatter(x=t_pt['thn'],  y=t_pt['total'],  name="Penganggur (PT)", line=dict(color=ACCENT_RED, width=2, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=5)))
    apply_chart(fig, height=420)
    fig.update_layout(title=dict(text=f"📈 Tren Ketenagakerjaan — {loc_name} (2018–2025)", font=dict(size=15)))
    st.plotly_chart(fig, use_container_width=True)

    # Footer
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:{subtext_color};font-size:0.8rem;'>Dashboard Ketenagakerjaan Nasional 2018–2025 · Kementerian Ketenagakerjaan RI</p>", unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════════
#  INDIVIDUAL DATASET DASHBOARDS
# ═══════════════════════════════════════════════════════════════════════════════════

total_val = data['total'].sum()

# ── KPI Cards ────────────────────────────────────────────────────────────────────
if is_puk:
    c1, c2, c3, c4 = st.columns(4)
    working    = data.get('keg_pyb', pd.Series([0])).sum()
    unemployed = data.get('keg_pt',  pd.Series([0])).sum()
    others     = data.get('keg_lain', pd.Series([0])).sum()
    c1.metric("Total PUK",            f"{total_val:,.0f}")
    c2.metric("Penduduk Bekerja",      f"{working:,.0f}")
    c3.metric("Pengangguran Terbuka",  f"{unemployed:,.0f}")
    c4.metric("Kegiatan Lainnya",      f"{others:,.0f}")
elif is_pt:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Pengangguran",      f"{total_val:,.0f}")
    c2.metric("Mencari Pekerjaan",       f"{data.get('kat_mp', pd.Series([0])).sum():,.0f}")
    c3.metric("Mempersiapkan Usaha",     f"{data.get('kat_mu', pd.Series([0])).sum():,.0f}")
    c4.metric("Putus Asa",              f"{data.get('kat_pa', pd.Series([0])).sum():,.0f}")
elif is_ak:
    c1, = st.columns(1)
    c1.metric("Total Angkatan Kerja", f"{total_val:,.0f}")
else:
    c1, = st.columns(1)
    c1.metric("Total Penduduk Bekerja", f"{total_val:,.0f}")

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Row 1: Age Profile (Area) + Education (Bar) ─────────────────────────────────
r1c1, r1c2 = st.columns(2)

with r1c1:
    age_cols = {
        'ku_1519': '15–19', 'ku_2024': '20–24', 'ku_2529': '25–29',
        'ku_3034': '30–34', 'ku_3539': '35–39', 'ku_4044': '40–44',
        'ku_4549': '45–49', 'ku_5054': '50–54', 'ku_5559': '55–59',
        'ku_6064': '60–64', 'ku_65+': '65+',
    }
    age_vals = [data[c].sum() for c in age_cols]
    adf = pd.DataFrame({'Usia': list(age_cols.values()), 'Jumlah': age_vals})

    fig = px.area(adf, x='Usia', y='Jumlah', markers=True, color_discrete_sequence=['#005BAB'])
    fig.update_traces(line_width=2.5, line_shape='spline', marker=dict(size=5),
                      fillcolor='rgba(0,91,171,0.12)',
                      hovertemplate='<b>%{x} tahun</b><br>Jumlah: %{y:,.0f}<extra></extra>')
    apply_chart(fig)
    fig.update_layout(title=dict(text="👤 Distribusi Kelompok Usia", font=dict(size=14)),
                      xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    edu_cols = {
        'pd_sd': 'SD', 'pd_smp': 'SMP', 'pd_smau': 'SMA',
        'pd_smak': 'SMK', 'pd_dipl': 'Diploma', 'pd_univ': 'Universitas',
    }
    edu_vals = [data[c].sum() if c in data.columns else 0 for c in edu_cols]
    edf = pd.DataFrame({'Pendidikan': list(edu_cols.values()), 'Jumlah': edu_vals})

    fig = px.bar(edf, x='Pendidikan', y='Jumlah', text='Jumlah',
                 color='Pendidikan', color_discrete_sequence=BLUE_SEQ)
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=10,
                      hovertemplate='<b>%{x}</b><br>Jumlah: %{y:,.0f}<extra></extra>')
    apply_chart(fig)
    fig.update_layout(title=dict(text="🎓 Tingkat Pendidikan", font=dict(size=14)),
                      showlegend=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Row 2: Gender + Context-specific chart ──────────────────────────────────────
if is_ak:
    r2c1, = st.columns(1)
else:
    r2c1, r2c2 = st.columns(2)

with r2c1:
    lk = data['jk_lk'].sum()
    pr = data['jk_pr'].sum()
    gdf = pd.DataFrame({'Gender': ['Laki-laki', 'Perempuan'], 'Jumlah': [lk, pr]})
    fig = px.pie(gdf, values='Jumlah', names='Gender', hole=0.55, color_discrete_sequence=['#003D73', '#5DADE2'])
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12,
                      hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<br>Proporsi: %{percent}<extra></extra>')
    apply_chart(fig)
    fig.update_layout(title=dict(text="⚤ Distribusi Jenis Kelamin", font=dict(size=14)), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

if is_puk:
    with r2c2:
        act_map = {
            'keg_pyb': 'Bekerja', 'keg_pt': 'Pengangguran',
            'keg_sklh': 'Sekolah', 'keg_mrt': 'Rumah Tangga', 'keg_lain': 'Lainnya',
        }
        act_vals = [data[c].sum() if c in data.columns else 0 for c in act_map]
        adf2 = pd.DataFrame({'Aktivitas': list(act_map.values()), 'Jumlah': act_vals})
        fig = px.pie(adf2, values='Jumlah', names='Aktivitas', hole=0.55, color_discrete_sequence=BLUE_SEQ)
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=11,
                          hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<extra></extra>')
        apply_chart(fig)
        fig.update_layout(title=dict(text="📋 Status Aktivitas", font=dict(size=14)), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

elif is_pt:
    with r2c2:
        pt_map = {
            'kat_mp': 'Mencari Pekerjaan', 'kat_mu': 'Mempersiapkan Usaha',
            'kat_pa': 'Putus Asa', 'kat_bmb': 'Diterima Belum Bekerja',
        }
        pt_vals = [data[c].sum() if c in data.columns else 0 for c in pt_map]
        pdf = pd.DataFrame({'Kategori': list(pt_map.values()), 'Jumlah': pt_vals})
        fig = px.pie(pdf, values='Jumlah', names='Kategori', hole=0.55,
                     color_discrete_sequence=['#003D73', '#005BAB', '#2E86DE', '#85C1E9'])
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=11,
                          hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<extra></extra>')
        apply_chart(fig)
        fig.update_layout(title=dict(text="📋 Kategori Pengangguran", font=dict(size=14)), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

elif is_pyb:
    with r2c2:
        sta_map = {
            'sta_1': 'Berusaha Sendiri', 'sta_2': 'Dibantu Buruh Tdk Tetap', 'sta_3': 'Dibantu Buruh Tetap',
            'sta_4': 'Buruh/Karyawan', 'sta_5': 'Pekerja Bebas (Tani)', 'sta_6': 'Pekerja Bebas (Non-Tani)',
            'sta_7': 'Pekerja Keluarga',
        }
        sta_vals = [data[c].sum() if c in data.columns else 0 for c in sta_map]
        sdf = pd.DataFrame({'Status': list(sta_map.values()), 'Jumlah': sta_vals})
        fig = px.pie(sdf, values='Jumlah', names='Status', hole=0.55, color_discrete_sequence=BLUE_SEQ)
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=10,
                          hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<extra></extra>')
        apply_chart(fig)
        fig.update_layout(title=dict(text="📋 Status Pekerjaan", font=dict(size=14)), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── PYB Row 3: Lapangan Usaha + Jabatan ──────────────────────────────────────
    r3c1, r3c2 = st.columns(2)
    with r3c1:
        lapus_map = {
            'lapus_A': 'Pertanian & Perikanan', 'lapus_B': 'Pertambangan', 'lapus_C': 'Industri Pengolahan',
            'lapus_D': 'Listrik & Gas', 'lapus_E': 'Air & Limbah', 'lapus_F': 'Konstruksi',
            'lapus_G': 'Perdagangan', 'lapus_H': 'Transportasi', 'lapus_I': 'Akomodasi & F&B',
            'lapus_J': 'IT & Komunikasi', 'lapus_K': 'Keuangan', 'lapus_L': 'Real Estat',
            'lapus_MN': 'Jasa Profesional', 'lapus_O': 'Administrasi', 'lapus_P': 'Pendidikan',
            'lapus_Q': 'Kesehatan', 'lapus_RSTU': 'Jasa Lainnya',
        }
        lv = [data[c].sum() if c in data.columns else 0 for c in lapus_map]
        ldf = pd.DataFrame({'Sektor': list(lapus_map.values()), 'Jumlah': lv}).sort_values('Jumlah')
        fig = px.bar(ldf, x='Jumlah', y='Sektor', orientation='h', text='Jumlah',
                     color_discrete_sequence=['#005BAB'])
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=10,
                          hovertemplate='<b>%{y}</b><br>Jumlah: %{x:,.0f}<extra></extra>')
        apply_chart(fig, height=520)
        fig.update_layout(title=dict(text="🏭 Lapangan Usaha", font=dict(size=14)), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with r3c2:
        jab_map = {
            'jab_0': 'TNI/POLRI', 'jab_1': 'Manajer', 'jab_2': 'Profesional',
            'jab_3': 'Teknisi & Asisten', 'jab_4': 'Tata Usaha', 'jab_5': 'Jasa & Penjualan',
            'jab_6': 'Pekerja Terampil Tani', 'jab_7': 'Pengolah & Umum',
            'jab_8': 'Operator Mesin', 'jab_9': 'Kebersihan & Kasar',
        }
        jv = [data[c].sum() if c in data.columns else 0 for c in jab_map]
        jdf = pd.DataFrame({'Jabatan': list(jab_map.values()), 'Jumlah': jv}).sort_values('Jumlah')
        fig = px.bar(jdf, x='Jumlah', y='Jabatan', orientation='h', text='Jumlah',
                     color_discrete_sequence=['#2E86DE'])
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside', textfont_size=10,
                          hovertemplate='<b>%{y}</b><br>Jumlah: %{x:,.0f}<extra></extra>')
        apply_chart(fig, height=520)
        fig.update_layout(title=dict(text="💼 Pekerjaan / Jabatan", font=dict(size=14)), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── PYB Row 4: Jam Kerja ─────────────────────────────────────────────────────
    r4c1, r4c2 = st.columns(2)
    with r4c1:
        jam_map = {'jam_114': '1–14', 'jam_1534': '15–34', 'jam_3540': '35–40', 'jam_4148': '41–48', 'jam_>48': '>48'}
        jmv = [data[c].sum() if c in data.columns else 0 for c in jam_map]
        jmdf = pd.DataFrame({'Jam/Minggu': list(jam_map.values()), 'Jumlah': jmv})
        fig = px.pie(jmdf, values='Jumlah', names='Jam/Minggu', hole=0.55,
                     color_discrete_sequence=BLUE_SEQ)
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=11,
                          hovertemplate='<b>%{label} jam</b><br>Jumlah: %{value:,.0f}<extra></extra>')
        apply_chart(fig)
        fig.update_layout(title=dict(text="⏱️ Jam Kerja per Minggu", font=dict(size=14)), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Trend Chart ──────────────────────────────────────────────────────────────────
reg_df = df.copy()
if selected_level == "Nasional":
    trend_df = reg_df[reg_df['lvl_wil'] == 'nasional']
elif selected_level == "Provinsi":
    trend_df = reg_df[(reg_df['lvl_wil'] == 'provinsi') & (reg_df['nm_prov'] == selected_prov)]
elif selected_level == "Kabupaten/Kota":
    trend_df = reg_df[(reg_df['lvl_wil'].isin(['kabupaten', 'kota'])) & (reg_df['nm_kabkot'] == selected_kabkot)]

fig = go.Figure()

if is_puk:
    ts = trend_df.groupby('thn')[['total', 'keg_pyb', 'keg_pt']].sum().reset_index()
    fig.add_trace(go.Scatter(x=ts['thn'], y=ts['total'],   name="Total PUK",   line=dict(color='#AED6F1', dash='dot', width=2, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=ts['thn'], y=ts['keg_pyb'], name="Bekerja",      line=dict(color='#005BAB', width=3, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=6),
                             fill='tozeroy', fillcolor='rgba(0,91,171,0.06)'))
    fig.add_trace(go.Scatter(x=ts['thn'], y=ts['keg_pt'],  name="Pengangguran", line=dict(color=ACCENT_RED, width=2, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=5)))
    title = f"📈 Tren PUK — {loc_name}"
elif is_pt:
    ts = trend_df.groupby('thn')[['total', 'kat_mp', 'kat_mu', 'kat_pa', 'kat_bmb']].sum().reset_index()
    fig.add_trace(go.Scatter(x=ts['thn'], y=ts['total'],  name="Total PT",             line=dict(color='#AED6F1', dash='dot', width=2, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=ts['thn'], y=ts['kat_mp'], name="Mencari Pekerjaan",     line=dict(color='#005BAB', width=3, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=ts['thn'], y=ts['kat_mu'], name="Mempersiapkan Usaha",   line=dict(color='#2E86DE', width=2, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=4)))
    fig.add_trace(go.Scatter(x=ts['thn'], y=ts['kat_pa'], name="Putus Asa",             line=dict(color=ACCENT_RED, width=2, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=4)))
    fig.add_trace(go.Scatter(x=ts['thn'], y=ts['kat_bmb'],name="Diterima Belum Bekerja",line=dict(color=ACCENT_AMBER, width=2, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=4)))
    title = f"📈 Tren PT — {loc_name}"
elif is_pyb:
    ts = trend_df.groupby('thn')['total'].sum().reset_index()
    fig.add_trace(go.Scatter(x=ts['thn'], y=ts['total'], name="Total PYB", line=dict(color='#005BAB', width=3, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=6),
                             fill='tozeroy', fillcolor='rgba(0,91,171,0.08)'))
    title = f"📈 Tren Penduduk Bekerja — {loc_name}"
else:
    ts = trend_df.groupby('thn')['total'].sum().reset_index()
    fig.add_trace(go.Scatter(x=ts['thn'], y=ts['total'], name="Total AK", line=dict(color='#005BAB', width=3, shape='spline', smoothing=1.3), mode='lines+markers', marker=dict(size=6),
                             fill='tozeroy', fillcolor='rgba(0,91,171,0.08)'))
    title = f"📈 Tren Angkatan Kerja — {loc_name}"

apply_chart(fig, height=400)
fig.update_layout(title=dict(text=title, font=dict(size=15)), xaxis_title="Tahun", yaxis_title="Jumlah Jiwa")
st.plotly_chart(fig, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────────
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;color:{subtext_color};font-size:0.8rem;'>Dashboard Ketenagakerjaan 2018–2025 · Kementerian Ketenagakerjaan RI</p>", unsafe_allow_html=True)
