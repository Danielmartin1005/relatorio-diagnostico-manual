import streamlit as st
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import tempfile
import os

st.set_page_config(page_title="Gerador de Relatório Diagnóstico", layout="centered")

st.title("📄 Gerador de Relatório Diagnóstico Personalizado")

st.markdown("Preencha os dados abaixo e envie os arquivos para gerar o relatório individual com base na régua de análise diagnóstica.")

nome_aluno = st.text_input("Nome do aluno")
turma = st.text_input("Turma")
respostas_input = st.text_input("Respostas do aluno (ex: A,B,C,D,A...)")

arquivo_regua = st.file_uploader("Envie o arquivo .CSV com a régua diagnóstica", type=["csv"])

if st.button("Gerar Relatório"):

    if not nome_aluno or not turma or not respostas_input or not arquivo_regua:
        st.error("Por favor, preencha todos os campos e envie o arquivo da régua.")
        st.stop()

    respostas = [x.strip().upper() for x in respostas_input.split(",")]
    df_regua = pd.read_csv(arquivo_regua)

    # Detectar colunas de questão (ex: Q1, Q2...) automaticamente
    colunas_questao = [col for col in df_regua.columns if col.startswith("Q")]

    # Dados consolidados por acerto/erro
    total_acertos = 0
    total_questoes = len(respostas)
    habilidades_domina = []
    habilidades_nao_domina = []

    for i, resposta in enumerate(respostas):
        questao_id = f"Q{i+1}"
        if questao_id not in colunas_questao:
            continue

        alternativas_validas = df_regua[questao_id].dropna().unique().tolist()

        # Pega a(s) linha(s) da questão para cada alternativa
        linhas_questao = df_regua[df_regua[questao_id].notna()]

        for idx, linha in linhas_questao.iterrows():
            alternativa_correta = linha[questao_id].strip().upper()
            if resposta == alternativa_correta:
                total_acertos += 1
                habilidades_domina.append(linha["BNCC relacionada"])
                break
        else:
            # Se não houve acerto, pega as habilidades da(s) alternativa(s) errada(s)
            for idx, linha in linhas_questao.iterrows():
                alternativa = linha[questao_id].strip().upper()
                if alternativa == resposta:
                    habilidades_nao_domina.append(linha["BNCC relacionada"])
                    break

    desempenho = round((total_acertos / total_questoes) * 100, 1)

    if desempenho >= 80:
        nivel = "Avançado"
    elif desempenho >= 60:
        nivel = "Intermediário"
    elif desempenho >= 40:
        nivel = "Básico"
    else:
        nivel = "Muito básico"

    if habilidades_domina:
        habilidades_domina_str = ", ".join(set(habilidades_domina))
    else:
        habilidades_domina_str = "Nenhuma habilidade evidenciada"

    if habilidades_nao_domina:
        habilidades_nao_domina_str = ", ".join(set(habilidades_nao_domina))
    else:
        habilidades_nao_domina_str = "Nenhuma habilidade crítica identificada"

    # Prepara template
    env = Environment(loader=FileSystemLoader("."), autoescape=True)
    template = env.get_template("relatorio_template.html")

    html_content = template.render(
        nome=nome_aluno,
        turma=turma,
        acertos=total_acertos,
        total=total_questoes,
        desempenho=desempenho,
        nivel=nivel,
        habilidades_domina=habilidades_domina_str,
        habilidades_nao_domina=habilidades_nao_domina_str
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pisa.CreatePDF(html_content, dest=tmp_pdf)
        tmp_pdf_path = tmp_pdf.name

    with open(tmp_pdf_path, "rb") as f:
        st.success("✅ Relatório gerado com sucesso!")
        st.download_button("📥 Baixar Relatório PDF", f, file_name=f"relatorio_{nome_aluno.replace(' ', '_')}.pdf")

    os.remove(tmp_pdf_path)
