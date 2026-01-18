# Configuração simples
st.set_page_config(page_title="Controlo Diabetes", layout="wide")

# Ligação sem necessidade de ficheiro JSON nos secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    # Lê a folha usando o URL que está nos secrets
    return conn.read(ttl="0s")

df = carregar_dados()

st.title("🩸 Monitor de Glicémia Seguro")

# --- Interface de Entrada ---
with st.sidebar:
    st.header("Novo Registo")
    with st.form("form_registo", clear_on_submit=True):
        data = st.date_input("Data", datetime.now())
        hora = st.time_input("Hora", datetime.now().time())
        glicemia = st.number_input("Glicémia", min_value=20, value=100)
        insulina = st.number_input("Insulina", min_value=0.0, step=0.5)
        notas = st.text_input("Notas")
        
        if st.form_submit_button("Guardar no Google Sheets"):
            nova_linha = pd.DataFrame([{
                "Data/Hora": datetime.combine(data, hora).strftime('%Y-%m-%d %H:%M:%S'),
                "Glicémia (mg/dL)": glicemia,
                "Insulina (U)": insulina,
                "Notas": notas
            }])
            
            # Adicionar aos dados existentes
            df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
            
            # Guardar de volta no Sheets
            conn.update(data=df_atualizado)
            st.success("Dados salvos na nuvem!")
            st.rerun()

# --- Visualização ---
if not df.empty:
    df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])
    fig = px.line(df.sort_values('Data/Hora'), x='Data/Hora', y='Glicémia (mg/dL)', markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Histórico Completo")
    st.dataframe(df.sort_values('Data/Hora', ascending=False), use_container_width=True)
else:
    st.info("A folha de cálculo está vazia. Começa a registar!")

