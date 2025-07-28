import streamlit as st
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import io
import os

# --- REGUA EMBUTIDA (exemplo com 5 questões) ---
regua_embutida = pd.DataFrame({
    "Série": ["6º ano"] * 5,
    "Questão": ["Q1", "Q2", "Q3", "Q4", "Q5"],
    "Alternativa marcada": ["A", "B", "C", "D", "A"],
    "Nível de conhecimento": ["Muito básico", "Básico", "Intermediário", "Avançado", "Básico"],
    "Habilidade BNCC": [
        "EF15LP01", "EF05MA07", "EF15CI09", "EF06GE01", "EF05HI03"
    ]
})

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Relatório Diagnóstico", layout="centered")

st.title("📋 Relatório Diagnóstico Manual")

with st.form("formulario"):
    nome = st.text_input("Nome do aluno")
    turma = st.selectbox("Série", regua_embutida["Série"].unique())

    respostas = {}
    for q in regua_embutida["Questão"].unique():
        respostas[q] = st.selectbox(f"{q}", ["A", "B", "C", "D"], key=q)

    gerar = st.form_submit_button("Gerar Relatório")

# --- GERAÇÃO DO RELATÓRIO ---
if gerar:
    acertos = 0
    total = 0
    habilidades_domina = []
    habilidades_atencao = []

    for q, resp in respostas.items():
        total += 1  # ← Agora conta todas as questões
        entrada = regua_embutida[
            (regua_embutida["Série"] == turma) &
            (regua_embutida["Questão"] == q) &
            (regua_embutida["Alternativa marcada"] == resp)
        ]
        if not entrada.empty:
            e = entrada.iloc[0]
            if e["Nível de conhecimento"] in ["Avançado", "Intermediário"]:
                habilidades_domina.append(e["Habilidade BNCC"])
            else:
                habilidades_atencao.append(e["Habilidade BNCC"])
            acertos += 1
        else:
            habilidades_atencao.append("Habilidade não identificada para " + q)

    percentual = int((acertos / total) * 100) if total > 0 else 0

    if percentual >= 80:
        nivel = "Avançado"
    elif percentual >= 50:
        nivel = "Intermediário"
    else:
        nivel = "Inicial"

    resumo = f"O aluno {nome} demonstrou desempenho **{nivel}**, com {acertos} de {total} acertos ({percentual}%)."
    if habilidades_domina:
        resumo += f"\n\n✅ Domina as habilidades: {', '.join(habilidades_domina)}"
    if habilidades_atencao:
        resumo += f"\n\n⚠️ Necessita atenção nas habilidades: {', '.join(habilidades_atencao)}"

    # --- GERAÇÃO DO PDF COM JINJA2 + xhtml2pdf ---
    template_env = Environment(loader=FileSystemLoader(searchpath="./"))
    template = template_env.get_template("relatorio_template.html")

    html_rendered = template.render(
        nome=nome,
        turma=turma,
        resumo=resumo.replace("\n", "<br>")
    )

    pdf_file = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_rendered), dest=pdf_file)
    pdf_file.seek(0)

    st.success("✅ Relatório gerado com sucesso!")
    st.download_button("📄 Baixar Relatório PDF", data=pdf_file, file_name=f"relatorio_{nome}.pdf")
