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
    
    # Convert all data columns to numeric (skip text/identifier columns)
    text_cols = {'thn', 'lvl_wil', 'kd_prov', 'nm_prov', 'kd_kabkot', 'nm_kabkot'}
    for col in df.columns:
        if col not in text_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Use the dataset's own total column (PUK, AK, PYB, PT) if available
    # Each ver2 dataset has a dedicated total column named after itself
    dataset_total_cols = ['PUK', 'AK', 'PYB', 'PT']
    total_found = False
    for tc in dataset_total_cols:
        if tc in df.columns:
            df['total'] = df[tc]
            total_found = True
            break
    
    # Fallback: calculate from jk_lk + jk_pr if no dedicated total column
    if not total_found and 'total' not in df.columns:
        if 'jk_lk' in df.columns and 'jk_pr' in df.columns:
            df['total'] = df['jk_lk'] + df['jk_pr']
        
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
