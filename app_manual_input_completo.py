# -*- coding: utf-8 -*-
# Streamlit App com régua embutida

import streamlit as st
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import io
import os

# --- REGUA EMBUTIDA COMPLETA ---
regua_embutida = pd.DataFrame([
    {'Série': '6º Ano', 'Questão': 'Q1', 'Alternativa marcada': 'A', 'Nível de conhecimento': 'Avançado', 'Possível causa do erro': 'Alternativa correta', 'Estratégia de intervenção': 'Propor novas leituras de HQs visuais e atividades de produção de tirinhas com e sem balões.', 'Habilidade BNCC': 'EF06LP12: Identificar efeitos de sentido decorrentes da combinação de elementos verbais e não verbais em diferentes gêneros.\nEF67LP08: Analisar efeitos de sentido provocados por elementos gráficos e recursos expressivos das HQs.\nEF67LP09: Inferir informações implícitas em textos de diferentes gêneros.'},
    {'Série': '6º Ano', 'Questão': 'Q1', 'Alternativa marcada': 'B', 'Nível de conhecimento': 'Intermediário', 'Possível causa do erro': 'Leitura incompleta do enunciado, confusão sobre a função da linguagem não verbal.', 'Estratégia de intervenção': 'Trabalhar leitura de imagens, interpretação de expressões faciais e ações nos quadrinhos.', 'Habilidade BNCC': 'EF06LP12: Identificar efeitos de sentido decorrentes da combinação de elementos verbais e não verbais em diferentes gêneros.\nEF67LP08: Analisar efeitos de sentido provocados por elementos gráficos e recursos expressivos das HQs.\nEF67LP09: Inferir informações implícitas em textos de diferentes gêneros.'},
    {'Série': '6º Ano', 'Questão': 'Q1', 'Alternativa marcada': 'C', 'Nível de conhecimento': 'Básico', 'Possível causa do erro': 'Confusão entre texto verbal e não verbal; pode ter se apoiado apenas no formato visual.', 'Estratégia de intervenção': 'Comparar tirinhas com e sem texto verbal, promovendo discussões sobre suas diferenças de estrutura e sentido.', 'Habilidade BNCC': 'EF06LP12: Identificar efeitos de sentido decorrentes da combinação de elementos verbais e não verbais em diferentes gêneros.\nEF67LP08: Analisar efeitos de sentido provocados por elementos gráficos e recursos expressivos das HQs.\nEF67LP09: Inferir informações implícitas em textos de diferentes gêneros.'},
    {'Série': '6º Ano', 'Questão': 'Q1', 'Alternativa marcada': 'D', 'Nível de conhecimento': 'Muito básico / Inicial', 'Possível causa do erro': 'Dificuldade em perceber a sequência narrativa e coesão entre os quadros.', 'Estratégia de intervenção': 'Explorar sequência de eventos visuais com HQs simples e narrativas com apoio visual (sem texto).', 'Habilidade BNCC': 'EF06LP12: Identificar efeitos de sentido decorrentes da combinação de elementos verbais e não verbais em diferentes gêneros.\nEF67LP08: Analisar efeitos de sentido provocados por elementos gráficos e recursos expressivos das HQs.\nEF67LP09: Inferir informações implícitas em textos de diferentes gêneros.'},
    {'Série': '6º Ano', 'Questão': 'Q2', 'Alternativa marcada': 'A', 'Nível de conhecimento': 'Avançado', 'Possível causa do erro': 'Alternativa correta', 'Estratégia de intervenção': 'Ampliar com produções de receitas, listas de instruções e outros textos instrucionais.', 'Habilidade BNCC': 'EF05LP18 (5º ano, podendo ser retomada no 6º): Reconhecer e compreender a finalidade de textos instrucionais.\nEF67LP04: Identificar e analisar elementos da organização estrutural de textos instrucionais, como receitas, regras, manuais etc.\nEF06LP12: Distinguir diferentes partes de um texto e suas funções (introdução, instrução, título, lista, etc.).'},
    {'Série': '6º Ano', 'Questão': 'Q2', 'Alternativa marcada': 'B', 'Nível de conhecimento': 'Intermediário', 'Possível causa do erro': 'Confusão entre as partes da receita (ingredientes × modo de preparo).', 'Estratégia de intervenção': 'Analisar receitas reais, destacando partes e funções com marca-texto ou esquemas.', 'Habilidade BNCC': 'EF05LP18 (5º ano, podendo ser retomada no 6º): Reconhecer e compreender a finalidade de textos instrucionais.\nEF67LP04: Identificar e analisar elementos da organização estrutural de textos instrucionais, como receitas, regras, manuais etc.\nEF06LP12: Distinguir diferentes partes de um texto e suas funções (introdução, instrução, título, lista, etc.).'},
    {'Série': '6º Ano', 'Questão': 'Q2', 'Alternativa marcada': 'C', 'Nível de conhecimento': 'Básico', 'Possível causa do erro': 'Interpretação literal ou leitura superficial. Pode ter confundido com tabela de compras.', 'Estratégia de intervenção': 'Trabalhar leitura de textos instrucionais e sua aplicabilidade prática (como usar receitas no dia a dia).', 'Habilidade BNCC': 'EF05LP18 (5º ano, podendo ser retomada no 6º): Reconhecer e compreender a finalidade de textos instrucionais.\nEF67LP04: Identificar e analisar elementos da organização estrutural de textos instrucionais, como receitas, regras, manuais etc.\nEF06LP12: Distinguir diferentes partes de um texto e suas funções (introdução, instrução, título, lista, etc.).'},
    {'Série': '6º Ano', 'Questão': 'Q2', 'Alternativa marcada': 'D', 'Nível de conhecimento': 'Muito básico / Inicial', 'Possível causa do erro': 'Confusão entre instrução e tempo, ou leitura automática sem análise do texto apresentado.', 'Estratégia de intervenção': 'Propor leitura guiada de receitas e produção coletiva de textos com foco nas funções de cada parte.', 'Habilidade BNCC': 'EF05LP18 (5º ano, podendo ser retomada no 6º): Reconhecer e compreender a finalidade de textos instrucionais.\nEF67LP04: Identificar e analisar elementos da organização estrutural de textos instrucionais, como receitas, regras, manuais etc.\nEF06LP12: Distinguir diferentes partes de um texto e suas funções (introdução, instrução, título, lista, etc.).'},
    {'Série': '6º Ano', 'Questão': 'Q3', 'Alternativa marcada': 'B', 'Nível de conhecimento': 'Avançado', 'Possível causa do erro': 'Alternativa correta', 'Estratégia de intervenção': 'Trabalhar produção e leitura de textos funcionais (envelopes, formulários, bilhetes).', 'Habilidade BNCC': 'EF05LP16 – Reconhecer a estrutura e a função de textos instrucionais e funcionais do cotidiano.\nEF67LP01 – Identificar a finalidade de textos do campo da vida cotidiana'},
    {'Série': '6º Ano', 'Questão': 'Q3', 'Alternativa marcada': 'A', 'Nível de conhecimento': 'Intermediário', 'Possível causa do erro': 'Confusão entre dados úteis e dados obrigatórios no contexto da carta.', 'Estratégia de intervenção': 'Comparar diferentes gêneros: carta, ficha cadastral, formulário, etc.', 'Habilidade BNCC': 'EF05LP16 – Reconhecer a estrutura e a função de textos instrucionais e funcionais do cotidiano.\nEF67LP01 – Identificar a finalidade de textos do campo da vida cotidiana'},
    {'Série': '6º Ano', 'Questão': 'Q3', 'Alternativa marcada': 'C', 'Nível de conhecimento': 'Básico', 'Possível causa do erro': 'Leitura superficial ou interpretação literal, focando em vínculos pessoais.', 'Estratégia de intervenção': 'Apresentar diferentes exemplos de cartas reais e trabalhar seus elementos essenciais.', 'Habilidade BNCC': 'EF05LP16 – Reconhecer a estrutura e a função de textos instrucionais e funcionais do cotidiano.\nEF67LP01 – Identificar a finalidade de textos do campo da vida cotidiana'},
    {'Série': '6º Ano', 'Questão': 'Q3', 'Alternativa marcada': 'D', 'Nível de conhecimento': 'Muito básico', 'Possível causa do erro': 'Interpretação baseada em outros contextos (documentos oficiais, cadastros).', 'Estratégia de intervenção': 'Analisar o propósito e público-alvo de diferentes tipos de texto.', 'Habilidade BNCC': 'EF05LP16 – Reconhecer a estrutura e a função de textos instrucionais e funcionais do cotidiano.\nEF67LP01 – Identificar a finalidade de textos do campo da vida cotidiana'},
    {'Série': '6º Ano', 'Questão': 'Q4', 'Alternativa marcada': 'D', 'Nível de conhecimento': 'Avançado', 'Possível causa do erro': 'Alternativa correta', 'Estratégia de intervenção': 'Reforçar padrões ortográficos por meio de leitura e escrita contextualizada.', 'Habilidade BNCC': 'EF06LP15 – Identificar e usar, em textos escritos, convenções ortográficas e gramaticais.\nEF05LP10 – Utilizar convenções ortográficas em textos, como uso de letras e grafemas com base na regularidade da escrita.'},
    {'Série': '6º Ano', 'Questão': 'Q4', 'Alternativa marcada': 'B', 'Nível de conhecimento': 'Intermediário', 'Possível causa do erro': 'Confusão entre o uso de S e SS em palavras com sons semelhantes.', 'Estratégia de intervenção': 'Prática com famílias de palavras e atividades com destaque para grafemas semelhantes.', 'Habilidade BNCC': 'EF06LP15 – Identificar e usar, em textos escritos, convenções ortográficas e gramaticais.\nEF05LP10 – Utilizar convenções ortográficas em textos, como uso de letras e grafemas com base na regularidade da escrita.'},
    {'Série': '6º Ano', 'Questão': 'Q4', 'Alternativa marcada': 'C', 'Nível de conhecimento': 'Básico', 'Possível causa do erro': 'Generalização incorreta do uso do Ç para o som /s/ em posição medial.', 'Estratégia de intervenção': 'Atividades que contrastem SS, Ç, S, C em diferentes contextos de uso.', 'Habilidade BNCC': 'EF06LP15 – Identificar e usar, em textos escritos, convenções ortográficas e gramaticais.\nEF05LP10 – Utilizar convenções ortográficas em textos, como uso de letras e grafemas com base na regularidade da escrita.'},
    {'Série': '6º Ano', 'Questão': 'Q4', 'Alternativa marcada': 'A', 'Nível de conhecimento': 'Muito básico', 'Possível causa do erro': 'Erro fonético mais grave, sem relação com a grafia correta ou próxima.', 'Estratégia de intervenção': 'Iniciar com atividades de escuta, leitura e escrita com palavras de uso frequente.', 'Habilidade BNCC': 'EF06LP15 – Identificar e usar, em textos escritos, convenções ortográficas e gramaticais.\nEF05LP10 – Utilizar convenções ortográficas em textos, como uso de letras e grafemas com base na regularidade da escrita.'},
    {'Série': '6º Ano', 'Questão': 'Q5', 'Alternativa marcada': 'B', 'Nível de conhecimento': 'Avançado', 'Possível causa do erro': 'Alternativa correta', 'Estratégia de intervenção': 'Propor exercícios de identificação de sílaba tônica com leitura em voz alta, e uso de dicionários com divisão silábica.', 'Habilidade BNCC': 'EF06LP18 – Identificar, em textos, regularidades da acentuação gráfica de acordo com a tonicidade das palavras.'},
    {'Série': '6º Ano', 'Questão': 'Q5', 'Alternativa marcada': 'A', 'Nível de conhecimento': 'Intermediário', 'Possível causa do erro': 'Confusão na classificação da palavra “caderno” (que é paroxítona, não proparoxítona).', 'Estratégia de intervenção': 'Práticas com divisão silábica e classificação em grupo (oxítonas, paroxítonas, proparoxítonas).', 'Habilidade BNCC': 'EF06LP18 – Identificar, em textos, regularidades da acentuação gráfica de acordo com a tonicidade das palavras.'},
    {'Série': '6º Ano', 'Questão': 'Q5', 'Alternativa marcada': 'C', 'Nível de conhecimento': 'Muito básico', 'Possível causa do erro': 'Respostas aleatórias ou com base apenas na terminação da palavra (sem análise da tonicidade).', 'Estratégia de intervenção': 'Reforçar o conceito de tonicidade com jogos de separação silábica e marcação da sílaba forte.', 'Habilidade BNCC': 'EF06LP18 – Identificar, em textos, regularidades da acentuação gráfica de acordo com a tonicidade das palavras.'},
    {'Série': '6º Ano', 'Questão': 'Q5', 'Alternativa marcada': 'D', 'Nível de conhecimento': 'Básico', 'Possível causa do erro': 'Inversão de conceitos, troca de oxítona por paroxítona e vice-versa.', 'Estratégia de intervenção': 'Explorar leitura pausada e rítmica de palavras, com destaque visual para a sílaba forte.', 'Habilidade BNCC': 'EF06LP18 – Identificar, em textos, regularidades da acentuação gráfica de acordo com a tonicidade das palavras.'},
])

# --- APP STREAMLIT ---
st.set_page_config(page_title="Relatório Diagnóstico", layout="centered")
st.title("📋 Relatório Diagnóstico Manual")

with st.form("formulario"):
    nome = st.text_input("Nome do aluno")
    turma = st.selectbox("Série", sorted(regua_embutida["Série"].unique()))
    respostas = {}
    for q in sorted(regua_embutida["Questão"].unique()):
        respostas[q] = st.selectbox(f"{q}", ["A", "B", "C", "D"], key=q)
    gerar = st.form_submit_button("Gerar Relatório")

if gerar:
    acertos = 0
    total = 0
    habilidades_domina = []
    habilidades_atencao = []
    estrategias = []

    for q, resp in respostas.items():
        total += 1
        entrada = regua_embutida[
            (regua_embutida["Série"].str.strip().str.lower() == turma.strip().lower()) &
            (regua_embutida["Questão"].str.strip().str.upper() == q.upper()) &
            (regua_embutida["Alternativa marcada"].str.strip().str.upper() == resp.strip().upper())
        ]
        if not entrada.empty:
            e = entrada.iloc[0]
            nivel = e["Nível de conhecimento"]
            habilidade = e["Habilidade BNCC"]
            if "avançado" in nivel.lower() or "intermediário" in nivel.lower():
                habilidades_domina.append(habilidade)
            else:
                habilidades_atencao.append(habilidade)
            if e["Estratégia de intervenção"]:
                estrategias.append(e["Estratégia de intervenção"])
            if "avançado" in nivel.lower() or e["Possível causa do erro"].lower() == "alternativa correta":
                acertos += 1
        else:
            habilidades_atencao.append(f"Habilidade não identificada para {q}")

    percentual = int((acertos / total) * 100) if total > 0 else 0
    if percentual >= 80:
        nivel = "Avançado"
    elif percentual >= 50:
        nivel = "Intermediário"
    else:
        nivel = "Inicial"

    resumo = f"O aluno {nome} demonstrou desempenho **{nivel}**, com {acertos} de {total} acertos ({percentual}%)."
    if habilidades_domina:
