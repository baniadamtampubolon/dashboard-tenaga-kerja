import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data, get_geo_structure, filter_data

# Page Config
st.set_page_config(
    page_title="Dashboard PUK 2018-2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Setup toggles before data load so we know which config to use
with st.sidebar:
    st.image("kemnaker-logo.png", use_container_width=True)
    st.markdown("### Konfigurasi Dashboard")
    dataset_choice = st.radio("Pilih Dataset", ["Ringkasan Eksekutif (Semua Data)", "Penduduk Usia Kerja (PUK)", "Angkatan Kerja (AK)", "Pengangguran Terbuka (PT)", "Penduduk yang Bekerja (PYB)"])
    theme_choice = st.radio("Mode Tampilan", ["Terang ☀️", "Gelap 🌙"], horizontal=True)

# Data Source setup
is_main = "Ringkasan" in dataset_choice
is_puk = "PUK" in dataset_choice
is_ak = "AK" in dataset_choice
is_pt = "PT" in dataset_choice
is_pyb = "PYB" in dataset_choice

if is_main:
    df_puk = load_data("Database/PUK-2018-2025.xlsx")
    df_ak = load_data("Database/AK-2018-2025.xlsx")
    df_pt = load_data("Database/PT-2018-2025.xlsx")
    df_pyb = load_data("Database/PYB-2018-2025.xlsx")
    df = df_puk # Base reference mapping
else:
    if is_puk:
        DATA_FILE = "Database/PUK-2018-2025.xlsx"
    elif is_ak:
        DATA_FILE = "Database/AK-2018-2025.xlsx"
    elif is_pt:
        DATA_FILE = "Database/PT-2018-2025.xlsx"
    else:
        DATA_FILE = "Database/PYB-2018-2025.xlsx"
        
    df = load_data(DATA_FILE)
geo_structure = get_geo_structure(df)

# CSS configuration
if "Terang" in theme_choice:
    main_bg = "#f8f9fa"
    metric_bg = "#ffffff"
    sidebar_bg = "#004A8B"
    header_col = "#004A8B"
    text_color = "#1e293b"
    plotly_template = "plotly_white"
else: # Gelap
    main_bg = "#121212"
    metric_bg = "#1E1E1E"
    sidebar_bg = "#0B1D3A" # Darker navy
    header_col = "#8BB5E8"
    text_color = "#E2E8F0"
    plotly_template = "plotly_dark"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {main_bg};
        color: {text_color};
    }}
    .stMetric {{
        background-color: {metric_bg};
        padding: 15px;
        border-radius: 8px;
        border: 1px solid rgba(128,128,128,0.1);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-top: 3px solid #005BAB;
    }}
    .stMetric label {{
        color: {text_color} !important;
    }}
    .stMetric [data-testid="stMetricValue"] {{
        color: {text_color} !important;
    }}
    div[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
    }}
    div[data-testid="stSidebar"] * {{
        color: white !important;
    }}
    .section-header {{
        font-size: 22px;
        font-weight: 600;
        color: {header_col};
        margin-top: 30px;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(128,128,128,0.2);
    }}
    p, span, div {{
        color: {text_color};
    }}
    </style>
    """, unsafe_allow_html=True)

# Filters (Continued in Sidebar)
with st.sidebar:
    st.markdown("---")
    st.markdown("### Filter Wilayah")
    
    selected_year = st.selectbox("Pilih Tahun", sorted(df['thn'].unique(), reverse=True))
    
    level_options = ["Nasional", "Provinsi", "Kabupaten/Kota"]
    selected_level = st.radio("Tingkat Wilayah", level_options)
    
    selected_prov = None
    selected_kabkot = None
    
    if selected_level in ["Provinsi", "Kabupaten/Kota"]:
        selected_prov = st.selectbox("Pilih Provinsi", sorted(geo_structure.keys()))
        
        if selected_level == "Kabupaten/Kota":
            selected_kabkot = st.selectbox("Pilih Kabupaten/Kota", geo_structure[selected_prov])

# Header Information
loc_name = "Nasional"
if selected_level == "Provinsi": loc_name = selected_prov
if selected_level == "Kabupaten/Kota": loc_name = selected_kabkot

# Apply Filter
if is_main:
    data_puk = filter_data(df_puk, selected_year, selected_level, selected_prov, selected_kabkot)
    data_ak = filter_data(df_ak, selected_year, selected_level, selected_prov, selected_kabkot)
    data_pt = filter_data(df_pt, selected_year, selected_level, selected_prov, selected_kabkot)
    data_pyb = filter_data(df_pyb, selected_year, selected_level, selected_prov, selected_kabkot)
    data = data_puk
else:
    data = filter_data(df, selected_year, selected_level, selected_prov, selected_kabkot)

if data.empty:
    st.warning("Data tidak ditemukan untuk filter ini.")
else:
    st.markdown(f"<div class='section-header'>Ringkasan Eksekutif - {loc_name} ({selected_year})</div>", unsafe_allow_html=True)

    if is_main:
        # MAIN DASHBOARD LAYOUT (All 4 Sources Combined)
        
        # Row 1: KPI Summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Penduduk Usia Kerja (PUK)", f"{data_puk['total'].sum():,.0f}")
        col2.metric("Angkatan Kerja (AK)", f"{data_ak['total'].sum():,.0f}")
        col3.metric("Penduduk Bekerja (PYB)", f"{data_pyb['total'].sum():,.0f}")
        col4.metric("Pengangguran Terbuka (PT)", f"{data_pt['total'].sum():,.0f}")
        st.write("")
        
        # ROW 2: Composition Funnels
        c1, c2 = st.columns(2)
        with c1:
            puk_tot = data_puk['total'].sum()
            ak_tot = data_ak['total'].sum()
            pie_puk = pd.DataFrame({'Kategori': ['Angkatan Kerja (AK)', 'Bukan Angkatan Kerja'], 'Jumlah': [ak_tot, max(0, puk_tot - ak_tot)]})
            fig_puk = px.pie(pie_puk, values='Jumlah', names='Kategori', title="Komposisi Populasi Usia Kerja", hole=0.5, color_discrete_sequence=['#005BAB', '#E2E8F0'])
            fig_puk.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_puk, use_container_width=True)
            
        with c2:
            pyb_tot = data_pyb['total'].sum()
            pt_tot = data_pt['total'].sum()
            pie_ak = pd.DataFrame({'Kategori': ['Penduduk Bekerja (PYB)', 'Pengangguran Terbuka (PT)'], 'Jumlah': [pyb_tot, pt_tot]})
            fig_ak = px.pie(pie_ak, values='Jumlah', names='Kategori', title="Komposisi Populasi Angkatan Kerja", hole=0.5, color_discrete_sequence=['#4A90E2', '#D32F2F'])
            fig_ak.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_ak, use_container_width=True)
            
        st.write("")
        
        # ROW 3: Highlight Top Focus
        c3, c4 = st.columns(2)
        with c3:
            lapus_cols = {'lapus_A': 'Pertanian, Kehutanan...', 'lapus_B': 'Pertambangan...', 'lapus_C': 'Industri Pengolahan', 'lapus_D': 'Pengadaan Listrik...', 'lapus_E': 'Pengadaan Air...', 'lapus_F': 'Konstruksi', 'lapus_G': 'Perdagangan Besar...', 'lapus_H': 'Transportasi...', 'lapus_I': 'Akomodasi...', 'lapus_J': 'Informasi...', 'lapus_K': 'Keuangan...', 'lapus_L': 'Real Estat', 'lapus_MN': 'Jasa Profesional', 'lapus_O': 'Administrasi', 'lapus_P': 'Pendidikan', 'lapus_Q': 'Jasa Kesehatan', 'lapus_RSTU': 'Jasa Lainnya'}
            l_values = [data_pyb[col].sum() if col in data_pyb.columns else 0 for col in lapus_cols.keys()]
            l_df = pd.DataFrame({'Sektor Utama': list(lapus_cols.values()), 'Jumlah': l_values}).sort_values('Jumlah', ascending=True).tail(5)
            fig_lap = px.bar(l_df, x='Jumlah', y='Sektor Utama', orientation='h', title="Top 5 Lapangan Usaha (Penyerap Tenaga Kerja)", color_discrete_sequence=['#005BAB'])
            fig_lap.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_lap, use_container_width=True)
            
        with c4:
            pt_cols = {'kat_mp': 'Mencari Pekerjaan', 'kat_mu': 'Mempersiapkan Usaha', 'kat_pa': 'Putus Asa', 'kat_bmb': 'Diterima Tdk Bekerja'}
            pt_values = [data_pt[col].sum() if col in data_pt.columns else 0 for col in pt_cols.keys()]
            pt_df = pd.DataFrame({'Kategori': list(pt_cols.values()), 'Jumlah': pt_values}).sort_values('Jumlah', ascending=True)
            fig_toppt = px.bar(pt_df, x='Jumlah', y='Kategori', orientation='h', title="Kategori Pengangguran Terbuka Eksisting", color_discrete_sequence=['#D32F2F'])
            fig_toppt.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_toppt, use_container_width=True)
            
        st.write("")
        
        # ROW 4: Master Trend
        def get_trend_main(d_df):
            if selected_level == "Nasional": return d_df[d_df['lvl_wil'] == 'nasional']
            elif selected_level == "Provinsi": return d_df[(d_df['lvl_wil'] == 'provinsi') & (d_df['nm_prov'] == selected_prov)]
            elif selected_level == "Kabupaten/Kota": return d_df[(d_df['lvl_wil'].isin(['kabupaten', 'kota'])) & (d_df['nm_kabkot'] == selected_kabkot)]
            return d_df
            
        trend_puk = get_trend_main(df_puk).groupby('thn')['total'].sum().reset_index()
        trend_ak = get_trend_main(df_ak).groupby('thn')['total'].sum().reset_index()
        trend_pyb = get_trend_main(df_pyb).groupby('thn')['total'].sum().reset_index()
        trend_pt = get_trend_main(df_pt).groupby('thn')['total'].sum().reset_index()
        
        fig_mt = go.Figure()
        fig_mt.add_trace(go.Scatter(x=trend_puk['thn'], y=trend_puk['total'], name="Total PUK", line_shape='spline', line=dict(color='#8BB5E8', dash='dot')))
        fig_mt.add_trace(go.Scatter(x=trend_ak['thn'], y=trend_ak['total'], name="Total AK", line_shape='spline', line=dict(color='#4A90E2', dash='dot')))
        fig_mt.add_trace(go.Scatter(x=trend_pyb['thn'], y=trend_pyb['total'], name="Penduduk Bekerja (PYB)", line_shape='spline', line=dict(color='#005BAB', width=3)))
        fig_mt.add_trace(go.Scatter(x=trend_pt['thn'], y=trend_pt['total'], name="Penganggur (PT)", line_shape='spline', line=dict(color='#D32F2F', width=2)))
        fig_mt.update_layout(title=f"Master Tren Ketenagakerjaan Nasional {loc_name} (2018 - 2025)", xaxis_title="Tahun", yaxis_title="Jumlah Jiwa", template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_mt, use_container_width=True)
        
        # Footer
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #64748b;'>Dashboard Ketenagakerjaan Nasional 2018-2025 | Dikembangkan oleh Antigravity</p>", unsafe_allow_html=True)
        st.stop()

    # Existing Individual Dataset Logic
    # 1. Metric Cards
    total_val = data['total'].sum()
    
    if is_puk:
        col1, col2, col3, col4 = st.columns(4)
        working = data.get('keg_pyb', pd.Series([0])).sum()
        unemployed = data.get('keg_pt', pd.Series([0])).sum()
        others = data.get('keg_lain', pd.Series([0])).sum()
        
        col1.metric("Total PUK", f"{total_val:,.0f}")
        col2.metric("Penduduk yang Bekerja", f"{working:,.0f}")
        col3.metric("Pengangguran Terbuka", f"{unemployed:,.0f}")
        col4.metric("Kegiatan Lainnya", f"{others:,.0f}")
    elif is_pt:
        col1, col2, col3, col4 = st.columns(4)
        mp = data.get('kat_mp', pd.Series([0])).sum()
        mu = data.get('kat_mu', pd.Series([0])).sum()
        pa = data.get('kat_pa', pd.Series([0])).sum()
        
        col1.metric("Total PT", f"{total_val:,.0f}")
        col2.metric("Mencari Pekerjaan", f"{mp:,.0f}")
        col3.metric("Mempersiapkan Usaha", f"{mu:,.0f}")
        col4.metric("Putus Asa", f"{pa:,.0f}")
    elif is_ak:
        col1, = st.columns(1)
        col1.metric("Total Angkatan Kerja", f"{total_val:,.0f}")
    else: # is_pyb
        col1, = st.columns(1)
        col1.metric("Total Penduduk yang Bekerja", f"{total_val:,.0f}")
    
    st.write("---")
    
    # ROW 1: Age Profile and Education
    c1, c2 = st.columns(2)
    
    with c1:
        # Age Groups (Line Chart)
        age_cols = {
            'ku_1519': '15-19', 'ku_2024': '20-24', 'ku_2529': '25-29', 
            'ku_3034': '30-34', 'ku_3539': '35-39', 'ku_4044': '40-44',
            'ku_4549': '45-49', 'ku_5054': '50-54', 'ku_5559': '55-59',
            'ku_6064': '60-64', 'ku_65+': '65+'
        }
        age_values = [data[col].sum() for col in age_cols.keys()]
        age_df = pd.DataFrame({'Kelompok Usia': list(age_cols.values()), 'Jumlah': age_values})
        
        fig_age = px.line(age_df, x='Kelompok Usia', y='Jumlah', title="Profil Usia Penduduk", markers=True)
        fig_age.update_traces(line_color='#005BAB', line_width=3, marker=dict(size=6))
        fig_age.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_age, use_container_width=True)
        
    with c2:
        # Education Bar Chart
        edu_cols = {
            'pd_sd': 'Sekolah Dasar (SD)', 'pd_smp': 'Sekolah Menengah Pertama (SMP)', 
            'pd_smau': 'SMA Umum', 'pd_smak': 'SMA Kejuruan', 
            'pd_dipl': 'Diploma', 'pd_univ': 'Universitas'
        }
        edu_values = [data[col].sum() if col in data.columns else 0 for col in edu_cols.keys()]
        edu_df = pd.DataFrame({'Pendidikan': list(edu_cols.values()), 'Jumlah': edu_values})
        fig_edu = px.bar(edu_df, x='Pendidikan', y='Jumlah', title="Distribusi Tingkat Pendidikan",
                        color='Pendidikan', color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_edu.update_layout(showlegend=False, template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_edu, use_container_width=True)

    st.write("") # Clean gap
    
    # ROW 2: Gender and Activity/PT/Status
    if is_ak:
        c3, = st.columns(1)
    else:
        c3, c4 = st.columns(2)
    
    with c3:
        # Gender Donut Chart
        gender_data = pd.DataFrame({
            'Gender': ['Laki-laki', 'Perempuan'],
            'Jumlah': [data['jk_lk'].sum(), data['jk_pr'].sum()]
        })
        fig_gender = px.pie(gender_data, values='Jumlah', names='Gender', title="Distribusi Jenis Kelamin",
                           color_discrete_sequence=['#004A8B', '#64B5F6'], hole=0.5)
        fig_gender.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gender, use_container_width=True)
        
    if is_puk:
        with c4:
            # Detailed Activity Breakdown (Pie Chart)
            act_cols = {
                'keg_pyb': 'Penduduk yang Bekerja', 'keg_pt': 'Pengangguran Terbuka', 
                'keg_sklh': 'Kegiatan Sekolah', 'keg_mrt': 'Mengurus Rumah Tangga', 'keg_lain': 'Kegiatan Lainnya'
            }
            act_values = [data[col].sum() if col in data.columns else 0 for col in act_cols.keys()]
            act_df = pd.DataFrame({'Aktivitas': list(act_cols.values()), 'Jumlah': act_values})
            
            # Professional Kemnaker Blue palette
            kemnaker_palette = ['#003366', '#005BAB', '#4A90E2', '#8BB5E8', '#BBD4EE']
            fig_act = px.pie(act_df, values='Jumlah', names='Aktivitas', title="Komposisi Status Aktivitas",
                            color_discrete_sequence=kemnaker_palette, hole=0.5)
            fig_act.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_act, use_container_width=True)
            
    elif is_pt:
        with c4:
            pt_cols = {
                'kat_mp': 'Mencari Pekerjaan', 'kat_mu': 'Mempersiapkan Usaha', 
                'kat_pa': 'Putus Asa', 'kat_bmb': 'Diterima Tapi Belum Bekerja'
            }
            pt_values = [data[col].sum() if col in data.columns else 0 for col in pt_cols.keys()]
            pt_df = pd.DataFrame({'Kategori': list(pt_cols.values()), 'Jumlah': pt_values})
            
            kemnaker_palette = ['#003366', '#005BAB', '#4A90E2', '#8BB5E8', '#BBD4EE']
            fig_pt = px.pie(pt_df, values='Jumlah', names='Kategori', title="Kategori Pengangguran",
                            color_discrete_sequence=kemnaker_palette, hole=0.5)
            fig_pt.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pt, use_container_width=True)

    elif is_pyb:
        with c4:
            sta_cols = {
                'sta_1': 'Berusaha Sendiri', 'sta_2': 'Dibantu Buruh Tdk Tetap', 'sta_3': 'Dibantu Buruh Tetap',
                'sta_4': 'Buruh/Karyawan/Pegawai', 'sta_5': 'Pekerja Bebas (Pertanian)', 
                'sta_6': 'Pekerja Bebas (Non-Pertanian)', 'sta_7': 'Pekerja Keluarga'
            }
            sta_values = [data[col].sum() if col in data.columns else 0 for col in sta_cols.keys()]
            sta_df = pd.DataFrame({'Status Pekerjaan': list(sta_cols.values()), 'Jumlah': sta_values})
            
            kemnaker_palette = ['#003366', '#005BAB', '#4A90E2', '#8BB5E8', '#BBD4EE', '#A0CCFF', '#4285F4']
            fig_sta = px.pie(sta_df, values='Jumlah', names='Status Pekerjaan', title="Status Pekerjaan",
                            color_discrete_sequence=kemnaker_palette, hole=0.5)
            fig_sta.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_sta, use_container_width=True)

        st.write("") # Clean gap
        
        # ROW 3: Lapangan Usaha dan Jabatan (Khusus PYB)
        c5, c6 = st.columns(2)
        with c5:
            lapus_cols = {
                'lapus_A': 'Pertanian, Kehutanan, Perikanan', 'lapus_B': 'Pertambangan & Penggalian',
                'lapus_C': 'Industri Pengolahan', 'lapus_D': 'Pengadaan Listrik, Gas dll', 'lapus_E': 'Pengadaan Air, Limbah dll',
                'lapus_F': 'Konstruksi', 'lapus_G': 'Perdagangan Besar, Reparasi', 'lapus_H': 'Transportasi & Pergudangan',
                'lapus_I': 'Akomodasi & Makan Minum', 'lapus_J': 'Informasi & Komunikasi', 'lapus_K': 'Keuangan & Asuransi',
                'lapus_L': 'Real Estat', 'lapus_MN': 'Jasa Profesional dll', 'lapus_O': 'Administrasi',
                'lapus_P': 'Pendidikan', 'lapus_Q': 'Jasa Kesehatan', 'lapus_RSTU': 'Jasa Lainnya'
            }
            lapus_values = [data[col].sum() if col in data.columns else 0 for col in lapus_cols.keys()]
            lapus_df = pd.DataFrame({'Lapangan Usaha': list(lapus_cols.values()), 'Jumlah': lapus_values})
            lapus_df = lapus_df.sort_values('Jumlah', ascending=True) # Ascending for horizontal bar
            
            fig_lapus = px.bar(lapus_df, x='Jumlah', y='Lapangan Usaha', orientation='h', title="Lapangan Usaha",
                               color_discrete_sequence=['#005BAB'])
            fig_lapus.update_layout(height=500, template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_lapus, use_container_width=True)

        with c6:
            jab_cols = {
                'jab_0': 'TNI/POLRI', 'jab_1': 'Manajer', 'jab_2': 'Profesional', 'jab_3': 'Teknisi & Asisten Profesional',
                'jab_4': 'Tenaga Tata Usaha', 'jab_5': 'Tenaga Jasa & Penjualan', 'jab_6': 'Pekerja Terampil Pertanian',
                'jab_7': 'Pekerja Pengolah & Umum', 'jab_8': 'Operator Mesin & Perakit', 'jab_9': 'Tenaga Kebersihan & Kasar'
            }
            jab_values = [data[col].sum() if col in data.columns else 0 for col in jab_cols.keys()]
            jab_df = pd.DataFrame({'Jabatan': list(jab_cols.values()), 'Jumlah': jab_values})
            jab_df = jab_df.sort_values('Jumlah', ascending=True)
            
            fig_jab = px.bar(jab_df, x='Jumlah', y='Jabatan', orientation='h', title="Pekerjaan / Jabatan",
                               color_discrete_sequence=['#4A90E2'])
            fig_jab.update_layout(height=500, template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_jab, use_container_width=True)

        st.write("") # Clean gap
        
        # ROW 4: Jam Kerja
        c7, c8 = st.columns(2)
        with c7:
            jam_cols = {
                'jam_114': '1-14 Jam', 'jam_1534': '15-34 Jam',
                'jam_3540': '35-40 Jam', 'jam_4148': '41-48 Jam', 'jam_>48': '>48 Jam'
            }
            jam_values = [data[col].sum() if col in data.columns else 0 for col in jam_cols.keys()]
            jam_df = pd.DataFrame({'Jam Kerja / Minggu': list(jam_cols.values()), 'Jumlah': jam_values})
            
            fig_jam = px.pie(jam_df, values='Jumlah', names='Jam Kerja / Minggu', title="Distribusi Jam Kerja Seminggu",
                             color_discrete_sequence=px.colors.sequential.Blues_r, hole=0.5)
            fig_jam.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_jam, use_container_width=True)

    st.write("") # Clean gap
    
    # ROW 3: Trend Analysis over time
    # Multi-year analysis for the selected region
    reg_df = df.copy()
    if selected_level == "Nasional":
        trend_df = reg_df[reg_df['lvl_wil'] == 'nasional']
    elif selected_level == "Provinsi":
        trend_df = reg_df[(reg_df['lvl_wil'] == 'provinsi') & (reg_df['nm_prov'] == selected_prov)]
    elif selected_level == "Kabupaten/Kota":
        trend_df = reg_df[(reg_df['lvl_wil'].isin(['kabupaten', 'kota'])) & (reg_df['nm_kabkot'] == selected_kabkot)]
        
    if is_puk:
        trend_summary = trend_df.groupby('thn')[['total', 'keg_pyb', 'keg_pt']].sum().reset_index()
    elif is_pt:
        trend_summary = trend_df.groupby('thn')[['total', 'kat_mp', 'kat_mu', 'kat_pa', 'kat_bmb']].sum().reset_index()
    else:
        trend_summary = trend_df.groupby('thn')['total'].sum().reset_index()
    
    fig_trend = go.Figure()
    
    if is_puk:
        fig_trend.add_trace(go.Scatter(x=trend_summary['thn'], y=trend_summary['total'], name="Total PUK", line_shape='spline', line=dict(color='#8BB5E8', dash='dot')))
        fig_trend.add_trace(go.Scatter(x=trend_summary['thn'], y=trend_summary['keg_pyb'], name="Penduduk yang Bekerja", line_shape='spline', line=dict(color='#005BAB', width=3)))
        fig_trend.add_trace(go.Scatter(x=trend_summary['thn'], y=trend_summary['keg_pt'], name="Pengangguran Terbuka", line_shape='spline', line=dict(color='#D32F2F', width=2)))
        fig_trend.update_layout(title=f"Tren Tahunan PUK {loc_name} (2018 - 2025)", xaxis_title="Tahun", yaxis_title="Jumlah Jiwa", template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    elif is_pt:
        fig_trend.add_trace(go.Scatter(x=trend_summary['thn'], y=trend_summary['total'], name="Total PT", line_shape='spline', line=dict(color='#8BB5E8', dash='dot')))
        fig_trend.add_trace(go.Scatter(x=trend_summary['thn'], y=trend_summary['kat_mp'], name="Mencari Pekerjaan", line_shape='spline', line=dict(color='#005BAB', width=3)))
        fig_trend.add_trace(go.Scatter(x=trend_summary['thn'], y=trend_summary['kat_mu'], name="Mempersiapkan Usaha", line_shape='spline', line=dict(color='#4A90E2', width=2)))
        fig_trend.add_trace(go.Scatter(x=trend_summary['thn'], y=trend_summary['kat_pa'], name="Putus Asa", line_shape='spline', line=dict(color='#D32F2F', width=2)))
        fig_trend.add_trace(go.Scatter(x=trend_summary['thn'], y=trend_summary['kat_bmb'], name="Diterima Belum Bekerja", line_shape='spline', line=dict(color='#FF9800', width=2)))
        fig_trend.update_layout(title=f"Tren Tahunan PT {loc_name} (2018 - 2025)", xaxis_title="Tahun", yaxis_title="Jumlah Jiwa", template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    elif is_pyb:
        fig_trend.add_trace(go.Scatter(x=trend_summary['thn'], y=trend_summary['total'], name="Total PYB", line_shape='spline', line=dict(color='#005BAB', width=3)))
        fig_trend.update_layout(title=f"Tren Tahunan Penduduk yang Bekerja {loc_name} (2018 - 2025)", xaxis_title="Tahun", yaxis_title="Jumlah Jiwa", template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    else:
        fig_trend.add_trace(go.Scatter(x=trend_summary['thn'], y=trend_summary['total'], name="Total Angkatan Kerja", line_shape='spline', line=dict(color='#005BAB', width=3)))
        fig_trend.update_layout(title=f"Tren Tahunan Angkatan Kerja {loc_name} (2018 - 2025)", xaxis_title="Tahun", yaxis_title="Jumlah Jiwa", template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    st.plotly_chart(fig_trend, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Dashboard PUK 2018-2025 | Dikembangkan oleh Antigravity</p>", unsafe_allow_html=True)
