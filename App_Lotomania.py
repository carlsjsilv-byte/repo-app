import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import requests
import numpy as np

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Lotomania Expert - 10 Jogos", page_icon="🧡", layout="wide")

# --- 1. BUSCA DE HISTÓRICO EXPANDIDO ---
@st.cache_data(ttl=3600)
def buscar_historico_lotomania():
    url_base = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotomania/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    historico = []
    try:
        req = requests.get(url_base, headers=headers, verify=False)
        ultimo_n = req.json()['numero']
        
        # Coletamos os últimos 10 concursos
        for i in range(10):
            res = requests.get(f"{url_base}{ultimo_n - i}", headers=headers, verify=False)
            if res.status_code == 200:
                dezenas = [int(n) for n in res.json()['listaDezenas']]
                historico.append(dezenas)
        return historico, ultimo_n
    except:
        return [random.sample(range(100), 20) for _ in range(10)], 0

# --- 2. MOTOR DE INTELIGÊNCIA ---
def analisar_tendencias(historico):
    contagem = {i: 0 for i in range(100)}
    for sorteio in historico:
        for num in sorteio:
            contagem[num] += 1
    return contagem

def gerar_jogo_otimizado(frequencia, ultimo_resultado):
    # Separar dezenas por performance nos últimos 10 jogos
    quentes = [n for n, f in frequencia.items() if f >= 4] # Saíram em 40% ou +
    frias = [n for n, f in frequencia.items() if f <= 1]   # Saíram em 10% ou -
    neutras = [n for n, f in frequencia.items() if 1 < f < 4]

    tentativas = 0
    while True:
        tentativas += 1
        # Estratégia Pro: 20 Quentes, 20 Neutras, 10 Frias (Equilíbrio de ciclos)
        jogo = random.sample(quentes, 20) + random.sample(neutras, 20) + random.sample(frias, 10)
        jogo = sorted(jogo)
        
        pares = len([n for n in jogo if n % 2 == 0])
        repetidos_ultimo = len(set(jogo) & set(ultimo_resultado))
        
        # Filtros de Elite para Lotomania (50 números):
        # Paridade: Entre 23 e 27 pares (Média histórica)
        # Repetidos: Entre 8 e 12 do último concurso
        if (23 <= pares <= 27) and (8 <= repetidos_ultimo <= 12):
            return jogo, tentativas, pares, repetidos_ultimo

# --- 3. INTERFACE ---
st.title("🧡 Lotomania Inteligente: Análise de Ciclos")

historico, n_concurso = buscar_historico_lotomania()
freq = analisar_tendencias(historico)

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📊 Mapa de Calor (Últimos 10)")
    
    # Criar matriz para o Heatmap
    mapa = np.array([freq[i] for i in range(100)]).reshape(10, 10)
    fig, ax = plt.subplots(figsize=(5, 5))
    im = ax.imshow(mapa, cmap='YlOrRd')
    plt.colorbar(im, ax=ax, label="Frequência")
    ax.set_title("Onde os números estão saindo?")
    st.pyplot(fig)
    st.info("🔥 Tons escuros: Dezenas que mais saíram recentemente.")



with col2:
    st.subheader("🎲 Gerador Baseado em Probabilidade")
    if st.button("Gerar Jogo de 50 Números"):
        jogo, busca, p, r = gerar_jogo_otimizado(freq, historico[0])
        
        st.success("### ✅ Dezenas Selecionadas:")
        txt_jogo = " ".join([f"`{n:02d}`" for n in jogo])
        st.write(txt_jogo)
        
        # Distribuição visual do jogo gerado
        volante = np.zeros(100)
        for n in jogo: volante[n] = 1
        volante = volante.reshape(10, 10)
        
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        ax2.imshow(volante, cmap='Oranges', edgecolors='black', linewidth=0.1)
        ax2.set_title("Distribuição no Volante")
        st.pyplot(fig2)
        
        st.write(f"⚙️ **Filtros Aplicados:** {p} Pares | {r} Repetidos do anterior.")
        st.caption(f"Analisadas {busca} combinações para chegar neste equilíbrio.")

st.divider()
st.sidebar.info(f"Conectado ao Concurso: {n_concurso}")