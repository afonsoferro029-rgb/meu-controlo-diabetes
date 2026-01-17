import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

# Configuração da Página
st.set_page_config(page_title="Controlo de Glicémia", layout="wide")

def carregar_dados():
    if os.path.exists('registos_diabetes.csv'):
        df = pd.read_csv('registos_diabetes.csv')
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])
        return df
    return pd.DataFrame(columns=['Data/Hora', 'Glicémia (mg/dL)', 'Insulina (U)', 'Notas'])

df = carregar_dados()

st.title("🩸 Monitor de Glicémia")

tab1, tab2, tab3 = st.tabs(["Gráfico e Registo", "Editar Histórico", "📄 Exportar PDF"])

# --- TAB 1 e TAB 2 mantêm a lógica anterior ---
with tab1:
    col_in, col_gr = st.columns([1, 2])
    with col_in:
        with st.form("novo_registo"):
            d = st.date_input("Data", datetime.now())
            t = st.time_input("Hora", datetime.now().time())
            g = st.number_input("Glicémia", value=100)
            i = st.number_input("Insulina", value=0.0)
            n = st.text_input("Notas")
            if st.form_submit_button("Salvar"):
                novo = pd.DataFrame([[datetime.combine(d, t), g, i, n]], columns=df.columns)
                df = pd.concat([df, novo], ignore_index=True)
                df.to_csv('registos_diabetes.csv', index=False)
                st.rerun()
    with col_gr:
        if not df.empty:
            fig = px.line(df.sort_values('Data/Hora'), x='Data/Hora', y='Glicémia (mg/dL)', markers=True)
            st.plotly_chart(fig, width='stretch')

with tab2:
    st.write("Funcionalidade de edição (conforme código anterior)")

# --- NOVA TAB 3: EXPORTAR PDF ---
with tab3:
    st.header("Gerar Relatório para o Médico")
    st.write("Este ficheiro incluirá o gráfico de tendências e a listagem de todos os valores.")

    if st.button("Gerar Relatório PDF"):
        if df.empty:
            st.error("Não há dados para exportar.")
        else:
            # 1. Criar Buffer para o PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Título do PDF
            elements.append(Paragraph("Relatório de Controlo de Glicémia", styles['Title']))
            elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            elements.append(Spacer(1, 20))

            # 2. Preparar Tabela para o PDF
            data_pdf = [["Data/Hora", "Glicémia", "Insulina", "Notas"]]
            for _, row in df.sort_values('Data/Hora', ascending=False).iterrows():
                data_pdf.append([
                    row['Data/Hora'].strftime('%d/%m/%Y %H:%M'),
                    str(row['Glicémia (mg/dL)']),
                    str(row['Insulina (U)']),
                    str(row['Notas'])
                ])

            t = Table(data_pdf)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            elements.append(t)

            # Construir PDF
            doc.build(elements)
            
            # Botão de Download
            st.download_button(
                label="Clique aqui para descarregar o PDF",
                data=buffer.getvalue(),
                file_name=f"relatorio_diabetes_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
            st.success("PDF gerado com sucesso!")