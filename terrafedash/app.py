import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from terrafedash.utils import load_and_process_data, get_orders_summary, get_ads_summary, filter_dataframe
import base64
import calendar
import locale

# Definir o locale para português brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

def main():
    # Page configuration
    st.set_page_config(
        page_title="Dashboard de Vendas e Marketing - Abril 2025",
        page_icon="☕",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Esconder o menu de configurações
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    # Load and process data
    @st.cache_data
    def get_data():
        return load_and_process_data()

    df_ads, df_orders = get_data()

    # Header with styled banner
    st.markdown("""
    <div style="background-color: #7E57C2; padding: 20px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
        <h1 style="color: white; margin: 0; padding: 0; text-align: center; font-size: 2.2em;">☕ Dashboard de Vendas e Marketing</h1>
        <p style="color: white; margin: 5px 0 0 0; padding: 0; text-align: center; font-size: 1.2em; opacity: 0.9;">Análise de Desempenho - Abril 2025</p>
    </div>
    """, unsafe_allow_html=True)

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Geral", "Instituto", "Ecommerce", "Tabela de Pedidos"])

    # ... resto do código ...

if __name__ == "__main__":
    main()
