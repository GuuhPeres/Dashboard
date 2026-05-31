# Documentação do `app.py`

## 1. Objetivo

O arquivo `app.py` implementa um dashboard comercial interativo usando Streamlit. O objetivo é permitir a análise estratégica de vendas dos últimos 2 anos, com filtros, métricas e visualizações de desempenho por período, região, cliente e produto.

## 2. Principais dependências

- `streamlit` - interface web reativa e exibição dos componentes.
- `pandas` - leitura e manipulação dos dados em tabelas.
- `plotly.express` - criação de gráficos interativos.
- `datetime` - conversão e manipulação de datas.

## 3. Estrutura do fluxo do aplicativo

### 3.1 Configuração da página

- `st.set_page_config(page_title="Dashboard Comercial", layout="wide")` define o título e o layout da página.
- `st.title` e `st.markdown` exibem o cabeçalho e a descrição do dashboard.

### 3.2 Carregamento e tratamento dos dados

A função `carregar_dados()` faz o seguinte:

- Lê os dados de um arquivo Excel chamado `Base_Laticinios_Ficticia_V2.xlsx`:
  - planilha `Pedidos`
  - planilha `Produtos`
- Converte a coluna `Data Pedido` para formato de data.
- Se a coluna `Categoria` não existir em `Pedidos`, faz um `merge` com a planilha `Produtos` para trazer `Categoria` e `Gramatura`.
- A função é decorada com `@st.cache_data` para armazenar os dados em cache e acelerar o app.

Se ocorrer erro ao carregar a planilha, o app exibe uma mensagem com `st.error` e interrompe a execução com `st.stop()`.

### 3.3 Filtros na barra lateral (sidebar)

A barra lateral permite selecionar os dados que serão exibidos:

- Período de análise:
  - `date_input` com valor inicial entre a data mínima e máxima da base.
  - Filtra registros entre a data inicial e final selecionadas.
- Região da loja:
  - `multiselect` com todas as regiões únicas encontradas em `Região Loja`.
- Categorias de produto:
  - `multiselect` com categorias disponíveis.
- Produtos:
  - `multiselect` com produtos disponíveis.
  - A lista de produtos é filtrada dinamicamente com base nas categorias selecionadas.

### 3.4 Aplicação dos filtros nos dados

O DataFrame é filtrado com base em:

- período selecionado,
- regiões selecionadas,
- categorias selecionadas,
- produtos selecionados.

Quando o período não está em formato de tupla válida, usa-se uma cópia do DataFrame completo.

### 3.5 Cálculo de KPIs

O app calcula três métricas macro importantes:

- `Faturamento Total`: soma da coluna `Valor Total Pedido` do conjunto filtrado.
- `Total de Vendas (Linhas)`: número de linhas após filtragem.
- `Volume Total de Itens`: soma de `Qtd Caixas` e `Qtd Unidades`.

Essas métricas são exibidas em três colunas com `st.metric`.

### 3.6 Abas de visualização

O dashboard possui três abas:

#### Aba 1: Evolução & Regiões

- Gráfico de linha do faturamento mensal ao longo do tempo.
  - Agrupa por mês (`Data Pedido` em período mensal) e soma `Valor Total Pedido`.
- Gráfico de pizza do faturamento por região de loja.

#### Aba 2: Análise de Clientes

- Top 10 clientes por faturamento.
  - Agrupa por `Cliente` e soma `Valor Total Pedido`, ordena e exibe os 10 maiores.
- Alerta de inatividade:
  - Calcula a última data de pedido por cliente.
  - Determina quantos dias se passaram desde a última compra até a data máxima da base.
  - Exibe clientes com mais de 90 dias sem compra.

#### Aba 3: Análise de Produtos

- Faturamento por categoria de produto.
  - Agrupa por `Categoria` e soma `Valor Total Pedido`.
- Preferência de formato de venda:
  - Soma total de `Qtd Caixas` e `Qtd Unidades`.
  - Exibe um gráfico de barras comparando caixas fechadas e unidades avulsas.

## 4. Comportamento quando não há dados

Em cada painel de gráficos, o app verifica se `df_filtrado` está vazio e exibe um aviso com `st.warning` caso não haja dados para os filtros selecionados.

## 5. Observações

- O arquivo depende de um Excel local (`Base_Laticinios_Ficticia_V2.xlsx`) com as colunas usadas no código.
- Os gráficos usam chaves únicas (`key=...`) para evitar conflitos no Streamlit.
- A formatação dos valores monetários e numéricos usa substituições para converter separadores de milhar e decimais para o padrão brasileiro.

---

### Resumo

Este `app.py` monta um dashboard completo para análise de vendas comerciais com filtros interativos, KPIs e três visões principais de performance: evolução temporal, análise de clientes e análise de produtos.
