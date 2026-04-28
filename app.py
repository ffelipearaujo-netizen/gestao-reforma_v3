import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página estilo Web App
st.set_page_config(page_title="Gestão Gerencial de Obra", layout="wide", page_icon="🏗️")

# Estilização CSS para um visual mais limpo
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Carrega o arquivo Excel (ou .xlsm)
    arquivo = 'Base geral Reforma.xlsm'
    df = pd.read_excel(arquivo, engine='openpyxl')
    
    # Limpeza básica de dados
    df.columns = [str(c).strip() for c in df.columns]
    cols_numericas = ['Custo Total (R$)', 'Quantidade Total', 'Área (m²)', 'Custo Unitário (R$)']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar ficheiro: {e}")
    st.stop()

# --- BARRA LATERAL (FILTROS GLOBAIS) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4342/4342728.png", width=80)
st.sidebar.title("Filtros do Projeto")

ambientes = sorted(df['Ambiente'].unique().tolist())
filtro_amb = st.sidebar.multiselect("Ambientes", ambientes, default=ambientes)

categorias = sorted(df['Categoria Padronizada'].unique().tolist())
filtro_cat = st.sidebar.multiselect("Categorias", categorias, default=categorias)

# Aplicar filtros
df_f = df[(df['Ambiente'].isin(filtro_amb)) & (df['Categoria Padronizada'].isin(filtro_cat))]

# --- NAVEGAÇÃO POR ABAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Visão Geral", 
    "📍 Por Ambiente", 
    "📦 Materiais & Compras", 
    "📉 Curva ABC", 
    "🛠️ Serviços vs Materiais"
])

# --- TAB 1: VISÃO GERAL ---
with tab1:
    st.header("Dashboard Executivo")
    
    # KPIs Principais
    c1, c2, c3, c4 = st.columns(4)
    total_obra = df_f['Custo Total (R$)'].sum()
    area_total = df.drop_duplicates('Ambiente')['Área (m²)'].sum()
    custo_m2 = total_obra / area_total if area_total > 0 else 0
    
    c1.metric("Investimento Total", f"R$ {total_obra:,.2f}")
    c2.metric("Área Total", f"{area_total:.2f} m²")
    c3.metric("Custo Médio/m²", f"R$ {custo_m2:,.2f}")
    c4.metric("Itens Planejados", len(df_f))

    st.divider()
    
    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        st.subheader("Custo por Categoria")
        fig_cat = px.pie(df_f, values='Custo Total (R$)', names='Categoria Padronizada', hole=0.5)
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col_g2:
        st.subheader("Top 10 Itens mais Caros")
        top_10 = df_f.nlargest(10, 'Custo Total (R$)')
        fig_top = px.bar(top_10, x='Custo Total (R$)', y='Item', orientation='h', color='Custo Total (R$)')
        st.plotly_chart(fig_top, use_container_width=True)

# --- TAB 2: POR AMBIENTE ---
with tab2:
    st.header("Análise Detalhada por Ambiente")
    
    # Agrupamento por ambiente
    df_amb = df_f.groupby('Ambiente').agg({
        'Custo Total (R$)': 'sum',
        'Área (m²)': 'max'
    }).reset_index()
    df_amb['Custo/m²'] = df_amb['Custo Total (R$)'] / df_amb['Área (m²)']
    
    fig_amb = px.bar(df_amb, x='Ambiente', y='Custo Total (R$)', color='Custo Total (R$)', text_auto='.2s')
    st.plotly_chart(fig_amb, use_container_width=True)
    
    st.subheader("Tabela de Eficiência por Ambiente")
    st.dataframe(df_amb.sort_values('Custo Total (R$)', ascending=False), use_container_width=True)

# --- TAB 3: MATERIAIS & COMPRAS ---
with tab3:
    st.header("Controle Consolidado de Materiais")
    
    # Consolidação para compras
    df_materiais = df_f.groupby(['Item', 'Unidade', 'Classe ABC']).agg({
        'Quantidade Total': 'sum',
        'Custo Total (R$)': 'sum'
    }).reset_index().sort_values('Custo Total (R$)', ascending=False)
    
    st.markdown("### Lista de Aquisição")
    st.dataframe(df_materiais, use_container_width=True)

# --- TAB 4: CURVA ABC ---
with tab4:
    st.header("Distribuição de Criticidade (ABC)")
    
    abc_summary = df_f.groupby('Classe ABC')['Custo Total (R$)'].sum().reset_index()
    abc_summary['% do Total'] = (abc_summary['Custo Total (R$)'] / total_obra) * 100
    
    c_abc1, c_abc2 = st.columns([1, 2])
    with c_abc1:
        st.write("Resumo Financeiro")
        st.table(abc_summary.style.format({'Custo Total (R$)': 'R$ {:,.2f}', '% do Total': '{:.1f}%'}))
    
    with c_abc2:
        fig_abc = px.bar(abc_summary, x='Classe ABC', y='Custo Total (R$)', color='Classe ABC',
                         color_discrete_map={'A':'#d62728', 'B':'#ff7f0e', 'C':'#2ca02c'})
        st.plotly_chart(fig_abc, use_container_width=True)

# --- TAB 5: SERVIÇOS VS MATERIAIS ---
with tab5:
    st.header("Composição do Custo: Material vs Mão de Obra")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        fig_ms = px.pie(df_f, values='Custo Total (R$)', names='Tipo (Mat/Serv)', hole=0.4)
        st.plotly_chart(fig_ms, use_container_width=True)
        
    with col_s2:
        # Comparativo por ambiente
        ms_amb = df_f.groupby(['Ambiente', 'Tipo (Mat/Serv)'])['Custo Total (R$)'].sum().reset_index()
        fig_ms_amb = px.bar(ms_amb, x='Ambiente', y='Custo Total (R$)', color='Tipo (Mat/Serv)', barmode='group')
        st.plotly_chart(fig_ms_amb, use_container_width=True)
    
   