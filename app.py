import streamlit as st
from st_gsheets_connection import GSheetsConnection

st.set_page_config(page_title="Gestão de Obra v2", layout="wide")

st.title("🏗️ Gestão Colaborativa de Reforma")

# 1. Ligação ao Google Sheets
# Nota: Cole o link da sua folha do Google aqui
url = "https://docs.google.com/spreadsheets/d/1dBJcJ1SOSWrI0k0p3ZoB8pYyGAquYwfn3OTrrNU3er0/edit?gid=0#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Ler os dados
df = conn.read(spreadsheet=url)

# 3. INTERFACE DE EDIÇÃO (O Nível Profissional)
st.subheader("📝 Edição em Tempo Real")
st.info("Pode alterar os valores abaixo como se fosse um Excel. Clique em 'Gravar' para atualizar o Google Sheets.")

df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("💾 Gravar Alterações"):
    conn.update(spreadsheet=url, data=df_editado)
    st.success("Dados atualizados no Google Sheets com sucesso!")

# 4. DASHBOARD AUTOMÁTICO
st.divider()
st.subheader("📊 Resumo Financeiro")
total = df_editado['Custo Total (R$)'].sum()
st.metric("Investimento Atualizado", f"R$ {total:,.2f}")   
