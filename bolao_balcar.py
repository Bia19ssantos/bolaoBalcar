import streamlit as st
import pandas as pd
import requests
import datetime
import pytz
from PIL import Image
import os

# --- CONFIGURAÇÕES DO GOOGLE FORMS (Substitua pelos novos IDs da BALCAR) ---
URL_FORM_POST = "https://docs.google.com/forms/d/e/[SEU_NOVO_ID_AQUI]/formResponse"
ENTRY_NOME = "entry.155949992"     # ID da pergunta 'Motorista'
ENTRY_JOGO = "entry.1025675970"    # ID da pergunta 'Jogo'
ENTRY_PALPITE = "entry.626328654"  # ID da pergunta 'Palpite'

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bolão BALCAR - Rumo ao Hexa", page_icon="🚖", layout="centered")

# Estilização CSS personalizada para o visual Dark/Premium da BALCAR
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .caixa-balcar {
        background-color: #141414;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #ffffff;
        margin-bottom: 20px;
        border-right: 1px solid #222222;
        border-top: 1px solid #222222;
        border-bottom: 1px solid #222222;
    }
    h1, h2, h3, h4 { color: #ffffff !important; font-family: 'Arial Black', sans-serif; }
    .stTabs [data-baseweb="tab"] { color: #888888; }
    .stTabs [data-baseweb="tab"]:hover { color: #ffffff; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #ffffff; border-bottom-color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# --- EXIBIÇÃO DO LOGO LOGO NO TOPO ---
col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
with col_logo_2:
    if os.path.exists("logo.jpeg"):
        imagem_logo = Image.open("logo.jpeg")
        st.image(imagem_logo, use_container_width=True)
    else:
        # Título reserva caso o arquivo de imagem não seja encontrado na pasta
        st.markdown('<h1 style="text-align: center;">BALCAR</h1>', unsafe_allow_html=True)

st.markdown('<h3 style="text-align: center; margin-top: -10px;">🏆 BOLÃO DOS MOTORISTAS PARCEIROS 🇧🇷</h3>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888888; font-size: 14px;">Pilote seus palpites nos jogos do Brasil e lidere o ranking corporativo!</p>', unsafe_allow_html=True)
st.markdown("---")

# --- LISTA OFICIAL DE MOTORISTAS BALCAR ---
motoristas_lista = [
    "Alexandre", "Carlos Silva", "Daniel Santos", "Eduardo", 
    "Fernando", "Marcos Motorista", "Rodrigo BALCAR", "Wanderson"
]
motoristas_lista.sort()

# --- COLOQUE SUAS FUNÇÕES DE LEITURA DA PLANILHA AQUI ---
# def carregar_jogos(): ...
# def carregar_palpites(): ...

# Configurações de Fuso Horário
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.datetime.now(fuso_br)

if "jogos" not in st.session_state:
    st.session_state.jogos = carregar_jogos()
if "palpites" not in st.session_state:
    st.session_state.palpites = carregar_palpites()

# Criando a estrutura de abas limpas
tab1, tab2, tab3 = st.tabs(["🎯 Lançar Palpite", "🔍 Palpites da Rodada", "🏆 Ranking Geral"])

# --- ABA 1: PALPITES (Apenas Jogos do Brasil no Dia) ---
with tab1:
    st.markdown("""
        <div class="caixa-balcar">
            <h4 style="margin-top:0;">📊 Critérios de Pontuação BALCAR</h4>
            <ul style="margin-bottom:0; padding-left:20px;">
                <li><strong>🟢 Placar Exato:</strong> Você ganha <strong>10 pontos</strong>.</li>
                <li><strong>🟡 Acertou a Tendência (Vencedor/Empate):</strong> Você ganha <strong>4 pontos</strong>.</li>
                <li><strong>🔴 Errou o Resultado:</strong> Você ganha <strong>0 pontos</strong>.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("✍️ Registrar Nova Corrida")
    nome = st.selectbox("Quem é o motorista?", ["Selecione seu nome..."] + motoristas_lista)
    
    # Filtro focado estritamente nas 24h do dia de hoje
    inicio_hoje = agora_br.replace(hour=0, minute=0, second=0, microsecond=0)
    fim_hoje = agora_br.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    jogos_disponiveis = {
        k: v for k, v in st.session_state.jogos.items() 
        if inicio_hoje <= v["data_completa"] <= fim_hoje and not v["encerrado"] and agora_br < v["data_completa"]
    }
    
    if not jogos_disponiveis:
        st.info("📆 Nenhuma partida da Seleção Brasileira aberta para palpites hoje!")
    else:
        jogo_selecionado = st.selectbox(
            "Selecione o confronto do Brasil:", 
            list(jogos_disponiveis.keys()), 
            format_func=lambda x: f"{jogos_disponiveis[x]['confronto']} ({jogos_disponiveis[x]['data_completa'].strftime('%H:%M')})"
        )
        
        if nome != "Selecione seu nome...":
            dados_jogo = jogos_disponiveis[jogo_selecionado]
            nome_confronto = dados_jogo['confronto']
            
            # Trava para impedir mais de um palpite por motorista por partida
            ja_palpitou = False
            palpite_anterior = ""
            for p in st.session_state.palpites:
                if p["Participante"].lower() == nome.lower() and p["Jogo"].upper().strip() == nome_confronto.upper().strip():
                    ja_palpitou = True
                    palpite_anterior = p["Palpite"]
                    break
            
            if ja_palpitou:
                st.warning(f"⚠️ **{nome}**, você já salvou um palpite para este confronto! Seu placar registrado é: **{palpite_anterior}**.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    gols_1 = st.number_input(f"Gols: Brasil", min_value=0, value=0, step=1, key="g1")
                with col2:
                    # Isola o nome do adversário dinamicamente para a interface
                    times = nome_confronto.split(' X ')
                    adversario = times[1] if "Brasil" in times[0] else times[0]
                    gols_2 = st.number_input(f"Gols: {adversario}", min_value=0, value=0, step=1, key="g2")
                    
                if st.button("Confirmar Palpite! 🚖"):
                    placar_string = f"{gols_1}X{gols_2}" if "Brasil" in times[0] else f"{gols_2}X{gols_1}"
                    
                    dados_envio = {ENTRY_NOME: nome, ENTRY_JOGO: nome_confronto, ENTRY_PALPITE: placar_string}
                    resposta = requests.post(URL_FORM_POST, data=dados_envio)
                    
                    if resposta.status_code == 200 or "formResponse" in resposta.url:
                        st.success(f"🏁 Excelente, {nome}! Seu palpite ({placar_string}) foi computado!")
                        st.session_state.palpites = carregar_palpites()
                        st.rerun()
                    else:
                        st.error("❌ Falha técnica ao sincronizar. Comunique o administrador da BALCAR.")

# --- ABA 2: VISUALIZAÇÃO DOS PALPITES COM FILTROS ---
with tab2:
    st.subheader("🔍 Painel de Monitoramento de Palpites")
    busca_nome = st.selectbox("Filtrar por Motorista:", ["Todos"] + motoristas_lista)
    
    mapa_resultados = {}
    for j_id, info in st.session_state.jogos.items():
        chave_jogo = str(info["confronto"]).upper().strip()
        mapa_resultados[chave_jogo] = str(info["resultado"]).upper().replace(" ", "") if info["resultado"] else None

    palpites_filtrados = [p for p in st.session_state.palpites if busca_nome == "Todos" or p["Participante"].lower() == busca_nome.lower()]
            
    if palpites_filtrados:
        dados_tabela = []
        for p in palpites_filtrados:
            nome_jogo = str(p["Jogo"]).upper().strip()
            palpite_limpo = str(p["Palpite"]).upper().replace(" ", "")
            status_icone = "⏳ Corrida em andamento"
            
            if nome_jogo in mapa_resultados and mapa_resultados[nome_jogo]:
                res_real = mapa_resultados[nome_jogo]
                if palpite_limpo == res_real:
                    status_icone = "🟢 Placar Exato (+10 pts)"
                else:
                    try:
                        g_p1, g_p2 = map(int, palpite_limpo.split("X"))
                        g_r1, g_r2 = map(int, res_real.split("X"))
                        vencedor_p = 1 if g_p1 > g_p2 else (2 if g_p2 > g_p1 else 0)
                        vencedor_r = 1 if g_r1 > g_r2 else (2 if g_r2 > g_r1 else 0)
                        status_icone = "🟡 Acertou o Vencedor (+4 pts)" if vencedor_p == vencedor_r else "🔴 Zero Pontos"
                    except: status_icone = "❌ Formato Incorreto"
            
            dados_tabela.append({"Motorista": p["Participante"], "Confronto": p["Jogo"], "Palpite": p["Palpite"], "Análise de Desempenho": status_icone})
            
        st.dataframe(pd.DataFrame(dados_tabela), use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum palpite foi localizado para este filtro.")

# --- ABA 3: RANKING CORPORATIVO ---
with tab3:
    st.subheader("🏆 Pódio de Líderes BALCAR")
    # Insira aqui seu loop idêntico de soma de pontos da classificação geral