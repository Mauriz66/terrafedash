import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from utils import load_and_process_data, get_orders_summary, get_ads_summary, filter_dataframe
import base64

# Page configuration
st.set_page_config(
    page_title="Dashboard de Vendas e Marketing - Abril 2025",
    page_icon="☕",
    layout="wide",
)

# CSS para estilização da página
def local_css():
    st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 16px;
        background-color: #f0f2f6;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #7E57C2 !important;
        color: white !important;
    }
    h1, h2, h3 {
        font-family: 'Sans serif';
        font-weight: 700;
        color: #333;
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    .metric-label {
        font-size: 0.9em;
        font-weight: 500;
        color: #555;
    }
    .metric-value {
        font-size: 1.8em;
        font-weight: 700;
        color: #333;
    }
    .divider {
        margin: 20px 0;
        border-bottom: 1px solid #eee;
    }
    .tab-header {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #7E57C2;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Funções para componentes estilizados
def metric_card(title, value, delta=None, color="#7E57C2"):
    if delta is not None:
        delta_html = f"""<div style="color: {'#4CAF50' if delta > 0 else '#F44336'}; font-size: 0.8em; margin-top: 5px;">
                        {'↑' if delta > 0 else '↓'} {abs(delta):.2f}%
                      </div>"""
    else:
        delta_html = ""
    
    html = f"""
    <div style="background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 15px; border-left: 5px solid {color};">
        <div style="font-size: 0.9em; font-weight: 500; color: #555; margin-bottom: 5px;">{title}</div>
        <div style="font-size: 1.8em; font-weight: 700; color: #333;">{value}</div>
        {delta_html}
    </div>
    """
    return st.markdown(html, unsafe_allow_html=True)

def banner_header():
    st.markdown("""
    <div style="background-color: #7E57C2; padding: 20px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
        <h1 style="color: white; margin: 0; padding: 0; text-align: center; font-size: 2.2em;">☕ Dashboard de Vendas e Marketing</h1>
        <p style="color: white; margin: 5px 0 0 0; padding: 0; text-align: center; font-size: 1.2em; opacity: 0.9;">Análise de Desempenho - Abril 2025</p>
    </div>
    """, unsafe_allow_html=True)

# Load and process data
@st.cache_data
def get_data():
    return load_and_process_data()

df_ads, df_orders = get_data()

# Header with styled banner
banner_header()

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Geral", "Instituto", "Ecommerce", "Tabela de Pedidos"])

# ---------- GENERAL TAB ----------
with tab1:
    st.markdown("""
    <div class="tab-header">
        <h2>Visão Geral</h2>
        <p>Análise completa de desempenho de vendas e marketing para abril de 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary metrics
    orders_summary = get_orders_summary(df_orders)
    ads_summary = get_ads_summary(df_ads)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card("Total de Vendas", f"R$ {orders_summary['total_vendas']:,.2f}", color="#4CAF50")
    
    with col2:
        metric_card("Total de Pedidos", f"{orders_summary['total_pedidos']:,}", color="#2196F3")
    
    with col3:
        metric_card("Ticket Médio", f"R$ {orders_summary['ticket_medio']:,.2f}", color="#FF9800")
    
    with col4:
        roi = ((orders_summary['total_vendas'] - ads_summary['total_gasto']) / ads_summary['total_gasto']) * 100
        metric_card("ROI Geral", f"{roi:.2f}%", color="#9C27B0")
    
    st.divider()
    
    # ROI Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Receita vs. Investimento em Marketing")
        
        # Create a dataframe for the chart
        roi_data = pd.DataFrame({
            'Categoria': ['Receita', 'Investimento em Marketing'],
            'Valor': [orders_summary['total_vendas'], ads_summary['total_gasto']]
        })
        
        fig = px.bar(
            roi_data, 
            x='Categoria', 
            y='Valor',
            text_auto='.2s',
            title="Receita vs. Investimento",
            color='Categoria',
            color_discrete_sequence=['#4CAF50', '#2196F3']
        )
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Valor (R$)",
            yaxis_tickprefix="R$ "
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate and display ROI
        roi = ((orders_summary['total_vendas'] - ads_summary['total_gasto']) / ads_summary['total_gasto']) * 100
        st.metric("ROI Geral", f"{roi:.2f}%")
    
    with col2:
        st.subheader("Distribuição de Vendas por Tipo")
        
        # Group by tipo_venda
        vendas_por_tipo = df_orders.groupby('tipo_venda')['produto_valor_total'].sum().reset_index()
        vendas_por_tipo.columns = ['Tipo', 'Valor Total']
        
        fig = px.pie(
            vendas_por_tipo,
            values='Valor Total',
            names='Tipo',
            title="Distribuição de Vendas",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Sales over time
    st.subheader("Vendas ao Longo do Mês")
    
    # Group by date
    vendas_diarias = df_orders.groupby('pedido_data')['produto_valor_total'].sum().reset_index()
    
    fig = px.line(
        vendas_diarias,
        x='pedido_data',
        y='produto_valor_total',
        markers=True,
        title="Vendas Diárias em Abril 2025",
        labels={'pedido_data': 'Data', 'produto_valor_total': 'Valor Total (R$)'}
    )
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Valor (R$)",
        yaxis_tickprefix="R$ "
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Geographic distribution
    st.subheader("Distribuição Geográfica das Vendas")
    
    # Group by state
    vendas_por_estado = df_orders.groupby('envio_estado')['produto_valor_total'].sum().reset_index()
    vendas_por_estado.columns = ['Estado', 'Valor Total']
    vendas_por_estado = vendas_por_estado.sort_values('Valor Total', ascending=False)
    
    fig = px.bar(
        vendas_por_estado,
        x='Estado',
        y='Valor Total',
        text_auto='.2s',
        title="Vendas por Estado",
        color='Valor Total',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        xaxis_title="Estado",
        yaxis_title="Valor (R$)",
        yaxis_tickprefix="R$ "
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Campaign performance
    st.subheader("Desempenho das Campanhas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Group by campaign type
        campanhas_por_tipo = df_ads.groupby('tipo_campanha').agg({
            'valor_gasto': 'sum',
            'cliques': 'sum',
            'impressoes': 'sum',
            'adicoes_carrinho': 'sum'
        }).reset_index()
        
        # Calculate CTR and conversion rate
        campanhas_por_tipo['ctr'] = (campanhas_por_tipo['cliques'] / campanhas_por_tipo['impressoes']) * 100
        campanhas_por_tipo['taxa_conversao'] = (campanhas_por_tipo['adicoes_carrinho'] / campanhas_por_tipo['cliques']) * 100
        
        fig = px.bar(
            campanhas_por_tipo,
            x='tipo_campanha',
            y='valor_gasto',
            text_auto='.2s',
            title="Investimento por Tipo de Campanha",
            color='tipo_campanha'
        )
        fig.update_layout(
            xaxis_title="Tipo de Campanha",
            yaxis_title="Valor Gasto (R$)",
            yaxis_tickprefix="R$ "
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            campanhas_por_tipo,
            x='tipo_campanha',
            y=['ctr', 'taxa_conversao'],
            barmode='group',
            title="CTR e Taxa de Conversão por Tipo de Campanha",
            labels={
                'value': 'Percentual (%)',
                'variable': 'Métrica',
                'tipo_campanha': 'Tipo de Campanha'
            }
        )
        fig.update_layout(
            xaxis_title="Tipo de Campanha",
            yaxis_title="Percentual (%)",
            yaxis_ticksuffix="%"
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------- INSTITUTO TAB ----------
with tab2:
    st.markdown("""
    <div class="tab-header">
        <h2>Instituto - Cursos e Workshops</h2>
        <p>Análise de desempenho da área educacional - cursos, workshops e oficinas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter data for Instituto
    instituto_orders = filter_dataframe(df_orders, 'tipo_venda', 'Instituto')
    instituto_ads = filter_dataframe(df_ads, 'tipo_campanha', 'Instituto')
    
    instituto_orders_summary = get_orders_summary(instituto_orders)
    instituto_ads_summary = get_ads_summary(instituto_ads)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card("Total de Vendas", f"R$ {instituto_orders_summary['total_vendas']:,.2f}", color="#4CAF50")
    
    with col2:
        metric_card("Total de Pedidos", f"{instituto_orders_summary['total_pedidos']:,}", color="#2196F3")
    
    with col3:
        metric_card("Ticket Médio", f"R$ {instituto_orders_summary['ticket_medio']:,.2f}", color="#FF9800")
    
    with col4:
        if instituto_ads_summary['total_gasto'] > 0:
            roi = ((instituto_orders_summary['total_vendas'] - instituto_ads_summary['total_gasto']) / instituto_ads_summary['total_gasto']) * 100
            metric_card("ROI Instituto", f"{roi:.2f}%", color="#9C27B0")
        else:
            metric_card("ROI Instituto", "N/A", color="#9C27B0")
    
    st.divider()
    
    # ROI Analysis for Instituto
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Receita vs. Investimento em Marketing (Instituto)")
        
        # Create a dataframe for the chart
        roi_data = pd.DataFrame({
            'Categoria': ['Receita', 'Investimento em Marketing'],
            'Valor': [instituto_orders_summary['total_vendas'], instituto_ads_summary['total_gasto']]
        })
        
        fig = px.bar(
            roi_data, 
            x='Categoria', 
            y='Valor',
            text_auto='.2s',
            title="Receita vs. Investimento (Instituto)",
            color='Categoria',
            color_discrete_sequence=['#4CAF50', '#2196F3']
        )
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Valor (R$)",
            yaxis_tickprefix="R$ "
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate and display ROI
        if instituto_ads_summary['total_gasto'] > 0:
            roi = ((instituto_orders_summary['total_vendas'] - instituto_ads_summary['total_gasto']) / instituto_ads_summary['total_gasto']) * 100
            st.metric("ROI Instituto", f"{roi:.2f}%")
        else:
            st.metric("ROI Instituto", "N/A")
    
    with col2:
        st.subheader("Métricas de Campanha (Instituto)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("CTR", f"{instituto_ads_summary['ctr']:.2f}%")
            st.metric("Impressões", f"{instituto_ads_summary['total_impressoes']:,}")
        with col2:
            st.metric("Taxa de Conversão", f"{instituto_ads_summary['taxa_conversao']:.2f}%")
            st.metric("Cliques", f"{instituto_ads_summary['total_cliques']:,}")
    
    st.divider()
    
    # Courses popularity
    st.subheader("Popularidade dos Cursos e Workshops")
    
    # Find popular courses
    cursos = instituto_orders[instituto_orders['categoria_produto'] == 'Cursos e Workshops']
    cursos_populares = cursos.groupby('produto_nome').agg({
        'produto_quantidade': 'sum',
        'produto_valor_total': 'sum'
    }).reset_index().sort_values('produto_valor_total', ascending=False)
    
    if not cursos_populares.empty:
        fig = px.bar(
            cursos_populares,
            x='produto_nome',
            y='produto_valor_total',
            text_auto='.2s',
            title="Receita por Curso/Workshop",
            color='produto_nome'
        )
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Valor Total (R$)",
            yaxis_tickprefix="R$ ",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Não foram encontrados dados de cursos e workshops.")
    
    st.divider()
    
    # Sales over time for Instituto
    st.subheader("Vendas ao Longo do Mês (Instituto)")
    
    # Group by date
    instituto_vendas_diarias = instituto_orders.groupby('pedido_data')['produto_valor_total'].sum().reset_index()
    
    fig = px.line(
        instituto_vendas_diarias,
        x='pedido_data',
        y='produto_valor_total',
        markers=True,
        title="Vendas Diárias de Cursos e Workshops em Abril 2025",
        labels={'pedido_data': 'Data', 'produto_valor_total': 'Valor Total (R$)'}
    )
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Valor (R$)",
        yaxis_tickprefix="R$ "
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- ECOMMERCE TAB ----------
with tab3:
    st.markdown("""
    <div class="tab-header">
        <h2>Ecommerce - Cafés e Produtos</h2>
        <p>Análise de desempenho da área de vendas de cafés e produtos físicos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter data for Ecommerce
    ecommerce_orders = filter_dataframe(df_orders, 'tipo_venda', 'Ecommerce')
    ecommerce_ads = filter_dataframe(df_ads, 'tipo_campanha', 'Ecommerce')
    
    ecommerce_orders_summary = get_orders_summary(ecommerce_orders)
    ecommerce_ads_summary = get_ads_summary(ecommerce_ads)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card("Total de Vendas", f"R$ {ecommerce_orders_summary['total_vendas']:,.2f}", color="#4CAF50")
    
    with col2:
        metric_card("Total de Pedidos", f"{ecommerce_orders_summary['total_pedidos']:,}", color="#2196F3")
    
    with col3:
        metric_card("Ticket Médio", f"R$ {ecommerce_orders_summary['ticket_medio']:,.2f}", color="#FF9800")
    
    with col4:
        if ecommerce_ads_summary['total_gasto'] > 0:
            roi = ((ecommerce_orders_summary['total_vendas'] - ecommerce_ads_summary['total_gasto']) / ecommerce_ads_summary['total_gasto']) * 100
            metric_card("ROI Ecommerce", f"{roi:.2f}%", color="#9C27B0")
        else:
            metric_card("ROI Ecommerce", "N/A", color="#9C27B0")
    
    st.divider()
    
    # ROI Analysis for Ecommerce
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Receita vs. Investimento em Marketing (Ecommerce)")
        
        # Create a dataframe for the chart
        roi_data = pd.DataFrame({
            'Categoria': ['Receita', 'Investimento em Marketing'],
            'Valor': [ecommerce_orders_summary['total_vendas'], ecommerce_ads_summary['total_gasto']]
        })
        
        fig = px.bar(
            roi_data, 
            x='Categoria', 
            y='Valor',
            text_auto='.2s',
            title="Receita vs. Investimento (Ecommerce)",
            color='Categoria',
            color_discrete_sequence=['#4CAF50', '#2196F3']
        )
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Valor (R$)",
            yaxis_tickprefix="R$ "
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate and display ROI
        if ecommerce_ads_summary['total_gasto'] > 0:
            roi = ((ecommerce_orders_summary['total_vendas'] - ecommerce_ads_summary['total_gasto']) / ecommerce_ads_summary['total_gasto']) * 100
            st.metric("ROI Ecommerce", f"{roi:.2f}%")
        else:
            st.metric("ROI Ecommerce", "N/A")
    
    with col2:
        st.subheader("Métricas de Campanha (Ecommerce)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("CTR", f"{ecommerce_ads_summary['ctr']:.2f}%")
            st.metric("Impressões", f"{ecommerce_ads_summary['total_impressoes']:,}")
        with col2:
            st.metric("Taxa de Conversão", f"{ecommerce_ads_summary['taxa_conversao']:.2f}%")
            st.metric("Cliques", f"{ecommerce_ads_summary['total_cliques']:,}")
    
    st.divider()
    
    # Products by category
    st.subheader("Vendas por Categoria de Produto")
    
    # Group by product category
    vendas_por_categoria = ecommerce_orders.groupby('categoria_produto')['produto_valor_total'].sum().reset_index()
    vendas_por_categoria.columns = ['Categoria', 'Valor Total']
    vendas_por_categoria = vendas_por_categoria.sort_values('Valor Total', ascending=False)
    
    fig = px.pie(
        vendas_por_categoria,
        values='Valor Total',
        names='Categoria',
        title="Distribuição de Vendas por Categoria",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Top products
    st.subheader("Produtos Mais Vendidos")
    
    # Group by product
    produtos_mais_vendidos = ecommerce_orders.groupby('produto_nome').agg({
        'produto_quantidade': 'sum',
        'produto_valor_total': 'sum'
    }).reset_index().sort_values('produto_valor_total', ascending=False).head(10)
    
    fig = px.bar(
        produtos_mais_vendidos,
        x='produto_nome',
        y='produto_valor_total',
        text_auto='.2s',
        title="Top 10 Produtos por Receita",
        color='produto_nome'
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Valor Total (R$)",
        yaxis_tickprefix="R$ ",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Sales over time for Ecommerce
    st.subheader("Vendas ao Longo do Mês (Ecommerce)")
    
    # Group by date
    ecommerce_vendas_diarias = ecommerce_orders.groupby('pedido_data')['produto_valor_total'].sum().reset_index()
    
    fig = px.line(
        ecommerce_vendas_diarias,
        x='pedido_data',
        y='produto_valor_total',
        markers=True,
        title="Vendas Diárias de Produtos em Abril 2025",
        labels={'pedido_data': 'Data', 'produto_valor_total': 'Valor Total (R$)'}
    )
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Valor (R$)",
        yaxis_tickprefix="R$ "
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- ORDERS TABLE TAB ----------
with tab4:
    st.markdown("""
    <div class="tab-header">
        <h2>Tabela de Pedidos</h2>
        <p>Detalhamento completo de todos os pedidos realizados em Abril 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #7E57C2;">
        <h3 style="margin-top: 0; font-size: 1.2em;">Filtros</h3>
        <p style="margin-bottom: 0;">Selecione os critérios para filtrar os pedidos.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_options = ['Todos'] + sorted(df_orders['pedido_status'].unique().tolist())
        status_filter = st.selectbox('Status do Pedido', status_options)
    
    with col2:
        state_options = ['Todos'] + sorted(df_orders['envio_estado'].unique().tolist())
        state_filter = st.selectbox('Estado', state_options)
    
    with col3:
        category_options = ['Todos'] + sorted(df_orders['categoria_produto'].unique().tolist())
        category_filter = st.selectbox('Categoria do Produto', category_options)
    
    # Apply filters
    filtered_orders = df_orders.copy()
    
    if status_filter != 'Todos':
        filtered_orders = filtered_orders[filtered_orders['pedido_status'] == status_filter]
    
    if state_filter != 'Todos':
        filtered_orders = filtered_orders[filtered_orders['envio_estado'] == state_filter]
    
    if category_filter != 'Todos':
        filtered_orders = filtered_orders[filtered_orders['categoria_produto'] == category_filter]
    
    # Display the filtered table
    st.dataframe(
        filtered_orders.sort_values('pedido_data', ascending=False),
        use_container_width=True,
        column_config={
            'pedido_id': 'ID do Pedido',
            'pedido_data': st.column_config.DateColumn('Data do Pedido'),
            'pedido_hora': 'Hora do Pedido',
            'pedido_status': 'Status',
            'envio_estado': 'Estado',
            'produto_nome': 'Produto',
            'produto_valor_unitario': st.column_config.NumberColumn('Valor Unitário', format="R$ %.2f"),
            'produto_quantidade': 'Quantidade',
            'produto_valor_total': st.column_config.NumberColumn('Valor Total', format="R$ %.2f"),
            'categoria_produto': 'Categoria',
            'tipo_venda': 'Tipo'
        },
        hide_index=True
    )
    
    # Summary of filtered data
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #4CAF50;">
        <h3 style="margin-top: 0; font-size: 1.2em;">Resumo dos Dados Filtrados</h3>
        <p style="margin-bottom: 0;">Estatísticas dos pedidos após aplicação dos filtros selecionados.</p>
    </div>
    """, unsafe_allow_html=True)
    
    filtered_summary = get_orders_summary(filtered_orders)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card("Total de Vendas", f"R$ {filtered_summary['total_vendas']:,.2f}", color="#4CAF50")
    
    with col2:
        metric_card("Total de Pedidos", f"{filtered_summary['total_pedidos']:,}", color="#2196F3")
    
    with col3:
        metric_card("Ticket Médio", f"R$ {filtered_summary['ticket_medio']:,.2f}", color="#FF9800")
    
    with col4:
        metric_card("Produtos Vendidos", f"{filtered_summary['produtos_vendidos']:,}", color="#9C27B0")
