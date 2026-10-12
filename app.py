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
# 1. CONFIGURAÇÃO DA PÁGINA E DESIGN SYSTEM (LIGHT THEME ULTRA-CLEAN)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Master Café - Gestão de Frota",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* ========================================================
           RESET E VARIÁVEIS DO SISTEMA DE DESIGN (LIGHT SYSTEM)
           ======================================================== */
        :root {
            --bg-canvas: #F8FAFC;
            --bg-card: #FFFFFF;
            --border-light: #E2E8F0;
            --border-input: #CBD5E1;
            --text-title: #0F172A;
            --text-body: #334155;
            --text-muted: #64748B;
            --primary: #2563EB;
            --primary-hover: #1D4ED8;
            --primary-light: #EFF6FF;
            --primary-border: #BFDBFE;
            --shadow-subtle: 0 1px 3px rgba(15, 23, 42, 0.05), 0 1px 2px rgba(15, 23, 42, 0.03);
            --shadow-card: 0 4px 12px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.02);
            --radius-md: 10px;
            --radius-lg: 14px;
        }

        /* Oculta marca d'água e menus do Streamlit Cloud */
        #MainMenu, footer, .stDeployButton, [data-testid="stToolbarActions"],
        [data-testid="stDecoration"], [data-testid="manage-app-button"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Fundo global da aplicação */
        .stApp {
            background-color: var(--bg-canvas) !important;
            color: var(--text-body) !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif !important;
        }

        /* Sidebar Limpa */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid var(--border-light) !important;
        }
        section[data-testid="stSidebar"] * {
            color: var(--text-body) !important;
        }

        /* ========================================================
           CONTAINERS, CABEÇALHOS E CARTÕES
           ======================================================== */
        .header-card {
            background: var(--bg-card);
            padding: 24px;
            border-radius: var(--radius-lg);
            text-align: center;
            border: 1px solid var(--border-light);
            box-shadow: var(--shadow-card);
            margin-bottom: 1.5rem;
        }
        .header-title {
            font-size: 1.45rem;
            font-weight: 700;
            color: var(--text-title);
            margin-top: 8px;
            margin-bottom: 2px;
            letter-spacing: -0.02em;
        }
        .header-subtitle {
            font-size: 0.90rem;
            color: var(--text-muted);
            margin: 0;
            font-weight: 500;
        }

        /* Informações e Status */
        .card-info {
            background-color: #FFFFFF;
            border: 1px solid var(--border-light);
            border-left: 4px solid var(--primary);
            padding: 16px 18px;
            border-radius: var(--radius-md);
            margin: 14px 0;
            box-shadow: var(--shadow-subtle);
            color: var(--text-body);
            line-height: 1.6;
            font-size: 0.93rem;
        }
        .card-status-running {
            background-color: var(--primary-light);
            border: 1px solid var(--primary-border);
            padding: 16px 18px;
            border-radius: var(--radius-md);
            margin-bottom: 1.2rem;
            color: #1E3A8A;
            line-height: 1.65;
            font-size: 0.93rem;
        }

        /* Container de Formulário */
        [data-testid="stForm"] {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-light) !important;
            border-radius: var(--radius-lg) !important;
            box-shadow: var(--shadow-card) !important;
            padding: 26px !important;
        }

        /* Títulos e Subtítulos */
        h1, h2, h3, h4 {
            color: var(--text-title) !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }

        /* Labels dos campos */
        label, .stWidgetLabel p {
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            margin-bottom: 4px !important;
        }

        /* ========================================================
           INPUTS: TEXTO, NÚMERO, DATA, HORA E CALENDÁRIO
           ======================================================== */
        /* Estilização universal de caixas de entrada */
        .stTextInput input, 
        .stNumberInput input, 
        .stDateInput input, 
        .stTimeInput input {
            background-color: #FFFFFF !important;
            border: 1px solid var(--border-input) !important;
            color: var(--text-title) !important;
            border-radius: var(--radius-md) !important;
            font-size: 0.94rem !important;
            box-shadow: var(--shadow-subtle) !important;
            transition: all 0.2s ease !important;
            padding: 8px 12px !important;
        }

        /* Efeito de foco */
        .stTextInput input:focus, 
        .stNumberInput input:focus, 
        .stDateInput input:focus, 
        .stTimeInput input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
            outline: none !important;
        }

        /* Selectbox e Dropdown (Listas) */
        div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            border: 1px solid var(--border-input) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-title) !important;
            box-shadow: var(--shadow-subtle) !important;
        }
        div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
            background-color: #FFFFFF !important;
            border: 1px solid var(--border-light) !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08) !important;
            border-radius: var(--radius-md) !important;
        }
        li[role="option"] {
            color: var(--text-title) !important;
            background-color: #FFFFFF !important;
        }
        li[role="option"]:hover, li[aria-selected="true"] {
            background-color: var(--primary-light) !important;
            color: var(--primary) !important;
        }

        /* Popover do Calendário (Datepicker) */
        div[data-baseweb="calendar"] {
            background-color: #FFFFFF !important;
            color: var(--text-title) !important;
        }
        div[data-baseweb="calendar"] * {
            color: var(--text-title) !important;
        }
        div[data-baseweb="calendar"] button:hover {
            background-color: var(--primary-light) !important;
        }

        /* ========================================================
           BOTÕES MODERNOS
           ======================================================== */
        div.stButton > button {
            width: 100% !important;
            border-radius: var(--radius-md) !important;
            height: 48px !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 3px 10px rgba(37, 99, 235, 0.22) !important;
            transition: all 0.2s ease-in-out !important;
            cursor: pointer !important;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #1D4ED8, #1E40AF) !important;
            box-shadow: 0 5px 14px rgba(37, 99, 235, 0.32) !important;
            transform: translateY(-1px) !important;
        }
        div.stButton > button:active {
            transform: translateY(0px) !important;
        }

        /* Botão secundário na barra lateral */
        section[data-testid="stSidebar"] div.stButton > button {
            background: #F1F5F9 !important;
            color: #475569 !important;
            box-shadow: none !important;
            border: 1px solid var(--border-light) !important;
        }
        section[data-testid="stSidebar"] div.stButton > button:hover {
            background: #E2E8F0 !important;
            color: #1E293B !important;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. DEFINIÇÃO DAS VARIÁVEIS GLOBAIS E LINKS
# -------------------------------------------------------------
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxXSQRM3lPFIQ6VkDs4OK7HrjnfIDrPEPOTM2sAHhogHNhb2PhSoUSw06fYT-rGeiS2uw/exec"
SPREADSHEET_ID = "1-Bn0VBnRV1zp_f7QrKTldKB03L9_k7DyRO3YslGMnnU"

GID_USUARIOS = "426012097"       # Aba com Login / Condutores
GID_VEICULOS = "0"               # Aba com a lista de veículos da frota
GID_LANCAMENTOS = "379222602"    # Aba onde serão gravados os lançamentos de frota

# -------------------------------------------------------------
# 3. SUPORTE A LOGOTIPO E CABEÇALHO MODERNO
# -------------------------------------------------------------
def obter_caminho_logotipo():
    """Localiza o arquivo do logotipo com qualquer extensão compatível na mesma pasta."""
    extensoes = [".png", ".jpg", ".jpeg", ".svg", ".webp", ""]
    nomes = ["Logotipo", "logotipo", "Logo", "logo"]
    for nome in nomes:
        for ext in extensoes:
            caminho = f"{nome}{ext}"
            if os.path.exists(caminho) and not os.path.isdir(caminho):
                return caminho
    return None

def renderizar_cabecalho(subtitulo="Gestão e Controle de Frota"):
    """Exibe o cabeçalho estilizado em tema claro com o Logotipo se existente."""
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
# 4. GESTÃO DE PERSISTÊNCIA DA VIAGEM (CONTRA REFRESH / F5)
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
# 5. FUNÇÕES DE SUPORTE E LEITURA DA PLANILHA
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

                km_ini = st.number_input("Km Inicial:", min_value=0.0, step=1.0, format="%.0f", key="km_ini_input")
                destino_ini = st.text_input("Destino / Rota planejada:", placeholder="Ex: Rota Araraquara, São Carlos...")

                btn_start_inicial = st.form_submit_button("🚀 Iniciar Viagem (Start Inicial)")

            if btn_start_inicial:
                if km_ini <= 0:
                    st.error("⚠️ Informe o Km Inicial do veículo.")
                    return
                if not destino_ini.strip():
                    st.error("⚠️ Informe o Destino da viagem.")
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

            km_fim = st.number_input(
                "Km Final:", 
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
            if km_fim < dados_ativos.get("km_inicial", 0):
                st.error("⚠️ O Km Final não pode ser menor que o Km Inicial.")
                st.stop()

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

            # Backup local em CSV para garantia
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