import streamlit as st
import pandas as pd
import io
import tempfile
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import os

st.set_page_config(page_title="Relatório Diagnóstico Individual", layout="centered")

st.title("📄 Relatório Diagnóstico Individual")

st.markdown("""
Preencha os dados abaixo e envie os arquivos para gerar o relatório individual com base na régua de análise diagnóstica.
""")

nome_aluno = st.text_input("Nome do aluno")
turma = st.text_input("Turma")
respostas_texto = st.text_input("Respostas do aluno (ex: A,B,C,D,A...)")
arquivo_regua = st.file_uploader("Envie o arquivo .CSV com a régua diagnóstica", type="csv")

if st.button("Gerar Relatório"):
    if not nome_aluno or not turma or not respostas_texto or not arquivo_regua:
        st.warning("Por favor, preencha todos os campos e envie o arquivo da régua diagnóstica.")
    else:
        # Padroniza e separa as respostas do aluno
        respostas_aluno = [resp.strip().upper() for resp in respostas_texto.split(",")]

        # Carrega a régua diagnóstica
        regua_df = pd.read_csv(arquivo_regua)

        # Inicializa contadores
        total_questoes = len(respostas_aluno)
        total_acertos = 0
        habilidades_domina = []
        habilidades_atencao = []

        for i, resposta_aluno in enumerate(respostas_aluno):
            num_questao = i + 1

            linha = regua_df[regua_df["Questao"] == num_questao]

            if not linha.empty:
                alternativa_correta = linha.iloc[0]["Alternativa correta"]
                habilidade = linha.iloc[0]["Conteúdo"]

                if str(resposta_aluno).strip().upper() == str(alternativa_correta).strip().upper():
                    total_acertos += 1
                    habilidades_domina.append(habilidade)
                else:
                    habilidades_atencao.append(habilidade)

        desempenho = (total_acertos / total_questoes) * 100 if total_questoes > 0 else 0

        if desempenho >= 80:
            nivel_conhecimento = "Avançado"
        elif desempenho >= 60:
            nivel_conhecimento = "Intermediário"
        elif desempenho >= 40:
            nivel_conhecimento = "Básico"
        else:
            nivel_conhecimento = "Muito básico"

        habilidades_domina = list(set(habilidades_domina))
        habilidades_atencao = list(set(habilidades_atencao))

        # Carrega template
        env = Environment(loader=FileSystemLoader("."))  # Atualize se estiver em subpasta
        template = env.get_template("relatorio_template.html")

        html_rendered = template.render(
            nome_aluno=nome_aluno,
            turma=turma,
            total_acertos=total_acertos,
            total_questoes=total_questoes,
            desempenho=f"{desempenho:.1f}",
            nivel_conhecimento=nivel_conhecimento,
            habilidades_domina=habilidades_domina,
            habilidades_atencao=habilidades_atencao
        )

        # Gera PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pisa.CreatePDF(io.StringIO(html_rendered), dest=tmp_pdf)
            tmp_pdf_path = tmp_pdf.name

        with open(tmp_pdf_path, "rb") as file:
            st.download_button(
                label="📥 Baixar Relatório PDF",
                data=file,
                file_name=f"relatorio_{nome_aluno.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

        os.remove(tmp_pdf_path)
