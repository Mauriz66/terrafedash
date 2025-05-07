import pandas as pd
import numpy as np
import re
import os
from datetime import datetime

def load_and_process_data():
    """
    Load and process both CSV files
    Returns processed dataframes for ads and orders
    """
    # Determine path
    path = os.path.join(os.path.dirname(__file__), 'attached_assets')
    
    # Load ad campaign data
    ads_path = os.path.join(path, 'adsabril.csv')
    df_ads = pd.read_csv(ads_path, sep=';')
    
    # Load order data
    orders_path = os.path.join(path, 'pedidosabril.csv')
    df_orders = pd.read_csv(orders_path, sep=';')
    
    # Process ad campaign data
    df_ads = process_ad_data(df_ads)
    
    # Process order data
    df_orders = process_order_data(df_orders)
    
    return df_ads, df_orders

def process_ad_data(df):
    """
    Process advertising data
    """
    # Rename columns to be more user-friendly
    df.columns = [
        'data_inicio', 'data_fim', 'nome_campanha', 'alcance', 'impressoes',
        'cpm', 'cliques', 'cpc', 'views_pagina', 'custo_view_pagina',
        'adicoes_carrinho', 'custo_adicao_carrinho', 'valor_conversao_carrinho',
        'valor_gasto'
    ]
    
    # Convert date columns to datetime
    df['data_inicio'] = pd.to_datetime(df['data_inicio'], format='%Y-%m-%d')
    df['data_fim'] = pd.to_datetime(df['data_fim'], format='%Y-%m-%d')
    
    # Convert numeric columns to appropriate types
    numeric_columns = ['alcance', 'impressoes', 'cpm', 'cliques', 'cpc', 
                      'views_pagina', 'custo_view_pagina', 'adicoes_carrinho', 
                      'custo_adicao_carrinho', 'valor_conversao_carrinho', 'valor_gasto']
    
    for col in numeric_columns:
        # Replace comma with dot in numeric values if needed
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
    
    # Extract campaign type
    df['tipo_campanha'] = df['nome_campanha'].apply(
        lambda x: 'Instituto' if '[INSTITUTO]' in x else 'Ecommerce'
    )
    
    # Calculate metrics
    df['taxa_conversao'] = (df['adicoes_carrinho'] / df['cliques']) * 100
    df['roi'] = ((df['valor_conversao_carrinho'] - df['valor_gasto']) / df['valor_gasto']) * 100
    
    return df

def process_order_data(df):
    """
    Process order data
    """
    # Rename columns to be more user-friendly
    df.columns = [
        'pedido_id', 'pedido_data', 'pedido_hora', 'pedido_status', 
        'envio_estado', 'produto_nome', 'produto_valor_unitario', 
        'produto_quantidade', 'produto_valor_total'
    ]
    
    # Convert data types
    df['pedido_id'] = df['pedido_id'].astype(int)
    
    # Handle numeric columns with comma as decimal separator
    numeric_columns = ['produto_valor_unitario', 'produto_valor_total']
    for col in numeric_columns:
        df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
    
    df['produto_quantidade'] = df['produto_quantidade'].astype(int)
    
    # Convert date to datetime
    df['pedido_data'] = pd.to_datetime(df['pedido_data'], format='%d/%m/%Y')
    
    # Extract categories
    df['categoria_produto'] = df['produto_nome'].apply(categorize_product)
    
    # Add tipo_venda column (Instituto or Ecommerce)
    df['tipo_venda'] = df['categoria_produto'].apply(
        lambda x: 'Instituto' if x == 'Cursos e Workshops' else 'Ecommerce'
    )
    
    return df

def categorize_product(product_name):
    """
    Categorize products based on their names
    """
    if re.search(r'\b(Curso|Oficina|Workshop)\b', product_name, re.IGNORECASE):
        return 'Cursos e Workshops'
    elif 'Café' in product_name:
        return 'Café'
    elif 'Kit' in product_name:
        return 'Kits'
    elif 'Xícara' in product_name:
        return 'Acessórios'
    elif 'Aquarelas' in product_name:
        return 'Arte'
    elif 'Doce' in product_name:
        return 'Alimentos'
    else:
        return 'Outros'

def get_orders_summary(df_orders):
    """
    Calculate summary statistics for orders
    """
    total_pedidos = df_orders['pedido_id'].nunique()
    total_vendas = df_orders['produto_valor_total'].sum()
    ticket_medio = total_vendas / total_pedidos
    produtos_vendidos = df_orders['produto_quantidade'].sum()
    
    # Status counts
    status_counts = df_orders.groupby('pedido_status')['pedido_id'].nunique().reset_index()
    status_counts.columns = ['Status', 'Contagem']
    
    # Vendas por estado
    vendas_por_estado = df_orders.groupby('envio_estado')['produto_valor_total'].sum().reset_index()
    vendas_por_estado.columns = ['Estado', 'Valor Total']
    
    # Vendas por categoria
    vendas_por_categoria = df_orders.groupby('categoria_produto')['produto_valor_total'].sum().reset_index()
    vendas_por_categoria.columns = ['Categoria', 'Valor Total']
    
    # Vendas por dia
    vendas_por_dia = df_orders.groupby('pedido_data')['produto_valor_total'].sum().reset_index()
    vendas_por_dia.columns = ['Data', 'Valor Total']
    
    return {
        'total_pedidos': total_pedidos,
        'total_vendas': total_vendas,
        'ticket_medio': ticket_medio,
        'produtos_vendidos': produtos_vendidos,
        'status_counts': status_counts,
        'vendas_por_estado': vendas_por_estado,
        'vendas_por_categoria': vendas_por_categoria,
        'vendas_por_dia': vendas_por_dia
    }

def get_ads_summary(df_ads):
    """
    Calculate summary statistics for ad campaigns
    """
    total_gasto = df_ads['valor_gasto'].sum()
    total_impressoes = df_ads['impressoes'].sum()
    total_cliques = df_ads['cliques'].sum()
    total_conversoes = df_ads['adicoes_carrinho'].sum()
    
    ctr = (total_cliques / total_impressoes) * 100 if total_impressoes > 0 else 0
    taxa_conversao = (total_conversoes / total_cliques) * 100 if total_cliques > 0 else 0
    cpm_medio = df_ads['cpm'].mean()
    cpc_medio = df_ads['cpc'].mean()
    
    # Gasto por tipo de campanha
    gasto_por_tipo = df_ads.groupby('tipo_campanha')['valor_gasto'].sum().reset_index()
    gasto_por_tipo.columns = ['Tipo', 'Valor Gasto']
    
    # Conversões por tipo de campanha
    conv_por_tipo = df_ads.groupby('tipo_campanha')['adicoes_carrinho'].sum().reset_index()
    conv_por_tipo.columns = ['Tipo', 'Conversões']
    
    return {
        'total_gasto': total_gasto,
        'total_impressoes': total_impressoes,
        'total_cliques': total_cliques,
        'total_conversoes': total_conversoes,
        'ctr': ctr,
        'taxa_conversao': taxa_conversao,
        'cpm_medio': cpm_medio,
        'cpc_medio': cpc_medio,
        'gasto_por_tipo': gasto_por_tipo,
        'conv_por_tipo': conv_por_tipo
    }

def filter_dataframe(df, column, value):
    """
    Filter dataframe based on a column value
    """
    return df[df[column] == value]
