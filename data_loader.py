import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file_path):
    """
    Load and preprocess the PUK data.
    """
    df = pd.read_excel(file_path)
    
    # Ensure years are integers
    df['thn'] = df['thn'].astype(int)
    
    # Standardize lvl_wil to lowercase to handle variations like 'Kabupaten', 'kabupaten', 'Provinsi', 'Nasional'
    df['lvl_wil'] = df['lvl_wil'].astype(str).str.lower()
    
    # Fill NaN values for geographic names/codes if any
    df['nm_prov'] = df['nm_prov'].fillna('NASIONAL')
    df['nm_kabkot'] = df['nm_kabkot'].fillna('-')
    
    # Handle missing 'total' column in datasets like AK
    if 'total' not in df.columns and 'jk_lk' in df.columns and 'jk_pr' in df.columns:
        df['total'] = pd.to_numeric(df['jk_lk'], errors='coerce').fillna(0) + pd.to_numeric(df['jk_pr'], errors='coerce').fillna(0)
        
    return df

def get_geo_structure(df):
    """
    Extract the hierarchical structure: Provinsi -> Kabupaten/Kota
    """
    structure = {}
    
    # Filter only provinsi level rows to get all provinces
    provinces = df[df['nm_prov'] != 'NASIONAL']['nm_prov'].unique()
    
    for prov in provinces:
        # Get unique kabkot for each province
        kabkots = df[(df['nm_prov'] == prov) & (df['nm_kabkot'] != '-')]['nm_kabkot'].unique()
        structure[prov] = sorted(list(kabkots))
        
    return structure

def filter_data(df, year, level, province=None, kabkot=None):
    """
    Filter dataframe based on user selection.
    """
    filtered_df = df[df['thn'] == year]
    
    if level == 'Nasional':
        return filtered_df[filtered_df['lvl_wil'] == 'nasional']
    elif level == 'Provinsi':
        return filtered_df[(filtered_df['lvl_wil'] == 'provinsi') & (filtered_df['nm_prov'] == province)]
    elif level == 'Kabupaten/Kota':
        return filtered_df[(filtered_df['lvl_wil'].isin(['kabupaten', 'kota'])) & (filtered_df['nm_kabkot'] == kabkot)]
    
    return filtered_df
