import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from utils import load_and_process_data, get_orders_summary, get_ads_summary, filter_dataframe
import base64
import calendar
import locale

# Definir o locale para português brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

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

# CSS para estilização da página com responsividade mobile
def local_css():
    st.markdown("""
    <style>
    /* Estilos gerais */
    .main {
        padding-top: 1rem;
    }
    
    /* Estilo para as abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        min-height: 50px;
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
    
    /* Estilos de tipografia */
    h1, h2, h3 {
        font-family: 'Sans serif';
        font-weight: 700;
        color: #333;
    }
    
    /* Cards e métricas */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        overflow: hidden;
        height: 100%;
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
    
    /* Elementos estruturais */
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
    
    /* Gráficos */
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Cards de insights */
    .insight-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #4CAF50;
    }
    .insight-card h4 {
        margin-top: 0;
        color: #333;
    }
    .insight-card p {
        margin-bottom: 0;
        color: #555;
    }
    
    /* Tooltips e explicações */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltip-text {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    /* Responsividade para mobile */
    @media (max-width: 768px) {
        .row-widget.stButton {
            width: 100%;
        }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        .stDataFrame {
            overflow-x: auto;
        }
    }
    
    /* Tabelas mais legíveis em dispositivos móveis */
    .dataframe-container {
        overflow-x: auto;
        width: 100%;
    }
    
    /* Ajustes para gráficos em mobile */
    @media (max-width: 768px) {
        .stPlotlyChart > div {
            min-height: 350px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Funções de utilidade para análise e insights
def format_currency(value):
    """Formata valores monetários em reais"""
    return f"R$ {value:,.2f}"

def get_percentage_change(current_value, previous_value):
    """Calcula a variação percentual entre dois valores"""
    if previous_value == 0:
        return float('inf')
    return ((current_value - previous_value) / previous_value) * 100

def get_trend_icon(value):
    """Retorna ícone de tendência baseado no valor"""
    if value > 0:
        return "↗️"
    elif value < 0:
        return "↘️"
    else:
        return "➡️"

def get_trend_color(value):
    """Retorna cor de tendência baseado no valor"""
    if value > 0:
        return "#4CAF50"  # verde
    elif value < 0:
        return "#F44336"  # vermelho
    else:
        return "#9E9E9E"  # cinza

# Funções para componentes estilizados
def metric_card(title, value, delta=None, color="#7E57C2", tooltip=None):
    """Card personalizado para métricas com estilo melhorado"""
    # Definir cor do delta
    delta_color = "#4CAF50" if delta and delta > 0 else "#F44336" if delta and delta < 0 else "#9E9E9E"
    
    # Definir ícone de delta
    delta_icon = "↑" if delta and delta > 0 else "↓" if delta and delta < 0 else "→"
    
    # Construir o HTML do card
    html = f"""
    <div style="background-color: white; border-radius: 10px; padding: 15px; 
         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 15px; 
         border-left: 5px solid {color}; height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <h3 style="margin: 0; font-size: 1.1em; color: #555; font-weight: 600;">{title}</h3>
            {f'<div title="{tooltip}" style="cursor: help; color: #7E57C2; font-size: 0.9em;">ℹ️</div>' if tooltip else ''}
        </div>
        <div style="font-size: 1.8em; font-weight: 700; color: #333; margin: 10px 0 5px 0;">{value}</div>
        {f'<div style="color: {delta_color}; font-size: 0.9em;">{delta_icon} {abs(delta):.2f}%</div>' if delta is not None else ''}
    </div>
    """
    return st.markdown(html, unsafe_allow_html=True)

def insight_card(title, description, icon="💡", color="#4CAF50"):
    html = f"""
    <div style="background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
         margin-bottom: 20px; border-left: 5px solid {color};">
        <div style="display: flex; align-items: flex-start;">
            <div style="font-size: 1.5em; margin-right: 10px; color: {color};">{icon}</div>
            <div>
                <h4 style="margin-top: 0; margin-bottom: 8px; color: #333;">{title}</h4>
                <p style="margin: 0; color: #555; line-height: 1.5;">{description}</p>
            </div>
        </div>
    </div>
    """
    return st.markdown(html, unsafe_allow_html=True)

def explainer(title, explanation, is_expanded=False):
    """Componente de explicação expansível"""
    with st.expander(title, expanded=is_expanded):
        st.markdown(explanation)
        
def chart_with_explanation(fig, title, explanation):
    """Função para exibir gráfico com explicação mais destacada"""
    st.subheader(title)
    
    # Mostrar o gráfico com largura responsiva
    st.plotly_chart(fig, use_container_width=True)
    
    # Adicionar explicação em um card estilizado
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; 
         margin: 0 0 30px 0; border-left: 5px solid #7E57C2;">
        <div style="display: flex; align-items: flex-start;">
            <div style="font-size: 1.2em; margin-right: 8px; color: #7E57C2;">💡</div>
            <div style="color: #555; line-height: 1.5;">{explanation}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
    
    # Calcular métricas importantes
    roi = ((orders_summary['total_vendas'] - ads_summary['total_gasto']) / ads_summary['total_gasto']) * 100
    cpa = ads_summary['total_gasto'] / ads_summary['total_conversoes'] if ads_summary['total_conversoes'] > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            "Total de Vendas", 
            f"R$ {orders_summary['total_vendas']:,.2f}", 
            color="#4CAF50",
            tooltip="Valor total de todas as vendas realizadas em abril de 2025"
        )
    
    with col2:
        metric_card(
            "Total de Pedidos", 
            f"{orders_summary['total_pedidos']:,}", 
            color="#2196F3",
            tooltip="Número total de pedidos únicos realizados no período"
        )
    
    with col3:
        metric_card(
            "Ticket Médio", 
            f"R$ {orders_summary['ticket_medio']:,.2f}", 
            color="#FF9800",
            tooltip="Valor médio gasto por pedido (total de vendas ÷ total de pedidos)"
        )
    
    with col4:
        metric_card(
            "ROI Geral", 
            f"{roi:.2f}%", 
            color="#9C27B0",
            tooltip="Retorno sobre o investimento em marketing (quanto cada R$ investido retornou em vendas)"
        )
    
    # Principais insights
    st.markdown("### 📊 Principais Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        instituto_orders = filter_dataframe(df_orders, 'tipo_venda', 'Instituto')
        ecommerce_orders = filter_dataframe(df_orders, 'tipo_venda', 'Ecommerce')
        instituto_total = instituto_orders['produto_valor_total'].sum()
        ecommerce_total = ecommerce_orders['produto_valor_total'].sum()
        
        vendas_por_tipo = df_orders.groupby('tipo_venda')['produto_valor_total'].sum().reset_index()
        vendas_por_tipo.columns = ['Tipo', 'Valor Total']
        
        # Tipo que teve maior venda
        tipo_maior_venda = vendas_por_tipo.iloc[vendas_por_tipo['Valor Total'].argmax()]
        percentual_maior = (tipo_maior_venda['Valor Total'] / orders_summary['total_vendas']) * 100
        
        insight_card(
            f"Vendas de {tipo_maior_venda['Tipo']} representam {percentual_maior:.1f}% do faturamento",
            f"A área de {tipo_maior_venda['Tipo']} trouxe {format_currency(tipo_maior_venda['Valor Total'])} em receita, " +
            f"o que representa {percentual_maior:.1f}% do faturamento total de abril.",
            icon="💰"
        )
    
    with col2:
        # CTR e taxa de conversão
        insight_card(
            f"Taxa de conversão média: {ads_summary['taxa_conversao']:.2f}%",
            f"Para cada 100 cliques nos anúncios, {ads_summary['taxa_conversao']:.2f} resultaram em adições ao carrinho. " +
            f"O custo médio por aquisição (CPA) foi de {format_currency(cpa)}.",
            icon="🎯",
            color="#2196F3"
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Estado com mais vendas
        estado_mais_vendas = orders_summary['vendas_por_estado'].iloc[0]
        insight_card(
            f"{estado_mais_vendas['Estado']} é o estado com maior volume de vendas",
            f"As vendas em {estado_mais_vendas['Estado']} totalizaram {format_currency(estado_mais_vendas['Valor Total'])}, " +
            f"representando uma oportunidade importante para expansão regional.",
            icon="📍",
            color="#FF9800"
        )
    
    with col2:
        # Encontrar dia com maior venda
        vendas_diarias = df_orders.groupby('pedido_data')['produto_valor_total'].sum().reset_index()
        dia_maior_venda = vendas_diarias.iloc[vendas_diarias['produto_valor_total'].argmax()]
        dia_formatado = dia_maior_venda['pedido_data'].strftime('%d/%m/%Y')
        
        insight_card(
            f"Maior pico de vendas: {dia_formatado}",
            f"O dia com maior volume de vendas foi {dia_formatado}, com total de {format_currency(dia_maior_venda['produto_valor_total'])}. " +
            f"Isso representa {(dia_maior_venda['produto_valor_total']/orders_summary['total_vendas']*100):.1f}% das vendas mensais.",
            icon="📅",
            color="#9C27B0"
        )
    
    st.divider()
    
    # ROI Analysis
    col1, col2 = st.columns(2)
    
    with col1:
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
        
        chart_with_explanation(
            fig,
            "Receita vs. Investimento em Marketing",
            "Comparativo entre a receita total gerada e o valor investido em campanhas de marketing. " +
            f"Para cada R$ 1,00 investido em marketing, foram gerados R$ {roi/100+1:.2f} em vendas."
        )
    
    with col2:
        # Group by tipo_venda
        fig = px.pie(
            vendas_por_tipo,
            values='Valor Total',
            names='Tipo',
            title="Distribuição de Vendas",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        chart_with_explanation(
            fig,
            "Distribuição de Vendas por Tipo",
            "Proporção de vendas entre os segmentos de Instituto (cursos e workshops) e Ecommerce (cafés e produtos). " +
            f"O segmento de {tipo_maior_venda['Tipo']} representa a maior parte do faturamento."
        )
    
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
    
    # Análise de vendas por dia da semana e hora
    st.subheader("Padrões de Vendas por Dia da Semana e Hora")
    
    # Adicionar dias da semana e extrair hora
    df_orders_temporal = df_orders.copy()
    df_orders_temporal['dia_da_semana'] = df_orders_temporal['pedido_data'].dt.day_name()
    df_orders_temporal['hora'] = df_orders_temporal['pedido_hora'].str.split(':').str[0].astype(int)
    
    # Definir ordem dos dias da semana
    dias_semana_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dias_semana_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    mapa_dias = dict(zip(dias_semana_ordem, dias_semana_pt))
    df_orders_temporal['dia_da_semana_pt'] = df_orders_temporal['dia_da_semana'].map(mapa_dias)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Vendas por dia da semana
        vendas_por_dia_semana = df_orders_temporal.groupby('dia_da_semana_pt')['produto_valor_total'].sum().reset_index()
        # Reordenar para ordem dos dias da semana
        ordem_dias_pt = [mapa_dias[dia] for dia in dias_semana_ordem]
        vendas_por_dia_semana['dia_da_semana_pt'] = pd.Categorical(
            vendas_por_dia_semana['dia_da_semana_pt'], 
            categories=ordem_dias_pt, 
            ordered=True
        )
        vendas_por_dia_semana = vendas_por_dia_semana.sort_values('dia_da_semana_pt')
        
        # Encontrar dia da semana com maior venda
        dia_maior_vendas = vendas_por_dia_semana.iloc[vendas_por_dia_semana['produto_valor_total'].argmax()]
        
        fig = px.bar(
            vendas_por_dia_semana,
            x='dia_da_semana_pt',
            y='produto_valor_total',
            text_auto='.2s',
            title="Vendas por Dia da Semana",
            color='produto_valor_total',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            xaxis_title="Dia da Semana",
            yaxis_title="Valor Total (R$)",
            yaxis_tickprefix="R$ "
        )
        
        # Exibir gráfico com explicação
        st.plotly_chart(fig, use_container_width=True)
        
        # Adicionar explicação em um card estilizado
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; 
             margin: 0 0 20px 0; border-left: 5px solid #4CAF50;">
            <div style="display: flex; align-items: flex-start;">
                <div style="font-size: 1.2em; margin-right: 8px; color: #4CAF50;">📊</div>
                <div style="color: #555; line-height: 1.5;">
                    <strong>{dia_maior_vendas['dia_da_semana_pt']}</strong> é o dia da semana com maior volume de vendas, 
                    totalizando {format_currency(dia_maior_vendas['produto_valor_total'])}. Considere aumentar esforços de marketing 
                    e preparar estoque para este dia da semana.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Vendas por hora do dia
        vendas_por_hora = df_orders_temporal.groupby('hora')['produto_valor_total'].sum().reset_index()
        
        # Encontrar hora com maior venda
        hora_maior_vendas = vendas_por_hora.iloc[vendas_por_hora['produto_valor_total'].argmax()]
        
        # Formatar para exibir horário comercial
        vendas_por_hora['hora_formatada'] = vendas_por_hora['hora'].apply(lambda x: f"{x}:00")
        
        fig = px.line(
            vendas_por_hora,
            x='hora',
            y='produto_valor_total',
            markers=True,
            title="Vendas por Hora do Dia",
            labels={'hora': 'Hora do dia', 'produto_valor_total': 'Valor Total (R$)'}
        )
        fig.update_layout(
            xaxis_title="Hora do Dia",
            yaxis_title="Valor (R$)",
            yaxis_tickprefix="R$ ",
            xaxis_tickmode='linear',
            xaxis_tick0=0,
            xaxis_dtick=2,  # Mais espaçado para melhor visualização mobile
            height=350  # Altura fixa para melhor aspecto
        )
        
        # Exibir gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # Adicionar explicação em um card estilizado
        periodo = "manhã" if 6 <= hora_maior_vendas['hora'] <= 12 else "tarde" if 13 <= hora_maior_vendas['hora'] <= 18 else "noite"
        
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; 
             margin: 0 0 20px 0; border-left: 5px solid #FF9800;">
            <div style="display: flex; align-items: flex-start;">
                <div style="font-size: 1.2em; margin-right: 8px; color: #FF9800;">⏰</div>
                <div style="color: #555; line-height: 1.5;">
                    <strong>{hora_maior_vendas['hora']}h</strong> é o horário com maior volume de vendas, 
                    totalizando {format_currency(hora_maior_vendas['produto_valor_total'])}. Este pico no período da {periodo} 
                    sugere um padrão de compra que pode ser aproveitado em campanhas específicas.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Geographic distribution
    st.subheader("Distribuição Geográfica das Vendas")
    
    # Group by state
    vendas_por_estado = df_orders.groupby('envio_estado')['produto_valor_total'].sum().reset_index()
    vendas_por_estado.columns = ['Estado', 'Valor Total']
    vendas_por_estado = vendas_por_estado.sort_values('Valor Total', ascending=False)
    
    # Encontrar os 3 maiores estados
    top3_estados = vendas_por_estado.head(3)
    estados_destaque = ", ".join([f"{estado}" for estado in top3_estados['Estado'].values])
    percentual_top3 = (top3_estados['Valor Total'].sum() / vendas_por_estado['Valor Total'].sum()) * 100
    
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
        yaxis_tickprefix="R$ ",
        height=400  # Altura fixa para melhor visualização
    )
    
    # Exibir gráfico com explicação 
    st.plotly_chart(fig, use_container_width=True)
    
    # Adicionar explicação em um card estilizado
    estado_maior = vendas_por_estado.iloc[0]
    
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; 
         margin: 0 0 30px 0; border-left: 5px solid #7E57C2;">
        <div style="display: flex; align-items: flex-start;">
            <div style="font-size: 1.2em; margin-right: 8px; color: #7E57C2;">📍</div>
            <div style="color: #555; line-height: 1.5;">
                <strong>Concentração regional</strong>: Os estados de {estados_destaque} representam {percentual_top3:.1f}% 
                do total de vendas no período. <strong>{estado_maior['Estado']}</strong> lidera com 
                {format_currency(estado_maior['Valor Total'])}. Considere estratégias específicas 
                para fortalecer a presença nos estados de menor performance.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
            'adicoes_carrinho': 'sum'  # Mantemos o nome da coluna original do DataFrame
        }).reset_index()
        
        # Calculate CTR and conversion rate
        campanhas_por_tipo['ctr'] = (campanhas_por_tipo['cliques'] / campanhas_por_tipo['impressoes']) * 100
        campanhas_por_tipo['taxa_conversao'] = (campanhas_por_tipo['adicoes_carrinho'] / campanhas_por_tipo['cliques']) * 100
        
        # Encontrar campanha com maior investimento
        campanha_maior_invest = campanhas_por_tipo.iloc[campanhas_por_tipo['valor_gasto'].argmax()]
        
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
        
        # Exibir gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # Adicionar explicação em um card estilizado
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; 
             margin: 0 0 20px 0; border-left: 5px solid #2196F3;">
            <div style="display: flex; align-items: flex-start;">
                <div style="font-size: 1.2em; margin-right: 8px; color: #2196F3;">💼</div>
                <div style="color: #555; line-height: 1.5;">
                    A campanha de <strong>{campanha_maior_invest['tipo_campanha']}</strong> recebeu o maior investimento, 
                    totalizando {format_currency(campanha_maior_invest['valor_gasto'])}, o que corresponde a 
                    {(campanha_maior_invest['valor_gasto']/campanhas_por_tipo['valor_gasto'].sum()*100):.1f}% 
                    do orçamento total de marketing.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Encontrar campanha com maior taxa de conversão
        campanha_maior_conv = campanhas_por_tipo.iloc[campanhas_por_tipo['taxa_conversao'].argmax()]
        
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
        
        # Exibir gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # Adicionar explicação em um card estilizado
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; 
             margin: 0 0 20px 0; border-left: 5px solid #4CAF50;">
            <div style="display: flex; align-items: flex-start;">
                <div style="font-size: 1.2em; margin-right: 8px; color: #4CAF50;">📈</div>
                <div style="color: #555; line-height: 1.5;">
                    A campanha de <strong>{campanha_maior_conv['tipo_campanha']}</strong> apresentou a maior taxa de conversão: 
                    {campanha_maior_conv['taxa_conversao']:.2f}%. Isso significa que de cada 100 cliques, 
                    aproximadamente {campanha_maior_conv['taxa_conversao']:.2f} resultaram em adições ao carrinho, 
                    demonstrando maior efetividade nesse tipo de campanha.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------- INSTITUTO TAB ----------
with tab2:
    st.markdown("""
    <div class="tab-header">
        <h2>Instituto - Cursos e Workshops</h2>
        <p>Análise de desempenho da área educacional - cursos, workshops e oficinas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Explicação do que é a área Instituto
    explainer(
        "O que é a área de Instituto?",
        """
        A área de **Instituto** engloba todos os produtos educacionais oferecidos, incluindo:
        - Cursos presenciais de barista
        - Workshops de degustação de café
        - Oficinas sensoriais e cupping
        - Cursos de métodos filtrados
        - Aulas e introduções aos cafés especiais
        
        Esta área é fundamental para a construção da marca como autoridade no mercado de cafés especiais.
        """,
        is_expanded=False
    )
    
    # Filter data for Instituto
    instituto_orders = filter_dataframe(df_orders, 'tipo_venda', 'Instituto')
    instituto_ads = filter_dataframe(df_ads, 'tipo_campanha', 'Instituto')
    
    instituto_orders_summary = get_orders_summary(instituto_orders)
    instituto_ads_summary = get_ads_summary(instituto_ads)
    
    # Calcular métricas adicionais
    if instituto_ads_summary['total_gasto'] > 0:
        roi_instituto = ((instituto_orders_summary['total_vendas'] - instituto_ads_summary['total_gasto']) / 
                         instituto_ads_summary['total_gasto']) * 100
        cpa_instituto = instituto_ads_summary['total_gasto'] / instituto_ads_summary['total_conversoes'] if instituto_ads_summary['total_conversoes'] > 0 else 0
    else:
        roi_instituto = 0
        cpa_instituto = 0
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            "Total de Vendas", 
            f"R$ {instituto_orders_summary['total_vendas']:,.2f}", 
            color="#4CAF50",
            tooltip="Valor total de vendas de cursos e workshops em abril"
        )
    
    with col2:
        metric_card(
            "Total de Pedidos", 
            f"{instituto_orders_summary['total_pedidos']:,}", 
            color="#2196F3",
            tooltip="Número de matrículas e inscrições realizadas"
        )
    
    with col3:
        metric_card(
            "Ticket Médio", 
            f"R$ {instituto_orders_summary['ticket_medio']:,.2f}", 
            color="#FF9800",
            tooltip="Valor médio gasto por inscrição em cursos"
        )
    
    with col4:
        if instituto_ads_summary['total_gasto'] > 0:
            metric_card(
                "ROI Instituto", 
                f"{roi_instituto:.2f}%", 
                color="#9C27B0",
                tooltip="Retorno sobre o investimento em marketing para a área educacional"
            )
        else:
            metric_card(
                "ROI Instituto", 
                "N/A", 
                color="#9C27B0",
                tooltip="Não há dados de investimento em marketing para cálculo do ROI"
            )
    
    # Insights específicos do Instituto
    st.markdown("### 🎓 Insights da Área Educacional")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Encontrar curso mais popular
        cursos = instituto_orders[instituto_orders['categoria_produto'] == 'Cursos e Workshops']
        cursos_populares = cursos.groupby('produto_nome').agg({
            'produto_quantidade': 'sum',
            'produto_valor_total': 'sum'
        }).reset_index().sort_values('produto_valor_total', ascending=False)
        
        if not cursos_populares.empty:
            curso_mais_vendido = cursos_populares.iloc[0]
            insight_card(
                f"Curso mais popular: {curso_mais_vendido['produto_nome'].split('|')[0].strip()}",
                f"Este curso gerou {format_currency(curso_mais_vendido['produto_valor_total'])} em receita " +
                f"com {curso_mais_vendido['produto_quantidade']} inscrições.",
                icon="🏆"
            )
        
    with col2:
        # Análise da efetividade das campanhas
        if instituto_ads_summary['total_gasto'] > 0:
            insight_card(
                f"Campanhas de Instituto: {instituto_ads_summary['taxa_conversao']:.2f}% de conversão",
                f"As campanhas para cursos tiveram um custo médio por aquisição (CPA) de {format_currency(cpa_instituto)}. " +
                f"Para cada 100 cliques, {instituto_ads_summary['taxa_conversao']:.2f} se converteram em vendas.",
                icon="📢",
                color="#2196F3"
            )
        else:
            insight_card(
                "Sem dados de campanhas para Instituto",
                "Não há registros de campanhas específicas para a área educacional no período analisado.",
                icon="ℹ️",
                color="#9E9E9E"
            )
    
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
    
    # Explicação do que é a área Ecommerce
    explainer(
        "O que é a área de Ecommerce?",
        """
        A área de **Ecommerce** abrange todos os produtos físicos à venda, incluindo:
        - Cafés especiais em diversos formatos (grãos, moído)
        - Kits e combos de produtos
        - Acessórios como xícaras e itens para preparo
        - Produtos comestíveis (doces e outros alimentos)
        - Itens de arte e decoração relacionados à cultura do café
        
        Este segmento é responsável pela maior parte das vendas recorrentes da empresa.
        """,
        is_expanded=False
    )
    
    # Filter data for Ecommerce
    ecommerce_orders = filter_dataframe(df_orders, 'tipo_venda', 'Ecommerce')
    ecommerce_ads = filter_dataframe(df_ads, 'tipo_campanha', 'Ecommerce')
    
    ecommerce_orders_summary = get_orders_summary(ecommerce_orders)
    ecommerce_ads_summary = get_ads_summary(ecommerce_ads)
    
    # Calcular métricas adicionais
    if ecommerce_ads_summary['total_gasto'] > 0:
        roi_ecommerce = ((ecommerce_orders_summary['total_vendas'] - ecommerce_ads_summary['total_gasto']) / 
                        ecommerce_ads_summary['total_gasto']) * 100
        cpa_ecommerce = ecommerce_ads_summary['total_gasto'] / ecommerce_ads_summary['total_conversoes'] if ecommerce_ads_summary['total_conversoes'] > 0 else 0
    else:
        roi_ecommerce = 0
        cpa_ecommerce = 0
    
    # Calcular produtos vendidos
    produtos_vendidos = ecommerce_orders['produto_quantidade'].sum()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            "Total de Vendas", 
            f"R$ {ecommerce_orders_summary['total_vendas']:,.2f}", 
            color="#4CAF50",
            tooltip="Valor total de vendas de produtos físicos em abril"
        )
    
    with col2:
        metric_card(
            "Total de Pedidos", 
            f"{ecommerce_orders_summary['total_pedidos']:,}", 
            color="#2196F3",
            tooltip="Número de pedidos únicos de produtos físicos"
        )
    
    with col3:
        metric_card(
            "Produtos Vendidos", 
            f"{produtos_vendidos:,}", 
            color="#FF9800",
            tooltip="Quantidade total de itens vendidos"
        )
    
    with col4:
        if ecommerce_ads_summary['total_gasto'] > 0:
            metric_card(
                "ROI Ecommerce", 
                f"{roi_ecommerce:.2f}%", 
                color="#9C27B0",
                tooltip="Retorno sobre o investimento em marketing para produtos físicos"
            )
        else:
            metric_card(
                "ROI Ecommerce", 
                "N/A", 
                color="#9C27B0",
                tooltip="Não há dados de investimento em marketing para cálculo do ROI"
            )
    
    # Insights específicos do Ecommerce
    st.markdown("### 🛒 Insights de Vendas de Produtos")
    
    # Agrupar por categorias para análise
    vendas_por_categoria = ecommerce_orders.groupby('categoria_produto')['produto_valor_total'].sum().reset_index()
    vendas_por_categoria.columns = ['Categoria', 'Valor Total']
    vendas_por_categoria = vendas_por_categoria.sort_values('Valor Total', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Categoria mais vendida
        if not vendas_por_categoria.empty:
            categoria_mais_vendida = vendas_por_categoria.iloc[0]
            percentual_categoria = (categoria_mais_vendida['Valor Total'] / ecommerce_orders_summary['total_vendas']) * 100
            
            insight_card(
                f"Categoria mais vendida: {categoria_mais_vendida['Categoria']}",
                f"Essa categoria representa {percentual_categoria:.1f}% das vendas de Ecommerce, " +
                f"totalizando {format_currency(categoria_mais_vendida['Valor Total'])}.",
                icon="🥇"
            )
        
    with col2:
        # Análise de estados/regiões
        vendas_por_estado = ecommerce_orders.groupby('envio_estado')['produto_valor_total'].sum().reset_index()
        vendas_por_estado = vendas_por_estado.sort_values('produto_valor_total', ascending=False)
        
        if not vendas_por_estado.empty:
            estado_mais_vendas = vendas_por_estado.iloc[0]
            percentual_estado = (estado_mais_vendas['produto_valor_total'] / ecommerce_orders_summary['total_vendas']) * 100
            
            insight_card(
                f"Principal mercado: {estado_mais_vendas['envio_estado']}",
                f"O estado de {estado_mais_vendas['envio_estado']} representa {percentual_estado:.1f}% das vendas " +
                f"de produtos físicos, com {format_currency(estado_mais_vendas['produto_valor_total'])}.",
                icon="📍",
                color="#2196F3"
            )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Produto mais vendido
        produtos_mais_vendidos = ecommerce_orders.groupby('produto_nome').agg({
            'produto_quantidade': 'sum',
            'produto_valor_total': 'sum'
        }).reset_index().sort_values('produto_valor_total', ascending=False)
        
        if not produtos_mais_vendidos.empty:
            produto_mais_vendido = produtos_mais_vendidos.iloc[0]
            produto_nome_curto = produto_mais_vendido['produto_nome'].split('-')[0].strip()
            
            insight_card(
                f"Produto mais rentável: {produto_nome_curto}",
                f"Gerou {format_currency(produto_mais_vendido['produto_valor_total'])} em receita " +
                f"com {produto_mais_vendido['produto_quantidade']} unidades vendidas.",
                icon="⭐",
                color="#FF9800"
            )
    
    with col2:
        # Campanhas de marketing
        if ecommerce_ads_summary['total_gasto'] > 0:
            roi_texto = "positivo" if roi_ecommerce > 0 else "negativo"
            
            # Verificar se a chave existe
            if 'total_conversoes' in ecommerce_ads_summary:
                conversoes_text = f"{ecommerce_ads_summary['total_conversoes']} conversões"
            else:
                conversoes_text = "conversões (dados não disponíveis)"
            
            insight_card(
                f"Campanhas: ROI {roi_texto} de {roi_ecommerce:.1f}%",
                f"As campanhas para produtos geraram {conversoes_text} " +
                f"com taxa de {ecommerce_ads_summary['taxa_conversao']:.2f}%. CPA de {format_currency(cpa_ecommerce)}.",
                icon="📊",
                color="#9C27B0"
            )
        else:
            insight_card(
                "Campanhas: dados insuficientes",
                "Não há informações suficientes sobre as campanhas de marketing para produtos.",
                icon="ℹ️",
                color="#9E9E9E"
            )
    
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
    
    # Explicação da tabela de pedidos
    explainer(
        "Como utilizar esta seção",
        """
        Esta seção permite uma análise detalhada dos pedidos realizados em abril de 2025. Você pode:
        
        1. **Filtrar os pedidos** usando os controles abaixo para focar em segmentos específicos
        2. **Visualizar todos os detalhes** de cada pedido na tabela interativa
        3. **Analisar estatísticas** geradas automaticamente a partir dos filtros aplicados
        
        **Dica:** Combine diferentes filtros para análises mais específicas, como "vendas de cafés no estado de SP" ou 
        "pedidos de cursos com status 'entregue'".
        """,
        is_expanded=True
    )
    
    # Filters
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #7E57C2;">
        <h3 style="margin-top: 0; font-size: 1.2em;">Filtros de Pedidos</h3>
        <p style="margin-bottom: 0;">Selecione os critérios abaixo para filtrar os dados de pedidos.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_options = ['Todos'] + sorted(df_orders['tipo_venda'].unique().tolist())
        tipo_filter = st.selectbox('Tipo de Negócio', tipo_options, 
                                  help="Filtre por Instituto (cursos/workshops) ou Ecommerce (produtos)")
        
        status_options = ['Todos'] + sorted(df_orders['pedido_status'].unique().tolist())
        status_filter = st.selectbox('Status do Pedido', status_options,
                                    help="Status atual do pedido (entregue, em separação, etc.)")
    
    with col2:
        state_options = ['Todos'] + sorted(df_orders['envio_estado'].unique().tolist())
        state_filter = st.selectbox('Estado', state_options,
                                   help="Estado brasileiro de destino do pedido")
        
        category_options = ['Todos'] + sorted(df_orders['categoria_produto'].unique().tolist())
        category_filter = st.selectbox('Categoria do Produto', category_options,
                                      help="Categoria do produto vendido")
    
    # Pesquisa por palavra-chave
    keyword_filter = st.text_input('Pesquisar por palavra-chave no nome do produto', 
                                  placeholder="Ex: Café, Curso, Barista...",
                                  help="Digite uma palavra para buscar nos nomes dos produtos")
    
    # Apply filters
    filtered_orders = df_orders.copy()
    
    if tipo_filter != 'Todos':
        filtered_orders = filtered_orders[filtered_orders['tipo_venda'] == tipo_filter]
    
    if status_filter != 'Todos':
        filtered_orders = filtered_orders[filtered_orders['pedido_status'] == status_filter]
    
    if state_filter != 'Todos':
        filtered_orders = filtered_orders[filtered_orders['envio_estado'] == state_filter]
    
    if category_filter != 'Todos':
        filtered_orders = filtered_orders[filtered_orders['categoria_produto'] == category_filter]
    
    if keyword_filter:
        filtered_orders = filtered_orders[filtered_orders['produto_nome'].str.contains(keyword_filter, case=False)]
    
    # Calcular número de linhas após filtro
    num_rows = len(filtered_orders)
    
    # Display the filtered table
    st.markdown(f"##### Mostrando {num_rows} resultados:")
    
    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
    st.dataframe(
        filtered_orders.sort_values('pedido_data', ascending=False),
        use_container_width=True,
        column_config={
            'pedido_id': st.column_config.NumberColumn('ID do Pedido', format="%d"),
            'pedido_data': st.column_config.DateColumn('Data do Pedido', format="DD/MM/YYYY"),
            'pedido_hora': 'Hora do Pedido',
            'pedido_status': st.column_config.Column('Status', help="Situação atual do pedido"),
            'envio_estado': st.column_config.Column('Estado', help="UF de destino"),
            'produto_nome': st.column_config.Column('Produto', help="Nome do produto ou serviço"),
            'produto_valor_unitario': st.column_config.NumberColumn('Valor Unitário', format="R$ %.2f"),
            'produto_quantidade': st.column_config.NumberColumn('Quantidade', format="%d"),
            'produto_valor_total': st.column_config.NumberColumn('Valor Total', format="R$ %.2f"),
            'categoria_produto': st.column_config.Column('Categoria', help="Categoria do produto"),
            'tipo_venda': st.column_config.Column('Tipo', help="Instituto ou Ecommerce")
        },
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if num_rows == 0:
        st.info("Nenhum pedido encontrado com os filtros selecionados. Tente ajustar os critérios de busca.")
    
    st.divider()
    
    # Summary of filtered data
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #4CAF50;">
        <h3 style="margin-top: 0; font-size: 1.2em;">Resumo dos Dados Filtrados</h3>
        <p style="margin-bottom: 0;">Estatísticas dos pedidos após aplicação dos filtros selecionados.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if num_rows > 0:
        filtered_summary = get_orders_summary(filtered_orders)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric_card(
                "Total de Vendas", 
                f"R$ {filtered_summary['total_vendas']:,.2f}", 
                color="#4CAF50",
                tooltip="Valor total de vendas nos pedidos filtrados"
            )
        
        with col2:
            metric_card(
                "Total de Pedidos", 
                f"{filtered_summary['total_pedidos']:,}", 
                color="#2196F3",
                tooltip="Número de pedidos únicos nos resultados filtrados"
            )
        
        with col3:
            metric_card(
                "Ticket Médio", 
                f"R$ {filtered_summary['ticket_medio']:,.2f}", 
                color="#FF9800",
                tooltip="Valor médio por pedido nos resultados filtrados"
            )
        
        with col4:
            metric_card(
                "Produtos Vendidos", 
                f"{filtered_summary['produtos_vendidos']:,}", 
                color="#9C27B0",
                tooltip="Quantidade total de itens nos pedidos filtrados"
            )
        
        # Mostrar gráfico rápido baseado nos filtros
        if num_rows >= 5:  # Só mostrar gráfico se houver dados suficientes
            st.subheader("Visualização Rápida dos Dados Filtrados")
            
            visualization_type = st.radio(
                "Escolha o tipo de visualização:",
                ["Vendas por Data", "Vendas por Estado", "Vendas por Categoria"],
                horizontal=True
            )
            
            if visualization_type == "Vendas por Data":
                vendas_diarias = filtered_orders.groupby('pedido_data')['produto_valor_total'].sum().reset_index()
                
                fig = px.line(
                    vendas_diarias,
                    x='pedido_data',
                    y='produto_valor_total',
                    markers=True,
                    title="Vendas Diárias - Dados Filtrados",
                    labels={'pedido_data': 'Data', 'produto_valor_total': 'Valor Total (R$)'}
                )
                fig.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Valor (R$)",
                    yaxis_tickprefix="R$ "
                )
                st.plotly_chart(fig, use_container_width=True)
                
            elif visualization_type == "Vendas por Estado":
                vendas_por_estado = filtered_orders.groupby('envio_estado')['produto_valor_total'].sum().reset_index()
                vendas_por_estado = vendas_por_estado.sort_values('produto_valor_total', ascending=False)
                
                fig = px.bar(
                    vendas_por_estado,
                    x='envio_estado',
                    y='produto_valor_total',
                    text_auto='.2s',
                    title="Vendas por Estado - Dados Filtrados",
                    color='envio_estado'
                )
                fig.update_layout(
                    xaxis_title="Estado",
                    yaxis_title="Valor (R$)",
                    yaxis_tickprefix="R$ "
                )
                st.plotly_chart(fig, use_container_width=True)
                
            else:  # Vendas por Categoria
                vendas_por_categoria = filtered_orders.groupby('categoria_produto')['produto_valor_total'].sum().reset_index()
                vendas_por_categoria = vendas_por_categoria.sort_values('produto_valor_total', ascending=False)
                
                fig = px.pie(
                    vendas_por_categoria,
                    values='produto_valor_total',
                    names='categoria_produto',
                    title="Vendas por Categoria - Dados Filtrados"
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aplique filtros que retornem dados para visualizar o resumo estatístico.")
