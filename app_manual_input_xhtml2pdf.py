
import streamlit as st
import pandas as pd
import tempfile
from io import BytesIO
from xhtml2pdf import pisa
from PIL import Image
import base64
from jinja2 import Environment, FileSystemLoader
import os

st.set_page_config(page_title="Relatório Diagnóstico", layout="centered")
st.title("📈 Relatório Diagnóstico Personalizado")
st.markdown("Preencha os dados abaixo e envie os arquivos para gerar o relatório individual com base na régua de análise diagnóstica.")

# Upload de CSV da régua
regua_file = st.file_uploader("📄 Envie o arquivo CSV da régua diagnóstica", type="csv")

# Upload do logotipo da escola
logo_file = st.file_uploader("🏫 (Opcional) Envie o logotipo da escola", type=["png", "jpg", "jpeg"])

# Campos do aluno
nome = st.text_input("Nome do aluno")
turma = st.text_input("Turma")
st.markdown("### 📌 Digite as respostas do aluno para as questões:")
respostas_dict = {}
for i in range(1, 21):
    respostas_dict[f"Q{i}"] = st.text_input(f"Q{i}", max_chars=1)

if st.button("📤 Gerar Relatório"):
    if not nome or not turma:
        st.warning("Por favor, preencha nome e turma.")
    elif not regua_file:
        st.warning("Envie o arquivo CSV da régua diagnóstica.")
    else:
        regua_df = pd.read_csv(regua_file, dtype=str).fillna("")

        respostas_aluno = {k.upper(): v.strip().upper() for k, v in respostas_dict.items() if v.strip()}
        total_questoes = 0
        acertos = 0
        habilidades_domina = []
        habilidades_atencao = []
        estrategias = []

        for questao, resposta in respostas_aluno.items():
            linha_regua = regua_df[
                (regua_df["Série"].str.strip().str.lower() == turma.strip().lower()) &
                (regua_df["Questão"].str.strip().str.upper() == questao.upper()) &
                (regua_df["Alternativa marcada"].str.strip().str.upper() == resposta)
            ]
            if not linha_regua.empty:
                total_questoes += 1
                nivel = linha_regua["Nível de conhecimento do estudante"].values[0]
                habilidade = linha_regua["Habilidades necessárias (BNCC)"].values[0]
                causa = linha_regua["Possível causa do erro"].values[0]
                estrategia = linha_regua["Estratégia de intervenção"].values[0]

                if "avançado" in nivel.lower() or "correta" in causa.lower():
                    acertos += 1
                    habilidades_domina.append(habilidade)
                else:
                    habilidades_atencao.append(habilidade)
                    if estrategia:
                        estrategias.append(estrategia)

        desempenho = round((acertos / total_questoes) * 100, 1) if total_questoes else 0

        def classificar_nivel(p):
            if p >= 85: return "Avançado"
            if p >= 65: return "Intermediário"
            if p >= 40: return "Básico"
            return "Muito básico / Requer apoio"

        nivel_conhecimento = classificar_nivel(desempenho)
        habilidades_domina = sorted(set(habilidades_domina))
        habilidades_atencao = sorted(set(habilidades_atencao))
        estrategias = sorted(set(estrategias))

        # Gerar resumo
        if nivel_conhecimento == "Avançado":
            resumo = "O aluno demonstra domínio nas habilidades avaliadas e está apto a acompanhar a turma com segurança."
        elif nivel_conhecimento == "Intermediário":
            resumo = "O aluno apresenta desempenho satisfatório, mas pode se beneficiar de reforços pontuais nas habilidades destacadas."
        elif nivel_conhecimento == "Básico":
            resumo = "O aluno tem conhecimentos iniciais e precisará de acompanhamento em diversas habilidades."
        else:
            resumo = "O aluno apresenta dificuldades significativas e necessita de um plano individualizado de apoio."

        # LOGOTIPO
        logo_base64 = ""
        if logo_file:
            image = Image.open(logo_file)
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            logo_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Renderizar HTML com Jinja2
        env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
        template = env.get_template("relatorio_template.html")
        html_rendered = template.render(
            nome=nome,
            turma=turma,
            acertos=acertos,
            desempenho=desempenho,
            nivel_conhecimento=nivel_conhecimento,
            resumo_pedagogico=resumo,
            habilidades_domina=habilidades_domina,
            habilidades_atencao=habilidades_atencao,
            logo_base64=logo_base64
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
            pisa.CreatePDF(BytesIO(html_rendered.encode("utf-8")), dest=pdf_file)
            st.success("✅ Relatório gerado com sucesso!")
            with open(pdf_file.name, "rb") as f:
                st.download_button("📥 Baixar PDF", f.read(), file_name=f"relatorio_{nome}.pdf", mime="application/pdf")
