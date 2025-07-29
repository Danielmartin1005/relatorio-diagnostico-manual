import streamlit as st import pandas as pd import tempfile from io import BytesIO from xhtml2pdf import pisa from PIL import Image import base64

st.set_page_config(page_title="Relatório Diagnóstico", layout="centered") st.title("📈 Relatório Diagnóstico Personalizado") st.markdown("Preencha os dados abaixo e envie os arquivos para gerar o relatório individual com base na régua de análise diagnóstica.")

nome_aluno = st.text_input("Nome do aluno") turma = st.text_input("Turma") respostas = st.text_input("Respostas do aluno (ex: A,B,C,D,A...)") arquivo_regua = st.file_uploader("Envie o arquivo .CSV com a régua diagnóstica", type=["csv"]) arquivo_logo = st.file_uploader("Deseja adicionar o logotipo da escola? (PNG/JPG)", type=["png", "jpg", "jpeg"])

def calcular_nivel_conhecimento(porcentagem): if porcentagem >= 80: return "Avançado" elif porcentagem >= 60: return "Intermediário" elif porcentagem >= 40: return "Básico" else: return "Muito básico / Requer apoio"

def gerar_html(relatorio, logo_b64): html = f""" <html> <head><meta charset='utf-8'></head> <body style='font-family: Arial;'> <div style='display: flex; justify-content: space-between; align-items: center;'> <h2>Relatório Diagnóstico Individual</h2> {'<img src="data:image/png;base64,' + logo_b64 + '" style="height: 60px;">' if logo_b64 else ''} </div> <p><strong>Nome do aluno:</strong> {relatorio['nome']}</p> <p><strong>Turma:</strong> {relatorio['turma']}</p> <p><strong>Total de acertos:</strong> {relatorio['acertos']}</p> <p><strong>Desempenho:</strong> {relatorio['desempenho']}%</p> <p><strong>Nível de conhecimento:</strong> {relatorio['nivel']}</p>

<p><strong>■ Habilidades que o aluno já domina:</strong></p>
<ul>
    {''.join(f'<li>{hab}</li>' for hab in relatorio['habilidades_domina']) if relatorio['habilidades_domina'] else '<li>Nenhuma habilidade evidenciada</li>'}
</ul>

<p><strong>■■ Habilidades que precisam de atenção:</strong></p>
<ul>
    {''.join(f'<li>{hab}</li>' for hab in relatorio['habilidades_erro']) if relatorio['habilidades_erro'] else '<li>Nenhuma habilidade crítica identificada</li>'}
</ul>

<p style='font-size: small; color: gray;'>Relatório gerado automaticamente com base na análise das respostas e habilidades da BNCC.</p>
</body>
</html>
"""
return html

def converter_pdf(html):

