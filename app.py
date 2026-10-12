import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
try:
    from zoneinfo import ZoneInfo
    FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")
except Exception:
    FUSO_BRASIL = timezone(timedelta(hours=-3))

import os
import unicodedata
import requests
import json
import time
from PIL import Image

def obter_agora_brasil():
    """Retorna datetime atual de Brasília."""
    return datetime.now(FUSO_BRASIL)

# -------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS (FORÇAR TEMA CLARO ABSOLUTO)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Master Café - Gestão de Frota",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* Desativa menus e botões padrão do Streamlit */
        #MainMenu, footer, .stDeployButton, [data-testid="stToolbarActions"],
        [data-testid="stDecoration"], [data-testid="manage-app-button"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* 1. FUNDO GERAL DA PÁGINA */
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }

        /* 2. LABELS E TEXTOS */
        p, span, label, h1, h2, h3, h4, div {
            color: #0F172A !important;
        }
        .stWidgetLabel p, label p {
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 0.90rem !important;
        }

        /* 3. FORMULÁRIO E CARTÕES */
        [data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 14px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
            padding: 24px !important;
        }
        .header-card {
            background: #FFFFFF !important;
            padding: 22px !important;
            border-radius: 14px !important;
            text-align: center !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04) !important;
            margin-bottom: 1.5rem !important;
        }
        .header-title {
            font-size: 1.45rem !important;
            font-weight: 700 !important;
            color: #0F172A !important;
            margin-top: 8px !important;
            margin-bottom: 2px !important;
        }
        .header-subtitle {
            font-size: 0.90rem !important;
            color: #64748B !important;
            margin: 0 !important;
        }
        .card-info {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-left: 4px solid #2563EB !important;
            padding: 14px 16px !important;
            border-radius: 10px !important;
            margin: 12px 0 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
            color: #334155 !important;
            line-height: 1.6 !important;
        }
        .card-status-running {
            background-color: #EFF6FF !important;
            border: 1px solid #BFDBFE !important;
            padding: 16px !important;
            border-radius: 12px !important;
            margin-bottom: 1.2rem !important;
            color: #1E3A8A !important;
            line-height: 1.65 !important;
        }
        .card-status-running b, .card-status-running span {
            color: #1E3A8A !important;
        }

        /* 4. FORÇAR TEMA CLARO EM TODAS AS CAIXAS DE ENTRADA (BASEWEB) */
        div[data-baseweb="input"],
        div[data-baseweb="base-input"],
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] > div,
        div[data-testid="stDateInput"] > div,
        div[data-testid="stTimeInput"] > div,
        div[data-testid="stNumberInput"] > div {
            background-color: #FFFFFF !important;
            border-color: #CBD5E1 !important;
            color: #0F172A !important;
            border-radius: 8px !important;
        }

        /* Inputs reais de digitação */
        input[type="text"], 
        input[type="number"], 
        input[type="password"],
        input {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: none !important;
            -webkit-text-fill-color: #0F172A !important;
        }
        input::placeholder {
            color: #94A3B8 !important;
            -webkit-text-fill-color: #94A3B8 !important;
        }

        /* 5. BOTÕES DE + E - DO KM INICIAL / KM FINAL (NUMBER INPUT) */
        div[data-testid="stNumberInputStepDown"],
        div[data-testid="stNumberInputStepUp"] {
            background-color: #F1F5F9 !important;
            border: 1px solid #CBD5E1 !important;
            color: #0F172A !important;
            border-radius: 6px !important;
            margin: 2px !important;
        }
        div[data-testid="stNumberInputStepDown"]:hover,
        div[data-testid="stNumberInputStepUp"]:hover {
            background-color: #E2E8F0 !important;
        }
        div[data-testid="stNumberInputStepDown"] svg,
        div[data-testid="stNumberInputStepUp"] svg {
            fill: #0F172A !important;
            stroke: #0F172A !important;
        }

        /* 6. CALENDÁRIO / POPOVER / DROPDOWN CLARO */
        div[data-baseweb="popover"],
        div[data-baseweb="calendar"],
        div[data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
            border-radius: 10px !important;
        }
        div[data-baseweb="calendar"] * {
            background-color: transparent !important;
            color: #0F172A !important;
        }
        div[data-baseweb="calendar"] [aria-selected="true"] {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            border-radius: 50% !important;
        }
        div[data-baseweb="calendar"] button:hover {
            background-color: #EFF6FF !important;
            color: #2563EB !important;
        }
        li[role="option"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
        }
        li[role="option"]:hover, li[aria-selected="true"] {
            background-color: #EFF6FF !important;
            color: #2563EB !important;
        }

        /* 7. BOTÕES PRINCIPAIS (START INICIAL E START FINAL) - AZUL VIBRANTE CLARO */
        div.stButton > button:first-child,
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            height: 48px !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.28) !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }
        div.stButton > button:first-child:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            background: linear-gradient(135deg, #1D4ED8, #1E40AF) !important;
            background-color: #1D4ED8 !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.38) !important;
        }

        /* Barra Lateral */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
        }
        section[data-testid="stSidebar"] div.stButton > button {
            background: #F1F5F9 !important;
            color: #334155 !important;
            -webkit-text-fill-color: #334155 !important;
            box-shadow: none !important;
            border: 1px solid #CBD5E1 !important;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. VARIÁVEIS GLOBAIS E LINKS
# -------------------------------------------------------------
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxXSQRM3lPFIQ6VkDs4OK7HrjnfIDrPEPOTM2sAHhogHNhb2PhSoUSw06fYT-rGeiS2uw/exec"
SPREADSHEET_ID = "1-Bn0VBnRV1zp_f7QrKTldKB03L9_k7DyRO3YslGMnnU"

GID_USUARIOS = "426012097"       # Aba com Login / Condutores
GID_VEICULOS = "0"               # Aba com a lista de veículos da frota
GID_LANCAMENTOS = "379222602"    # Aba onde serão gravados os registros de frota

# -------------------------------------------------------------
# 3. SUPORTE A LOGOTIPO E CABEÇALHO
# -------------------------------------------------------------
def obter_caminho_logotipo():
    extensoes = [".png", ".jpg", ".jpeg", ".svg", ".webp", ""]
    nomes = ["Logotipo", "logotipo", "Logo", "logo"]
    for nome in nomes:
        for ext in extensoes:
            caminho = f"{nome}{ext}"
            if os.path.exists(caminho) and not os.path.isdir(caminho):
                return caminho
    return None

def renderizar_cabecalho(subtitulo="Gestão e Controle de Frota"):
    caminho_logo = obter_caminho_logotipo()
    st.markdown('<div class="header-card">', unsafe_allow_html=True)
    if caminho_logo:
        try:
            logo_img = Image.open(caminho_logo)
            col_l, col_m, col_r = st.columns([1, 2.2, 1])
            with col_m:
                st.image(logo_img, use_container_width=True)
        except Exception:
            st.markdown('<div class="header-title">Master Café ☕</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="header-title">Master Café ☕</div>', unsafe_allow_html=True)
    
    st.markdown(f'<p class="header-subtitle">{subtitulo}</p></div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. GESTÃO DE PERSISTÊNCIA DA VIAGEM
# -------------------------------------------------------------
PASTA_SESSAO = "viagens_ativas"
os.makedirs(PASTA_SESSAO, exist_ok=True)

def caminho_arquivo_viagem(usuario):
    user_sanitizado = "".join(c for c in str(usuario) if c.isalnum() or c in "_-")
    return os.path.join(PASTA_SESSAO, f"viagem_{user_sanitizado}.json")

def salvar_viagem_em_andamento(usuario, dados):
    try:
        with open(caminho_arquivo_viagem(usuario), "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def carregar_viagem_em_andamento(usuario):
    caminho = caminho_arquivo_viagem(usuario)
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def limpar_viagem_em_andamento(usuario):
    caminho = caminho_arquivo_viagem(usuario)
    if os.path.exists(caminho):
        try:
            os.remove(caminho)
        except Exception:
            pass

# -------------------------------------------------------------
# 5. SUPORTE E LEITURA DA PLANILHA
# -------------------------------------------------------------
def normalizar_texto(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.strip().lower()

@st.cache_data(ttl=60)
def carregar_usuarios():
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_USUARIOS}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_USUARIOS}"
    ]
    for url in urls:
        try:
            df = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df.empty:
                cols_norm = {normalizar_texto(c): c for c in df.columns}
                c_user = cols_norm.get("usuario", cols_norm.get("login", df.columns[0]))
                c_pass = cols_norm.get("senha", df.columns[1] if len(df.columns) > 1 else df.columns[0])
                c_nome = cols_norm.get("nome", cols_norm.get("condutor", c_user))

                df_res = pd.DataFrame()
                df_res["usuario"] = df[c_user].fillna("").astype(str).str.strip().str.lower()
                df_res["senha"] = df[c_pass].fillna("").astype(str).str.strip()
                df_res["nome"] = df[c_nome].fillna(df[c_user]).astype(str).str.strip()
                return df_res
        except Exception:
            continue

    return pd.DataFrame([{"usuario": "admin", "senha": "123", "nome": "Condutor"}])

@st.cache_data(ttl=30)
def carregar_veiculos():
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_VEICULOS}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_VEICULOS}"
    ]
    for url in urls:
        try:
            df_raw = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df_raw.empty and len(df_raw.columns) >= 5:
                col_veiculo = df_raw.columns[1]  # Coluna B
                col_placa = df_raw.columns[4]    # Coluna E

                df_veiculos = pd.DataFrame()
                df_veiculos["placa"] = df_raw[col_placa].dropna().astype(str).str.strip().str.upper()
                df_veiculos["veiculo"] = df_raw[col_veiculo].fillna("Não informado").astype(str).str.strip()
                
                df_veiculos = df_veiculos[df_veiculos["placa"].str.len() >= 5].drop_duplicates(subset=["placa"])
                return df_veiculos
        except Exception:
            continue

    return pd.DataFrame(columns=["placa", "veiculo"])

def salvar_lancamento_frota(dados):
    """Envia o lançamento para o Google Apps Script contornando redirecionamentos."""
    try:
        corpo = json.dumps(dados, ensure_ascii=False)
        headers = {
            "Content-Type": "text/plain;charset=utf-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        with requests.Session() as session:
            resposta = session.post(
                WEBHOOK_URL,
                data=corpo.encode("utf-8"),
                headers=headers,
                timeout=35,
                allow_redirects=True
            )

        if resposta.status_code == 200:
            try:
                ret = resposta.json()
                if ret.get("status") == "success":
                    return True, "Registro salvo com sucesso na planilha!"
                elif ret.get("status") == "error":
                    return False, f"Aviso do Apps Script: {ret.get('message')}"
            except Exception:
                pass

            if "success" in resposta.text.lower() or "sucesso" in resposta.text.lower():
                return True, "Registro salvo na planilha!"
            return True, "Lançamento registrado com sucesso!"

        elif resposta.status_code == 403:
            return False, "Erro HTTP 403: No Apps Script, configure 'Quem tem acesso' para 'Qualquer pessoa'."
        else:
            return False, f"Erro HTTP {resposta.status_code}: {resposta.text[:180]}"

    except requests.exceptions.Timeout:
        return False, "Tempo limite esgotado ao tentar salvar na planilha (Timeout)."
    except Exception as e:
        return False, f"Falha na comunicação: {str(e)}"

# -------------------------------------------------------------
# 6. TELA DE LOGIN
# -------------------------------------------------------------
def tela_login(df_usuarios):
    renderizar_cabecalho("Acesso de Condutores")
    
    with st.form("form_login"):
        st.subheader("Identificação do Condutor")
        usuario_digitado = st.text_input("Usuário:").strip().lower()
        senha_digitada = st.text_input("Senha:", type="password").strip()
        btn_login = st.form_submit_button("Entrar no Sistema")
        
        if btn_login:
            if df_usuarios.empty:
                st.error("Não foi possível carregar a lista de condutores da planilha.")
                return

            usuario_valido = df_usuarios[
                (df_usuarios["usuario"] == usuario_digitado) & 
                (df_usuarios["senha"] == senha_digitada)
            ]

            if not usuario_valido.empty:
                st.session_state["autenticado"] = True
                st.session_state["usuario_logado"] = usuario_digitado
                st.session_state["nome_condutor"] = usuario_valido.iloc[0]["nome"]
                st.query_params["u"] = usuario_digitado
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

# -------------------------------------------------------------
# 7. APLICATIVO PRINCIPAL
# -------------------------------------------------------------
def main():
    df_usuarios = carregar_usuarios()

    # Recupera sessão por parâmetro da URL se houver refresh
    if not st.session_state.get("autenticado", False):
        usuario_url = st.query_params.get("u", None)
        if usuario_url and not df_usuarios.empty:
            usuario_url = str(usuario_url).strip().lower()
            usuario_valido = df_usuarios[df_usuarios["usuario"] == usuario_url]
            if not usuario_valido.empty:
                st.session_state["autenticado"] = True
                st.session_state["usuario_logado"] = usuario_url
                st.session_state["nome_condutor"] = usuario_valido.iloc[0]["nome"]

    if not st.session_state.get("autenticado", False):
        tela_login(df_usuarios)
        return

    usuario_atual = st.session_state.get("usuario_logado")
    nome_condutor = st.session_state.get("nome_condutor", "Condutor")

    # Verifica se há viagem ativa salva em disco
    if "viagem_ativa" not in st.session_state:
        viagem_recuperada = carregar_viagem_em_andamento(usuario_atual)
        if viagem_recuperada:
            st.session_state["viagem_ativa"] = True
            st.session_state["dados_viagem"] = viagem_recuperada
        else:
            st.session_state["viagem_ativa"] = False
            st.session_state["dados_viagem"] = {}

    # Menu Lateral
    with st.sidebar:
        st.write(f"🚗 **Condutor:**\n### {nome_condutor}")
        if st.session_state.get("viagem_ativa", False):
            st.info("ℹ️ Viagem em andamento para este perfil.")
        if st.button("🚪 Cancelar e Sair"):
            limpar_viagem_em_andamento(usuario_atual)
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

    renderizar_cabecalho("Registro e Controle de Saída de Veículos")

    agora = obter_agora_brasil()

    # =========================================================================
    # ETAPA 1: SELEÇÃO DO VEÍCULO E START INICIAL (SAÍDA)
    # =========================================================================
    if not st.session_state.get("viagem_ativa", False):
        df_veiculos = carregar_veiculos()

        if df_veiculos.empty:
            st.error("Nenhum veículo disponível na base. Verifique a planilha.")
            if st.button("🔄 Recarregar Veículos"):
                st.cache_data.clear()
                st.rerun()
            return

        st.subheader("1. Selecione o Veículo")
        
        opcoes = ["-- Selecione um veículo --"] + (df_veiculos["placa"] + " - " + df_veiculos["veiculo"]).tolist()
        veiculo_escolhido = st.selectbox("Veículo da Frota:", options=opcoes, key="select_veiculo")

        # Só exibe os campos após a escolha do veículo
        if veiculo_escolhido != "-- Selecione um veículo --":
            dados_veiculo = df_veiculos[
                (df_veiculos["placa"] + " - " + df_veiculos["veiculo"]) == veiculo_escolhido
            ].iloc[0]
            placa = dados_veiculo["placa"]
            modelo = dados_veiculo["veiculo"]

            st.markdown(f"""
                <div class="card-info">
                    <b>👤 Condutor:</b> {nome_condutor}<br>
                    <b>🚙 Veículo:</b> {modelo}<br>
                    <b>🔢 Placa:</b> {placa}
                </div>
            """, unsafe_allow_html=True)

            st.subheader("2. Start Inicial (Saída do Veículo)")
            with st.form("form_start_inicial"):
                col_d, col_h = st.columns(2)
                with col_d:
                    data_ini = st.date_input("Data Inicial:", value=agora.date(), format="DD/MM/YYYY")
                with col_h:
                    hora_ini = st.time_input("Horário Inicial:", value=agora.time().replace(microsecond=0))

                # Campo sem valor inicial pré-preenchido
                km_ini = st.number_input(
                    "Km Inicial:", 
                    value=None, 
                    placeholder="Digite o Km Inicial...", 
                    min_value=0.0, 
                    step=1.0, 
                    format="%.0f", 
                    key="km_ini_input"
                )
                destino_ini = st.text_input("Destino / Rota planejada:", placeholder="Ex: Rota Araraquara, São Carlos...")

                btn_start_inicial = st.form_submit_button("🚀 Iniciar Viagem (Start Inicial)")

            if btn_start_inicial:
                if km_ini is None or km_ini <= 0:
                    st.error("⚠️ Por favor, digite o Km Inicial do veículo.")
                    return
                if not destino_ini.strip():
                    st.error("⚠️ Por favor, informe o Destino da viagem.")
                    return

                dados_partida = {
                    "condutor": nome_condutor,
                    "usuario": usuario_atual,
                    "placa": placa,
                    "veiculo": modelo,
                    "data_inicial": data_ini.strftime("%d/%m/%Y"),
                    "horario_inicial": hora_ini.strftime("%H:%M:%S"),
                    "km_inicial": int(km_ini),
                    "destino": destino_ini.strip()
                }

                salvar_viagem_em_andamento(usuario_atual, dados_partida)
                st.session_state["viagem_ativa"] = True
                st.session_state["dados_viagem"] = dados_partida
                st.success("✅ Start Inicial registrado com sucesso! Viagem em andamento.")
                st.rerun()

    # =========================================================================
    # ETAPA 2: START FINAL (RETORNO E FINALIZAÇÃO DO LOGIN)
    # =========================================================================
    else:
        dados_ativos = st.session_state["dados_viagem"]

        st.subheader("Viagem em Andamento")
        st.markdown(f"""
            <div class="card-status-running">
                <b>👤 Condutor:</b> {dados_ativos.get('condutor')}<br>
                <b>🚙 Veículo:</b> {dados_ativos.get('veiculo')} (Placa: {dados_ativos.get('placa')})<br>
                <b>📍 Destino:</b> {dados_ativos.get('destino')}<br>
                <b>⏱️ Saída:</b> {dados_ativos.get('data_inicial')} às {dados_ativos.get('horario_inicial')}<br>
                <b>🔢 Km Inicial:</b> {dados_ativos.get('km_inicial')} km
            </div>
        """, unsafe_allow_html=True)

        st.subheader("Start Final (Retorno do Veículo)")
        with st.form("form_start_final"):
            col_df, col_hf = st.columns(2)
            with col_df:
                data_fim = st.date_input("Data Final:", value=agora.date(), format="DD/MM/YYYY")
            with col_hf:
                hora_fim = st.time_input("Horário Final:", value=agora.time().replace(microsecond=0))

            # Campo sem valor inicial pré-preenchido
            km_fim = st.number_input(
                "Km Final:", 
                value=None, 
                placeholder="Digite o Km Final...", 
                min_value=float(dados_ativos.get("km_inicial", 0)), 
                step=1.0, 
                format="%.0f", 
                key="km_fim_input"
            )

            destino_atualizado = st.text_input(
                "Destino / Rota realizada:", 
                value=dados_ativos.get("destino", "")
            )

            btn_start_final = st.form_submit_button("🏁 Concluir Viagem (Start Final)")

        if btn_start_final:
            if km_fim is None:
                st.error("⚠️ Por favor, digite o Km Final do veículo.")
                return

            if km_fim < dados_ativos.get("km_inicial", 0):
                st.error("⚠️ O Km Final não pode ser menor que o Km Inicial.")
                return

            km_percorrido = int(km_fim - dados_ativos.get("km_inicial", 0))

            payload_completo = {
                "gid_destino": GID_LANCAMENTOS,
                "data_inicial": dados_ativos.get("data_inicial"),
                "horario_inicial": dados_ativos.get("horario_inicial"),
                "km_inicial": dados_ativos.get("km_inicial"),
                "data_final": data_fim.strftime("%d/%m/%Y"),
                "horario_final": hora_fim.strftime("%H:%M:%S"),
                "km_final": int(km_fim),
                "condutor": dados_ativos.get("condutor"),
                "destino": destino_atualizado.strip() if destino_atualizado.strip() else dados_ativos.get("destino"),
                "placa": dados_ativos.get("placa"),
                "veiculo": dados_ativos.get("veiculo"),
                "km_percorrido": km_percorrido,
                "data_registro": agora.strftime("%d/%m/%Y %H:%M:%S")
            }

            with st.spinner("Gravando registro e finalizando..."):
                sucesso, msg = salvar_lancamento_frota(payload_completo)

            # Backup local em CSV
            try:
                arquivo_backup = "historico_frotas.csv"
                df_hist = pd.DataFrame([payload_completo])
                df_hist.to_csv(
                    arquivo_backup,
                    mode="a",
                    header=not os.path.exists(arquivo_backup),
                    index=False
                )
            except Exception:
                pass

            if sucesso:
                limpar_viagem_em_andamento(usuario_atual)
                st.session_state.clear()
                st.query_params.clear()
                st.success("✅ Viagem concluída e registrada com sucesso na planilha!")
                st.balloons()
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"❌ {msg}")
                st.warning("Os dados foram mantidos na tela para você tentar novamente.")

if __name__ == "__main__":
    main()