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
        /* 1. ELIMINAÇÃO DE ELEMENTOS FANTASMAS SUPERIORES */
        .e1o1x6gp2,
        .st-emotion-cache-k2h9z6,
        div[data-testid="stDecoration"],
        div[data-testid="stToolbar"],
        header[data-testid="stHeader"],
        [data-testid="stHeader"],
        #MainMenu, footer, .stDeployButton, [data-testid="stToolbarActions"],
        [data-testid="manage-app-button"] {
            display: none !important;
            height: 0px !important;
            min-height: 0px !important;
            max-height: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
            border: none !important;
            visibility: hidden !important;
        }

        [data-testid="collapsedControl"] {
            display: none !important;
        }

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

        /* 2. PLANO DE FUNDO EM GRADIENTE RADIAL ESCURO */
        :root, html, body {
            background-color: #0b0217 !important;
            background: radial-gradient(at 93.69543598317607% 5.616169708078966%, hsla(267.88732394366195, 100%, 13.92156862745098%, 1) 0%, hsla(267.88732394366195, 100%, 13.92156862745098%, 0) 100%), radial-gradient(at 49.6250738166925% 50.14065564263524%, hsla(264.11764705882354, 100%, 20%, 1) 0%, hsla(264.11764705882354, 100%, 20%, 0) 100%), radial-gradient(at 37.00403509139429% 89.3640844672993%, hsla(240.81081081081078, 100%, 29.01960784313726%, 1) 0%, hsla(240.81081081081078, 100%, 29.01960784313726%, 0) 100%), radial-gradient(at 76.13084977631372% 73.97772700476057%, hsla(267.88732394366195, 100%, 13.92156862745098%, 1) 0%, hsla(267.88732394366195, 100%, 13.92156862745098%, 0) 100%), radial-gradient(at 20.535772964012743% 97.27562379868434%, hsla(264.11764705882354, 100%, 20%, 1) 0%, hsla(264.11764705882354, 100%, 20%, 0) 100%), radial-gradient(at 45.86269066661277% 99.26966956219938%, hsla(240.81081081081078, 100%, 29.01960784313726%, 1) 0%, hsla(240.81081081081078, 100%, 29.01960784313726%, 0) 100%), radial-gradient(at 33.24174772772377% 84.28822907756046%, hsla(267.88732394366195, 100%, 13.92156862745098%, 1) 0%, hsla(267.88732394366195, 100%, 13.92156862745098%, 0) 100%), radial-gradient(at 30.932790321943536% 31.05233181318352%, hsla(264.11764705882354, 100%, 20%, 1) 0%, hsla(264.11764705882354, 100%, 20%, 0) 100%), radial-gradient(at 87.19757331823584% 4.189116488339084%, hsla(240.81081081081078, 100%, 29.01960784313726%, 1) 0%, hsla(240.81081081081078, 100%, 29.01960784313726%, 0) 100%) !important;
            background-attachment: fixed !important;
            color: #0F172A !important;
            color-scheme: light !important;
        }

        .stApp, [data-testid="stAppViewContainer"] {
            background: transparent !important;
            color: #0F172A !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }

        /* 3. CARD BRANCO UNIFICADO */
        .block-container,
        div[data-testid="stAppViewContainer"] > .main > .block-container,
        div[data-testid="stAppViewBlockContainer"] {
            background-color: #FFFFFF !important;
            border-radius: 20px !important;
            box-shadow: 0 20px 50px rgba(11, 2, 23, 0.55), 0 0 0 1px rgba(255, 255, 255, 0.9) !important;
            padding: 24px 26px 32px 26px !important;
            margin-top: 1rem !important;
            margin-bottom: 2rem !important;
            max-width: 660px !important;
        }

        div[data-testid="stVerticalBlock"] {
            background-color: transparent !important;
        }

        .user-status-pill {
            background: #EFF6FF;
            color: #1E40AF;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 700;
            border: 1px solid #DBEAFE;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .internal-menu-panel {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        }

        /* Tipografia */
        h1, h2, h3, h4, h5, h6, p, span, label, div {
            color: #0F172A !important;
        }
        .stWidgetLabel p, label p {
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            margin-bottom: 4px !important;
        }

        .card-header-block {
            text-align: center;
            margin-bottom: 1rem;
            margin-top: 0.4rem;
        }
        .corporate-title {
            font-size: 1.35rem !important;
            font-weight: 800 !important;
            color: #1E3A8A !important;
            margin: 4px 0 2px 0 !important;
            letter-spacing: -0.02em !important;
        }
        .corporate-subtitle {
            font-size: 0.86rem !important;
            color: #64748B !important;
            margin: 0 !important;
            font-weight: 500 !important;
        }

        /* Centralização universal de imagens */
        div[data-testid="stImage"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin-left: auto !important;
            margin-right: auto !important;
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
            width: 100% !important;
            text-align: center !important;
        }
        div[data-testid="stImage"] img {
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
            display: block !important;
            margin-left: auto !important;
            margin-right: auto !important;
            margin-bottom: 0px !important;
        }

        div[data-testid="element-container"]:has(> div[data-testid="stImage"]) {
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }

        /* Formulários operacionais */
        [data-testid="stForm"] {
            background-color: #F8FAFC !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 14px !important;
            box-shadow: none !important;
            padding: 20px 20px !important;
            margin-top: 10px !important;
        }

        .card-vehicle-info {
            background-color: #F8FAFC !important;
            border: 1px solid #DBEAFE !important;
            border-left: 5px solid #2563EB !important;
            padding: 14px 16px !important;
            border-radius: 12px !important;
            margin: 14px 0 !important;
            color: #334155 !important;
            line-height: 1.6 !important;
            font-size: 0.90rem !important;
        }

        /* CARD RESUMO DA VIAGEM ATIVA COM ALTO DESTAQUE */
        .card-active-trip {
            background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%) !important;
            border: 1px solid #86EFAC !important;
            border-left: 6px solid #16A34A !important;
            padding: 18px 20px !important;
            border-radius: 14px !important;
            margin-bottom: 1.4rem !important;
            margin-top: 0.8rem !important;
            color: #14532D !important;
            line-height: 1.75 !important;
            font-size: 0.95rem !important;
            box-shadow: 0 6px 18px rgba(22, 163, 74, 0.12) !important;
        }
        .card-active-trip b {
            color: #064E3B !important;
            font-weight: 700 !important;
        }

        /* Inputs e controles */
        div[data-baseweb="input"],
        div[data-baseweb="base-input"],
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] > div,
        div[data-testid="stDateInput"] > div,
        div[data-testid="stTimeInput"] > div,
        div[data-testid="stNumberInput"] > div,
        div[data-testid="stNumberInputContainer"] {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            color: #0F172A !important;
            border-radius: 8px !important;
        }

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"]:focus-within,
        div[data-testid="stNumberInputContainer"]:focus-within {
            border-color: #2563EB !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.20) !important;
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

        /* Botões principais */
        div.stButton > button:first-child,
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
            background-color: #1D4ED8 !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            height: 46px !important;
            font-size: 0.98rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(29, 78, 216, 0.35) !important;
            cursor: pointer !important;
            transition: all 0.2s ease-in-out !important;
        }
        div.stButton > button:first-child:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            background: linear-gradient(135deg, #1E40AF, #1D4ED8) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 16px rgba(29, 78, 216, 0.45) !important;
        }

        .btn-menu-card button {
            background: #F1F5F9 !important;
            color: #334155 !important;
            -webkit-text-fill-color: #334155 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            height: 38px !important;
            font-size: 0.88rem !important;
            box-shadow: none !important;
        }
        .btn-menu-card button:hover {
            background: #E2E8F0 !important;
            transform: none !important;
            box-shadow: none !important;
        }

        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #DBEAFE !important;
            z-index: 10000000 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #1E293B !important;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. VARIÁVEIS GLOBAIS E ENDPOINTS
# -------------------------------------------------------------
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxXSQRM3lPFIQ6VkDs4OK7HrjnfIDrPEPOTM2sAHhogHNhb2PhSoUSw06fYT-rGeiS2uw/exec"
SPREADSHEET_ID = "1-Bn0VBnRV1zp_f7QrKTldKB03L9_k7DyRO3YslGMnnU"

GID_USUARIOS = "426012097"       # Aba Condutores / Logins
GID_VEICULOS = "0"               # Aba Frota
GID_LANCAMENTOS = "379222602"    # Aba Lançamentos de Viagens

# -------------------------------------------------------------
# 3. SUPORTE A ARQUIVOS LOCAIS
# -------------------------------------------------------------
def obter_caminho_arquivo(nomes_possiveis):
    extensoes = [".png", ".jpg", ".jpeg", ".svg", ".webp", ""]
    for nome in nomes_possiveis:
        for ext in extensoes:
            caminho = f"{nome}{ext}"
            if os.path.exists(caminho) and not os.path.isdir(caminho):
                return caminho
    return None

def obter_caminho_logotipo():
    return obter_caminho_arquivo(["Logotipo", "logotipo", "Logo", "logo"])

def obter_caminho_imagem_veiculo():
    return obter_caminho_arquivo([
        "veiculo", "veiculos", "Veiculo", "Veiculos",
        "frota", "Frota", "carro", "carros", "Carro", "Carros",
        "banner", "Banner"
    ])

def renderizar_cabecalho_interno(subtitulo="Gestão e Controle Operacional de Frotas"):
    caminho_logo = obter_caminho_logotipo()

    if caminho_logo:
        try:
            logo_img = Image.open(caminho_logo)
            st.image(logo_img, width=110)
        except Exception:
            st.markdown('<div class="corporate-title" style="text-align:center;">🚗 Controle de Frotas</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="corporate-title" style="text-align:center;">🚗 Controle de Frotas</div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div class="card-header-block">
            <div class="corporate-title">Registro e Controle de Saída de Veículos</div>
            <p class="corporate-subtitle">{subtitulo}</p>
        </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. FUNÇÕES DE SUPORTE E LEITURA DA PLANILHA
# -------------------------------------------------------------
def normalizar_texto(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.strip().lower()

def limpar_placa(placa_str):
    return re.sub(r'[^A-Za-z0-9]', '', str(placa_str)).upper()

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

@st.cache_data(ttl=30)
def carregar_veiculos():
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_VEICULOS}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_VEICULOS}"
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
                for k in ["veiculo", "modelo", "carro", "descricao"]:
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
    t_anti_cache = int(time.time())
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_LANCAMENTOS}&_nocache={t_anti_cache}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_LANCAMENTOS}&_nocache={t_anti_cache}"
    ]
    for url in urls:
        try:
            df = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df.empty:
                return df
        except Exception:
            continue
    return pd.DataFrame()

def extrair_viagens_abertas(df_lanc):
    abertos_por_condutor = {}
    veiculos_ocupados = {}

    if df_lanc.empty:
        return abertos_por_condutor, veiculos_ocupados

    col_map = {normalizar_texto(c): c for c in df_lanc.columns}
    
    col_data_ini = col_map.get("data inicial", col_map.get("data_inicial", df_lanc.columns[0]))
    col_hora_ini = col_map.get("horario inicial", col_map.get("horario_inicial", df_lanc.columns[1] if len(df_lanc.columns) > 1 else df_lanc.columns[0]))
    col_km_ini = col_map.get("km inicial", col_map.get("km_inicial", df_lanc.columns[2] if len(df_lanc.columns) > 2 else df_lanc.columns[0]))
    col_data_fim = col_map.get("data final", col_map.get("data_final", df_lanc.columns[3] if len(df_lanc.columns) > 3 else df_lanc.columns[0]))
    col_hora_fim = col_map.get("horario final", col_map.get("horario_final", df_lanc.columns[4] if len(df_lanc.columns) > 4 else df_lanc.columns[0]))
    col_km_fim = col_map.get("km final", col_map.get("km_final", df_lanc.columns[5] if len(df_lanc.columns) > 5 else df_lanc.columns[0]))
    col_condutor = col_map.get("condutor", col_map.get("motorista", df_lanc.columns[6] if len(df_lanc.columns) > 6 else df_lanc.columns[0]))
    col_destino = col_map.get("destino", col_map.get("rota", df_lanc.columns[7] if len(df_lanc.columns) > 7 else df_lanc.columns[0]))
    col_placa = col_map.get("placa", df_lanc.columns[8] if len(df_lanc.columns) > 8 else df_lanc.columns[0])
    col_veiculo = col_map.get("veiculo", col_map.get("modelo", df_lanc.columns[9] if len(df_lanc.columns) > 9 else df_lanc.columns[0]))
    col_rv = col_map.get("rv", col_map.get("registro", df_lanc.columns[12] if len(df_lanc.columns) > 12 else df_lanc.columns[-1]))

    for _, row in df_lanc.iterrows():
        val_data_fim = str(row.get(col_data_fim, "")).strip()
        val_km_fim = str(row.get(col_km_fim, "")).strip()
        val_cond = str(row.get(col_condutor, "")).strip()
        val_placa = str(row.get(col_placa, "")).strip()
        val_rv = str(row.get(col_rv, "")).strip()

        tem_fim = (
            (val_data_fim != "" and val_data_fim.lower() not in ["nan", "none", "null"]) or
            (val_km_fim != "" and val_km_fim.lower() not in ["nan", "none", "null", "0", "0.0"])
        )

        if not tem_fim and val_rv:
            info = {
                "rv": val_rv,
                "condutor": val_cond,
                "placa": val_placa,
                "veiculo": str(row.get(col_veiculo, "")).strip(),
                "data_inicial": str(row.get(col_data_ini, "")).strip(),
                "horario_inicial": str(row.get(col_hora_ini, "")).strip(),
                "km_inicial": str(row.get(col_km_ini, "0")).strip(),
                "destino": str(row.get(col_destino, "")).strip()
            }

            p_limpa = limpar_placa(val_placa)
            if p_limpa:
                veiculos_ocupados[p_limpa] = info

            if val_cond:
                abertos_por_condutor[normalizar_texto(val_cond)] = info

    return abertos_por_condutor, veiculos_ocupados

def verificar_lancamento_duplicado(df_lancamentos, rv_codigo, placa, condutor, data_ini, km_ini):
    if df_lancamentos.empty or len(df_lancamentos.columns) < 13:
        return False, ""

    placa_limpa_alvo = limpar_placa(placa)
    condutor_norm_alvo = normalizar_texto(condutor)
    data_ini_alvo = str(data_ini).strip()
    km_ini_alvo = str(int(km_ini)).strip() if km_ini is not None else ""
    rv_alvo = str(rv_codigo).strip().upper()

    for _, row in df_lancamentos.iterrows():
        rv_row = str(row.iloc[12]).strip().upper() if pd.notna(row.iloc[12]) else ""
        placa_row = limpar_placa(row.iloc[8]) if pd.notna(row.iloc[8]) else ""
        cond_row = normalizar_texto(row.iloc[6]) if pd.notna(row.iloc[6]) else ""
        data_row = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        km_row = str(row.iloc[2]).split(".")[0].strip() if pd.notna(row.iloc[2]) else ""

        if rv_row and rv_row == rv_alvo:
            return True, f"O Registro de Viagem {rv_alvo} já existe na planilha."

        if (placa_row == placa_limpa_alvo and 
            cond_row == condutor_norm_alvo and 
            data_row == data_ini_alvo and 
            km_row == km_ini_alvo):
            return True, f"Já existe uma viagem registrada para este condutor e veículo com Data {data_ini_alvo} e Km {km_ini_alvo}."

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
                    return True, ret.get("message", "Operação realizada!")
                return False, ret.get("message", "Erro retornado pelo script.")
            except Exception:
                if "success" in resposta.text.lower() or "sucesso" in resposta.text.lower():
                    return True, "Operação realizada com sucesso!"
                return True, "Registro atualizado!"
        elif resposta.status_code == 403:
            return False, "Erro 403: No Apps Script, configure 'Quem tem acesso' para 'Qualquer pessoa'."
        else:
            return False, f"Erro HTTP {resposta.status_code}: {resposta.text[:180]}"
    except Exception as e:
        return False, f"Falha na comunicação: {str(e)}"

# -------------------------------------------------------------
# 5. TELA DE LOGIN (LOGOTIPO + IMAGEM DA FROTA 317PX)
# -------------------------------------------------------------
def tela_login(df_usuarios):
    caminho_logo = obter_caminho_logotipo()
    caminho_veiculo = obter_caminho_imagem_veiculo()
    
    with st.form("form_login"):
        if caminho_logo:
            try:
                logo_img = Image.open(caminho_logo)
                st.image(logo_img, width=110)
            except Exception:
                st.markdown("<h3 style='text-align:center;'>🚗 Master Café</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align:center;'>🚗 Master Café</h3>", unsafe_allow_html=True)

        if caminho_veiculo:
            try:
                img_veiculo = Image.open(caminho_veiculo)
                st.image(img_veiculo, width=317)
            except Exception:
                pass

        usuario_digitado = st.text_input("Usuário:", placeholder="Digite seu usuário").strip().lower()
        senha_digitada = st.text_input("Senha:", type="password", placeholder="Digite sua senha").strip()
        btn_login = st.form_submit_button("Entrar no Sistema")
        
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
                st.session_state["menu_aberto"] = False
                st.query_params["u"] = usuario_digitado
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

# -------------------------------------------------------------
# 6. APLICATIVO PRINCIPAL (TELA DA VIAGEM)
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
                st.session_state["menu_aberto"] = False

    if not st.session_state.get("autenticado", False):
        tela_login(df_usuarios)
        return

    usuario_atual = st.session_state.get("usuario_logado", "")
    nome_condutor = st.session_state.get("nome_condutor", "Condutor")
    acesso_local = st.session_state.get("acesso_local", "Geral")

    df_lanc = carregar_lancamentos_existentes()
    viagens_abertas_por_condutor, veiculos_em_uso = extrair_viagens_abertas(df_lanc)

    condutor_chave = normalizar_texto(nome_condutor)
    usuario_chave = normalizar_texto(usuario_atual)

    # Identificação por estado ativo local ou busca por nome/login
    viagem_pendente_condutor = st.session_state.get("viagem_ativa", None)

    if not viagem_pendente_condutor:
        viagem_pendente_condutor = (
            viagens_abertas_por_condutor.get(condutor_chave) or 
            viagens_abertas_por_condutor.get(usuario_chave)
        )
        if viagem_pendente_condutor:
            st.session_state["viagem_ativa"] = viagem_pendente_condutor

    # Menu Lateral
    with st.sidebar:
        st.write(f"🚗 **Condutor:**\n### {nome_condutor}")
        st.caption(f"📍 **Base de Acesso:** {acesso_local}")
        if viagem_pendente_condutor:
            st.warning(f"⚠️ Viagem aberta no veículo: **{viagem_pendente_condutor.get('placa')}**\n(RV: {viagem_pendente_condutor.get('rv')})")
        if st.button("🚪 Sair do Sistema", key="btn_logout_sidebar"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

    agora = obter_agora_brasil()
    ano_atual = agora.strftime("%Y")

    # -------------------------------------------------------------
    # 7. CONTEÚDO PRINCIPAL (DENTRO DO CARD BRANCO UNIFICADO)
    # -------------------------------------------------------------
    
    # 1. BOTÃO DE ACESSO AO MENU EMBUTIDO NO TOPO DO CARD
    col_menu_btn, col_user_info = st.columns([1.1, 2.2])
    
    with col_menu_btn:
        st.markdown('<div class="btn-menu-card">', unsafe_allow_html=True)
        texto_botao = "✖ Fechar Menu" if st.session_state.get("menu_aberto", False) else "☰ Menu do Condutor"
        if st.button(texto_botao, key="toggle_menu_card", use_container_width=True):
            st.session_state["menu_aberto"] = not st.session_state.get("menu_aberto", False)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_user_info:
        st.markdown(f"""
            <div style="text-align: right; padding-top: 6px;">
                <span class="user-status-pill">👤 {nome_condutor} • {acesso_local}</span>
            </div>
        """, unsafe_allow_html=True)

    if st.session_state.get("menu_aberto", False):
        st.markdown(f"""
            <div class="internal-menu-panel">
                <b>🚗 Painel do Condutor</b><br>
                <span style="font-size: 0.88rem; color: #475569;">Usuário: <b>{usuario_atual}</b> | Cidade Base: <b>{acesso_local}</b></span>
            </div>
        """, unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("🔄 Atualizar Informações", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        with col_m2:
            if st.button("🚪 Desconectar / Sair", use_container_width=True):
                st.session_state.clear()
                st.query_params.clear()
                st.rerun()
        st.markdown("<hr style='margin: 12px 0 16px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # 2. Cabeçalho interno (Logo e Título - SEM a imagem da frota)
    renderizar_cabecalho_interno("Controle de Deslocamentos e Quilometragem")

    # =========================================================================
    # CENÁRIO 1: CONDUTOR EM VIAGEM ABERTA (EXIBE CARD RESUMO + FORM FINAL)
    # =========================================================================
    if viagem_pendente_condutor is not None:
        dados_ativos = viagem_pendente_condutor

        st.warning("⚠️ **Você possui uma viagem em andamento!** Finalize o retorno abaixo para liberar novos lançamentos.")
        
        # CARD COM AS INFORMAÇÕES DETALHADAS APÓS O START INICIAL
        st.markdown(f"""
            <div class="card-active-trip">
                <div style="font-size: 1.05rem; font-weight: 800; margin-bottom: 8px; color: #166534; border-bottom: 1px solid #86EFAC; padding-bottom: 4px;">
                    📋 Resumo da Viagem em Andamento
                </div>
                <b>🎫 Registro de Viagem:</b> {dados_ativos.get('rv')}<br>
                <b>👤 Usuário / Condutor:</b> {dados_ativos.get('condutor')}<br>
                <b>🚙 Veículo:</b> {dados_ativos.get('veiculo')} (Placa: <b>{dados_ativos.get('placa')}</b>)<br>
                <b>⏱️ Início da Viagem:</b> {dados_ativos.get('data_inicial')} às {dados_ativos.get('horario_inicial')}<br>
                <b>🔢 Km Inicial (Saída):</b> {dados_ativos.get('km_inicial')} km<br>
                <b>📍 Destino Planejado:</b> {dados_ativos.get('destino') or 'Não especificado'}
            </div>
        """, unsafe_allow_html=True)

        st.subheader("Start Final (Retorno do Veículo)")
        with st.form("form_start_final"):
            col_df, col_hf = st.columns(2)
            with col_df:
                data_fim = st.date_input("Data Final:", value=agora.date(), format="DD/MM/YYYY")
            with col_hf:
                hora_fim = st.time_input("Horário Final:", value=agora.time().replace(microsecond=0))

            km_inicial_val = float(str(dados_ativos.get("km_inicial") or 0).replace(",", "."))
            km_fim = st.number_input(
                "Km Final:", 
                value=None, 
                placeholder="Digite o Km Final...", 
                min_value=km_inicial_val, 
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
                st.error("⚠️ Por favor, preencha o Km Final.")
                return
            if km_fim < km_inicial_val:
                st.error("⚠️ O Km Final não pode ser menor que o Km Inicial.")
                return

            km_percorrido = int(km_fim - km_inicial_val)

            chave_transacao_final = f"finalizar_{dados_ativos.get('rv')}_{km_fim}"
            if st.session_state.get("ultima_transacao") == chave_transacao_final:
                st.warning("⚠️ Esta finalização já está sendo processada. Aguarde...")
                return
            st.session_state["ultima_transacao"] = chave_transacao_final

            payload_finalizar = {
                "acao": "finalizar",
                "gid_destino": GID_LANCAMENTOS,
                "rv": dados_ativos.get("rv"),
                "data_final": data_fim.strftime("%d/%m/%Y"),
                "horario_final": hora_fim.strftime("%H:%M:%S"),
                "km_final": int(km_fim),
                "km_percorrido": km_percorrido,
                "destino": destino_atualizado.strip() if destino_atualizado.strip() else dados_ativos.get("destino")
            }

            with st.spinner("Atualizando e concluindo a viagem na planilha..."):
                sucesso, msg = enviar_requisicao_apps_script(payload_finalizar)

            if sucesso:
                st.session_state["viagem_ativa"] = None
                st.session_state["ultima_transacao"] = None
                st.success(f"✅ Viagem {dados_ativos.get('rv')} finalizada com sucesso na planilha!")
                st.balloons()
                st.cache_data.clear()
                time.sleep(2)
                st.rerun()
            else:
                st.session_state["ultima_transacao"] = None
                st.error(f"❌ Falha ao finalizar na planilha: {msg}")

    # =========================================================================
    # CENÁRIO 2: CONDUTOR LIVRE (NOVO REGISTRO / START INICIAL)
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

        st.subheader("1. Seleção do Veículo")
        
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

            st.subheader("2. Start Inicial (Saída do Veículo)")
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

                btn_start_inicial = st.form_submit_button("🚀 Iniciar Viagem (Start Inicial)")

            if btn_start_inicial:
                if km_ini is None or km_ini <= 0:
                    st.error("⚠️ Por favor, digite o Km Inicial do veículo.")
                    return
                if not destino_ini.strip():
                    st.error("⚠️ Por favor, informe o Destino da viagem.")
                    return

                # Verificação anti-duplicidade em tempo real
                df_lanc_tempo_real = carregar_lancamentos_existentes()
                duplicado, motivo_duplicado = verificar_lancamento_duplicado(
                    df_lanc_tempo_real,
                    rv_codigo=codigo_rv_previsto,
                    placa=placa,
                    condutor=nome_condutor,
                    data_ini=data_ini.strftime("%d/%m/%Y"),
                    km_ini=km_ini
                )

                if duplicado:
                    st.error(f"🚫 **Lançamento Duplicado Impedido:** {motivo_duplicado}")
                    st.warning("Recarregue a página ou aguarde a atualização da planilha antes de tentar novamente.")
                    return

                chave_transacao_ini = f"iniciar_{codigo_rv_previsto}_{placa}_{km_ini}"
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
                    "km_inicial": int(km_ini),
                    "destino": destino_ini.strip(),
                    "data_registro": agora.strftime("%d/%m/%Y %H:%M:%S")
                }

                with st.spinner(f"Gravando início da viagem ({codigo_rv_previsto}) na planilha..."):
                    sucesso, msg = enviar_requisicao_apps_script(payload_iniciar)

                if sucesso:
                    st.session_state["viagem_ativa"] = {
                        "rv": codigo_rv_previsto,
                        "condutor": nome_condutor,
                        "placa": placa,
                        "veiculo": modelo,
                        "data_inicial": data_ini.strftime("%d/%m/%Y"),
                        "horario_inicial": hora_ini.strftime("%H:%M:%S"),
                        "km_inicial": int(km_ini),
                        "destino": destino_ini.strip()
                    }
                    st.success(f"✅ Viagem {codigo_rv_previsto} iniciada e registrada com sucesso!")
                    st.cache_data.clear()
                    time.sleep(1.0)
                    st.rerun()
                else:
                    st.session_state["ultima_transacao"] = None
                    st.error(f"❌ Falha ao iniciar viagem na planilha: {msg}")

if __name__ == "__main__":
    main()