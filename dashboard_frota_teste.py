import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timezone, timedelta, date
import requests
import json
import os
import re
import urllib.parse
import unicodedata
from PIL import Image

try:
    from zoneinfo import ZoneInfo
    FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")
except Exception:
    FUSO_BRASIL = timezone(timedelta(hours=-3))

def obter_agora_brasil():
    """Retorna datetime oficial de Brasília."""
    return datetime.now(FUSO_BRASIL)

# -------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS MODERNO CORPORATIVO
# -------------------------------------------------------------
st.set_page_config(
    page_title="Painel de Frotas | Master Café",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        /* 1. OCULTAR ELEMENTOS PADRÃO DO STREAMLIT */
        #MainMenu, footer, .stDeployButton, [data-testid="stToolbarActions"],
        [data-testid="manage-app-button"], div[data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
        }

        header[data-testid="stHeader"] {
            background-color: transparent !important;
            height: 2.0rem !important;
        }

        /* 2. BASE DO CONTAINER PRINCIPAL COM MARGENS EM AMBOS OS LADOS */
        .block-container,
        div[data-testid="stAppViewContainer"] > .main > .block-container,
        div[data-testid="stAppViewBlockContainer"] {
            padding-top: 1.2rem !important;
            padding-bottom: 3rem !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            max-width: 1320px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            width: 100% !important;
        }

        :root, html, body {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
            color-scheme: light !important;
        }

        .stApp, [data-testid="stAppViewContainer"] {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }

        h1, h2, h3, h4, h5, p, span, label, div {
            color: #0F172A !important;
        }

        .stWidgetLabel p, label p {
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
        }

        /* 3. SIDEBAR CORPORATIVA */
        section[data-testid="stSidebar"] {
            background-color: #0F172A !important;
            border-right: 1px solid #1E293B !important;
            padding-top: 0.5rem !important;
            width: 18rem !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] span {
            color: #F8FAFC !important;
        }

        .sidebar-brand-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: #FFFFFF !important;
            line-height: 1.2;
            letter-spacing: -0.02em;
        }

        .sidebar-brand-sub {
            font-size: 0.70rem;
            color: #94A3B8 !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .user-card {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 1.2rem;
        }

        .user-card-name {
            font-size: 0.85rem;
            font-weight: 700;
            color: #FFFFFF !important;
            margin: 0;
        }

        .user-card-role {
            font-size: 0.72rem;
            color: #38BDF8 !important;
            font-weight: 600;
            margin: 0;
            text-transform: uppercase;
        }

        .user-card-time {
            font-size: 0.68rem;
            color: #94A3B8 !important;
            margin-top: 3px;
        }

        /* 4. BOTÕES DE NAVEGAÇÃO DA SIDEBAR PADRONIZADOS */
        section[data-testid="stSidebar"] div.stButton > button {
            background: #1E293B !important;
            color: #CBD5E1 !important;
            -webkit-text-fill-color: #CBD5E1 !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            padding: 0 14px !important;
            min-height: 2.6rem !important;
            height: 2.6rem !important;
            width: 100% !important;
            box-shadow: none !important;
            transition: all 0.2s ease-in-out !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            text-align: left !important;
            margin-bottom: 6px !important;
        }

        section[data-testid="stSidebar"] div.stButton > button:hover {
            background: #2563EB !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border-color: #3B82F6 !important;
            transform: translateX(3px);
        }

        /* BOTÃO ATIVO NA SIDEBAR */
        section[data-testid="stSidebar"] .nav-active div.stButton > button {
            background: #2563EB !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border-color: #60A5FA !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35) !important;
        }

        /* BOTÕES DE SISTEMA NA SIDEBAR */
        section[data-testid="stSidebar"] .btn-sync div.stButton > button {
            background: #065F46 !important;
            color: #ECFDF5 !important;
            -webkit-text-fill-color: #ECFDF5 !important;
            border: 1px solid #059669 !important;
            justify-content: center !important;
        }
        section[data-testid="stSidebar"] .btn-sync div.stButton > button:hover {
            background: #059669 !important;
        }

        section[data-testid="stSidebar"] .btn-exit div.stButton > button {
            background: #7F1D1D !important;
            color: #FEF2F2 !important;
            -webkit-text-fill-color: #FEF2F2 !important;
            border: 1px solid #DC2626 !important;
            justify-content: center !important;
        }
        section[data-testid="stSidebar"] .btn-exit div.stButton > button:hover {
            background: #DC2626 !important;
        }

        /* 5. CABEÇALHO DA PÁGINA PRINCIPAL HARMONIZADO */
        .main-header-title {
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            color: #0F172A !important;
            line-height: 1.25 !important;
            letter-spacing: -0.015em !important;
            margin: 0 !important;
        }

        .main-header-sub {
            font-size: 0.75rem !important;
            color: #64748B !important;
            font-weight: 500 !important;
            letter-spacing: 0.02em !important;
            margin: 2px 0 0 0 !important;
        }

        /* 6. CARDS, KPIS E COMPONENTES NO CONTEÚDO PRINCIPAL */
        .filter-panel, .kpi-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 14px 18px;
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.03);
            margin-bottom: 1rem;
        }

        .kpi-title {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B;
            margin: 0;
        }
        .kpi-value {
            font-size: 1.65rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.1;
            margin: 0;
        }
        .kpi-caption {
            font-size: 0.74rem;
            color: #94A3B8;
            margin: 0;
        }

        .badge-open {
            background-color: #FEF3C7;
            color: #92400E;
            padding: 3px 8px;
            border-radius: 14px;
            font-size: 0.72rem;
            font-weight: 700;
            border: 1px solid #FDE68A;
        }
        .badge-done {
            background-color: #DEF7EC;
            color: #03543F;
            padding: 3px 8px;
            border-radius: 14px;
            font-size: 0.72rem;
            font-weight: 700;
            border: 1px solid #BCF0DA;
        }

        [data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
            padding: 22px !important;
        }

        div[data-baseweb="input"],
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] > div,
        div[data-testid="stDateInput"] > div,
        div[data-testid="stTimeInput"] > div,
        div[data-testid="stNumberInput"] > div {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            color: #0F172A !important;
            border-radius: 6px !important;
        }
        input, textarea {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            -webkit-text-fill-color: #0F172A !important;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. CONFIGURAÇÕES DA FOLHA DE CÁLCULO
# -------------------------------------------------------------
SPREADSHEET_ID = "1-Bn0VBnRV1zp_f7QrKTldKB03L9_k7DyRO3YslGMnnU"
GID_LANCAMENTOS = "379222602"
GID_USUARIOS = "426012097"
GID_FROTA = "1438914619"
NOME_ABA_ABASTECIMENTO = "Controle de combustivel"
NOME_ABA_POSTOS = "Posto de Combustivel"

WEBHOOK_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxXSQRM3lPFIQ6VkDs4OK7HrjnfIDrPEPOTM2sAHhogHNhb2PhSoUSw06fYT-rGeiS2uw/exec"

# -------------------------------------------------------------
# 3. SUPORTE A LOGOTIPO E PADRONIZAÇÃO
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

def normalizar_texto(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.strip().lower()

def formatar_nome_padrao(nome: str) -> str:
    partes = str(nome).strip().split()
    if not partes:
        return ""
    conjuncoes = {"de", "da", "do", "das", "dos", "e"}
    resultado = []
    for idx, p in enumerate(partes):
        p_lower = p.lower()
        if p_lower in conjuncoes and 0 < idx < len(partes) - 1:
            resultado.append(p_lower)
        else:
            resultado.append(p.capitalize())
    return " ".join(resultado)

def gerar_usuario_padrao(nome_completo: str) -> str:
    texto_sem_acento = unicodedata.normalize('NFKD', str(nome_completo)).encode('ASCII', 'ignore').decode('ASCII')
    partes = re.sub(r'[^a-zA-Z\s]', '', texto_sem_acento).strip().split()
    if not partes:
        return ""
    if len(partes) == 1:
        return partes[0].lower()
    primeira_letra = partes[0][0].lower()
    sobrenome = partes[-1].lower()
    return f"{primeira_letra}{sobrenome}"

# -------------------------------------------------------------
# 4. CARREGAMENTO E GRAVAÇÃO DE DADOS (ETL)
# -------------------------------------------------------------
@st.cache_data(ttl=15)
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
                c_acesso = cols_norm.get("acesso", cols_norm.get("cidade", None))

                df_res = pd.DataFrame()
                df_res["usuario"] = df[c_user].fillna("").astype(str).str.strip().str.lower()
                df_res["senha"] = df[c_pass].fillna("").astype(str).str.strip()
                df_res["nome"] = df[c_nome].fillna(df[c_user]).astype(str).str.strip().apply(formatar_nome_padrao)
                
                if c_acesso and c_acesso in df.columns:
                    df_res["acesso"] = df[c_acesso].fillna("Geral").astype(str).str.strip()
                else:
                    df_res["acesso"] = "Geral"

                return df_res
        except Exception:
            continue
    return pd.DataFrame([{"usuario": "admin", "senha": "123", "nome": "Gestor Master Café", "acesso": "Geral"}])

def obter_usuarios_ativos():
    df_base_user = carregar_usuarios()
    if "novos_usuarios_sessao" not in st.session_state:
        st.session_state["novos_usuarios_sessao"] = []
    
    if st.session_state["novos_usuarios_sessao"]:
        df_novos = pd.DataFrame(st.session_state["novos_usuarios_sessao"])
        return pd.concat([df_base_user, df_novos], ignore_index=True).drop_duplicates(subset=["usuario"], keep="last")
    return df_base_user

def gravar_usuario_na_planilha(usuario_dict: dict) -> bool:
    if WEBHOOK_APPS_SCRIPT_URL:
        try:
            payload = usuario_dict.copy()
            payload["acao"] = "cadastrar_usuario"
            
            corpo = json.dumps(payload, ensure_ascii=False)
            r = requests.post(
                WEBHOOK_APPS_SCRIPT_URL,
                data=corpo.encode("utf-8"),
                headers={"Content-Type": "text/plain;charset=utf-8"},
                allow_redirects=True,
                timeout=18
            )
            if r.status_code == 200:
                try:
                    res_json = r.json()
                    status_r = str(res_json.get("status", "")).lower().strip()
                    return status_r in ["sucesso", "success", "ok"]
                except Exception:
                    texto_resp = r.text.lower()
                    return "sucesso" in texto_resp or "success" in texto_resp
            return False
        except Exception as e:
            st.error(f"Erro ao conectar com a planilha: {e}")
            return False
    return False

def gravar_abastecimento_na_planilha(abastecimento_dict: dict) -> bool:
    """Envia o novo registro de abastecimento para a aba 'Controle de combustivel' via Webhook."""
    if WEBHOOK_APPS_SCRIPT_URL:
        try:
            payload = abastecimento_dict.copy()
            payload["acao"] = "cadastrar_abastecimento"
            for chave_excluir in ["data_dt", "Ano", "Mes"]:
                payload.pop(chave_excluir, None)

            corpo = json.dumps(payload, ensure_ascii=False)
            r = requests.post(
                WEBHOOK_APPS_SCRIPT_URL,
                data=corpo.encode("utf-8"),
                headers={"Content-Type": "text/plain;charset=utf-8"},
                allow_redirects=True,
                timeout=18
            )
            if r.status_code == 200:
                try:
                    res_json = r.json()
                    status_r = str(res_json.get("status", "")).lower().strip()
                    return status_r in ["sucesso", "success", "ok"]
                except Exception:
                    texto_resp = r.text.lower()
                    return "sucesso" in texto_resp or "success" in texto_resp
            return False
        except Exception as e:
            st.error(f"Erro ao registrar abastecimento: {e}")
            return False
    return False

@st.cache_data(ttl=45)
def carregar_dados_frota():
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_FROTA}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_FROTA}"
    ]
    for url in urls:
        try:
            df = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df.empty:
                cols_map = {}
                for c in df.columns:
                    c_norm = normalizar_texto(c)
                    if "placa" in c_norm:
                        cols_map["placa"] = c
                    elif "modelo" in c_norm or "veiculo" in c_norm:
                        cols_map["veiculo"] = c
                    elif "tipo" in c_norm or "categoria" in c_norm:
                        cols_map["tipo"] = c
                
                df_out = pd.DataFrame()
                if "placa" in cols_map:
                    df_out["Placa"] = df[cols_map["placa"]].fillna("").astype(str).str.strip().str.upper()
                else:
                    df_out["Placa"] = df.iloc[:, 0].fillna("").astype(str).str.strip().str.upper()
                
                if "veiculo" in cols_map:
                    df_out["Veiculo"] = df[cols_map["veiculo"]].fillna("").astype(str).str.strip()
                else:
                    df_out["Veiculo"] = df.iloc[:, 1].fillna("").astype(str).str.strip() if len(df.columns) > 1 else ""
                
                if "tipo" in cols_map:
                    df_out["Tipo"] = df[cols_map["tipo"]].fillna("Passeio").astype(str).str.strip()
                else:
                    df_out["Tipo"] = "Passeio"
                
                for orig_col in df.columns:
                    if orig_col not in df_out.columns:
                        df_out[orig_col] = df[orig_col]

                return df_out
        except Exception:
            continue
    return pd.DataFrame(columns=["Placa", "Veiculo", "Tipo"])

@st.cache_data(ttl=60)
def carregar_dados_postos():
    """Carrega os postos cadastrados na coluna A da aba 'Posto de Combustivel'."""
    sheet_nome_enc = urllib.parse.quote(NOME_ABA_POSTOS)
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_nome_enc}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&sheet={sheet_nome_enc}"
    ]
    for url in urls:
        try:
            df_postos = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df_postos.empty:
                col_a = df_postos.iloc[:, 0].dropna().astype(str).str.strip().tolist()
                nome_col = str(df_postos.columns[0]).strip()
                
                lista_postos = []
                if nome_col and not nome_col.lower().startswith("unnamed") and normalizar_texto(nome_col) not in ["posto", "postos", "nome"]:
                    lista_postos.append(nome_col)
                
                for p in col_a:
                    if p and p.lower() != "nan" and normalizar_texto(p) not in ["posto", "postos", "nome"]:
                        lista_postos.append(p)
                
                lista_postos = sorted(list(dict.fromkeys(lista_postos)))
                if lista_postos:
                    return lista_postos
        except Exception:
            continue

    # Fallback caso a aba ainda não esteja preenchida
    return ["Posto Shell Central", "Posto Ipiranga", "Posto Petrobras", "Posto Graal", "Auto Posto Master"]

@st.cache_data(ttl=30)
def carregar_dados_viagens():
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_LANCAMENTOS}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_LANCAMENTOS}"
    ]
    df_raw = pd.DataFrame()
    for url in urls:
        try:
            df_temp = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df_temp.empty and len(df_temp.columns) >= 7:
                df_raw = df_temp
                break
        except Exception:
            continue

    if df_raw.empty:
        return pd.DataFrame()

    col_names = [
        "data_inicial", "horario_inicial", "km_inicial",
        "data_final", "horario_final", "km_final",
        "condutor", "destino", "placa", "veiculo",
        "km_percorrido", "data_registro", "rv"
    ]

    df = pd.DataFrame()
    for i, nome in enumerate(col_names):
        if i < len(df_raw.columns):
            df[nome] = df_raw.iloc[:, i].fillna("").astype(str).str.strip()
        else:
            df[nome] = ""

    df["placa"] = df["placa"].str.upper()
    df["condutor"] = df["condutor"].str.strip()
    df["veiculo"] = df["veiculo"].str.strip()
    df["rv"] = df["rv"].str.upper()

    def converter_numero(val):
        try:
            val_limpo = str(val).replace(".", "").replace(",", ".").strip()
            return float(val_limpo) if val_limpo and val_limpo.lower() != "nan" else np.nan
        except Exception:
            return np.nan

    df["km_inicial_num"] = df["km_inicial"].apply(converter_numero)
    df["km_final_num"] = df["km_final"].apply(converter_numero)
    df["km_percorrido_num"] = df["km_percorrido"].apply(converter_numero)

    mascara_recalc = df["km_percorrido_num"].isna() & df["km_inicial_num"].notna() & df["km_final_num"].notna()
    df.loc[mascara_recalc, "km_percorrido_num"] = df.loc[mascara_recalc, "km_final_num"] - df.loc[mascara_recalc, "km_inicial_num"]
    df["km_percorrido_num"] = df["km_percorrido_num"].apply(lambda x: max(x, 0) if pd.notna(x) else np.nan)

    df["data_ini_dt"] = pd.to_datetime(df["data_inicial"], format="%d/%m/%Y", errors="coerce", dayfirst=True)
    df["data_fim_dt"] = pd.to_datetime(df["data_final"], format="%d/%m/%Y", errors="coerce", dayfirst=True)

    def definir_status(row):
        tem_fim = (row["data_final"] != "" and row["data_final"].lower() != "nan") or (pd.notna(row["km_final_num"]) and row["km_final_num"] > 0)
        return "Concluída" if tem_fim else "Em Aberto"

    df["status"] = df.apply(definir_status, axis=1)
    df["rotulo_veiculo"] = df.apply(
        lambda r: f"{r['placa']} - {r['veiculo']}" if r['veiculo'] else r['placa'], axis=1
    )
    return df

@st.cache_data(ttl=20)
def carregar_dados_abastecimento():
    """Carrega o histórico de abastecimentos da aba 'Controle de combustivel' com tolerância a cabeçalhos."""
    sheet_nome_enc = urllib.parse.quote(NOME_ABA_ABASTECIMENTO)
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_nome_enc}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&sheet={sheet_nome_enc}"
    ]
    df_abast = pd.DataFrame()
    for url in urls:
        try:
            df_temp = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df_temp.empty and len(df_temp.columns) >= 2:
                df_abast = df_temp
                break
        except Exception:
            continue

    if "abastecimentos_sessao" not in st.session_state:
        st.session_state["abastecimentos_sessao"] = []

    if st.session_state["abastecimentos_sessao"]:
        df_sess = pd.DataFrame(st.session_state["abastecimentos_sessao"])
        df_abast = pd.concat([df_abast, df_sess], ignore_index=True)

    if not df_abast.empty:
        col_map = {}
        for c in df_abast.columns:
            cn = normalizar_texto(c)
            if "data" in cn:
                col_map["Data"] = c
            elif "placa" in cn:
                col_map["Placa"] = c
            elif "modelo" in cn or "veiculo" in cn:
                if "tipo" not in cn:
                    col_map["Veiculo"] = c
            elif "tipo" in cn or "categoria" in cn:
                col_map["Tipo de Veiculo"] = c
            elif "litro" in cn:
                col_map["Litros"] = c
            elif "valor" in cn or "r$" in cn or "preco" in cn:
                col_map["Valor (R$)"] = c
            elif "combust" in cn:
                col_map["Combustivel"] = c
            elif "motorista" in cn or "condutor" in cn:
                col_map["Motorista"] = c
            elif "posto" in cn:
                col_map["Posto"] = c
            elif "obs" in cn:
                col_map["Observação"] = c

        df_padronizado = pd.DataFrame()
        for padrao, original in col_map.items():
            df_padronizado[padrao] = df_abast[original].fillna("").astype(str).str.strip()
        df_abast = df_padronizado

    colunas_obrigatorias = [
        "Data", "Placa", "Veiculo", "Tipo de Veiculo", 
        "Litros", "Valor (R$)", "Combustivel", "Motorista", "Posto", "Observação"
    ]
    for col in colunas_obrigatorias:
        if col not in df_abast.columns:
            df_abast[col] = ""

    agora = obter_agora_brasil()
    
    df_abast["data_dt"] = pd.to_datetime(df_abast["Data"], format="%d/%m/%Y", errors="coerce", dayfirst=True)
    
    df_abast["Litros"] = pd.to_numeric(
        df_abast["Litros"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce"
    ).fillna(0.0)

    df_abast["Valor (R$)"] = pd.to_numeric(
        df_abast["Valor (R$)"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce"
    ).fillna(0.0)

    df_abast["Ano"] = df_abast["data_dt"].dt.year.fillna(agora.year).astype(int)
    df_abast["Mes"] = df_abast["data_dt"].dt.month.fillna(agora.month).astype(int)

    return df_abast

def obter_viagens_consolidadas():
    df = carregar_dados_viagens().copy()
    if df.empty:
        return df

    if "edicoes_viagens" in st.session_state and st.session_state["edicoes_viagens"]:
        for rv_editado, dados_editados in st.session_state["edicoes_viagens"].items():
            idx_match = df[df["rv"] == rv_editado].index
            if not idx_match.empty:
                for col, valor in dados_editados.items():
                    df.loc[idx_match, col] = valor

                for idx in idx_match:
                    r = df.loc[idx]
                    try:
                        ki = float(str(r["km_inicial"]).replace(".", "").replace(",", "."))
                        df.loc[idx, "km_inicial_num"] = ki
                    except Exception:
                        pass
                    
                    try:
                        kf = float(str(r["km_final"]).replace(".", "").replace(",", "."))
                        df.loc[idx, "km_final_num"] = kf
                    except Exception:
                        pass

                    if pd.notna(df.loc[idx, "km_final_num"]) and pd.notna(df.loc[idx, "km_inicial_num"]):
                        df.loc[idx, "km_percorrido_num"] = max(df.loc[idx, "km_final_num"] - df.loc[idx, "km_inicial_num"], 0)

                    tem_fim = (str(df.loc[idx, "data_final"]).strip() != "" and str(df.loc[idx, "data_final"]).lower() != "nan") or (pd.notna(df.loc[idx, "km_final_num"]) and df.loc[idx, "km_final_num"] > 0)
                    df.loc[idx, "status"] = "Concluída" if tem_fim else "Em Aberto"
    return df

# -------------------------------------------------------------
# 5. TELA DE LOGIN
# -------------------------------------------------------------
def tela_login(df_usuarios):
    caminho_logo = obter_caminho_logotipo()
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if caminho_logo:
            try:
                st.image(Image.open(caminho_logo), width=180)
            except Exception:
                st.markdown("<h2 style='text-align:center;'>☕</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='text-align:center;'>☕</h2>", unsafe_allow_html=True)

        st.markdown("<p style='text-align:center; color:#64748B; font-weight:500; margin-bottom:1rem;'>Acesso ao Painel de Frotas</p>", unsafe_allow_html=True)

        with st.form("form_login_dash"):
            usuario_digitado = st.text_input("Usuário Gestor:", placeholder="Digite seu usuário").strip().lower()
            senha_digitada = st.text_input("Senha:", type="password", placeholder="Digite sua senha (números)").strip()
            btn_login = st.form_submit_button("Acessar Painel")

            if btn_login:
                if df_usuarios.empty:
                    st.error("Lista de usuários inacessível.")
                    return

                usuario_valido = df_usuarios[
                    (df_usuarios["usuario"] == usuario_digitado) & 
                    (df_usuarios["senha"] == senha_digitada)
                ]

                if not usuario_valido.empty:
                    usr_info = usuario_valido.iloc[0]
                    st.session_state["dash_autenticado"] = True
                    st.session_state["dash_usuario"] = usuario_digitado
                    st.session_state["dash_nome"] = usr_info["nome"]
                    st.session_state["dash_acesso"] = usr_info.get("acesso", "Geral")
                    st.query_params["u"] = usuario_digitado
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

# -------------------------------------------------------------
# 6. APLICATIVO PRINCIPAL (SISTEMA CORPORATIVO)
# -------------------------------------------------------------
def main():
    df_usuarios = obter_usuarios_ativos()

    if not st.session_state.get("dash_autenticado", False):
        usuario_url = st.query_params.get("u", None)
        if usuario_url and not df_usuarios.empty:
            usuario_url = str(usuario_url).strip().lower()
            usuario_valido = df_usuarios[df_usuarios["usuario"] == usuario_url]
            if not usuario_valido.empty:
                usr_info = usuario_valido.iloc[0]
                st.session_state["dash_autenticado"] = True
                st.session_state["dash_usuario"] = usuario_url
                st.session_state["dash_nome"] = usr_info["nome"]
                st.session_state["dash_acesso"] = usr_info.get("acesso", "Geral")

    if not st.session_state.get("dash_autenticado", False):
        tela_login(df_usuarios)
        return

    nome_gestor = st.session_state.get("dash_nome", "Gestor")
    acesso_gestor = st.session_state.get("dash_acesso", "Geral")

    itens_menu = [
        {"id": "dash", "label": "Dashboard Geral", "icon": "📊"},
        {"id": "abastecimento", "label": "Abastecimento", "icon": "⛽"},
        {"id": "consultas", "label": "Consultas & Filtros", "icon": "🔍"},
        {"id": "editar", "label": "Editar Viagens", "icon": "✍️"},
        {"id": "usuarios", "label": "Gestão de Usuários", "icon": "👥"}
    ]

    if "pagina_selecionada_id" not in st.session_state:
        st.session_state["pagina_selecionada_id"] = "dash"

    # =========================================================================
    # SIDEBAR: MENU LATERAL
    # =========================================================================
    with st.sidebar:
        st.markdown("""
            <div style="margin-bottom: 1.2rem; padding-bottom: 0.8rem; border-bottom: 1px solid #1E293B;">
                <div class="sidebar-brand-title">Painel de Frotas</div>
                <div class="sidebar-brand-sub">Master Café Gestão</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="user-card">
                <p class="user-card-name">👤 {nome_gestor}</p>
                <p class="user-card-role">Acesso: {acesso_gestor}</p>
                <div class="user-card-time">🕒 {obter_agora_brasil().strftime('%d/%m/%Y • %H:%M')}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px;'>Navegação</p>", unsafe_allow_html=True)

        for item in itens_menu:
            is_active = (st.session_state["pagina_selecionada_id"] == item["id"])
            prefix = "▶ " if is_active else ""
            st.markdown(f'<div class="{"nav-active" if is_active else ""}">', unsafe_allow_html=True)
            if st.button(f"{prefix}{item['icon']}  {item['label']}", key=f"nav_btn_{item['id']}"):
                st.session_state["pagina_selecionada_id"] = item["id"]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px;'>Sistema</p>", unsafe_allow_html=True)

        st.markdown('<div class="btn-sync">', unsafe_allow_html=True)
        if st.button("⟳  Sincronizar Dados", key="side_btn_sync"):
            st.cache_data.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-exit">', unsafe_allow_html=True)
        if st.button("→  Sair do Painel", key="side_btn_exit"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÁREA PRINCIPAL: BANNER TOPO
    # =========================================================================
    df_base = obter_viagens_consolidadas()
    df_frota = carregar_dados_frota()
    df_abastecimento = carregar_dados_abastecimento()
    lista_postos_combustivel = carregar_dados_postos()

    if df_base.empty:
        st.warning("Nenhum registro de viagem encontrado na planilha.")
        return

    hoje_brasil = obter_agora_brasil().date()
    pagina_atual = st.session_state["pagina_selecionada_id"]

    titulos_paginas = {
        "dash": ("Dashboard Geral", "Indicadores operacionais consolidados e consumo de combustível"),
        "abastecimento": ("Controle de Abastecimento", "Lançamento oficial de despesas e controle de combustível da frota"),
        "consultas": ("Consultas & Relatórios", "Pesquise históricos com múltiplos filtros e exporte extratos"),
        "editar": ("Edição & Fechamento de Viagens", "Retificação de dados de saída e encerramento de percursos"),
        "usuarios": ("Gestão de Usuários", "Controle de credenciais, permissões de frota e cadastro sincronizado")
    }

    titulo_pg, sub_pg = titulos_paginas.get(pagina_atual, ("Painel de Frotas", "Master Café Gestão"))

    col_banner_logo, col_banner_txt = st.columns([0.16, 0.84], gap="medium", vertical_alignment="center")
    caminho_logo = obter_caminho_logotipo()

    with col_banner_logo:
        if caminho_logo:
            try:
                st.image(Image.open(caminho_logo), width=110)
            except Exception:
                st.markdown("<h1 style='margin:0; font-size:2.8rem;'>☕</h1>", unsafe_allow_html=True)
        else:
            st.markdown("<h1 style='margin:0; font-size:2.8rem;'>☕</h1>", unsafe_allow_html=True)

    with col_banner_txt:
        st.markdown(f"""
            <div style="line-height:1.25;">
                <h3 class="main-header-title">{titulo_pg}</h3>
                <p class="main-header-sub">{sub_pg}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 10px 0 16px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # =========================================================================
    # PÁGINA 1: DASHBOARD
    # =========================================================================
    if pagina_atual == "dash":
        total_viagens = len(df_base)
        viagens_abertas_df = df_base[df_base["status"] == "Em Aberto"]
        total_em_aberto = len(viagens_abertas_df)

        viagens_concluidas = df_base[df_base["status"] == "Concluída"]
        total_km_rodado = viagens_concluidas["km_percorrido_num"].sum()
        media_km_geral = viagens_concluidas["km_percorrido_num"].mean() if not viagens_concluidas.empty else 0
        total_concluidas = len(viagens_concluidas)

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        with kpi1:
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 4px solid #2563EB;">
                    <p class="kpi-title">Total de Viagens</p>
                    <p class="kpi-value">{total_viagens}</p>
                    <p class="kpi-caption">Histórico acumulado</p>
                </div>
            """, unsafe_allow_html=True)

        with kpi2:
            cor_aberto = "#F59E0B" if total_em_aberto > 0 else "#10B981"
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 4px solid {cor_aberto};">
                    <p class="kpi-title">Veículos em Aberto</p>
                    <p class="kpi-value" style="color: {'#B45309' if total_em_aberto > 0 else '#065F46'};">{total_em_aberto}</p>
                    <p class="kpi-caption">Em trânsito agora</p>
                </div>
            """, unsafe_allow_html=True)

        with kpi3:
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 4px solid #10B981;">
                    <p class="kpi-title">Km Total Rodado</p>
                    <p class="kpi-value">{total_km_rodado:,.0f} <span style="font-size: 0.85rem; font-weight: 500;">km</span></p>
                    <p class="kpi-caption">Viagens concluídas</p>
                </div>
            """, unsafe_allow_html=True)

        with kpi4:
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 4px solid #6366F1;">
                    <p class="kpi-title">Média Km / Viagem</p>
                    <p class="kpi-value">{media_km_geral:,.1f} <span style="font-size: 0.85rem; font-weight: 500;">km</span></p>
                    <p class="kpi-caption">Média por percurso</p>
                </div>
            """, unsafe_allow_html=True)

        with kpi5:
            perc_conc = (total_concluidas / total_viagens * 100) if total_viagens > 0 else 0
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 4px solid #0EA5E9;">
                    <p class="kpi-title">Viagens Concluídas</p>
                    <p class="kpi-value">{total_concluidas}</p>
                    <p class="kpi-caption">{perc_conc:.0f}% de finalização</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        st.markdown("### ◷ **Veículos em Aberto (Atualmente em Trânsito)**")
        if viagens_abertas_df.empty:
            st.success("✔ **Todos os veículos estão no pátio.** Nenhuma viagem em aberto no momento.")
        else:
            grid_abertos = st.columns(min(len(viagens_abertas_df), 3))
            for idx, (_, v_aberta) in enumerate(viagens_abertas_df.iterrows()):
                col_target = grid_abertos[idx % 3]
                dest_aberta = str(v_aberta['destino']).strip() if v_aberta.get('destino') and str(v_aberta['destino']).lower() != 'nan' else 'Não especificado'
                card_aberto_html = (
                    f'<div style="background: #FFFBEB; border: 1px solid #FDE68A; border-left: 4px solid #F59E0B; padding: 12px 14px; border-radius: 8px; margin-bottom: 6px;">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">'
                    f'<span style="font-weight: 800; font-size: 1rem; color: #92400E;">🚗 {v_aberta["placa"]}</span>'
                    f'<span class="badge-open">EM TRÂNSITO</span>'
                    f'</div>'
                    f'<div style="font-size: 0.85rem; color: #78350F; font-weight: 600;">{v_aberta["veiculo"]}</div>'
                    f'<hr style="margin: 6px 0; border: none; border-top: 1px solid #FEE382;">'
                    f'<div style="font-size: 0.82rem; color: #451A03; line-height: 1.4;">'
                    f'<b>Condutor:</b> {v_aberta["condutor"]}<br>'
                    f'<b>Saída:</b> {v_aberta["data_inicial"]} às {v_aberta["horario_inicial"]}<br>'
                    f'<b>Km Saída:</b> {v_aberta["km_inicial"]} km<br>'
                    f'<b>Destino:</b> {dest_aberta}<br>'
                    f'<b>RV:</b> <code style="background: #FEF3C7; color: #92400E; padding: 1px 4px; border-radius: 4px;">{v_aberta["rv"]}</code>'
                    f'</div>'
                    f'</div>'
                )
                with col_target:
                    st.markdown(card_aberto_html, unsafe_allow_html=True)
                    if st.button(f"✎ Editar/Baixar ({v_aberta['rv']})", key=f"btn_quick_{v_aberta['rv']}"):
                        st.session_state["rv_para_editar"] = v_aberta["rv"]
                        st.session_state["pagina_selecionada_id"] = "editar"
                        st.rerun()

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        st.markdown("### 📊 **Quilometragem Acumulada da Frota**")
        g_col1, g_col2 = st.columns(2)

        with g_col1:
            st.markdown("##### ◈ **Km Total Acumulado por Veículo**")
            if not viagens_concluidas.empty:
                df_acumulado_veiculo = (
                    viagens_concluidas.groupby("placa")["km_percorrido_num"]
                    .sum()
                    .reset_index()
                    .rename(columns={"km_percorrido_num": "Km_Total", "placa": "Placa"})
                    .sort_values(by="Km_Total", ascending=False)
                )

                df_acumulado_veiculo["rotulo_km"] = df_acumulado_veiculo["Km_Total"].apply(lambda v: f"{v:,.0f} km")

                bars1 = alt.Chart(df_acumulado_veiculo).mark_bar(
                    color="#2563EB", cornerRadiusTopLeft=6, cornerRadiusTopRight=6
                ).encode(
                    x=alt.X("Placa:N", sort="-y", title="Placa do Veículo", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Km_Total:Q", title="Km Total Acumulado"),
                    tooltip=[alt.Tooltip("Placa:N", title="Placa"), alt.Tooltip("rotulo_km:N", title="Km Total")]
                )

                text1 = alt.Chart(df_acumulado_veiculo).mark_text(
                    align="center", baseline="bottom", dy=-4, fontSize=11, fontWeight=700, color="#1E40AF"
                ).encode(
                    x=alt.X("Placa:N", sort="-y"),
                    y=alt.Y("Km_Total:Q"),
                    text="rotulo_km:N"
                )

                grafico_km_total = (bars1 + text1).properties(height=300)
                st.altair_chart(grafico_km_total, use_container_width=True)
            else:
                st.caption("Sem dados suficientes para calcular valores acumulados.")

        with g_col2:
            st.markdown("##### ◈ **Média de Km por Veículo**")
            if not viagens_concluidas.empty:
                df_media_veiculo = (
                    viagens_concluidas.groupby("placa")["km_percorrido_num"]
                    .agg(Media_Km="mean")
                    .reset_index()
                    .rename(columns={"placa": "Placa", "Media_Km": "Media_Km"})
                    .sort_values(by="Media_Km", ascending=False)
                )

                df_media_veiculo["rotulo_media"] = df_media_veiculo["Media_Km"].apply(lambda v: f"{v:,.1f} km")

                bars2 = alt.Chart(df_media_veiculo).mark_bar(
                    color="#059669", cornerRadiusTopLeft=6, cornerRadiusTopRight=6
                ).encode(
                    x=alt.X("Placa:N", sort="-y", title="Placa do Veículo", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Media_Km:Q", title="Média Km por Viagem"),
                    tooltip=[alt.Tooltip("Placa:N", title="Placa"), alt.Tooltip("rotulo_media:N", title="Média Km")]
                )

                text2 = alt.Chart(df_media_veiculo).mark_text(
                    align="center", baseline="bottom", dy=-4, fontSize=11, fontWeight=700, color="#064E3B"
                ).encode(
                    x=alt.X("Placa:N", sort="-y"),
                    y=alt.Y("Media_Km:Q"),
                    text="rotulo_media:N"
                )

                grafico_media_km = (bars2 + text2).properties(height=300)
                st.altair_chart(grafico_media_km, use_container_width=True)
            else:
                st.caption("Sem dados suficientes para calcular médias.")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # SEÇÃO DE CONSUMO POR VEÍCULO (ABAIXO DA QUILOMETRAGEM ACUMULADA)
        # ---------------------------------------------------------------------
        st.markdown("### ⛽ **Consumo de Combustível por Veículo**")
        st.markdown("<p style='font-size:0.83rem; color:#64748B;'>Dados obtidos da aba <b>Controle de combustivel</b> com filtros dinâmicos e destaque no ano e mês vigentes.</p>", unsafe_allow_html=True)

        ano_atual = hoje_brasil.year
        mes_atual = hoje_brasil.month

        anos_disponiveis = sorted(list(set(df_abastecimento["Ano"].dropna().unique().tolist() + [ano_atual])), reverse=True)
        idx_ano_default = anos_disponiveis.index(ano_atual) if ano_atual in anos_disponiveis else 0

        meses_nomes = {
            1: "01 - Janeiro", 2: "02 - Fevereiro", 3: "03 - Março", 4: "04 - Abril",
            5: "05 - Maio", 6: "06 - Junho", 7: "07 - Julho", 8: "08 - Agosto",
            9: "09 - Setembro", 10: "10 - Outubro", 11: "11 - Novembro", 12: "12 - Dezembro"
        }

        col_filtro_ano, col_filtro_mes, col_filtro_badge = st.columns([1.5, 2, 2.5], vertical_alignment="bottom")

        with col_filtro_ano:
            ano_sel = st.selectbox("Selecione o Ano:", options=anos_disponiveis, index=idx_ano_default, key="dash_filtro_ano_comb")

        with col_filtro_mes:
            opcoes_mes = ["Todos os Meses"] + [meses_nomes[m] for m in range(1, 13)]
            idx_mes_default = mes_atual
            mes_sel = st.selectbox("Selecione o Mês:", options=opcoes_mes, index=idx_mes_default, key="dash_filtro_mes_comb")

        with col_filtro_badge:
            is_destaque_atual = (ano_sel == ano_atual and mes_sel == meses_nomes.get(mes_atual, ""))
            if is_destaque_atual:
                st.markdown(
                    f"""<div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #2563EB; padding: 6px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; color: #1E40AF; margin-bottom: 4px;">
                    ⭐ PERÍODO VIGENTE EM DESTAQUE: {meses_nomes[mes_atual].split(' - ')[1].upper()} / {ano_atual}
                    </div>""", 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""<div style="background: #F1F5F9; border: 1px solid #CBD5E1; padding: 6px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; color: #475569; margin-bottom: 4px;">
                    Visualizando filtro histórico selecionado
                    </div>""", 
                    unsafe_allow_html=True
                )

        df_abast_filtrado = df_abastecimento[df_abastecimento["Ano"] == ano_sel].copy()
        if mes_sel != "Todos os Meses":
            num_mes_sel = int(mes_sel.split(" - ")[0])
            df_abast_filtrado = df_abast_filtrado[df_abast_filtrado["Mes"] == num_mes_sel]

        df_abast_filtrado = df_abast_filtrado[df_abast_filtrado["Placa"] != ""]

        cg_col1, cg_col2 = st.columns(2)

        with cg_col1:
            st.markdown("##### ◈ **Volume Consumido (Litros) por Veículo**")
            if not df_abast_filtrado.empty and df_abast_filtrado["Litros"].sum() > 0:
                df_litros_veiculo = (
                    df_abast_filtrado.groupby(["Placa", "Veiculo"])["Litros"]
                    .sum()
                    .reset_index()
                    .sort_values(by="Litros", ascending=False)
                )
                df_litros_veiculo["rotulo_litros"] = df_litros_veiculo["Litros"].apply(lambda v: f"{v:,.1f} L")
                cor_litros = "#2563EB" if is_destaque_atual else "#475569"

                bars_l = alt.Chart(df_litros_veiculo).mark_bar(
                    color=cor_litros, cornerRadiusTopLeft=6, cornerRadiusTopRight=6
                ).encode(
                    x=alt.X("Placa:N", sort="-y", title="Placa do Veículo", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Litros:Q", title="Volume Total (Litros)"),
                    tooltip=[
                        alt.Tooltip("Placa:N", title="Placa"),
                        alt.Tooltip("Veiculo:N", title="Veículo"),
                        alt.Tooltip("rotulo_litros:N", title="Consumo")
                    ]
                )

                text_l = alt.Chart(df_litros_veiculo).mark_text(
                    align="center", baseline="bottom", dy=-4, fontSize=11, fontWeight=700, color="#1E3A8A"
                ).encode(
                    x=alt.X("Placa:N", sort="-y"),
                    y=alt.Y("Litros:Q"),
                    text="rotulo_litros:N"
                )

                st.altair_chart((bars_l + text_l).properties(height=300), use_container_width=True)
            else:
                st.info("Nenhum dado de abastecimento registrado na aba 'Controle de combustivel' para o período filtrado.")

        with cg_col2:
            st.markdown("##### ◈ **Gasto Total em Combustível (R$) por Veículo**")
            if not df_abast_filtrado.empty and df_abast_filtrado["Valor (R$)"].sum() > 0:
                df_valor_veiculo = (
                    df_abast_filtrado.groupby(["Placa", "Combustivel"])["Valor (R$)"]
                    .sum()
                    .reset_index()
                    .sort_values(by="Valor (R$)", ascending=False)
                )
                df_valor_veiculo["rotulo_reais"] = df_valor_veiculo["Valor (R$)"].apply(lambda v: f"R$ {v:,.2f}")

                bars_v = alt.Chart(df_valor_veiculo).mark_bar(
                    cornerRadiusTopLeft=5, cornerRadiusTopRight=5
                ).encode(
                    x=alt.X("Placa:N", title="Placa do Veículo", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Valor (R$):Q", title="Gasto Total (R$)"),
                    color=alt.Color("Combustivel:N", scale=alt.Scale(range=["#059669", "#D97706", "#DC2626"]), title="Combustível"),
                    tooltip=[
                        alt.Tooltip("Placa:N", title="Placa"),
                        alt.Tooltip("Combustivel:N", title="Combustível"),
                        alt.Tooltip("rotulo_reais:N", title="Total Gasto")
                    ]
                )

                st.altair_chart(bars_v.properties(height=300), use_container_width=True)
            else:
                st.info("Nenhum custo financeiro registrado na aba 'Controle de combustivel' para o período filtrado.")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        st.markdown("### 📅 **Carros Utilizados no Dia**")
        c_dia_col1, c_dia_col2 = st.columns([1.5, 4])
        with c_dia_col1:
            dia_selecionado = st.date_input(
                "Filtrar data de operação:",
                value=hoje_brasil,
                format="DD/MM/YYYY",
                key="filtro_dia_atual"
            )
        with c_dia_col2:
            st.caption(f"Exibindo deslocamentos com saída registrada em **{dia_selecionado.strftime('%d/%m/%Y')}**.")

        df_carros_dia = df_base[df_base["data_ini_dt"].dt.date == dia_selecionado].copy()

        if df_carros_dia.empty:
            st.info(f"ℹ️ Nenhum registro de veículo em atividade na data de **{dia_selecionado.strftime('%d/%m/%Y')}**.")
        else:
            qtd_carros_dia = df_carros_dia["placa"].nunique()
            km_dia_total = df_carros_dia[df_carros_dia["status"] == "Concluída"]["km_percorrido_num"].sum()

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Veículos Ativados", f"{qtd_carros_dia}")
            with m2:
                st.metric("Viagens Registradas", f"{len(df_carros_dia)}")
            with m3:
                st.metric("Km Total no Dia", f"{km_dia_total:,.0f} km")

            df_cards_dia = df_carros_dia.sort_values(by=["status", "horario_inicial"], ascending=[True, False])
            num_cols = min(len(df_cards_dia), 3)
            grid_dia = st.columns(num_cols)

            for idx, (_, v_dia) in enumerate(df_cards_dia.iterrows()):
                col_target = grid_dia[idx % num_cols]
                em_aberto = (v_dia["status"] == "Em Aberto")

                card_bg = "#FFFBEB" if em_aberto else "#F8FAFC"
                card_border = "#FDE68A" if em_aberto else "#E2E8F0"
                card_border_left = "#F59E0B" if em_aberto else "#10B981"
                badge_html = '<span class="badge-open">EM TRÂNSITO</span>' if em_aberto else '<span class="badge-done">CONCLUÍDA</span>'
                title_color = "#92400E" if em_aberto else "#0F172A"
                sub_color = "#78350F" if em_aberto else "#475569"
                divider_color = "#FEE382" if em_aberto else "#E2E8F0"
                text_color = "#451A03" if em_aberto else "#1E293B"
                rv_bg = "#FEF3C7" if em_aberto else "#DEF7EC"
                rv_color = "#92400E" if em_aberto else "#03543F"

                km_sai_txt = f"{v_dia['km_inicial_num']:,.0f} km" if pd.notna(v_dia.get('km_inicial_num')) else (f"{v_dia['km_inicial']} km" if v_dia['km_inicial'] else "Não inf.")
                km_ret_txt = f"{v_dia['km_final_num']:,.0f} km" if pd.notna(v_dia.get('km_final_num')) else (f"{v_dia['km_final']} km" if v_dia['km_final'] else "—")
                km_rod_txt = f"{v_dia['km_percorrido_num']:,.0f} km" if pd.notna(v_dia.get('km_percorrido_num')) else "—"
                hora_ret_txt = f"{v_dia['data_final']} às {v_dia['horario_final']}" if v_dia.get('horario_final') else "Em trânsito"
                destino_txt = str(v_dia['destino']).strip() if v_dia.get('destino') and str(v_dia['destino']).lower() != "nan" else "Não especificado"
                rv_txt = str(v_dia['rv']).strip()

                bloco_retorno = ""
                if not em_aberto:
                    bloco_retorno = f'<b>Retorno:</b> {hora_ret_txt}<br><b>Km Retorno:</b> {km_ret_txt}<br><b>Km Rodado:</b> <span style="font-weight: 700; color: #047857;">{km_rod_txt}</span><br>'

                card_html = (
                    f'<div style="background: {card_bg}; border: 1px solid {card_border}; border-left: 4px solid {card_border_left}; padding: 12px 14px; border-radius: 8px; margin-bottom: 8px;">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">'
                    f'<span style="font-weight: 800; font-size: 1rem; color: {title_color};">🚗 {v_dia["placa"]}</span>'
                    f'{badge_html}'
                    f'</div>'
                    f'<div style="font-size: 0.85rem; color: {sub_color}; font-weight: 600;">{v_dia["veiculo"]}</div>'
                    f'<hr style="margin: 6px 0; border: none; border-top: 1px solid {divider_color};">'
                    f'<div style="font-size: 0.82rem; color: {text_color}; line-height: 1.4;">'
                    f'<b>Condutor:</b> {v_dia["condutor"]}<br>'
                    f'<b>Saída:</b> {v_dia["data_inicial"]} às {v_dia["horario_inicial"]}<br>'
                    f'<b>Km Saída:</b> {km_sai_txt}<br>'
                    f'{bloco_retorno}'
                    f'<b>Destino:</b> {destino_txt}<br>'
                    f'<b>RV:</b> <code style="background: {rv_bg}; color: {rv_color}; padding: 1px 4px; border-radius: 4px;">{rv_txt}</code>'
                    f'</div>'
                    f'</div>'
                )
                with col_target:
                    st.markdown(card_html, unsafe_allow_html=True)

    # =========================================================================
    # PÁGINA 2: CONTROLE DE ABASTECIMENTO (FORMULÁRIO E VÍNCULO AUTOMÁTICO)
    # =========================================================================
    elif pagina_atual == "abastecimento":
        tab_form_abast, tab_historico_abast = st.tabs(["⛽ Novo Lançamento", "📋 Histórico de Abastecimentos"])

        lista_placas = []
        mapa_veiculos = {}
        mapa_tipos = {}

        if not df_frota.empty and "Placa" in df_frota.columns:
            for _, f_row in df_frota.iterrows():
                plc = str(f_row["Placa"]).strip().upper()
                if plc and plc != "NAN":
                    lista_placas.append(plc)
                    mapa_veiculos[plc] = str(f_row.get("Veiculo", f_row.get("Modelo", ""))).strip()
                    mapa_tipos[plc] = str(f_row.get("Tipo", f_row.get("Categoria", "Passeio"))).strip()
        else:
            lista_placas = sorted(list(df_base["placa"].unique()))
            for plc in lista_placas:
                match = df_base[df_base["placa"] == plc]
                mapa_veiculos[plc] = match.iloc[0]["veiculo"] if not match.empty else ""
                mapa_tipos[plc] = "Passeio"

        if not lista_placas:
            lista_placas = ["PADRAO"]

        with tab_form_abast:
            st.markdown("<p style='font-size:0.85rem; color:#64748B;'>Preencha os dados do abastecimento. O veículo e seu tipo são vinculados automaticamente pela placa selecionada.</p>", unsafe_allow_html=True)

            if "reset_abast_key" not in st.session_state:
                st.session_state["reset_abast_key"] = 0

            reset_abast = st.session_state["reset_abast_key"]

            c_placa, c_vinc1, c_vinc2 = st.columns(3)
            with c_placa:
                placa_selecionada = st.selectbox(
                    "Placa do Veículo (Pré-lista da Frota):",
                    options=lista_placas,
                    key=f"placa_abast_{reset_abast}"
                )

            veiculo_vinculado = mapa_veiculos.get(placa_selecionada, "")
            tipo_vinculado = mapa_tipos.get(placa_selecionada, "Passeio")

            with c_vinc1:
                st.text_input(
                    "Veículo (Vinculado à Placa):",
                    value=veiculo_vinculado,
                    disabled=True,
                    help="Identificação vinculada automaticamente à placa."
                )

            with c_vinc2:
                st.text_input(
                    "Tipo de Veículo (Vinculado à Placa):",
                    value=tipo_vinculado,
                    disabled=True,
                    help="Categoria / tipo do veículo cadastrado na frota."
                )

            with st.form(f"form_abastecimento_{reset_abast}"):
                c_data, c_comb, c_motorista = st.columns(3)
                with c_data:
                    data_abast = st.date_input("Data do Abastecimento:", value=hoje_brasil, format="DD/MM/YYYY")
                with c_comb:
                    combustivel_sel = st.selectbox("Combustível:", options=["Alcool", "Gasolina", "Diesel"])
                with c_motorista:
                    lista_motoristas = sorted(list(df_usuarios["nome"].unique()))
                    idx_m = 0
                    if nome_gestor in lista_motoristas:
                        idx_m = lista_motoristas.index(nome_gestor)
                    motorista_sel = st.selectbox("Motorista (Pré-lista de Usuários):", options=lista_motoristas, index=idx_m)

                c_litros, c_reais, c_posto = st.columns(3)
                with c_litros:
                    litros_abast = st.number_input("Litros Abastecidos:", min_value=0.0, step=0.1, format="%.2f")
                with c_reais:
                    reais_abast = st.number_input("Valor Total Pago (R$):", min_value=0.0, step=1.0, format="%.2f")
                with c_posto:
                    posto_abast = st.selectbox(
                        "Posto de Abastecimento:",
                        options=lista_postos_combustivel,
                        help="Pré-lista carregada da aba 'Posto de Combustivel' (Coluna A)."
                    )

                obs_abast = st.text_area("Observação:", placeholder="Ex: Abastecimento de rota emergencial, nota fiscal anexada.", height=70).strip()

                btn_salvar_abast = st.form_submit_button("⛽ Salvar Abastecimento")

                if btn_salvar_abast:
                    if litros_abast <= 0:
                        st.error("Informe a quantidade de litros abastecida.")
                    elif reais_abast <= 0:
                        st.error("Informe o valor total em R$.")
                    elif not posto_abast:
                        st.error("Selecione o posto de abastecimento.")
                    else:
                        novo_abast_dict = {
                            "Data": data_abast.strftime("%d/%m/%Y"),
                            "Placa": placa_selecionada,
                            "Veiculo": veiculo_vinculado,
                            "Tipo de Veiculo": tipo_vinculado,
                            "Litros": float(litros_abast),
                            "Valor (R$)": float(reais_abast),
                            "Combustivel": combustivel_sel,
                            "Motorista": motorista_sel,
                            "Posto": posto_abast,
                            "Observação": obs_abast,
                            "data_dt": pd.to_datetime(data_abast),
                            "Ano": int(data_abast.year),
                            "Mes": int(data_abast.month)
                        }

                        gravou = gravar_abastecimento_na_planilha(novo_abast_dict)

                        if "abastecimentos_sessao" not in st.session_state:
                            st.session_state["abastecimentos_sessao"] = []
                        st.session_state["abastecimentos_sessao"].append(novo_abast_dict)

                        st.session_state["reset_abast_key"] += 1
                        st.cache_data.clear()

                        if gravou:
                            st.success(f"✔ Abastecimento do veículo **{placa_selecionada}** registrado na aba '{NOME_ABA_ABASTECIMENTO}' com sucesso!")
                        else:
                            st.success(f"✔ Abastecimento do veículo **{placa_selecionada}** gravado com sucesso no painel!")
                        st.rerun()

        with tab_historico_abast:
            st.markdown("##### 📋 Extrato Geral de Abastecimentos (Controle de combustivel)")
            df_abast_valido = df_abastecimento[df_abastecimento["Placa"] != ""].copy()
            if df_abast_valido.empty:
                st.info("Nenhum lançamento de abastecimento localizado na aba 'Controle de combustivel'.")
            else:
                colunas_exibir = ["Data", "Placa", "Veiculo", "Tipo de Veiculo", "Combustivel", "Litros", "Valor (R$)", "Motorista", "Posto", "Observação"]
                cols_presentes = [c for c in colunas_exibir if c in df_abast_valido.columns]
                
                df_tab = df_abast_valido[cols_presentes].copy()
                st.dataframe(
                    df_tab,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Litros": st.column_config.NumberColumn("Litros", format="%.2f L"),
                        "Valor (R$)": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f")
                    }
                )

                csv_abast = df_tab.to_csv(index=False, sep=";").encode("utf-8-sig")
                st.download_button(
                    label="📥 Baixar Extrato de Abastecimentos (CSV)",
                    data=csv_abast,
                    file_name=f"abastecimentos_frota_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )

    # =========================================================================
    # PÁGINA 3: CONSULTAS & FILTROS AVANÇADOS
    # =========================================================================
    elif pagina_atual == "consultas":
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.90rem; font-weight:700; color:#0F172A; margin-bottom:6px;'>◈ Parâmetros de Pesquisa</p>", unsafe_allow_html=True)
        
        f_col1, f_col2, f_col3, f_col4 = st.columns([1.2, 1.8, 1.8, 1.4])

        with f_col1:
            status_opcoes = ["Todos", "Em Aberto", "Concluída"]
            status_sel = st.selectbox("Status da Viagem:", status_opcoes)

        with f_col2:
            lista_veiculos = sorted([v for v in df_base["rotulo_veiculo"].unique() if v])
            veiculos_sel = st.multiselect("Veículo(s):", options=lista_veiculos, placeholder="Todos...")

        with f_col3:
            lista_condutores = sorted([c for c in df_base["condutor"].unique() if c and c.lower() != "nan"])
            condutores_sel = st.multiselect("Condutor(es):", options=lista_condutores, placeholder="Todos...")

        with f_col4:
            datas_validas = df_base["data_ini_dt"].dropna()
            min_d = datas_validas.min().date() if not datas_validas.empty else date.today() - timedelta(days=30)
            max_d = datas_validas.max().date() if not datas_validas.empty else date.today()
            periodo_sel = st.date_input("Período de Saída:", value=(min_d, max_d), format="DD/MM/YYYY")
        st.markdown('</div>', unsafe_allow_html=True)

        df_consulta = df_base.copy()

        if status_sel != "Todos":
            df_consulta = df_consulta[df_consulta["status"] == status_sel]

        if veiculos_sel:
            df_consulta = df_consulta[df_consulta["rotulo_veiculo"].isin(veiculos_sel)]

        if condutores_sel:
            df_consulta = df_consulta[df_consulta["condutor"].isin(condutores_sel)]

        if isinstance(periodo_sel, (tuple, list)) and len(periodo_sel) == 2:
            d_inicio, d_fim = periodo_sel
            df_consulta = df_consulta[
                (df_consulta["data_ini_dt"].dt.date >= d_inicio) & 
                (df_consulta["data_ini_dt"].dt.date <= d_fim)
            ]

        qtd_res = len(df_consulta)
        df_conc_consulta = df_consulta[df_consulta["status"] == "Concluída"]
        km_res = df_conc_consulta["km_percorrido_num"].sum()
        media_km_res = df_conc_consulta["km_percorrido_num"].mean() if not df_conc_consulta.empty else 0

        r_col1, r_col2, r_col3 = st.columns([1.2, 1.4, 1.4])
        with r_col1:
            st.metric("Viagens Localizadas", f"{qtd_res}")
        with r_col2:
            st.metric("Km Total no Filtro", f"{km_res:,.0f} km")
        with r_col3:
            st.metric("Média Km / Viagem", f"{media_km_res:,.1f} km")

        st.markdown("#### 📋 **Extrato Detalhado de Viagens**")

        if df_consulta.empty:
            st.info("Nenhuma viagem localizada com a combinação de filtros selecionada.")
        else:
            df_grid = df_consulta[[
                "rv", "status", "placa", "veiculo", "condutor",
                "data_inicial", "horario_inicial", "km_inicial_num",
                "data_final", "horario_final", "km_final_num", "km_percorrido_num", "destino"
            ]].copy()

            df_grid.columns = [
                "Registro (RV)", "Status", "Placa", "Veículo", "Condutor",
                "Data Saída", "Hora Saída", "Km Saída",
                "Data Retorno", "Hora Retorno", "Km Retorno", "Km Rodado", "Destino"
            ]

            df_grid = df_grid.sort_values(by=["Status", "Data Saída"], ascending=[True, False])

            st.dataframe(
                df_grid,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Registro (RV)": st.column_config.TextColumn("Registro (RV)", width="medium"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Km Saída": st.column_config.NumberColumn("Km Saída", format="%d km"),
                    "Km Retorno": st.column_config.NumberColumn("Km Retorno", format="%d km"),
                    "Km Rodado": st.column_config.NumberColumn("Km Rodado", format="%d km"),
                }
            )

            csv_data = df_grid.to_csv(index=False, sep=";").encode("utf-8-sig")
            st.download_button(
                label="📥 Exportar Dados Filtrados (CSV / Excel)",
                data=csv_data,
                file_name=f"relatorio_frota_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

        if not df_conc_consulta.empty:
            with st.expander("◈ **Visualizar Matriz Cruzada: Km Total por Veículo e por Condutor**"):
                pivot_km = df_conc_consulta.pivot_table(
                    index="veiculo",
                    columns="condutor",
                    values="km_percorrido_num",
                    aggfunc="sum",
                    fill_value=0
                )
                st.dataframe(pivot_km.style.format("{:,.0f} km"), use_container_width=True)

    # =========================================================================
    # PÁGINA 4: EDITAR VIAGENS
    # =========================================================================
    elif pagina_atual == "editar":
        if "edicoes_viagens" not in st.session_state:
            st.session_state["edicoes_viagens"] = {}

        viagens_em_aberto = df_base[df_base["status"] == "Em Aberto"].copy()

        opcoes_rv = list(viagens_em_aberto["rv"].unique())
        if not opcoes_rv:
            st.info("ℹ️ Não existem viagens com status **Em Aberto** no momento. Selecione uma viagem concluída para retificação:")
            opcoes_rv = list(df_base["rv"].unique())

        rv_padrao = st.session_state.get("rv_para_editar", opcoes_rv[0] if opcoes_rv else "")
        idx_padrao = opcoes_rv.index(rv_padrao) if rv_padrao in opcoes_rv else 0

        c_sel_rv, c_info_rv = st.columns([2, 3])
        with c_sel_rv:
            rv_selecionado = st.selectbox("Registro de Viagem (RV):", options=opcoes_rv, index=idx_padrao)
        
        linha_viagem = df_base[df_base["rv"] == rv_selecionado]

        if not linha_viagem.empty:
            dados_v = linha_viagem.iloc[0]
            with c_info_rv:
                st.markdown(f"""
                    <div style="background:#F1F5F9; border:1px solid #CBD5E1; padding:8px 12px; border-radius:6px; font-size:0.83rem;">
                        <b>Veículo:</b> {dados_v['placa']} ({dados_v['veiculo']}) | <b>Status:</b> <code>{dados_v['status']}</code><br>
                        <b>Condutor:</b> {dados_v['condutor']} | <b>Saída:</b> {dados_v['data_inicial']} às {dados_v['horario_inicial']}
                    </div>
                """, unsafe_allow_html=True)

            with st.form("form_editar_viagem"):
                st.markdown("##### ✎ Dados da Viagem")
                e_col1, e_col2, e_col3 = st.columns(3)
                
                with e_col1:
                    lista_condutores = sorted(list(df_usuarios["nome"].unique()))
                    condutor_atual = dados_v["condutor"]
                    idx_c = lista_condutores.index(condutor_atual) if condutor_atual in lista_condutores else 0
                    novo_condutor = st.selectbox("Condutor Responsável:", options=lista_condutores, index=idx_c)
                
                with e_col2:
                    novo_destino = st.text_input("Destino Informado:", value=str(dados_v["destino"]))

                with e_col3:
                    novo_km_inicial = st.number_input("Km Inicial:", min_value=0.0, value=float(dados_v["km_inicial_num"]) if pd.notna(dados_v["km_inicial_num"]) else 0.0, step=1.0)

                st.markdown("---")
                st.markdown("##### ◷ Retorno / Fechamento")
                fechar_agora = st.checkbox("Encerrar e fechar esta viagem agora?", value=(dados_v["status"] == "Concluída"))

                f_col1, f_col2, f_col3 = st.columns(3)
                with f_col1:
                    data_fim_default = dados_v["data_fim_dt"].date() if pd.notna(dados_v["data_fim_dt"]) else hoje_brasil
                    nova_data_fim = st.date_input("Data de Retorno:", value=data_fim_default, format="DD/MM/YYYY")
                
                with f_col2:
                    hora_fim_default = dados_v["horario_final"] if dados_v["horario_final"] else obter_agora_brasil().strftime("%H:%M")
                    novo_hora_fim = st.text_input("Horário Retorno (HH:MM):", value=hora_fim_default)

                with f_col3:
                    km_fim_val = float(dados_v["km_final_num"]) if pd.notna(dados_v["km_final_num"]) else float(novo_km_inicial)
                    novo_km_final = st.number_input("Km Final:", min_value=0.0, value=km_fim_val, step=1.0)

                btn_salvar_edicao = st.form_submit_button("💾 Salvar Alterações")

                if btn_salvar_edicao:
                    if fechar_agora and novo_km_final < novo_km_inicial:
                        st.error("❌ O Km Final de retorno não pode ser menor que o Km Inicial.")
                    else:
                        dict_atualizacao = {
                            "condutor": novo_condutor,
                            "destino": novo_destino,
                            "km_inicial": str(int(novo_km_inicial)),
                            "km_inicial_num": novo_km_inicial
                        }

                        if fechar_agora:
                            dict_atualizacao["data_final"] = nova_data_fim.strftime("%d/%m/%Y")
                            dict_atualizacao["horario_final"] = novo_hora_fim
                            dict_atualizacao["km_final"] = str(int(novo_km_final))
                            dict_atualizacao["km_final_num"] = novo_km_final
                            dict_atualizacao["km_percorrido_num"] = max(novo_km_final - novo_km_inicial, 0)
                            dict_atualizacao["km_percorrido"] = str(int(dict_atualizacao["km_percorrido_num"]))
                            dict_atualizacao["status"] = "Concluída"
                        else:
                            dict_atualizacao["data_final"] = ""
                            dict_atualizacao["horario_final"] = ""
                            dict_atualizacao["km_final"] = ""
                            dict_atualizacao["km_final_num"] = np.nan
                            dict_atualizacao["status"] = "Em Aberto"

                        st.session_state["edicoes_viagens"][rv_selecionado] = dict_atualizacao
                        st.success(f"✔ Viagem `{rv_selecionado}` atualizada com sucesso!")
                        st.rerun()

    # =========================================================================
    # PÁGINA 5: USUÁRIOS (GERAÇÃO AUTOMÁTICA DE LOGIN, GRAVAÇÃO E LIMPEZA)
    # =========================================================================
    elif pagina_atual == "usuarios":
        tab_lista, tab_novo = st.tabs(["📋 Usuários Cadastrados", "➕ Novo Usuário"])

        with tab_lista:
            cols_exibicao = ["nome", "usuario", "acesso"] if "acesso" in df_usuarios.columns else ["nome", "usuario"]
            st.dataframe(
                df_usuarios[cols_exibicao],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "nome": st.column_config.TextColumn("Nome Completo / Condutor", width="large"),
                    "usuario": st.column_config.TextColumn("Login de Acesso", width="medium"),
                    "acesso": st.column_config.TextColumn("Permissão / Acesso (Cidade/Geral)", width="large"),
                }
            )
            st.caption(f"Total: {len(df_usuarios)} usuário(s) ativos.")

        with tab_novo:
            locais_conhecidos = ["Geral", "Araraquara", "Ribeirão Preto", "São Paulo", "São José do Rio Preto", "São José dos Campos", "Campinas"]
            
            if "reset_cadastro_key" not in st.session_state:
                st.session_state["reset_cadastro_key"] = 0

            reset_idx = st.session_state["reset_cadastro_key"]

            nome_digitado = st.text_input(
                "Nome Completo:",
                key=f"input_nome_cadastro_{reset_idx}",
                placeholder="Ex: Roberto da Silva"
            )

            usuario_gerado = gerar_usuario_padrao(nome_digitado)
            nome_formatado = formatar_nome_padrao(nome_digitado)

            with st.form(f"form_cadastrar_usuario_{reset_idx}"):
                u_col1, u_col2 = st.columns(2)
                with u_col1:
                    st.text_input(
                        "Usuário:",
                        value=usuario_gerado,
                        disabled=True,
                        help="Gerado automaticamente pelo sistema a partir do nome informado."
                    )
                    
                    tipo_acesso_modo = st.radio(
                        "Tipo de Acesso:",
                        options=["Geral (Acesso a toda a frota)", "Cidade Específica (Restrito aos veículos da base)"],
                        horizontal=True
                    )
                    
                    if "Cidade" in tipo_acesso_modo:
                        cidade_acesso = st.selectbox("Selecione a Cidade Base:", options=[c for c in locais_conhecidos if c != "Geral"])
                    else:
                        cidade_acesso = "Geral"

                with u_col2:
                    nova_senha = st.text_input(
                        "Senha Inicial:",
                        type="password",
                        placeholder="Digite a senha (apenas números)"
                    ).strip()
                    confirma_senha = st.text_input(
                        "Confirme a Senha:",
                        type="password",
                        placeholder="Repita a senha (apenas números)"
                    ).strip()
                    
                    st.markdown("<b>Veículos liberados para este perfil:</b>", unsafe_allow_html=True)
                    if not df_frota.empty and "Local de pernoite" in df_frota.columns:
                        if cidade_acesso == "Geral":
                            veiculos_liberados = df_frota["Placa"].tolist()
                        else:
                            veiculos_liberados = df_frota[df_frota["Local de pernoite"].str.lower() == cidade_acesso.lower()]["Placa"].tolist()
                        
                        st.caption(f"Total de {len(veiculos_liberados)} veículo(s) liberado(s) para operação.")
                    else:
                        st.caption("Acesso total a todos os veículos disponíveis.")

                btn_cadastrar = st.form_submit_button("💾 Cadastrar e Salvar Usuário")

                if btn_cadastrar:
                    if not nome_formatado:
                        st.error("Informe o Nome Completo antes de cadastrar.")
                    elif not usuario_gerado:
                        st.error("Não foi possível gerar o usuário a partir do nome informado.")
                    elif not nova_senha:
                        st.error("Preencha a senha.")
                    elif not nova_senha.isdigit():
                        st.error("❌ A senha deve conter apenas números.")
                    elif nova_senha != confirma_senha:
                        st.error("❌ As senhas digitadas não coincidem.")
                    elif usuario_gerado in df_usuarios["usuario"].values:
                        st.error(f"❌ O usuário gerado `{usuario_gerado}` já está cadastrado.")
                    else:
                        novo_reg = {
                            "usuario": usuario_gerado,
                            "senha": nova_senha,
                            "nome": nome_formatado,
                            "acesso": cidade_acesso
                        }

                        gravou_nuvem = gravar_usuario_na_planilha(novo_reg)

                        if gravou_nuvem:
                            st.cache_data.clear()
                            st.session_state["reset_cadastro_key"] += 1
                            st.success(f"✔ Usuário **{nome_formatado}** (`{usuario_gerado}`) cadastrado e salvo com sucesso na folha de cálculo!")
                            st.rerun()
                        else:
                            if "novos_usuarios_sessao" not in st.session_state:
                                st.session_state["novos_usuarios_sessao"] = []
                            st.session_state["novos_usuarios_sessao"].append(novo_reg)
                            st.session_state["reset_cadastro_key"] += 1
                            st.warning(
                                "✔ Usuário adicionado temporariamente à sessão. Verifique a implantação do Apps Script para gravação em nuvem."
                            )
                            st.rerun()

if __name__ == "__main__":
    main()