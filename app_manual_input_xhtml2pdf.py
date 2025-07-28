import streamlit as st
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import tempfile
import os
from io import BytesIO

# Função para converter HTML em PDF
def converter_html_para_pdf(source_html, output_filename):
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(source_html, dest=result_file)
    return not pisa_status.err

# Função para gerar HTML do relatório
def gerar_html_relatorio(nome_aluno, turma, total_acertos, desempenho, nivel, habilidades_domina, habilidades_atencao):
    template_env = Environment(loader=FileSystemLoader(searchpath="./"))
    template = template_env.get_template("relatorio_template.html")

    html_content = template.render(
        nome_aluno=nome_aluno,
        turma=turma,
        total_acertos=total_acertos,
        desempenho=desempenho,
        nivel=nivel,
        habilidades_domina=habilidades_domina,
        habilidades_atencao=habilidades_atencao
    )

    return html_content

# Função para definir nível de conhecimento
def definir_nivel_conhecimento(desempenho):
    if desempenho == 100:
        return "Avançado"
    elif desempenho >= 75:
        return "Intermediário"
    elif desempenho >= 50:
        return "Básico"
    else:
        return "Muito básico"

# App Streamlit
st.title("📄 Relatório Diagnóstico Individual")

st.markdown("Preencha os dados abaixo e envie os arquivos para gerar o relatório individual com base na régua de análise diagnóstica.")

nome_aluno = st.text_input("Nome do aluno")
turma = st.text_input("Turma")
respostas_texto = st.text_input("Respostas do aluno (ex: A,B,C,D,A...)")
arquivo_regua = st.file_uploader("Envie o arquivo .CSV com a régua diagnóstica", type="csv")

if st.button("Gerar Relatório"):
    if not nome_aluno or not turma or not respostas_texto or not arquivo_regua:
        st.warning("⚠️ Por favor, preencha todos os campos e envie o arquivo CSV.")
    else:
        try:
            respostas = [r.strip().upper() for r in respostas_texto.split(",")]

            regua_df = pd.read_csv(arquivo_regua)

            # Padroniza os nomes das colunas
            regua_df.columns = [col.strip().lower().replace("ç", "c").replace("ã", "a").replace("á", "a") for col in regua_df.columns]

            total_questoes = len(respostas)
            acertos = 0
            habilidades_domina = []
            habilidades_atencao = []

            for i, resposta in enumerate(respostas):
                num_questao = i + 1
                linha = regua_df[regua_df["questao"] == num_questao]

                if not linha.empty:
                    alternativa_correta = linha.iloc[0]["alternativa correta"].strip().upper()
                    habilidade = linha.iloc[0]["conteudo"]

                    if resposta == alternativa_correta:
                        acertos += 1
                        habilidades_domina.append(habilidade)
                    else:
                        habilidades_atencao.append(habilidade)

            desempenho = round((acertos / total_questoes) * 100, 1)
            nivel = definir_nivel_conhecimento(desempenho)

            html_relatorio = gerar_html_relatorio(
                nome_aluno,
                turma,
                f"{acertos} de {total_questoes}",
                f"{desempenho}%",
                nivel,
                habilidades_domina,
                habilidades_atencao
            )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                converter_html_para_pdf(html_relatorio, tmp_pdf.name)
                tmp_pdf.seek(0)
                st.success("✅ Relatório gerado com sucesso!")
                st.download_button(
                    label="📥 Baixar Relatório PDF",
                    data=tmp_pdf.read(),
                    file_name=f"relatorio_{nome_aluno.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"Erro ao gerar relatório: {e}")
