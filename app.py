import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA WEB
st.set_page_config(page_title="Dashboard Comercial", layout="wide")
st.title("📊 Dashboard - Performance Comercial")
st.markdown("Análise estratégica de vendas dos últimos 2 anos")

# 2. CARREGAMENTO E TRATAMENTO DOS DADOS
@st.cache_data # Armazena em cache para o app ficar ultra rápido
def carregar_dados():
    # Substitua pelos caminhos corretos dos seus arquivos
    df_pedidos = pd.read_excel("Base_Laticinios_Ficticia_V2.xlsx", sheet_name="Pedidos")
    df_produtos = pd.read_excel("Base_Laticinios_Ficticia_V2.xlsx", sheet_name="Produtos")
    
    # Garantir formato de data
    df_pedidos['Data Pedido'] = pd.to_datetime(df_pedidos['Data Pedido'])
    
    # Trazer a Categoria e Gramatura da planilha de Produtos para a de Pedidos (Caso não tenha)
    if 'Categoria' not in df_pedidos.columns:
        df_pedidos = df_pedidos.merge(df_produtos[['Cod Produto', 'Categoria', 'Gramatura']], on='Cod Produto', how='left')
        
    return df_pedidos

try:
    df = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar a planilha. Verifique o nome do arquivo. Erro: {e}")
    st.stop()

# 3. FILTROS NA BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.header("Filtros Avançados")

# --- FILTRO DE PERÍODO (DATA ESPECÍFICA) ---
data_minima = df['Data Pedido'].min().date()
data_maxima = df['Data Pedido'].max().date()

periodo_selecionado = st.sidebar.date_input(
    "Selecione o Período",
    value=(data_minima, data_maxima), # Valor inicial: pega toda a base
    min_value=data_minima,
    max_value=data_maxima
)

# --- FILTRO DE REGIÃO ---
regiao_selecionada = st.sidebar.multiselect(
    "Selecione a Região da Loja", 
    options=df['Região Loja'].unique(), 
    default=df['Região Loja'].unique()
)

# --- FILTRO DE CATEGORIAS ---
categorias_disponiveis = sorted(df['Categoria'].dropna().unique())
categorias_selecionadas = st.sidebar.multiselect(
    "Selecione as Categorias",
    options=categorias_disponiveis,
    default=categorias_disponiveis
)

# --- FILTRO DE PRODUTOS (DIPAMICAMENTE FILTRADO POR CATEGORIA) ---
# Se o usuário escolher categorias, mostramos apenas os produtos delas
if categorias_selecionadas:
    produtos_disponiveis = sorted(df[df['Categoria'].isin(categorias_selecionadas)]['Produto'].unique())
else:
    produtos_disponiveis = sorted(df['Produto'].unique())

produtos_selecionados = st.sidebar.multiselect(
    "Selecione os Produtos",
    options=produtos_disponiveis,
    default=produtos_disponiveis
)

# ==========================================
# APLICANDO OS FILTROS NOS DADOS
# ==========================================
# 1. Aplicando filtro de data com segurança (Garante que o usuário escolheu início e fim no calendário)
if isinstance(periodo_selecionado, tuple) and len(periodo_selecionado) == 2:
    data_inicio, data_fim = periodo_selecionado
    df_filtrado = df[(df['Data Pedido'].dt.date >= data_inicio) & (df['Data Pedido'].dt.date <= data_fim)]
else:
    df_filtrado = df.copy()

# 2. Aplicando os filtros de Texto
df_filtrado = df_filtrado[
    (df_filtrado['Região Loja'].isin(regiao_selecionada)) &
    (df_filtrado['Categoria'].isin(categorias_selecionadas)) &
    (df_filtrado['Produto'].isin(produtos_selecionados))
]


# ==========================================
# 4. CÁLCULO DAS MÉTRICAS MACRO (KPIs)
# ==========================================
faturamento_total = df_filtrado['Valor Total Pedido'].sum()
total_transacoes = len(df_filtrado)
total_itens = df_filtrado['Qtd Caixas'].sum() + df_filtrado['Qtd Unidades'].sum()

# Exibindo os KPIs em colunas de destaque
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
kpi2.metric("Total de Vendas (Linhas)", f"{total_transacoes:,}".replace(",", "."))
kpi3.metric("Volume Total de Itens", f"{total_itens:,}".replace(",", "."))

st.markdown("---")

# ==========================================
# 5. CRIAÇÃO DAS ABAS DE VISÃO
# ==========================================

aba1, aba2, aba3 = st.tabs(["📈 Evolução & Regiões", "👥 Análise de Clientes", "📦 Análise de Produtos"])

# ================= TAB 1: EVOLUÇÃO E GEOGRAFIA =================
with aba1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Faturamento Mensal ao Longo do Tempo")
        if not df_filtrado.empty:
            df_mes = df_filtrado.groupby(df_filtrado['Data Pedido'].dt.to_period('M'))['Valor Total Pedido'].sum().reset_index()
            df_mes['Data Pedido'] = df_mes['Data Pedido'].astype(str)
            fig_linha = px.line(df_mes, x='Data Pedido', y='Valor Total Pedido', labels={'Valor Total Pedido': 'Faturamento', 'Data Pedido': 'Mês'}, markers=True)
            # ADICIONADO KEY ÚNICA AQUI
            st.plotly_chart(fig_linha, use_container_width=True, key="grafico_linha_evolucao")
        else:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
        
    with col2:
        st.subheader("Faturamento por Região da Loja")
        if not df_filtrado.empty:
            df_regiao = df_filtrado.groupby('Região Loja')['Valor Total Pedido'].sum().reset_index()
            fig_pizza = px.pie(df_regiao, values='Valor Total Pedido', names='Região Loja', hole=0.4)
            # ADICIONADO KEY ÚNICA AQUI
            st.plotly_chart(fig_pizza, use_container_width=True, key="grafico_pizza_regiao")
        else:
            st.write("")

# ================= TAB 2: ANÁLISE DE CLIENTES =================
with aba2:
    st.subheader("Top 10 Clientes por Faturamento")
    if not df_filtrado.empty:
        df_cliente = df_filtrado.groupby('Cliente')['Valor Total Pedido'].sum().reset_index()
        df_cliente = df_cliente.sort_values(by='Valor Total Pedido', ascending=False).head(10)
        
        fig_cliente = px.bar(df_cliente, x='Valor Total Pedido', y='Cliente', orientation='h', text_auto='.2s', color='Valor Total Pedido', color_continuous_scale='Blugrn')
        fig_cliente.update_layout(yaxis={'categoryorder':'total ascending'})
        # ADICIONADO KEY ÚNICA AQUI
        st.plotly_chart(fig_cliente, use_container_width=True, key="grafico_barra_clientes")
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
    
    st.subheader("⚠️ Alerta de Inatividade (Última compra há mais de 90 dias)")
    if not df_filtrado.empty:
        df_recencia = df_filtrado.groupby('Cliente')['Data Pedido'].max().reset_index()
        data_maxima_base = df['Data Pedido'].max()
        df_recencia['Dias Sem Comprar'] = (data_maxima_base - df_recencia['Data Pedido']).dt.days
        
        clientes_inativos = df_recencia[df_recencia['Dias Sem Comprar'] > 90].sort_values(by='Dias Sem Comprar', ascending=False)
        st.dataframe(clientes_inativos[['Cliente', 'Data Pedido', 'Dias Sem Comprar']].rename(columns={'Data Pedido': 'Última Compra'}), use_container_width=True)

# ================= TAB 3: ANÁLISE DE PRODUTOS =================
with aba3:
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Faturamento por Categoria de Produto")
        if not df_filtrado.empty:
            df_cat = df_filtrado.groupby('Categoria')['Valor Total Pedido'].sum().reset_index().sort_values(by='Valor Total Pedido', ascending=False)
            fig_cat = px.bar(df_cat, x='Categoria', y='Valor Total Pedido', color='Categoria')
            # ADICIONADO KEY ÚNICA AQUI
            st.plotly_chart(fig_cat, use_container_width=True, key="grafico_barra_categoria")
        else:
            st.warning("Nenhum dado encontrado.")
        
    with col4:
        st.subheader("Preferência de Formato de Venda")
        if not df_filtrado.empty:
            total_cx = df_filtrado['Qtd Caixas'].sum()
            total_un = df_filtrado['Qtd Unidades'].sum()
            
            df_formato = pd.DataFrame({
                'Formato': ['Caixas Fechadas', 'Unidades Avulsas'],
                'Quantidade': [total_cx, total_un]
            })
            fig_formato = px.bar(df_formato, x='Formato', y='Quantidade', color='Formato', text_auto=True)
            # ADICIONADO KEY ÚNICA AQUI
            st.plotly_chart(fig_formato, use_container_width=True, key="grafico_barra_formato")
        else:
            st.warning("Nenhum dado encontrado.")

