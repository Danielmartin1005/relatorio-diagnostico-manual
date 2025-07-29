import streamlit as st
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import tempfile
import os

# Título do app
st.set_page_config(page_title="Relatório Diagnóstico", layout="centered")
st.title("📄 Geração de Relatório Diagnóstico")

# Upload do CSV da régua
arquivo_csv = st.file_uploader("📎 Envie o arquivo CSV da régua de análise diagnóstica", type="csv")

if arquivo_csv is not None:
    # Leitura da régua
    regua_df = pd.read_csv(arquivo_csv)
    regua_df["Questao"] = regua_df["Questao"].astype(str).str.upper().str.strip()
    regua_df["Alternativa"] = regua_df["Alternativa"].astype(str).str.upper().str.strip()
    regua_df["Série"] = regua_df["Série"].astype(str).str.strip()

    # Formulário do aluno
    with st.form("formulario_aluno"):
        nome = st.text_input("Nome do aluno")
        serie = st.text_input("Série (ex: 6º ano A)").strip()
        respostas_input = st.text_input("Respostas do aluno (ex: A,B,C,D,A...)")

        submit = st.form_submit_button("Gerar relatório")

    if submit:
        respostas = [r.strip().upper() for r in respostas_input.split(",") if r.strip()]
        total_acertos = 0
        habilidades_domina = []
        habilidades_atencao = []

        for i, resposta in enumerate(respostas):
            questao_id = f"Q{i+1}".upper()

            filtro = (
                (regua_df["Série"].str.lower() == serie.lower()) &
                (regua_df["Questao"] == questao_id) &
                (regua_df["Alternativa"] == resposta)
            )
            linha = regua_df[filtro]

            if not linha.empty:
                nivel = linha["Nível de conhecimento do estudante"].values[0]
                habilidade = linha["BNCC relacionada"].values[0]

                if "avançado" in nivel.lower() or "correta" in linha["Possível causa do erro"].values[0].lower():
                    total_acertos += 1
                    habilidades_domina.append(habilidade)
                else:
                    habilidades_atencao.append(habilidade)
            else:
                habilidades_atencao.append("Resposta não encontrada na régua")

        desempenho = (total_acertos / len(respostas)) * 100 if respostas else 0

        if desempenho >= 85:
            nivel = "Avançado"
        elif desempenho >= 65:
            nivel = "Intermediário"
        elif desempenho >= 40:
            nivel = "Básico"
        else:
            nivel = "Muito básico / Requer apoio"

        habilidades_domina = sorted(set(habilidades_domina))
        habilidades_atencao = sorted(set(habilidades_atencao) - set(habilidades_domina))

        # Geração do HTML com Jinja2
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("relatorio_template.html")
        html_rendered = template.render(
            nome_aluno=nome,
            turma=serie,
            total_acertos=total_acertos,
            desempenho=f"{desempenho:.1f}%",
            nivel=nivel,
            habilidades_domina=habilidades_domina,
            habilidades_atencao=habilidades_atencao
        )

        # Gerar PDF temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pisa.CreatePDF(html_rendered, dest=tmp_pdf)
            tmp_pdf_path = tmp_pdf.name

        # Baixar PDF
        with open(tmp_pdf_path, "rb") as pdf_file:
            st.success("✅ Relatório gerado com sucesso!")
            st.download_button("📥 Baixar PDF do Relatório", data=pdf_file, file_name=f"relatorio_{nome}.pdf", mime="application/pdf")

        os.remove(tmp_pdf_path)
