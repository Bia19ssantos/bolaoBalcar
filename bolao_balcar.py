import streamlit as st
import pandas as pd
import requests
import datetime
import pytz
from PIL import Image
import os

# ==============================================================================
# 1. CONFIGURAÇÕES INTEGRADAS DO GOOGLE (APONTANDO PARA FORM_RESPONSES)
# ==============================================================================
ID_PLANILHA = "1iB69UoTSku2biNsdAUYZrdglQU-m7M_wERQlIKagoDM"

ID_DO_FORMS = "1FAIpQLScVPiQTPAOdGLFXrXpXuG-GdYs81JX939Qp1GPWf6c-KAyu5Q"
URL_FORM_POST = f"https://docs.google.com/forms/d/e/{ID_DO_FORMS}/formResponse"

ENTRY_NOME = "entry.1751255709"     # Pergunta 'Participante'
ENTRY_JOGO = "entry.345816005"      # Pergunta 'Jogo'
ENTRY_PALPITE = "entry.1813555350"   # Pergunta 'Palpite'

# Links de comunicação direta corrigidos para puxar a aba Form_Responses exibida no print
URL_JOGOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/gviz/tq?tqx=out:csv&sheet=jogos"
URL_PALPITES = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/gviz/tq?tqx=out:csv&sheet=Form_Responses"

# ==============================================================================
# 2. CONFIGURAÇÃO VISUAL PREMIUM (MODO ESCURO BALCAR)
# ==============================================================================
st.set_page_config(page_title="Bolão BALCAR - Rumo ao Hexa", page_icon="🚖", layout="centered")

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

col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
with col_logo_2:
    if os.path.exists("logo.jpeg"):
        imagem_logo = Image.open("logo.jpeg")
        st.image(imagem_logo, use_container_width=True)
    else:
        st.markdown('<h1 style="text-align: center; margin-bottom: 0;">BALCAR</h1>', unsafe_allow_html=True)

st.markdown('<h3 style="text-align: center; margin-top: -10px;">🏆 BOLÃO DOS MOTORISTAS PARCEIROS 🇧🇷</h3>', unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# 3. LISTA OFICIAL DE MOTORISTAS BALCAR
# ==============================================================================
motoristas_lista = [
    "4 - Balthazar Noel De Souza", "104 - Silvio Adriano De Carvalho Silva", "152 - Ranieri Pereira Da Silva",
    "176 - Samuel Rosa Júnior", "191 - Giorgio Luis Gomes Da Silva", "197 - Johan Delvis Flores ESIS",
    "202 - Mario sergio Bertoldo", "225 - Fabio Correa De Oliveira", "247 - Leticia Aparecida Rodrigues Vieira",
    "267 - Laerte Do Amaral Junior", "269 - Rafael Dos Santos Lima", "285 - Leonardo Mota De Oliveira",
    "291 - Sidnei Dias De Freitas Junior", "309 - Luiz Paulo Feliz Fernandes", "319 - Wellington Bruno Ferraz",
    "320 - Kaique Ruivo", "322 - Gilmar Ribeiro Ferraz", "351 - Cleferson Araujo",
    "367 - Thalles Ismael Dos Santos", "397 - Juliano Eloy", "399 - Valdinei Bruno De Souza",
    "451 - Paulo Elias Servulo", "465 - Vagner Da Silva Moraes", "477 - Andreo Cristiano Gonzaga",
    "479 - Claudinei Paes", "486 - Silvia de Souza Martins", "497 - Gerson Da Silva Altesor",
    "498 - Luiz Antônio Gomes Dos Santos", "524 - Murilo De Paula", "526 - Matheus Arruda Pereira",
    "540 - Marcela Souza De Almeida", "542 - Vinicius Luiz Andrade Sousa", "543 - william jose cirrea",
    "545 - Araão Eduardo Dos Santos", "548 - Luciano Pacheco", "550 - Ricardo Claudino",
    "551 - Guilherme Alexandre", "554 - William Leandro Thomé", "558 - Lucas Godinho Correa"
]

# ==============================================================================
# 4. SISTEMA DE LEITURA COM EXPIRAÇÃO DE CACHE (ANTI-DUPLICADOS EM TEMPO REAL)
# ==============================================================================
def carregar_jogos():
    try:
        # Adiciona um marcador de tempo para forçar o Google a mandar os dados mais recentes
        df = pd.read_csv(f"{URL_JOGOS}&cachebuster={datetime.datetime.now().timestamp()}")
        df.columns = df.columns.str.strip()
        jogos_dict = {}
        
        for _, row in df.iterrows():
            id_jogo = str(row['Id']).strip()
            encerrado_val = str(row['Encerrado']).strip().upper()
            is_encerrado = True if encerrado_val in ['TRUE', '1', '1.0'] else False
            
            # Limpa o nome do confronto retirando espaços extras internos
            confronto_limpo = " ".join(str(row['Confronto']).strip().upper().split())
            
            jogos_dict[id_jogo] = {
                "confronto": confronto_limpo,
                "resultado": str(row['Resultado']).strip() if pd.notna(row['Resultado']) else None,
                "encerrado": is_encerrado
            }
        return jogos_dict
    except:
        return {}

def carregar_palpites():
    try:
        df = pd.read_csv(f"{URL_PALPITES}&cachebuster={datetime.datetime.now().timestamp()}")
        df.columns = df.columns.str.strip()
        palpites_lista = []
        
        col_nome = 'Participante' if 'Participante' in df.columns else df.columns[1]
        
        for _, row in df.iterrows():
            jogo_limpo = " ".join(str(row['Jogo']).strip().upper().split())
            palpites_lista.append({
                "Participante": str(row[col_nome]).strip(),
                "Jogo": jogo_limpo,
                "Palpite": str(row['Palpite']).strip().upper().replace(" ", "")
            })
        return palpites_lista
    except:
        return []

# Carrega os dados mais frescos do servidor do Sheets
st.session_state.jogos = carregar_jogos()
st.session_state.palpites = carregar_palpites()

tab1, tab2, tab3 = st.tabs(["🎯 Lançar Palpite", "🔍 Palpites da Rodada", "🏆 Ranking Geral"])

# ==============================================================================
# ABA 1: LANÇAR PALPITE
# ==============================================================================
with tab1:
    st.markdown("""
        <div class="caixa-balcar">
            <h4 style="margin-top:0;">📊 Regras de Pontuação</h4>
            <ul style="margin-bottom:0; padding-left:20px;">
                <li><strong>🟢 Placar Exato:</strong> Ganha 10 pontos</li>
                <li><strong>🟡 Vencedor ou Empate:</strong> Ganha 4 pontos</li>
                <li><strong>🔴 Erro de Tendência:</strong> Ganha 0 pontos</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("✍️ Escolha um jogo para palpitar")
    
    nome = st.selectbox("Quem está jogando?", ["Selecione seu nome..."] + motoristas_lista)
    
    jogos_disponiveis = {k: v for k, v in st.session_state.jogos.items() if not v["encerrado"]}
    
    if not jogos_disponiveis:
        st.info("📆 No momento, não há partidas disponíveis para palpite.")
    else:
        jogo_selecionado = st.selectbox(
            "Escolha o jogo:", 
            list(jogos_disponiveis.keys()), 
            format_func=lambda x: f"{jogos_disponiveis[x]['confronto']}"
        )
        
        dados_jogo = jogos_disponiveis[jogo_selecionado]
        nome_confronto = dados_jogo['confronto']
        
        # Só executa a validação se um motorista real for selecionado
        if nome != "Selecione seu nome...":
            ja_palpitou = False
            palpite_anterior = ""
            
            for p in st.session_state.palpites:
                # Compara limpando qualquer divergência de maiúsculas/minúsculas e de espaços extras
                if p["Participante"].strip().lower() == nome.strip().lower() and p["Jogo"] == nome_confronto:
                    ja_palpitou = True
                    palpite_anterior = p["Palpite"]
                    break
            
            if ja_palpitou:
                st.error(f"🚫 {nome}, você já registrou um palpite para {nome_confronto}: **{palpite_anterior}**.")
                st.info("💡 Não é permitido enviar mais de um palpite por jogo. O seu botão de envio foi bloqueado!")
            else:
                col1, col2 = st.columns(2)
                times = nome_confronto.split(' X ')
                
                with col1:
                    gols_1 = st.number_input(f"Gols: {times[0]}", min_value=0, value=0, step=1)
                with col2:
                    gols_2 = st.number_input(f"Gols: {times[1]}", min_value=0, value=0, step=1)
                    
                if st.button("Confirmar Palpite! 🚖"):
                    placar_string = f"{gols_1}X{gols_2}"
                    dados_envio = {ENTRY_NOME: nome, ENTRY_JOGO: nome_confronto, ENTRY_PALPITE: placar_string}
                    resposta = requests.post(URL_FORM_POST, data=dados_envio)
                    
                    if resposta.status_code == 200 or "formResponse" in resposta.url:
                        st.success(f"🏁 Palpite computado com sucesso, boa sorte!")
                        st.rerun()
                    else:
                        st.error("❌ Ocorreu um erro ao enviar os dados para a nuvem.")

# ==============================================================================
# ABA 2: PALPITES DA RODADA
# ==============================================================================
with tab2:
    st.subheader("🔍 Histórico de Palpites")
    busca_nome = st.selectbox("Filtrar por participante:", ["Todos"] + motoristas_lista, key="filtro_motorista")
    mapa_resultados = {str(info["confronto"]).upper().strip(): str(info["resultado"]).upper().replace(" ", "") for j_id, info in st.session_state.jogos.items() if info["resultado"]}
    palpites_filtrados = [p for p in st.session_state.palpites if busca_nome == "Todos" or p["Participante"].lower() == busca_nome.lower()]
            
    if palpites_filtrados:
        dados_tabela = []
        for p in palpites_filtrados:
            nome_jogo = str(p["Jogo"]).upper().strip()
            palpite_limpo = str(p["Palpite"]).upper().replace(" ", "")
            status_icone = "⏳ Jogo em andamento"
            
            if nome_jogo in mapa_resultados:
                res_real = mapa_resultados[nome_jogo]
                if palpite_limpo == res_real:
                    status_icone = "🟢 Placar Exato (+10)"
                else:
                    try:
                        g_p1, g_p2 = map(int, palpite_limpo.split("X"))
                        g_r1, g_r2 = map(int, res_real.split("X"))
                        v_p = 1 if g_p1 > g_p2 else (2 if g_p2 > g_p1 else 0)
                        v_r = 1 if g_r1 > g_r2 else (2 if g_r2 > g_r1 else 0)
                        status_icone = "🟡 Vencedor/Empate (+4)" if v_p == v_r else "🔴 0 pontos"
                    except: status_icone = "❌ Erro formatação"
            dados_tabela.append({"Motorista": p["Participante"], "Jogo": p["Jogo"], "Palpite": p["Palpite"], "Resultado": status_icone})
        st.dataframe(pd.DataFrame(dados_tabela), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum palpite localizado.")

# ==============================================================================
# ABA 3: RANKING GERAL
# ==============================================================================
with tab3:
    st.subheader("🏆 Classificação Geral")
    pontos = {nome: 0 for nome in motoristas_lista}
    mapa_ranking = {str(info["confronto"]).upper().strip(): str(info["resultado"]).upper().replace(" ", "") for j_id, info in st.session_state.jogos.items() if info["resultado"]}

    for p in st.session_state.palpites:
        ch = str(p["Jogo"]).upper().strip()
        pl = str(p["Palpite"]).upper().replace(" ", "")
        mot = p["Participante"]
        
        if ch in mapa_ranking and mot in pontos:
            rr = mapa_ranking[ch]
            if pl == rr:
                pontos[mot] += 10
            else:
                try:
                    g_p1, g_p2 = map(int, pl.split("X"))
                    g_r1, g_r2 = map(int, rr.split("X"))
                    if (g_p1 > g_p2 and g_r1 > g_r2) or (g_p2 > g_p1 and g_r2 > g_r1) or (g_p1 == g_p2 and g_r1 == g_r2):
                        pontos[mot] += 4
                except: pass
                    
    df_ranking = pd.DataFrame(list(pontos.items()), columns=["Motorista", "Pontos"]).sort_values(by="Pontos", ascending=False)
    st.dataframe(df_ranking, use_container_width=True, hide_index=True)
