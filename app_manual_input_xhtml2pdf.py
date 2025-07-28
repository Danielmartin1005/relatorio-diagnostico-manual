
import streamlit as st
import pandas as pd
import jinja2
from xhtml2pdf import pisa
import tempfile
import os

# Embutir a régua de diagnóstico
regua = pd.DataFrame([
    {"Série": "6º Ano", "Questão": "Q1", "Alternativa marcada": "A", "Nível de conhecimento do estudante": "Avançado", "Possível causa do erro": "Alternativa correta", "Estratégia de intervenção": "Propor novas leituras de HQs visuais e atividades de análise de imagem.", "Habilidades necessárias (BNCC)": "EF06LP12"},
    {"Série": "6º Ano", "Questão": "Q1", "Alternativa marcada": "B", "Nível de conhecimento do estudante": "Intermediário", "Possível causa do erro": "Leitura incompleta do enunciado", "Estratégia de intervenção": "Trabalhar leitura de imagens, interpretação de cenas.", "Habilidades necessárias (BNCC)": "EF06LP12"},
    {"Série": "6º Ano", "Questão": "Q1", "Alternativa marcada": "C", "Nível de conhecimento do estudante": "Básico", "Possível causa do erro": "Confusão entre texto verbal e não verbal", "Estratégia de intervenção": "Comparar tirinhas com e sem texto verbal", "Habilidades necessárias (BNCC)": "EF06LP12"},
    {"Série": "6º Ano", "Questão": "Q1", "Alternativa marcada": "D", "Nível de conhecimento do estudante": "Muito básico / Inicial", "Possível causa do erro": "Dificuldade em reconhecer sequência narrativa", "Estratégia de intervenção": "Explorar sequência de eventos visuais", "Habilidades necessárias (BNCC)": "EF06LP12"},
    {"Série": "6º Ano", "Questão": "Q2", "Alternativa marcada": "A", "Nível de conhecimento do estudante": "Avançado", "Possível causa do erro": "Alternativa correta", "Estratégia de intervenção": "Ampliar com produções de receitas.", "Habilidades necessárias (BNCC)": "EF05LP18"},
    {"Série": "6º Ano", "Questão": "Q3", "Alternativa marcada": "B", "Nível de conhecimento do estudante": "Avançado", "Possível causa do erro": "Alternativa correta", "Estratégia de intervenção": "", "Habilidades necessárias (BNCC)": "EF05LP15"},
    {"Série": "6º Ano", "Questão": "Q4", "Alternativa marcada": "D", "Nível de conhecimento do estudante": "Avançado", "Possível causa do erro": "Alternativa correta", "Estratégia de intervenção": "", "Habilidades necessárias (BNCC)": "EF05LP16"},
    {"Série": "6º Ano", "Questão": "Q5", "Alternativa marcada": "B", "Nível de conhecimento do estudante": "Avançado", "Possível causa do erro": "Alternativa correta", "Estratégia de intervenção": "", "Habilidades necessárias (BNCC)": "EF05LP17"},
])

def classificar_nivel(percentual):
    if percentual >= 85: return "Avançado"
    elif percentual >= 65: return "Intermediário"
    elif percentual >= 40: return "Básico"
    return "Muito básico / Requer apoio"

def classificar_habilidade(h):
    if pd.isna(h): return "Outros"
    if h.startswith("EF06LP") or h.startswith("EF67LP") or h.startswith("EF05LP"):
        return "Leitura e interpretação de texto"
    return "Outros"

def gerar_resumo(nivel, habilidades):
    dom = ", ".join(sorted(set(map(classificar_habilidade, habilidades))))
    if nivel == "Avançado":
        return f"O aluno demonstra domínio em {dom}, estando apto a acompanhar a turma."
    elif nivel == "Intermediário":
        return f"O aluno apresenta desempenho satisfatório em {dom}, com condições de acompanhar a turma, mas precisa de reforço em pontos específicos."
    elif nivel == "Básico":
        return f"O aluno tem conhecimentos iniciais em {dom}, sendo necessário um acompanhamento mais próximo e atividades de reforço."
    else:
        return f"O aluno apresenta dificuldades significativas nas competências avaliadas. Será necessário um plano individual de apoio focado em {dom}."

st.set_page_config("Diagnóstico Individual")
st.title("📘 Gerador de Relatório Diagnóstico")

nome = st.text_input("Nome do aluno")
turma = st.selectbox("Série", ["6º Ano"])
respostas = {}

st.markdown("### 📝 Respostas do aluno")
for q in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
    respostas[q] = st.radio(f"{q} - Marque a alternativa:", ["A", "B", "C", "D"], key=q)

if st.button("📄 Gerar Relatório PDF"):
    total = 0
    acertos = 0
    habilidades = []
    niveis = []
    estrategias = []

    for q, resp in respostas.items():
        entrada = regua[
            (regua["Série"] == turma) &
            (regua["Questão"] == q) &
            (regua["Alternativa marcada"] == resp)
        ]
        if not entrada.empty:
            total += 1
            e = entrada.iloc[0]
            nivel = e["Nível de conhecimento do estudante"]
            if "avançado" in nivel.lower() or e["Possível causa do erro"].lower() == "alternativa correta":
                acertos += 1
            niveis.append(nivel)
            habilidades.append(e["Habilidades necessárias (BNCC)"])
            if pd.notna(e["Estratégia de intervenção"]) and nivel.lower() != "avançado":
                estrategias.append(e["Estratégia de intervenção"])

    percentual = (acertos / total) * 100 if total else 0
    nivel_geral = classificar_nivel(percentual)
    resumo = gerar_resumo(nivel_geral, habilidades)
    pontos_atencao = ", ".join(sorted(set(
        classificar_habilidade(h) for i, h in enumerate(habilidades)
        if "básico" in niveis[i].lower() or "muito" in niveis[i].lower()
    )))
    estrategias_texto = " | ".join(sorted(set(estrategias)))

    template_loader = jinja2.FileSystemLoader(searchpath=".")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("relatorio_template.html")

    html_rendered = template.render(
        nome=nome,
        turma=turma,
        total_acertos=acertos,
        percentual_acertos=f"{percentual:.1f}%",
        nivel_geral=nivel_geral,
        resumo_pedagogico=resumo,
        pontos_atencao=pontos_atencao,
        estrategias=estrategias_texto
    )

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    with open(temp_pdf.name, "w+b") as pdf_file:
        pisa.CreatePDF(html_rendered, dest=pdf_file)

    with open(temp_pdf.name, "rb") as f:
        st.download_button("📥 Baixar PDF do Relatório", f, file_name=f"{nome}_relatorio.pdf")
