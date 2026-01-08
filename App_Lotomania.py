import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import requests
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Lotomania Inteligente - Pro", page_icon="🧡", layout="wide")

# --- 1. FUNÇÃO PARA BAIXAR DADOS REAIS DA CAIXA ---
@st.cache_data(ttl=3600)
def baixar_dados_reais():
    # URL da API de resultados da Lotomania
    url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotomania/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            dados_json = response.json()
            # Dezenas vêm como string, convertemos para int
            ultimo_resultado_lista = [int(n) for n in dados_json['listaDezenas']]
            concurso_n = dados_json['numero']
            st.sidebar.success(f"✅ Lotomania: Concurso {concurso_n} carregado!")
            return ultimo_resultado_lista, concurso_n
        else:
            st.sidebar.error("⚠️ Falha ao acessar API da Caixa. Usando dados fictícios.")
            return list(range(0, 20)), 0
    except Exception as e:
        st.sidebar.error(f"❌ Erro de conexão: {e}")
        return list(range(0, 20)), 0

# --- 2. LÓGICA DE FILTRAGEM (REGRAS DA LOTOMANIA) ---

def gerar_jogo_ideal(referencia_20):
    """
    Gera um jogo de 50 números baseado nos 20 números do sorteio anterior.
    Filtros: Paridade (23-27 pares), Repetidos (8-12 números do sorteio anterior).
    """
    tentativas = 0
    while True:
        tentativas += 1
        # Gera 50 números únicos entre 0 e 99
        jogo = sorted(random.sample(range(0, 100), 50))
        
        # 1. Filtro de Paridade (Ideal: metade/metade)
        pares = len([n for n in jogo if n % 2 == 0])
        
        # 2. Filtro de Repetidos (Quantos dos 50 escolhidos estavam nos 20 sorteados passados)
        # Estatisticamente, cerca de 10 números se repetem em uma aposta de 50.
        repetidos = len(set(jogo) & set(referencia_20))
        
        # Critérios de Aceitação para Lotomania
        if (23 <= pares <= 27) and (8 <= repetidos <= 12):
            return jogo, tentativas, pares, repetidos

# --- 3. INTERFACE DO USUÁRIO ---

st.title("🧡 Lotomania Pro: Gerador de 50 dezenas")
st.markdown("Analisa o último sorteio e gera um volante equilibrado com **Paridade** e **Repetição Estatística**.")

ultimo_real, n_concurso = baixar_dados_reais()

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader(f"📊 Último Sorteio (C{n_concurso})")
    # Mostrar as 20 dezenas sorteadas
    st.write("Dezenas que saíram:")
    # Formatação para mostrar 00 em vez de 0
    dezenas_formatadas = [f"{n:02d}" for n in sorted(ultimo_real)]
    st.markdown(f" `{' - '.join(dezenas_formatadas)}` ")

    st.divider()
    
    st.subheader("💡 Dica de Especialista")
    st.info("""A Lotomania sorteia 20 números. Ao escolher 50, a tendência 
    matemática é que você acerte cerca de **10 números** que saíram no concurso 
    anterior. O gerador usa essa 'frequência de repetição' a seu favor.""")
    
    # Gráfico Simples de Paridade ideal
    labels = 'Pares', 'Ímpares'
    sizes = [50, 50]
    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#FF9800', '#2196F3'])
    ax.set_title("Equilíbrio Sugerido (50 dezenas)")
    st.pyplot(fig)

with col2:
    st.subheader("🎲 Gerador Automático")
    st.write("Clique abaixo para gerar seu jogo de 50 números com filtros aplicados.")
    
    if st.button("Gerar Aposta de 50 Números"):
        with st.spinner('Analisando 100 dezenas...'):
            jogo_final, busca, p, r = gerar_jogo_ideal(ultimo_real)
        
        st.success(f"### ✅ Seu Jogo (50 dezenas):")
        
        # Exibir em formato de grade ou texto corrido
        txt_jogo = "  ".join([f"**{n:02d}**" for n in jogo_final])
        st.write(txt_jogo)
        
        with st.expander("🔍 Análise de Probabilidade do Jogo"):
            st.write(f"🔹 **Pares:** {p} de 50")
            st.write(f"🔹 **Ímpares:** {50-p} de 50")
            st.write(f"🔹 **Repetidos do Concurso {n_concurso}:** {r}")
            st.write(f"🔹 **Eficiência:** O motor descartou {busca} combinações desequilibradas.")

# --- VISUALIZAÇÃO DO VOLANTE ---
st.divider()
st.subheader("🗺️ Mapa Visual do Volante (10x10)")
st.write("Veja como as dezenas geradas se distribuem no cartão:")

if 'jogo_final' in locals():
    # Criar uma matriz 10x10 para o volante
    volante = np.zeros(100)
    for n in jogo_final:
        volante[n] = 1
    volante = volante.reshape((10, 10))

    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ax2.imshow(volante, cmap='Oranges', edgecolors='black', linewidth=0.5)
    
    # Ajustar labels do gráfico
    ax2.set_xticks(range(10))
    ax2.set_yticks(range(10))
    ax2.set_xticklabels([f"+{i}" for i in range(10)])
    ax2.set_yticklabels([f"{i}0" for i in range(10)])
    
    
    st.pyplot(fig2)
    st.caption("As áreas laranjas representam os números escolhidos.")

st.sidebar.markdown("---")
st.sidebar.warning("⚠️ Atenção: A Lotomania possui 1 em 11 milhões de chances para 20 acertos. Jogue com consciência.")