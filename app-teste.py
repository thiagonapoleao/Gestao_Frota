import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
try:
    from zoneinfo import ZoneInfo
    FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")
except Exception:
    FUSO_BRASIL = timezone(timedelta(hours=-3))

import os
import re
import unicodedata
import requests
import json
import time
from PIL import Image

def obter_agora_brasil():
    """Retorna datetime atual oficial de Brasília."""
    return datetime.now(FUSO_BRASIL)

# -------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS
# -------------------------------------------------------------
st.set_page_config(
    page_title="Gestão de Frota",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* 1. ELIMINA DIVS VAZIAS E ELEMENTOS FANTASMAS */
        div[data-testid="stMarkdownContainer"]:empty,
        div[data-testid="stMarkdownContainer"]:has(> style:only-child) {
            display: none !important;
            height: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
        }

        div[data-testid="element-container"]:has(> div[data-testid="stMarkdownContainer"]:empty),
        div[data-testid="element-container"]:has(> div[data-testid="stMarkdownContainer"] > style:only-child) {
            display: none !important;
            height: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
        }

        /* 2. OCULTA A SIDEBAR NATIVA E O HEADER EXTERNO */
        section[data-testid="stSidebar"],
        [data-testid="stSidebar"],
        header[data-testid="stHeader"],
        [data-testid="stHeader"],
        div[data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        button[data-testid="baseButton-headerNoPadding"] {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            width: 0px !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        #MainMenu, footer, .stDeployButton, [data-testid="stToolbarActions"],
        [data-testid="manage-app-button"], div[data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* 3. DEGRADÊ RADIAL NO BACKGROUND GERAL */
        :root, html, body, .stApp, [data-testid="stAppViewContainer"] {
            background-color: #110426 !important;
            background-image: 
                radial-gradient(at 93.69543598317607% 5.616169708078966%, hsla(267.88732394366195, 100%, 13.92156862745098%, 1) 0%, hsla(267.88732394366195, 100%, 13.92156862745098%, 0) 100%), 
                radial-gradient(at 49.6250738166925% 50.14065564263524%, hsla(264.11764705882354, 100%, 20%, 1) 0%, hsla(264.11764705882354, 100%, 20%, 0) 100%), 
                radial-gradient(at 37.00403509139429% 89.3640844672993%, hsla(240.81081081081078, 100%, 29.01960784313726%, 1) 0%, hsla(240.81081081081078, 100%, 29.01960784313726%, 0) 100%), 
                radial-gradient(at 76.13084977631372% 73.97772700476057%, hsla(267.88732394366195, 100%, 13.92156862745098%, 1) 0%, hsla(267.88732394366195, 100%, 13.92156862745098%, 0) 100%), 
                radial-gradient(at 20.535772964012743% 97.27562379868434%, hsla(264.11764705882354, 100%, 20%, 1) 0%, hsla(264.11764705882354, 100%, 20%, 0) 100%), 
                radial-gradient(at 45.86269066661277% 99.26966956219938%, hsla(240.81081081081078, 100%, 29.01960784313726%, 1) 0%, hsla(240.81081081081078, 100%, 29.01960784313726%, 0) 100%), 
                radial-gradient(at 33.24174772772377% 84.28822907756046%, hsla(267.88732394366195, 100%, 13.92156862745098%, 1) 0%, hsla(267.88732394366195, 100%, 13.92156862745098%, 0) 100%), 
                radial-gradient(at 30.932790321943536% 31.05233181318352%, hsla(264.11764705882354, 100%, 20%, 1) 0%, hsla(264.11764705882354, 100%, 20%, 0) 100%), 
                radial-gradient(at 87.19757331823584% 4.189116488339084%, hsla(240.81081081081078, 100%, 29.01960784313726%, 1) 0%, hsla(240.81081081081078, 100%, 29.01960784313726%, 0) 100%) !important;
            background-attachment: fixed !important;
            background-size: cover !important;
        }

        /* 4. CONTAINER BRANCO UNIFICADO ELEVADO */
        .block-container,
        div[data-testid="stAppViewContainer"] > .main > .block-container,
        div[data-testid="stAppViewBlockContainer"] {
            background-color: #FFFFFF !important;
            border-radius: 20px !important;
            padding-top: 14px !important;
            padding-left: 28px !important;
            padding-right: 28px !important;
            padding-bottom: 34px !important;
            margin-top: 1.2rem !important;
            margin-bottom: 2.5rem !important;
            max-width: 680px !important;
            box-shadow: 0 20px 45px rgba(0, 0, 0, 0.32) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }

        /* 5. MENU EXPANSÍVEL */
        div[data-testid="stExpander"] {
            border: 1px solid rgba(147, 51, 234, 0.4) !important;
            border-radius: 12px !important;
            background-color: #110426 !important;
            background-image: 
                radial-gradient(at 93% 5%, hsla(267.8, 100%, 18%, 1) 0%, transparent 100%),
                radial-gradient(at 49% 50%, hsla(264.1, 100%, 25%, 1) 0%, transparent 100%),
                radial-gradient(at 37% 89%, hsla(240.8, 100%, 32%, 1) 0%, transparent 100%) !important;
            margin-top: 0px !important;
            margin-bottom: 12px !important;
            box-shadow: 0 4px 14px rgba(17, 4, 38, 0.25) !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }

        div[data-testid="stExpander"] summary::-webkit-details-marker,
        div[data-testid="stExpander"] summary::marker {
            display: none !important;
        }

        div[data-testid="stExpander"] summary svg,
        div[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"],
        div[data-testid="stExpander"] summary > span:first-child:has(svg),
        div[data-testid="stExpander"] summary > div:first-child:has(svg) {
            display: none !important;
            visibility: hidden !important;
            width: 0px !important;
            height: 0px !important;
        }

        div[data-testid="stExpander"] summary {
            padding: 10px 18px !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            letter-spacing: 0.02em !important;
            list-style: none !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            width: 100% !important;
            box-sizing: border-box !important;
            user-select: none !important;
            cursor: pointer !important;
            border-radius: 11px !important;
            transition: all 0.2s ease-in-out !important;
        }

        div[data-testid="stExpander"] summary:hover {
            filter: brightness(1.15) !important;
            box-shadow: 0 0 16px rgba(168, 85, 247, 0.45) !important;
        }

        div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
            width: 100% !important;
            box-sizing: border-box !important;
            padding: 16px 18px !important;
            background-color: #FFFFFF !important;
            border-radius: 0 0 12px 12px !important;
            border-top: 1px solid #E2E8F0 !important;
        }

        /* 6. LOGOTIPO */
        .logo-wrapper {
            margin-top: 0px !important;
            padding-top: 0px !important;
            margin-bottom: 4px !important;
        }

        /* Tipografia Base */
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #0F172A !important;
        }

        .stWidgetLabel p, label p {
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 0.90rem !important;
            margin-bottom: 4px !important;
        }

        /* Cabeçalho Corporativo */
        .corporate-header {
            background: transparent !important;
            padding: 0 0 12px 0 !important;
            text-align: center !important;
            border-bottom: 1px solid #E2E8F0 !important;
            margin-bottom: 1.3rem !important;
        }
        .corporate-title {
            font-size: 1.45rem !important;
            font-weight: 700 !important;
            color: #0F172A !important;
            margin: 4px 0 2px 0 !important;
            letter-spacing: -0.025em !important;
        }
        .corporate-subtitle {
            font-size: 1.15rem !important;
            color: #475569 !important;
            margin: 0 !important;
            font-weight: 600 !important;
            letter-spacing: -0.015em !important;
        }

        .section-subheading {
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            color: #1E293B !important;
            margin-bottom: 1rem !important;
            margin-top: 0.4rem !important;
            letter-spacing: -0.01em !important;
        }

        [data-testid="stForm"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0px !important;
        }

        .card-vehicle-info {
            background-color: #F8FAFC !important;
            border: 1px solid #E2E8F0 !important;
            border-left: 4px solid #2563EB !important;
            padding: 14px 16px !important;
            border-radius: 10px !important;
            margin: 14px 0 !important;
            color: #334155 !important;
            line-height: 1.6 !important;
            font-size: 0.92rem !important;
        }

        .card-active-trip {
            background-color: #EFF6FF !important;
            border: 1px solid #BFDBFE !important;
            padding: 16px !important;
            border-radius: 12px !important;
            margin-bottom: 1.3rem !important;
            color: #1E3A8A !important;
            line-height: 1.65 !important;
            font-size: 0.93rem !important;
        }
        .card-active-trip b {
            color: #1E3A8A !important;
        }

        /* Inputs */
        div[data-baseweb="input"],
        div[data-baseweb="base-input"],
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] > div,
        div[data-testid="stDateInput"] > div,
        div[data-testid="stTimeInput"] > div,
        div[data-testid="stNumberInput"] > div,
        div[data-testid="stNumberInputContainer"] {
            background-color: #F8FAFC !important;
            border: 1px solid #CBD5E1 !important;
            color: #0F172A !important;
            border-radius: 8px !important;
        }

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"]:focus-within,
        div[data-testid="stNumberInputContainer"]:focus-within {
            border-color: #2563EB !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
        }

        input[type="text"], 
        input[type="number"], 
        input[type="password"],
        input {
            background-color: transparent !important;
            color: #0F172A !important;
            -webkit-text-fill-color: #0F172A !important;
            border: none !important;
            font-size: 0.94rem !important;
            font-weight: 500 !important;
        }

        /* 7. BOTÕES COM DEGRADÊ */
        div[data-testid="stFormSubmitButton"] > button,
        div.stButton > button[kind="primary"] {
            background-color: #110426 !important;
            background-image: 
                radial-gradient(at 93% 5%, hsla(267.8, 100%, 18%, 1) 0%, transparent 100%),
                radial-gradient(at 49% 50%, hsla(264.1, 100%, 25%, 1) 0%, transparent 100%),
                radial-gradient(at 37% 89%, hsla(240.8, 100%, 32%, 1) 0%, transparent 100%) !important;
            background-size: cover !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border: 1px solid rgba(147, 51, 234, 0.45) !important;
            border-radius: 12px !important;
            height: 50px !important;
            min-height: 50px !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.02em !important;
            box-shadow: 0 4px 16px rgba(17, 4, 38, 0.35) !important;
            cursor: pointer !important;
            transition: all 0.2s ease-in-out !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            box-sizing: border-box !important;
            margin-top: 14px !important;
        }

        div[data-testid="stFormSubmitButton"] > button:hover,
        div.stButton > button[kind="primary"]:hover {
            filter: brightness(1.18) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(168, 85, 247, 0.5) !important;
            border-color: rgba(168, 85, 247, 0.75) !important;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. VARIÁVEIS GLOBAIS E ENDPOINTS
# -------------------------------------------------------------
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxXSQRM3lPFIQ6VkDs4OK7HrjnfIDrPEPOTM2sAHhogHNhb2PhSoUSw06fYT-rGeiS2uw/exec"
SPREADSHEET_ID = "1-Bn0VBnRV1zp_f7QrKTldKB03L9_k7DyRO3YslGMnnU"

GID_USUARIOS = "426012097"       # Aba Usuario
GID_VEICULOS = "0"               # Aba Frota
GID_LANCAMENTOS = "379222602"    # Aba Controle de Uso

# -------------------------------------------------------------
# 3. SUPORTE A LOGOTIPO CORPORATIVO E IMAGEM DA FROTA
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

def obter_caminho_imagem_frota():
    extensoes = [".png", ".jpg", ".jpeg", ".webp", ".svg", ""]
    nomes = ["Frota", "frota", "FROTA"]
    for nome in nomes:
        for ext in extensoes:
            caminho = f"{nome}{ext}"
            if os.path.exists(caminho) and not os.path.isdir(caminho):
                return caminho
    return None

def renderizar_cabecalho(subtitulo="Portal de Acesso do Condutor"):
    caminho_logo = obter_caminho_logotipo()
    st.markdown('<div class="logo-wrapper">', unsafe_allow_html=True)
    if caminho_logo:
        try:
            logo_img = Image.open(caminho_logo)
            col_l1, col_logo, col_l2 = st.columns([1, 1.4, 1])
            with col_logo:
                st.image(logo_img, use_container_width=True)
        except Exception:
            st.markdown('<div class="corporate-title" style="text-align: center;">🚗 Controle de Frotas</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="corporate-title" style="text-align: center;">🚗 Controle de Frotas</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="corporate-header"><p class="corporate-subtitle">{subtitulo}</p></div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. FUNÇÕES DE SUPORTE E LEITURA DA PLANILHA
# -------------------------------------------------------------
def normalizar_texto(texto):
    if texto is None:
        return ""
    if not isinstance(texto, str):
        texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.strip().lower()

def limpar_placa(placa_str):
    return re.sub(r'[^A-Za-z0-9]', '', str(placa_str or '')).upper()

def eh_vazio_ou_nan(val):
    if val is None:
        return True
    s = str(val).strip().lower()
    return s in ["", "nan", "none", "null", "-", "--"]

def extrair_inteiro_km(valor):
    """Higieniza qualquer formato (ex: '1.250', '1250,0', 1250) para int puro."""
    if valor is None:
        return 0
    s = str(valor).split(",")[0].split(".")[0].strip()
    s = re.sub(r'[^0-9]', '', s)
    return int(s) if s else 0

@st.cache_data(ttl=30)
def carregar_usuarios():
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_USUARIOS}&t={int(time.time())}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_USUARIOS}&t={int(time.time())}"
    ]
    for url in urls:
        try:
            df = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df.empty:
                cols_norm = {normalizar_texto(c): c for c in df.columns}
                c_user = cols_norm.get("usuario", cols_norm.get("login", df.columns[0]))
                c_pass = cols_norm.get("senha", df.columns[1] if len(df.columns) > 1 else df.columns[0])
                c_nome = cols_norm.get("nome", cols_norm.get("condutor", c_user))
                
                c_acesso = None
                for col_k in ["acesso", "local", "cidade", "unidade", "pernoite", "base"]:
                    if col_k in cols_norm:
                        c_acesso = cols_norm[col_k]
                        break

                df_res = pd.DataFrame()
                df_res["usuario"] = df[c_user].fillna("").astype(str).str.strip().str.lower()
                df_res["senha"] = df[c_pass].fillna("").astype(str).str.strip()
                df_res["nome"] = df[c_nome].fillna(df[c_user]).astype(str).str.strip()
                
                if c_acesso:
                    df_res["acesso_local"] = df[c_acesso].fillna("Geral").astype(str).str.strip()
                else:
                    df_res["acesso_local"] = "Geral"
                
                return df_res
        except Exception:
            continue
    return pd.DataFrame([{"usuario": "admin", "senha": "123", "nome": "Condutor", "acesso_local": "Geral"}])

@st.cache_data(ttl=20)
def carregar_veiculos():
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_VEICULOS}&t={int(time.time())}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_VEICULOS}&t={int(time.time())}"
    ]
    for url in urls:
        try:
            df_raw = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df_raw.empty and len(df_raw.columns) >= 2:
                cols_norm = {normalizar_texto(c): c for c in df_raw.columns}
                
                c_placa = None
                for k in ["placa", "placas"]:
                    if k in cols_norm:
                        c_placa = cols_norm[k]
                        break
                if not c_placa:
                    c_placa = df_raw.columns[4] if len(df_raw.columns) >= 5 else df_raw.columns[0]

                c_veiculo = None
                for k in ["descricao", "veiculo", "modelo", "carro"]:
                    if k in cols_norm:
                        c_veiculo = cols_norm[k]
                        break
                if not c_veiculo:
                    c_veiculo = df_raw.columns[1] if len(df_raw.columns) >= 2 else df_raw.columns[0]

                c_pernoite = None
                for k in ["local de pernoite", "pernoite", "local", "cidade", "base", "unidade"]:
                    if k in cols_norm:
                        c_pernoite = cols_norm[k]
                        break

                df_veiculos = pd.DataFrame()
                df_veiculos["placa"] = df_raw[c_placa].dropna().astype(str).str.strip().str.upper()
                df_veiculos["veiculo"] = df_raw[c_veiculo].fillna("Não informado").astype(str).str.strip()
                
                if c_pernoite:
                    df_veiculos["local_pernoite"] = df_raw[c_pernoite].fillna("Não informado").astype(str).str.strip()
                else:
                    df_veiculos["local_pernoite"] = "Geral"

                df_veiculos = df_veiculos[df_veiculos["placa"].str.len() >= 5].drop_duplicates(subset=["placa"])
                return df_veiculos
        except Exception:
            continue
    return pd.DataFrame(columns=["placa", "veiculo", "local_pernoite"])

def carregar_lancamentos_existentes():
    timestamp_atual = int(time.time())
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_LANCAMENTOS}&cb={timestamp_atual}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_LANCAMENTOS}&cb={timestamp_atual}"
    ]
    for url in urls:
        try:
            df = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df.empty:
                return df
        except Exception:
            continue
    return pd.DataFrame()

def verificar_lancamento_duplicado(df_lancamentos, rv_codigo, placa, condutor, data_ini, km_ini):
    if df_lancamentos.empty or len(df_lancamentos.columns) < 13:
        return False, ""

    placa_limpa_alvo = limpar_placa(placa)
    condutor_norm_alvo = normalizar_texto(condutor)
    data_ini_alvo = str(data_ini).strip()
    km_ini_alvo = str(extrair_inteiro_km(km_ini))
    rv_alvo = str(rv_codigo).replace("-", "").strip().upper()

    for _, row in df_lancamentos.iterrows():
        rv_row = str(row.iloc[12]).replace("-", "").strip().upper() if pd.notna(row.iloc[12]) else ""
        placa_row = limpar_placa(row.iloc[8]) if pd.notna(row.iloc[8]) else ""
        cond_row = normalizar_texto(row.iloc[6]) if pd.notna(row.iloc[6]) else ""
        data_row = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        km_row = str(extrair_inteiro_km(row.iloc[2])) if pd.notna(row.iloc[2]) else ""

        if rv_row and rv_row == rv_alvo:
            return True, f"O Registro de Viagem {rv_codigo} já existe na planilha."

        if (placa_row == placa_limpa_alvo and 
            cond_row == condutor_norm_alvo and 
            data_row == data_ini_alvo and 
            km_row == km_ini_alvo):
            return True, f"Já existe uma viagem registrada para este veículo com Data {data_ini_alvo} e Km {km_ini_alvo}."

    return False, ""

def gerar_proximo_rv(df_lancamentos, placa, ano_atual):
    placa_limpa = limpar_placa(placa)
    prefixo = f"RV-{placa_limpa}-{ano_atual}-"
    maior_seq = 0

    if not df_lancamentos.empty and len(df_lancamentos.columns) >= 13:
        coluna_rv = df_lancamentos.iloc[:, 12].dropna().astype(str)
        for val in coluna_rv:
            val = val.strip().upper()
            if val.startswith(prefixo) or val.startswith(f"RV-{placa_limpa}_{ano_atual}-"):
                partes = val.split("-")
                if len(partes) == 4 and partes[3].isdigit():
                    num = int(partes[3])
                    if num > maior_seq:
                        maior_seq = num
                elif len(partes) == 3 and partes[2].isdigit():
                    num = int(partes[2])
                    if num > maior_seq:
                        maior_seq = num

    proximo_seq = maior_seq + 1
    return f"{prefixo}{proximo_seq:04d}"

def enviar_requisicao_apps_script(payload):
    try:
        corpo = json.dumps(payload, ensure_ascii=False)
        headers = {"Content-Type": "text/plain;charset=utf-8"}
        with requests.Session() as session:
            resposta = session.post(
                WEBHOOK_URL,
                data=corpo.encode("utf-8"),
                headers=headers,
                timeout=40,
                allow_redirects=True
            )

        if resposta.status_code == 200:
            try:
                ret = resposta.json()
                status_resp = str(ret.get("status", "")).lower().strip()
                if status_resp in ["sucesso", "success", "ok"]:
                    msg = ret.get("mensagem") or ret.get("message") or "Operação realizada com sucesso!"
                    return True, msg
                else:
                    msg_erro = ret.get("mensagem") or ret.get("message") or ret.get("error") or str(ret)
                    return False, f"Planilha recusou: {msg_erro}"
            except Exception:
                texto = resposta.text.strip()
                if "<html" in texto.lower() or "google" in texto.lower():
                    return False, "O Apps Script retornou página HTML. Certifique-se de implantar como 'Qualquer pessoa'."
                return False, f"Resposta não-JSON da planilha: {texto[:200]}"
        elif resposta.status_code == 403:
            return False, "Erro 403: No Apps Script, mude 'Quem tem acesso' para 'Qualquer pessoa'."
        else:
            return False, f"Erro HTTP {resposta.status_code}: {resposta.text[:180]}"
    except requests.exceptions.Timeout:
        return False, "Tempo limite excedido ao contatar o Google Apps Script (40s)."
    except Exception as e:
        return False, f"Falha de conexão: {str(e)}"

# -------------------------------------------------------------
# 5. TELA DE LOGIN
# -------------------------------------------------------------
def tela_login(df_usuarios):
    renderizar_cabecalho("Portal de Acesso do Condutor")
    
    caminho_frota = obter_caminho_imagem_frota()
    if caminho_frota:
        try:
            img_frota = Image.open(caminho_frota)
            col_esq, col_centro, col_dir = st.columns([1, 2.8, 1])
            with col_centro:
                st.image(img_frota, use_container_width=True)
        except Exception:
            pass

    with st.form("form_login"):
        st.markdown('<div class="section-subheading">Identificação do Condutor</div>', unsafe_allow_html=True)
        usuario_digitado = st.text_input("Usuário:", placeholder="Digite seu usuário").strip().lower()
        senha_digitada = st.text_input("Senha:", type="password", placeholder="Digite sua senha").strip()
        btn_login = st.form_submit_button("Entrar no Sistema", use_container_width=True)
        
        if btn_login:
            if df_usuarios.empty:
                st.error("Não foi possível carregar os condutores da planilha.")
                return

            usuario_valido = df_usuarios[
                (df_usuarios["usuario"] == usuario_digitado) & 
                (df_usuarios["senha"] == senha_digitada)
            ]

            if not usuario_valido.empty:
                row_user = usuario_valido.iloc[0]
                st.session_state["autenticado"] = True
                st.session_state["usuario_logado"] = usuario_digitado
                st.session_state["nome_condutor"] = row_user["nome"]
                st.session_state["acesso_local"] = row_user.get("acesso_local", "Geral")
                st.query_params["u"] = usuario_digitado
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

# -------------------------------------------------------------
# 6. APLICATIVO PRINCIPAL
# -------------------------------------------------------------
def main():
    df_usuarios = carregar_usuarios()

    if not st.session_state.get("autenticado", False):
        usuario_url = st.query_params.get("u", None)
        if usuario_url and not df_usuarios.empty:
            usuario_url = str(usuario_url).strip().lower()
            usuario_valido = df_usuarios[df_usuarios["usuario"] == usuario_url]
            if not usuario_valido.empty:
                row_user = usuario_valido.iloc[0]
                st.session_state["autenticado"] = True
                st.session_state["usuario_logado"] = usuario_url
                st.session_state["nome_condutor"] = row_user["nome"]
                st.session_state["acesso_local"] = row_user.get("acesso_local", "Geral")

    if not st.session_state.get("autenticado", False):
        tela_login(df_usuarios)
        return

    usuario_atual = st.session_state.get("usuario_logado")
    nome_condutor = st.session_state.get("nome_condutor", "Condutor")
    acesso_local = st.session_state.get("acesso_local", "Geral")

    df_lanc = carregar_lancamentos_existentes()

    viagens_abertas_por_condutor = {}
    veiculos_em_uso = {}

    if not df_lanc.empty and len(df_lanc.columns) >= 13:
        for _, row in df_lanc.iterrows():
            data_fim = row.iloc[3]
            km_fim = row.iloc[5]
            cond_row = str(row.iloc[6]).strip() if pd.notna(row.iloc[6]) else ""
            placa_row = str(row.iloc[8]).strip() if pd.notna(row.iloc[8]) else ""
            rv_row = str(row.iloc[12]).strip() if pd.notna(row.iloc[12]) else ""

            # Aberta = Sem Data Final ou Sem Km Final
            viagem_aberta = eh_vazio_ou_nan(data_fim) or eh_vazio_ou_nan(km_fim)

            if viagem_aberta and rv_row:
                info_aberta = {
                    "rv": rv_row,
                    "condutor": cond_row,
                    "placa": placa_row,
                    "veiculo": str(row.iloc[9]).strip() if pd.notna(row.iloc[9]) else "",
                    "data_inicial": str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else "",
                    "horario_inicial": str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else "",
                    "km_inicial": str(extrair_inteiro_km(row.iloc[2])),
                    "destino": str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else ""
                }
                
                placa_k = limpar_placa(placa_row)
                if placa_k:
                    veiculos_em_uso[placa_k] = info_aberta

                if cond_row:
                    viagens_abertas_por_condutor[normalizar_texto(cond_row)] = info_aberta

    condutor_chave = normalizar_texto(nome_condutor)
    viagem_pendente_condutor = viagens_abertas_por_condutor.get(condutor_chave, None)

    # ---------------------------------------------------------------------------------
    # MENU DO CONDUTOR
    # ---------------------------------------------------------------------------------
    with st.expander("Menu do Condutor", expanded=False):
        col_m1, col_m2 = st.columns([1.5, 1])
        with col_m1:
            st.write(f"👤 **Condutor:** {nome_condutor}")
            st.caption(f"📍 **Base:** {acesso_local}")
            if viagem_pendente_condutor:
                st.warning(f"⚠️ Viagem em aberto no veículo: **{viagem_pendente_condutor['placa']}**")
        with col_m2:
            if st.button("🔄 Atualizar Dados", use_container_width=True, key="btn_menu_refresh"):
                st.cache_data.clear()
                st.session_state["ultima_transacao"] = None
                st.rerun()
            if st.button("🚪 Sair do Sistema", use_container_width=True, key="btn_menu_logout"):
                st.session_state.clear()
                st.query_params.clear()
                st.rerun()

        st.markdown("---")
        with st.expander("➕ Cadastrar Novo Condutor", expanded=False):
            with st.form("form_novo_usuario"):
                novo_login = st.text_input("Usuário (Login):", placeholder="ex: joao.silva").strip().lower()
                nova_senha = st.text_input("Senha:", type="password", placeholder="Digite uma senha").strip()
                novo_nome = st.text_input("Nome Completo:", placeholder="ex: João da Silva").strip()
                novo_acesso = st.text_input("Base / Local de Acesso:", value=acesso_local if acesso_local != "Geral" else "Geral").strip()
                btn_cadastrar_user = st.form_submit_button("Salvar Novo Condutor", use_container_width=True)

            if btn_cadastrar_user:
                if not novo_login or not nova_senha or not novo_nome:
                    st.error("Preencha usuário, senha e nome completo.")
                else:
                    payload_user = {
                        "acao": "cadastrar_usuario",
                        "usuario": novo_login,
                        "senha": nova_senha,
                        "nome": novo_nome,
                        "acesso": novo_acesso
                    }
                    with st.spinner("Salvando condutor na planilha..."):
                        ok_user, msg_user = enviar_requisicao_apps_script(payload_user)
                    if ok_user:
                        st.success(f"✅ Usuário {novo_nome} cadastrado!")
                        st.cache_data.clear()
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_user}")

    renderizar_cabecalho("Registro e Controle de Saída de Veículos")
    agora = obter_agora_brasil()
    ano_atual = agora.strftime("%Y")

    # =========================================================================
    # CENÁRIO 1: VIAGEM ABERTA (FINALIZAR)
    # =========================================================================
    if viagem_pendente_condutor is not None:
        dados_ativos = viagem_pendente_condutor
        km_inicial_val = extrair_inteiro_km(dados_ativos.get("km_inicial"))

        st.warning("⚠️ **Você possui uma viagem em andamento!** Finalize o retorno para liberar novos lançamentos.")
        st.markdown(f"""
            <div class="card-active-trip">
                <b>🎫 Registro de Viagem:</b> {dados_ativos.get('rv')}<br>
                <b>👤 Condutor:</b> {dados_ativos.get('condutor')}<br>
                <b>🚙 Veículo:</b> {dados_ativos.get('veiculo')} (Placa: {dados_ativos.get('placa')})<br>
                <b>📍 Destino:</b> {dados_ativos.get('destino')}<br>
                <b>⏱️ Saída:</b> {dados_ativos.get('data_inicial')} às {dados_ativos.get('horario_inicial')}<br>
                <b>🔢 Km Inicial:</b> {km_inicial_val} km
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-subheading">Start Final (Retorno do Veículo)</div>', unsafe_allow_html=True)
        with st.form("form_start_final"):
            col_df, col_hf = st.columns(2)
            with col_df:
                data_fim = st.date_input("Data Final:", value=agora.date(), format="DD/MM/YYYY")
            with col_hf:
                hora_fim = st.time_input("Horário Final:", value=agora.time().replace(microsecond=0))

            # Campo inicializado SEM pré-preenchimento (value=None) para exibir o placeholder em branco
            km_fim = st.number_input(
                "Km Final:", 
                value=None, 
                placeholder=f"Digite o Km Final (mínimo: {km_inicial_val})...", 
                min_value=0.0, 
                step=1.0, 
                format="%.0f", 
                key="km_fim_input"
            )

            destino_atualizado = st.text_input(
                "Destino / Rota realizada:", 
                value=dados_ativos.get("destino", "")
            )

            btn_start_final = st.form_submit_button("🏁 Concluir Viagem (Start Final)", use_container_width=True)

        if btn_start_final:
            if km_fim is None:
                st.error("⚠️ Por favor, digite o Km Final.")
                return
            
            km_final_int = extrair_inteiro_km(km_fim)
            if km_final_int < km_inicial_val:
                st.error(f"⚠️ O Km Final ({km_final_int}) não pode ser menor que o Km Inicial ({km_inicial_val}).")
                return

            # Cálculo exato do KM rodado
            km_percorrido = int(km_final_int - km_inicial_val)

            chave_transacao_final = f"finalizar_{dados_ativos.get('rv')}_{km_final_int}"
            if st.session_state.get("ultima_transacao") == chave_transacao_final:
                st.warning("⚠️ Esta finalização já está sendo processada. Aguarde...")
                return
            st.session_state["ultima_transacao"] = chave_transacao_final

            payload_finalizar = {
                "acao": "finalizar",
                "gid_destino": GID_LANCAMENTOS,
                "rv": str(dados_ativos.get("rv")).strip(),
                "placa": str(dados_ativos.get("placa")).strip(),
                "condutor": str(dados_ativos.get("condutor")).strip(),
                "data_final": data_fim.strftime("%d/%m/%Y"),
                "horario_final": hora_fim.strftime("%H:%M:%S"),
                "km_inicial": km_inicial_val,
                "km_final": km_final_int,
                "km_percorrido": km_percorrido,
                "destino": destino_atualizado.strip() if destino_atualizado.strip() else dados_ativos.get("destino")
            }

            with st.spinner("Gravando encerramento na planilha..."):
                sucesso, msg = enviar_requisicao_apps_script(payload_finalizar)

            if sucesso:
                st.success(f"✅ Viagem {dados_ativos.get('rv')} finalizada! Total percorrido: {km_percorrido} km.")
                st.balloons()
                st.cache_data.clear()
                st.session_state["ultima_transacao"] = None
                time.sleep(2)
                st.rerun()
            else:
                st.session_state["ultima_transacao"] = None
                st.error(f"❌ Falha ao finalizar na planilha: {msg}")

    # =========================================================================
    # CENÁRIO 2: INÍCIO DE NOVA VIAGEM
    # =========================================================================
    else:
        df_veiculos_todos = carregar_veiculos()
        if df_veiculos_todos.empty:
            st.error("Nenhum veículo disponível na base. Verifique a planilha.")
            return

        acesso_norm = normalizar_texto(acesso_local)
        
        if acesso_norm in ["geral", "todas", "todos", "adm", "admin", ""]:
            df_veiculos = df_veiculos_todos.copy()
            st.caption("🌐 **Acesso Geral:** Todos os veículos da frota estão disponíveis para escolha.")
        else:
            df_veiculos = df_veiculos_todos[
                df_veiculos_todos["local_pernoite"].apply(lambda loc: acesso_norm in normalizar_texto(loc))
            ].copy()
            st.caption(f"📍 **Acesso Restrito:** Exibindo veículos com pernoite em **{acesso_local}**.")

        if df_veiculos.empty:
            st.warning(f"⚠️ Nenhum veículo cadastrado com pernoite para sua localidade ({acesso_local}). Contate o gestor de frota.")
            return

        st.markdown('<div class="section-subheading">1. Seleção do Veículo</div>', unsafe_allow_html=True)
        
        df_veiculos["rotulo_completo"] = df_veiculos.apply(
            lambda r: f"{r['placa']} - {r['veiculo']} ({r['local_pernoite']})" if r.get('local_pernoite') else f"{r['placa']} - {r['veiculo']}",
            axis=1
        )
        opcoes = ["-- Selecione um veículo --"] + df_veiculos["rotulo_completo"].tolist()
        veiculo_escolhido = st.selectbox("Veículo da Frota:", options=opcoes, key="select_veiculo")

        if veiculo_escolhido != "-- Selecione um veículo --":
            dados_veiculo = df_veiculos[df_veiculos["rotulo_completo"] == veiculo_escolhido].iloc[0]
            placa = dados_veiculo["placa"]
            modelo = dados_veiculo["veiculo"]
            cidade_veiculo = dados_veiculo.get("local_pernoite", "Não informado")
            placa_limpa = limpar_placa(placa)

            if placa_limpa in veiculos_em_uso:
                ocupante = veiculos_em_uso[placa_limpa]
                st.error(f"🚫 **Veículo Indisponível!** O veículo de placa **{placa}** já está em viagem aberta iniciada por **{ocupante['condutor']}** em {ocupante['data_inicial']} às {ocupante['horario_inicial']}.")
                st.info(f"Código da viagem aberta em andamento: **{ocupante['rv']}**. Escolha outro veículo ou aguarde a finalização.")
                return

            codigo_rv_previsto = gerar_proximo_rv(df_lanc, placa, ano_atual)

            st.markdown(f"""
                <div class="card-vehicle-info">
                    <b>🎫 Registro de Viagem:</b> {codigo_rv_previsto}<br>
                    <b>👤 Condutor:</b> {nome_condutor}<br>
                    <b>🚙 Veículo:</b> {modelo}<br>
                    <b>🔢 Placa:</b> {placa}<br>
                    <b>📍 Base/Pernoite:</b> {cidade_veiculo}
                </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-subheading">2. Start Inicial (Saída do Veículo)</div>', unsafe_allow_html=True)
            with st.form("form_start_inicial"):
                col_d, col_h = st.columns(2)
                with col_d:
                    data_ini = st.date_input("Data Inicial:", value=agora.date(), format="DD/MM/YYYY")
                with col_h:
                    hora_ini = st.time_input("Horário Inicial:", value=agora.time().replace(microsecond=0))

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

                btn_start_inicial = st.form_submit_button("🚀 Iniciar Viagem (Start Inicial)", use_container_width=True)

            if btn_start_inicial:
                if km_ini is None:
                    st.error("⚠️ Por favor, digite o Km Inicial do veículo.")
                    return
                
                km_ini_val = extrair_inteiro_km(km_ini)
                if km_ini_val <= 0:
                    st.error("⚠️ O Km Inicial deve ser maior que zero.")
                    return
                if not destino_ini.strip():
                    st.error("⚠️ Por favor, informe o Destino da viagem.")
                    return

                df_lanc_tempo_real = carregar_lancamentos_existentes()
                duplicado, motivo_duplicado = verificar_lancamento_duplicado(
                    df_lanc_tempo_real,
                    rv_codigo=codigo_rv_previsto,
                    placa=placa,
                    condutor=nome_condutor,
                    data_ini=data_ini.strftime("%d/%m/%Y"),
                    km_ini=km_ini_val
                )

                if duplicado:
                    st.error(f"🚫 **Lançamento Duplicado Impedido:** {motivo_duplicado}")
                    st.warning("Recarregue a página ou aguarde a atualização da planilha antes de tentar novamente.")
                    return

                chave_transacao_ini = f"iniciar_{codigo_rv_previsto}_{placa}_{km_ini_val}"
                if st.session_state.get("ultima_transacao") == chave_transacao_ini:
                    st.warning("⚠️ Esta viagem já está sendo enviada. Aguarde a confirmação...")
                    return
                st.session_state["ultima_transacao"] = chave_transacao_ini

                payload_iniciar = {
                    "acao": "iniciar",
                    "gid_destino": GID_LANCAMENTOS,
                    "rv": codigo_rv_previsto,
                    "condutor": nome_condutor,
                    "usuario": usuario_atual,
                    "placa": placa,
                    "veiculo": modelo,
                    "data_inicial": data_ini.strftime("%d/%m/%Y"),
                    "horario_inicial": hora_ini.strftime("%H:%M:%S"),
                    "km_inicial": km_ini_val,
                    "destino": destino_ini.strip(),
                    "data_registro": agora.strftime("%d/%m/%Y %H:%M:%S")
                }

                with st.spinner(f"Gravando início da viagem ({codigo_rv_previsto}) na planilha..."):
                    sucesso, msg = enviar_requisicao_apps_script(payload_iniciar)

                if sucesso:
                    st.success(f"✅ Viagem {codigo_rv_previsto} iniciada e registrada na planilha com sucesso!")
                    st.cache_data.clear()
                    st.session_state["ultima_transacao"] = None
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.session_state["ultima_transacao"] = None
                    st.error(f"❌ Falha ao iniciar viagem na planilha: {msg}")

if __name__ == "__main__":
    main()