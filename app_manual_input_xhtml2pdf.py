import streamlit as st
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import tempfile
import os

# Título do app
st.set_page_config(page_title="Relatório Diagnóstico", layout="centered")
st.title("📄 Relatório Diagnóstico Individual")

# Inputs do usuário
nome_aluno = st.text_input("Nome do aluno", placeholder="Ex: João da Silva")
turma = st.text_input("Turma", placeholder="Ex: 6º Ano A")
respostas_str = st.text_input("Respostas do aluno (ex: A,B,C,D,A...)", placeholder="Ex: A,B,C,D,A")

arquivo_csv = st.file_uploader("Envie o arquivo .CSV com a régua diagnóstica", type=["csv"])

def gerar_relatorio_pdf(contexto):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("relatorio_template.html")
    html_content = template.render(contexto)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
        pisa.CreatePDF(html_content, dest=pdf_file)
        return pdf_file.name

# Botão para gerar relatório
if st.button("Gerar Relatório"):
    if not nome_aluno or not turma or not respostas_str or not arquivo_csv:
        st.error("Por favor, preencha todos os campos e envie o arquivo CSV.")
    else:
        try:
            # Ler CSV
            regua_df = pd.read_csv(arquivo_csv)

            # Normalizar colunas
            regua_df["Questao"] = regua_df["Questao"].astype(str).str.strip().str.upper()
            regua_df["Alternativa"] = regua_df["Alternativa"].astype(str).str.strip().str.upper()

            # Processar respostas
            respostas_aluno = [r.strip().upper() for r in respostas_str.split(",")]
            total_questoes = len(respostas_aluno)
            acertos = 0
            habilidades_domina = []
            habilidades_atencao = []

            for i, resposta in enumerate(respostas_aluno):
                questao_id = f"Q{i+1}".upper()

                linha_regua = regua_df[
                    (regua_df["Questao"] == questao_id) & 
                    (regua_df["Alternativa"] == resposta)
                ]

                if not linha_regua.empty:
                    nivel = linha_regua["Nível de conhecimento do estudante"].values[0]
                    habilidade = linha_regua["BNCC relacionada"].values[0]
                    if nivel.strip().lower() in ["avançado", "fácil / avançado", "média / avançado"]:
                        acertos += 1
                        habilidades_domina.append(habilidade)
                    else:
                        habilidades_atencao.append(habilidade)
                else:
                    habilidades_atencao.append("Resposta não encontrada na régua")

            desempenho = (acertos / total_questoes) * 100 if total_questoes > 0 else 0

            if desempenho >= 80:
                nivel_conhecimento = "Avançado"
            elif desempenho >= 60:
                nivel_conhecimento = "Intermediário"
            elif desempenho >= 40:
                nivel_conhecimento = "Básico"
            else:
                nivel_conhecimento = "Muito básico / Requer apoio"

            contexto = {
                "nome_aluno": nome_aluno,
                "turma": turma,
                "acertos": acertos,
                "total_questoes": total_questoes,
                "desempenho": f"{desempenho:.1f}%",
                "nivel_conhecimento": nivel_conhecimento,
                "habilidades_domina": list(set(habilidades_domina)) or ["Nenhuma habilidade evidenciada"],
                "habilidades_atencao": list(set(habilidades_atencao)) or ["Nenhuma habilidade crítica identificada"],
            }

            pdf_path = gerar_relatorio_pdf(contexto)

            with open(pdf_path, "rb") as f:
                st.download_button("📥 Baixar Relatório PDF", f, file_name=f"relatorio_{nome_aluno}.pdf")

        except Exception as e:
            st.error(f"Erro ao gerar o relatório: {e}")
