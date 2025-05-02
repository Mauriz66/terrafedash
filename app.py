import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from utils import load_and_process_data, get_orders_summary, get_ads_summary, filter_dataframe

# Page configuration
st.set_page_config(
    page_title="Dashboard de Vendas e Marketing - Abril 2025",
    page_icon="📊",
    layout="wide",
)

# Load and process data
@st.cache_data
def get_data():
    return load_and_process_data()

df_ads, df_orders = get_data()

# Title
st.title("📊 Dashboard de Vendas e Marketing - Abril 2025")

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Geral", "Instituto", "Ecommerce", "Tabela de Pedidos"])

# ---------- GENERAL TAB ----------
with tab1:
    st.header("Visão Geral")
    
    # Summary metrics
    orders_summary = get_orders_summary(df_orders)
    ads_summary = get_ads_summary(df_ads)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Vendas", f"R$ {orders_summary['total_vendas']:,.2f}")
    
    with col2:
        st.metric("Total de Pedidos", f"{orders_summary['total_pedidos']}")
    
    with col3:
        st.metric("Ticket Médio", f"R$ {orders_summary['ticket_medio']:,.2f}")
    
    with col4:
        st.metric("Investimento em Campanhas", f"R$ {ads_summary['total_gasto']:,.2f}")
    
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
    st.header("Instituto - Cursos e Workshops")
    
    # Filter data for Instituto
    instituto_orders = filter_dataframe(df_orders, 'tipo_venda', 'Instituto')
    instituto_ads = filter_dataframe(df_ads, 'tipo_campanha', 'Instituto')
    
    instituto_orders_summary = get_orders_summary(instituto_orders)
    instituto_ads_summary = get_ads_summary(instituto_ads)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Vendas", f"R$ {instituto_orders_summary['total_vendas']:,.2f}")
    
    with col2:
        st.metric("Total de Pedidos", f"{instituto_orders_summary['total_pedidos']}")
    
    with col3:
        st.metric("Ticket Médio", f"R$ {instituto_orders_summary['ticket_medio']:,.2f}")
    
    with col4:
        st.metric("Investimento em Campanhas", f"R$ {instituto_ads_summary['total_gasto']:,.2f}")
    
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
    st.header("Ecommerce - Cafés e Produtos")
    
    # Filter data for Ecommerce
    ecommerce_orders = filter_dataframe(df_orders, 'tipo_venda', 'Ecommerce')
    ecommerce_ads = filter_dataframe(df_ads, 'tipo_campanha', 'Ecommerce')
    
    ecommerce_orders_summary = get_orders_summary(ecommerce_orders)
    ecommerce_ads_summary = get_ads_summary(ecommerce_ads)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Vendas", f"R$ {ecommerce_orders_summary['total_vendas']:,.2f}")
    
    with col2:
        st.metric("Total de Pedidos", f"{ecommerce_orders_summary['total_pedidos']}")
    
    with col3:
        st.metric("Ticket Médio", f"R$ {ecommerce_orders_summary['ticket_medio']:,.2f}")
    
    with col4:
        st.metric("Investimento em Campanhas", f"R$ {ecommerce_ads_summary['total_gasto']:,.2f}")
    
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
    st.header("Tabela de Pedidos")
    
    # Filters
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
    st.subheader("Resumo dos Dados Filtrados")
    
    filtered_summary = get_orders_summary(filtered_orders)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Vendas", f"R$ {filtered_summary['total_vendas']:,.2f}")
    
    with col2:
        st.metric("Total de Pedidos", f"{filtered_summary['total_pedidos']}")
    
    with col3:
        st.metric("Ticket Médio", f"R$ {filtered_summary['ticket_medio']:,.2f}")
    
    with col4:
        st.metric("Produtos Vendidos", f"{filtered_summary['produtos_vendidos']}")
