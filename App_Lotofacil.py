import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Lotofácil Inteligente V2", page_icon="🍀", layout="wide")

# --- 1. CAPTURA DE DADOS (Últimos 10 Jogos) ---
@st.cache_data(ttl=3600)
def buscar_historico_10():
    url_base = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    resultados = []
    try:
        # Busca o último para saber o número do concurso
        req = requests.get(url_base, headers=headers, verify=False)
        ultimo_n = req.json()['numero']
        
        # Loop para pegar os últimos 10 (Simulação de busca sequencial)
        # Nota: Na API oficial, você pode precisar iterar ou usar um endpoint de histórico
        for i in range(10):
            n_concurso = ultimo_n - i
            res = requests.get(f"{url_base}{n_concurso}", headers=headers, verify=False)
            if res.status_code == 200:
                dezenas = [int(n) for n in res.json()['listaDezenas']]
                resultados.append(dezenas)
        
        return resultados, ultimo_n
    except:
        # Fallback caso a API falhe (Dados fictícios para exemplo)
        return [[random.sample(range(1, 26), 15)] for _ in range(10)], 0

# --- 2. LÓGICA DE PROBABILIDADE ---
def analisar_frequencia(historico):
    # Conta quantas vezes cada número apareceu nos últimos 10
    contagem = {i: 0 for i in range(1, 26)}
    for sorteio in historico:
        for num in sorteio:
            contagem[num] += 1
    return contagem

def gerar_jogo_probabilistico(frequencia, ultimo_resultado):
    tentativas = 0
    # Classifica números
    quentes = [n for n, f in frequencia.items() if f >= 7] # Sairam em 70%+ dos jogos
    frios = [n for n, f in frequencia.items() if f <= 3]   # Sairam em 30%- dos jogos
    neutros = [n for n, f in frequencia.items() if 3 < f < 7]

    while True:
        tentativas += 1
        # Estratégia: Pegar 8 quentes, 4 neutros e 3 frios (Exemplo de balanço)
        jogo = random.sample(quentes, min(len(quentes), 8)) + \
               random.sample(neutros, min(len(neutros), 5)) + \
               random.sample(frios, min(len(frios), 2))
        
        # Preencher se faltar números para fechar 15
        while len(jogo) < 15:
            n = random.randint(1, 25)
            if n not in jogo: jogo.append(n)
            
        jogo = sorted(jogo)
        
        # Filtros Estatísticos
        pares = len([n for n in jogo if n % 2 == 0])
        repetidos = len(set(jogo) & set(ultimo_resultado))
        soma = sum(jogo)

        # Critérios de Ouro:
        if (7 <= pares <= 8) and (8 <= repetidos <= 10) and (170 <= soma <= 220):
            return jogo, tentativas, pares, repetidos, soma

# --- 3. INTERFACE ---
st.title("🍀 Lotofácil Pro: Análise dos Últimos 10 Jogos")

historico, ultimo_id = buscar_historico_10()
freq = analisar_frequencia(historico)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Frequência nos Últimos 10 Concursos")
    df_freq = pd.DataFrame(list(freq.items()), columns=['Número', 'Frequência'])
    
    # Gráfico de Calor
    fig, ax = plt.subplots(figsize=(10, 4))
    cores = ['red' if f > 7 else 'green' if f > 4 else 'gray' for f in df_freq['Frequência']]
    ax.bar(df_freq['Número'], df_freq['Frequência'], color=cores)
    ax.set_xticks(range(1, 26))
    ax.set_ylabel("Vezes que sorteado")
    st.pyplot(fig)
    st.caption("🔴 Quentes | 🟢 Médios | ⚪ Frios (Tendência de atraso)")



with col2:
    st.subheader("🎲 Gerador Baseado em Tendência")
    if st.button("Gerar Jogo Otimizado"):
        ultimo_sorteio = historico[0]
        jogo, busca, p, r, s = gerar_jogo_probabilistico(freq, ultimo_sorteio)
        
        st.success(f"### {jogo}")
        
        st.info(f"""
        **Análise Técnica:**
        - **Pares:** {p} | **Ímpares:** {15-p}
        - **Repetidos do último:** {r}
        - **Soma:** {s}
        - **Esforço computacional:** {busca} combinações analisadas.
        """)
