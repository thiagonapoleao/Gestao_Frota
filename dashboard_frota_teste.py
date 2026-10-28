import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timezone, timedelta, date

try:
    from zoneinfo import ZoneInfo
    FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")
except Exception:
    FUSO_BRASIL = timezone(timedelta(hours=-3))

import os
import re
import unicodedata
from PIL import Image

def obter_agora_brasil():
    """Retorna datetime oficial de Brasília."""
    return datetime.now(FUSO_BRASIL)

# -------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS (DESIGN SYSTEM CORPORATIVO)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Painel de Frotas",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* 1. OCULTAÇÃO DE CONTROLES NATIVOS DESNECESSÁRIOS */
        section[data-testid="stSidebar"],
        [data-testid="collapsedControl"],
        button[kind="header"],
        #MainMenu, footer, .stDeployButton, [data-testid="stToolbarActions"],
        [data-testid="manage-app-button"], div[data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
        }

        header[data-testid="stHeader"] {
            display: none !important;
        }

        .block-container,
        div[data-testid="stAppViewContainer"] > .main > .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
            max-width: 98% !important;
        }

        /* 2. BASE TIPOGRÁFICA E CORES */
        :root, html, body {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
            color-scheme: light !important;
        }

        .stApp, [data-testid="stAppViewContainer"] {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif !important;
        }

        h1, h2, h3, h4, h5, p, span, label, div {
            color: #0F172A !important;
        }
        .stWidgetLabel p, label p {
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 0.86rem !important;
        }

        /* 3. BRANDING */
        .brand-title-large {
            font-size: 1.75rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.1;
            letter-spacing: -0.025em;
            margin: 0;
            white-space: nowrap;
        }

        .brand-subtitle-large {
            font-size: 0.82rem;
            color: #64748B;
            font-weight: 500;
            margin-top: 2px;
        }

        /* 4. SUB-CONTAINER DE NAVEGAÇÃO */
        .nav-subcontainer {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 4px 6px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        /* BOTÕES DE NAVEGAÇÃO (AZUL PRIMÁRIO) */
        .nav-subcontainer div.stButton > button {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            font-size: 0.84rem !important;
            border: 1px solid #1D4ED8 !important;
            padding: 0 12px !important;
            min-height: 2.2rem !important;
            height: 2.2rem !important;
            width: 100% !important;
            box-shadow: 0 1px 2px rgba(37, 99, 235, 0.15) !important;
            transition: all 0.15s ease-in-out !important;
            white-space: nowrap !important;
            text-transform: none !important;
            letter-spacing: normal !important;
        }

        .nav-subcontainer div.stButton > button:hover {
            background-color: #1D4ED8 !important;
            border-color: #1E40AF !important;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25) !important;
        }

        /* BOTÃO ATIVO (DESTAQUE REFORÇADO) */
        .nav-active div.stButton > button {
            background-color: #1E40AF !important;
            border-color: #172554 !important;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2), 0 0 0 2px rgba(37, 99, 235, 0.4) !important;
            font-weight: 700 !important;
        }

        /* BOTÕES DE AÇÃO SECUNDÁRIA (SINCRONIZAR E SAIR) */
        .btn-action div.stButton > button {
            background-color: #F8FAFC !important;
            color: #334155 !important;
            -webkit-text-fill-color: #334155 !important;
            border: 1px solid #CBD5E1 !important;
            box-shadow: none !important;
            font-weight: 500 !important;
        }
        .btn-action div.stButton > button:hover {
            background-color: #E2E8F0 !important;
            color: #0F172A !important;
            -webkit-text-fill-color: #0F172A !important;
            border-color: #94A3B8 !important;
        }

        /* 5. CARDS E PAINÉIS */
        .filter-panel {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 16px 18px 8px 18px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
            margin-bottom: 1.2rem;
        }

        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 14px 16px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .kpi-title {
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B;
            margin: 0;
        }
        .kpi-value {
            font-size: 1.7rem;
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
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 700;
            border: 1px solid #FDE68A;
            letter-spacing: 0.03em;
        }
        .badge-done {
            background-color: #DEF7EC;
            color: #03543F;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 700;
            border: 1px solid #BCF0DA;
            letter-spacing: 0.03em;
        }

        [data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.03) !important;
            padding: 22px !important;
        }

        div[data-baseweb="input"],
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] > div,
        div[data-testid="stDateInput"] > div,
        div[data-testid="stTimeInput"] > div {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            color: #0F172A !important;
            border-radius: 6px !important;
        }
        input {
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
# 2. CONFIGURAÇÕES DA PLANILHA
# -------------------------------------------------------------
SPREADSHEET_ID = "1-Bn0VBnRV1zp_f7QrKTldKB03L9_k7DyRO3YslGMnnU"
GID_LANCAMENTOS = "379222602"
GID_USUARIOS = "426012097"

# -------------------------------------------------------------
# 3. SUPORTE A LOGOTIPO
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

# -------------------------------------------------------------
# 4. ETL DOS DADOS
# -------------------------------------------------------------
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
    return pd.DataFrame([{"usuario": "admin", "senha": "123", "nome": "Gestor Master Café"}])

def obter_usuarios_ativos():
    df_base_user = carregar_usuarios()
    if "novos_usuarios_sessao" not in st.session_state:
        st.session_state["novos_usuarios_sessao"] = []
    
    if st.session_state["novos_usuarios_sessao"]:
        df_novos = pd.DataFrame(st.session_state["novos_usuarios_sessao"])
        return pd.concat([df_base_user, df_novos], ignore_index=True).drop_duplicates(subset=["usuario"], keep="last")
    return df_base_user

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
                st.markdown("<h3 style='text-align:center;'>Master Café</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align:center;'>Master Café</h3>", unsafe_allow_html=True)

        st.markdown("<p style='text-align:center; color:#64748B; font-weight:600; font-size:1rem;'>Painel de Frotas</p>", unsafe_allow_html=True)

        with st.form("form_login_dash"):
            usuario_digitado = st.text_input("Usuário Gestor:", placeholder="Digite seu login").strip().lower()
            senha_digitada = st.text_input("Senha:", type="password", placeholder="Digite sua senha").strip()
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
                    st.session_state["dash_autenticado"] = True
                    st.session_state["dash_usuario"] = usuario_digitado
                    st.session_state["dash_nome"] = usuario_valido.iloc[0]["nome"]
                    st.query_params["u"] = usuario_digitado
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

# -------------------------------------------------------------
# 6. APLICATIVO PRINCIPAL
# -------------------------------------------------------------
def main():
    df_usuarios = obter_usuarios_ativos()

    if not st.session_state.get("dash_autenticado", False):
        usuario_url = st.query_params.get("u", None)
        if usuario_url and not df_usuarios.empty:
            usuario_url = str(usuario_url).strip().lower()
            usuario_valido = df_usuarios[df_usuarios["usuario"] == usuario_url]
            if not usuario_valido.empty:
                st.session_state["dash_autenticado"] = True
                st.session_state["dash_usuario"] = usuario_url
                st.session_state["dash_nome"] = usuario_valido.iloc[0]["nome"]

    if not st.session_state.get("dash_autenticado", False):
        tela_login(df_usuarios)
        return

    nome_gestor = st.session_state.get("dash_nome", "Gestor")

    opcoes_menu = [
        "Dashboard",
        "Consultas",
        "Editar Viagens",
        "Usuários"
    ]

    if "pagina_selecionada" not in st.session_state:
        st.session_state["pagina_selecionada"] = opcoes_menu[0]

    # =========================================================================
    # HEADER SUPERIOR LIMPO (BRANDING + NAVEGAÇÃO COMPACTA PADRONIZADA)
    # =========================================================================
    col_brand, col_subnav = st.columns([1.3, 2.7], vertical_alignment="center")

    with col_brand:
        caminho_logo = obter_caminho_logotipo()
        c_img, c_txt = st.columns([0.8, 3.2], vertical_alignment="center")
        with c_img:
            if caminho_logo:
                try:
                    st.image(Image.open(caminho_logo), width=80)
                except Exception:
                    pass
        with c_txt:
            st.markdown(f"""
                <div style="line-height:1.15;">
                    <div class="brand-title-large">Painel de Frotas</div>
                    <div class="brand-subtitle-large">Gestor: <b>{nome_gestor}</b> &bull; {obter_agora_brasil().strftime("%d/%m/%Y")}</div>
                </div>
            """, unsafe_allow_html=True)

    with col_subnav:
        st.markdown('<div class="nav-subcontainer">', unsafe_allow_html=True)
        btn1, btn2, btn3, btn4, btn5, btn6 = st.columns([1.3, 1.2, 1.5, 1.2, 1.3, 0.8], vertical_alignment="center")

        with btn1:
            is_active = (st.session_state["pagina_selecionada"] == opcoes_menu[0])
            st.markdown(f'<div class="{"nav-active" if is_active else ""}">', unsafe_allow_html=True)
            if st.button(opcoes_menu[0], key="nav_dash"):
                st.session_state["pagina_selecionada"] = opcoes_menu[0]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with btn2:
            is_active = (st.session_state["pagina_selecionada"] == opcoes_menu[1])
            st.markdown(f'<div class="{"nav-active" if is_active else ""}">', unsafe_allow_html=True)
            if st.button(opcoes_menu[1], key="nav_cons"):
                st.session_state["pagina_selecionada"] = opcoes_menu[1]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with btn3:
            is_active = (st.session_state["pagina_selecionada"] == opcoes_menu[2])
            st.markdown(f'<div class="{"nav-active" if is_active else ""}">', unsafe_allow_html=True)
            if st.button(opcoes_menu[2], key="nav_edit"):
                st.session_state["pagina_selecionada"] = opcoes_menu[2]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with btn4:
            is_active = (st.session_state["pagina_selecionada"] == opcoes_menu[3])
            st.markdown(f'<div class="{"nav-active" if is_active else ""}">', unsafe_allow_html=True)
            if st.button(opcoes_menu[3], key="nav_user"):
                st.session_state["pagina_selecionada"] = opcoes_menu[3]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with btn5:
            st.markdown('<div class="btn-action">', unsafe_allow_html=True)
            if st.button("Sincronizar", key="btn_top_sync"):
                st.cache_data.clear()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with btn6:
            st.markdown('<div class="btn-action">', unsafe_allow_html=True)
            if st.button("Sair", key="btn_top_exit"):
                st.session_state.clear()
                st.query_params.clear()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    df_base = obter_viagens_consolidadas()

    if df_base.empty:
        st.warning("Nenhum registro de viagem encontrado na base de dados.")
        return

    hoje_brasil = obter_agora_brasil().date()

    # =========================================================================
    # PÁGINA 1: DASHBOARD
    # =========================================================================
    if st.session_state["pagina_selecionada"] == opcoes_menu[0]:
        total_viagens = len(df_base)
        viagens_abertas_df = df_base[df_base["status"] == "Em Aberto"]
        total_em_aberto = len(viagens_abertas_df)

        viagens_concluidas = df_base[df_base["status"] == "Concluída"]
        total_km_rodado = viagens_concluidas["km_percorrido_num"].sum()
        media_km_geral = viagens_concluidas["km_percorrido_num"].mean() if not viagens_concluidas.empty else 0
        total_concluidas = len(viagens_concluidas)

        # 1. BLOCO DE KPIS
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        with kpi1:
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 3px solid #2563EB;">
                    <p class="kpi-title">Total de Viagens</p>
                    <p class="kpi-value">{total_viagens}</p>
                    <p class="kpi-caption">Histórico acumulado</p>
                </div>
            """, unsafe_allow_html=True)

        with kpi2:
            cor_aberto = "#F59E0B" if total_em_aberto > 0 else "#10B981"
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 3px solid {cor_aberto};">
                    <p class="kpi-title">Veículos em Aberto</p>
                    <p class="kpi-value" style="color: {'#B45309' if total_em_aberto > 0 else '#065F46'};">{total_em_aberto}</p>
                    <p class="kpi-caption">Em trânsito agora</p>
                </div>
            """, unsafe_allow_html=True)

        with kpi3:
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 3px solid #10B981;">
                    <p class="kpi-title">Km Total Rodado</p>
                    <p class="kpi-value">{total_km_rodado:,.0f} <span style="font-size: 0.85rem; font-weight: 500;">km</span></p>
                    <p class="kpi-caption">Viagens concluídas</p>
                </div>
            """, unsafe_allow_html=True)

        with kpi4:
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 3px solid #6366F1;">
                    <p class="kpi-title">Média Km / Viagem</p>
                    <p class="kpi-value">{media_km_geral:,.1f} <span style="font-size: 0.85rem; font-weight: 500;">km</span></p>
                    <p class="kpi-caption">Média por percurso</p>
                </div>
            """, unsafe_allow_html=True)

        with kpi5:
            perc_conc = (total_concluidas / total_viagens * 100) if total_viagens > 0 else 0
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 3px solid #0EA5E9;">
                    <p class="kpi-title">Viagens Concluídas</p>
                    <p class="kpi-value">{total_concluidas}</p>
                    <p class="kpi-caption">{perc_conc:.0f}% de finalização</p>
                </div>
            """, unsafe_allow_html=True)

        # 2. VEÍCULOS EM TRÂNSITO
        st.markdown("#### Veículos em Aberto (Em Trânsito)")
        if viagens_abertas_df.empty:
            st.info("Todos os veículos estão no pátio. Nenhuma viagem em aberto no momento.")
        else:
            grid_abertos = st.columns(min(len(viagens_abertas_df), 3))
            for idx, (_, v_aberta) in enumerate(viagens_abertas_df.iterrows()):
                col_target = grid_abertos[idx % 3]
                dest_aberta = str(v_aberta['destino']).strip() if v_aberta.get('destino') and str(v_aberta['destino']).lower() != 'nan' else 'Não especificado'
                card_aberto_html = (
                    f'<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #F59E0B; padding: 12px 14px; border-radius: 6px; margin-bottom: 6px;">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">'
                    f'<span style="font-weight: 700; font-size: 0.95rem; color: #0F172A;">{v_aberta["placa"]}</span>'
                    f'<span class="badge-open">EM TRÂNSITO</span>'
                    f'</div>'
                    f'<div style="font-size: 0.84rem; color: #475569; font-weight: 500;">{v_aberta["veiculo"]}</div>'
                    f'<div style="font-size: 0.82rem; color: #334155; line-height: 1.45; margin-top: 6px;">'
                    f'<b>Condutor:</b> {v_aberta["condutor"]}<br>'
                    f'<b>Saída:</b> {v_aberta["data_inicial"]} às {v_aberta["horario_inicial"]}<br>'
                    f'<b>Km Saída:</b> {v_aberta["km_inicial"]} km<br>'
                    f'<b>Destino:</b> {dest_aberta}<br>'
                    f'<b>Registro (RV):</b> <span style="font-family: monospace; background:#F1F5F9; padding: 1px 4px; border-radius: 3px;">{v_aberta["rv"]}</span>'
                    f'</div>'
                    f'</div>'
                )
                with col_target:
                    st.markdown(card_aberto_html, unsafe_allow_html=True)
                    if st.button(f"Editar ou Baixar ({v_aberta['rv']})", key=f"btn_quick_{v_aberta['rv']}"):
                        st.session_state["rv_para_editar"] = v_aberta["rv"]
                        st.session_state["pagina_selecionada"] = opcoes_menu[2]
                        st.rerun()

        # 3. GRÁFICOS
        st.markdown("#### Desempenho e Quilometragem da Frota")
        g_col1, g_col2 = st.columns(2)

        with g_col1:
            st.markdown("<p style='font-size:0.86rem; font-weight:600; color:#334155; margin-bottom:4px;'>Km Total Acumulado por Veículo</p>", unsafe_allow_html=True)
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
                    color="#2563EB", cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                ).encode(
                    x=alt.X("Placa:N", sort="-y", title="Placa do Veículo", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Km_Total:Q", title="Km Total"),
                    tooltip=[alt.Tooltip("Placa:N", title="Placa"), alt.Tooltip("rotulo_km:N", title="Km Total")]
                )

                text1 = alt.Chart(df_acumulado_veiculo).mark_text(
                    align="center",
                    baseline="bottom",
                    dy=-4,
                    fontSize=11,
                    fontWeight=600,
                    color="#1E3A8A"
                ).encode(
                    x=alt.X("Placa:N", sort="-y"),
                    y=alt.Y("Km_Total:Q"),
                    text="rotulo_km:N"
                )

                grafico_km_total = (bars1 + text1).properties(height=280)
                st.altair_chart(grafico_km_total, use_container_width=True)
            else:
                st.caption("Sem dados suficientes para cálculo acumulado.")

        with g_col2:
            st.markdown("<p style='font-size:0.86rem; font-weight:600; color:#334155; margin-bottom:4px;'>Média de Km por Viagem</p>", unsafe_allow_html=True)
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
                    color="#059669", cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                ).encode(
                    x=alt.X("Placa:N", sort="-y", title="Placa do Veículo", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Media_Km:Q", title="Média por Viagem (Km)"),
                    tooltip=[alt.Tooltip("Placa:N", title="Placa"), alt.Tooltip("rotulo_media:N", title="Média Km")]
                )

                text2 = alt.Chart(df_media_veiculo).mark_text(
                    align="center",
                    baseline="bottom",
                    dy=-4,
                    fontSize=11,
                    fontWeight=600,
                    color="#064E3B"
                ).encode(
                    x=alt.X("Placa:N", sort="-y"),
                    y=alt.Y("Media_Km:Q"),
                    text="rotulo_media:N"
                )

                grafico_media_km = (bars2 + text2).properties(height=280)
                st.altair_chart(grafico_media_km, use_container_width=True)
            else:
                st.caption("Sem dados suficientes para cálculo de médias.")

        # 4. OPERAÇÃO NO DIA
        st.markdown("#### Operação Diária")
        c_dia_col1, c_dia_col2 = st.columns([1.5, 4])
        with c_dia_col1:
            dia_selecionado = st.date_input(
                "Filtrar data:",
                value=hoje_brasil,
                format="DD/MM/YYYY",
                key="filtro_dia_atual"
            )
        with c_dia_col2:
            st.caption(f"Exibindo deslocamentos com saída em {dia_selecionado.strftime('%d/%m/%Y')}.")

        df_carros_dia = df_base[df_base["data_ini_dt"].dt.date == dia_selecionado].copy()

        if df_carros_dia.empty:
            st.info(f"Nenhum registro de veículo em atividade na data {dia_selecionado.strftime('%d/%m/%Y')}.")
        else:
            qtd_carros_dia = df_carros_dia["placa"].nunique()
            km_dia_total = df_carros_dia[df_carros_dia["status"] == "Concluída"]["km_percorrido_num"].sum()

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Veículos Ativos no Dia", f"{qtd_carros_dia}")
            with m2:
                st.metric("Total de Saídas Registradas", f"{len(df_carros_dia)}")
            with m3:
                st.metric("Km Total no Dia", f"{km_dia_total:,.0f} km")

            df_cards_dia = df_carros_dia.sort_values(by=["status", "horario_inicial"], ascending=[True, False])

            num_cols = min(len(df_cards_dia), 3)
            grid_dia = st.columns(num_cols)

            for idx, (_, v_dia) in enumerate(df_cards_dia.iterrows()):
                col_target = grid_dia[idx % num_cols]
                em_aberto = (v_dia["status"] == "Em Aberto")

                badge_html = '<span class="badge-open">EM TRÂNSITO</span>' if em_aberto else '<span class="badge-done">CONCLUÍDA</span>'
                card_border_left = "#F59E0B" if em_aberto else "#10B981"

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
                    f'<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid {card_border_left}; padding: 12px 14px; border-radius: 6px; margin-bottom: 8px;">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">'
                    f'<span style="font-weight: 700; font-size: 0.95rem; color: #0F172A;">{v_dia["placa"]}</span>'
                    f'{badge_html}'
                    f'</div>'
                    f'<div style="font-size: 0.84rem; color: #475569; font-weight: 500;">{v_dia["veiculo"]}</div>'
                    f'<div style="font-size: 0.82rem; color: #334155; line-height: 1.45; margin-top: 6px;">'
                    f'<b>Condutor:</b> {v_dia["condutor"]}<br>'
                    f'<b>Saída:</b> {v_dia["data_inicial"]} às {v_dia["horario_inicial"]}<br>'
                    f'<b>Km Saída:</b> {km_sai_txt}<br>'
                    f'{bloco_retorno}'
                    f'<b>Destino:</b> {destino_txt}<br>'
                    f'<b>Registro (RV):</b> <span style="font-family: monospace; background:#F1F5F9; padding: 1px 4px; border-radius: 3px;">{rv_txt}</span>'
                    f'</div>'
                    f'</div>'
                )

                with col_target:
                    st.markdown(card_html, unsafe_allow_html=True)

    # =========================================================================
    # PÁGINA 2: CONSULTAS & FILTROS AVANÇADOS
    # =========================================================================
    elif st.session_state["pagina_selecionada"] == opcoes_menu[1]:
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.88rem; font-weight:700; color:#0F172A; margin-bottom:6px;'>Filtros de Pesquisa</p>", unsafe_allow_html=True)
        
        f_col1, f_col2, f_col3, f_col4 = st.columns([1.2, 1.8, 1.8, 1.4])

        with f_col1:
            status_opcoes = ["Todos", "Em Aberto", "Concluída"]
            status_sel = st.selectbox("Status:", status_opcoes)

        with f_col2:
            lista_veiculos = sorted([v for v in df_base["rotulo_veiculo"].unique() if v])
            veiculos_sel = st.multiselect(
                "Veículo:",
                options=lista_veiculos,
                placeholder="Todos os veículos"
            )

        with f_col3:
            lista_condutores = sorted([c for c in df_base["condutor"].unique() if c and c.lower() != "nan"])
            condutores_sel = st.multiselect(
                "Condutor:",
                options=lista_condutores,
                placeholder="Todos os condutores"
            )

        with f_col4:
            datas_validas = df_base["data_ini_dt"].dropna()
            min_d = datas_validas.min().date() if not datas_validas.empty else date.today() - timedelta(days=30)
            max_d = datas_validas.max().date() if not datas_validas.empty else date.today()
            periodo_sel = st.date_input(
                "Período:",
                value=(min_d, max_d),
                format="DD/MM/YYYY"
            )
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
            st.metric("Registros Localizados", f"{qtd_res}")
        with r_col2:
            st.metric("Km Total no Filtro", f"{km_res:,.0f} km")
        with r_col3:
            st.metric("Média Km por Percurso", f"{media_km_res:,.1f} km")

        st.markdown("#### Extrato de Viagens")

        if df_consulta.empty:
            st.info("Nenhuma viagem localizada com a combinação de parâmetros selecionada.")
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
                label="Exportar Relatório (CSV)",
                data=csv_data,
                file_name=f"relatorio_frota_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

        if not df_conc_consulta.empty:
            with st.expander("Matriz: Quilometragem por Veículo e Condutor"):
                pivot_km = df_conc_consulta.pivot_table(
                    index="veiculo",
                    columns="condutor",
                    values="km_percorrido_num",
                    aggfunc="sum",
                    fill_value=0
                )
                st.dataframe(pivot_km.style.format("{:,.0f} km"), use_container_width=True)

    # =========================================================================
    # PÁGINA 3: EDITAR VIAGENS
    # =========================================================================
    elif st.session_state["pagina_selecionada"] == opcoes_menu[2]:
        if "edicoes_viagens" not in st.session_state:
            st.session_state["edicoes_viagens"] = {}

        viagens_em_aberto = df_base[df_base["status"] == "Em Aberto"].copy()

        opcoes_rv = list(viagens_em_aberto["rv"].unique())
        if not opcoes_rv:
            st.info("Não há viagens com status 'Em Aberto' no momento. Selecione uma viagem concluída para retificação:")
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
                    <div style="background:#FFFFFF; border:1px solid #CBD5E1; padding:8px 12px; border-radius:6px; font-size:0.82rem;">
                        <b>Veículo:</b> {dados_v['placa']} ({dados_v['veiculo']}) &bull; <b>Status:</b> <code>{dados_v['status']}</code><br>
                        <b>Condutor:</b> {dados_v['condutor']} &bull; <b>Saída:</b> {dados_v['data_inicial']} às {dados_v['horario_inicial']}
                    </div>
                """, unsafe_allow_html=True)

            with st.form("form_editar_viagem"):
                st.markdown("<p style='font-size:0.88rem; font-weight:700; color:#0F172A; margin-bottom:8px;'>Dados de Saída</p>", unsafe_allow_html=True)
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

                st.markdown("<p style='font-size:0.88rem; font-weight:700; color:#0F172A; margin: 14px 0 8px 0;'>Retorno e Encerramento</p>", unsafe_allow_html=True)
                fechar_agora = st.checkbox("Encerrar e fechar esta viagem", value=(dados_v["status"] == "Concluída"))

                f_col1, f_col2, f_col3 = st.columns(3)
                with f_col1:
                    data_fim_default = dados_v["data_fim_dt"].date() if pd.notna(dados_v["data_fim_dt"]) else hoje_brasil
                    nova_data_fim = st.date_input("Data de Retorno:", value=data_fim_default, format="DD/MM/YYYY")
                
                with f_col2:
                    hora_fim_default = dados_v["horario_final"] if dados_v["horario_final"] else obter_agora_brasil().strftime("%H:%M")
                    novo_hora_fim = st.text_input("Horário de Retorno (HH:MM):", value=hora_fim_default)

                with f_col3:
                    km_fim_val = float(dados_v["km_final_num"]) if pd.notna(dados_v["km_final_num"]) else float(novo_km_inicial)
                    novo_km_final = st.number_input("Km Final:", min_value=0.0, value=km_fim_val, step=1.0)

                btn_salvar_edicao = st.form_submit_button("Salvar Alterações")

                if btn_salvar_edicao:
                    if fechar_agora and novo_km_final < novo_km_inicial:
                        st.error("O Km Final de retorno não pode ser inferior ao Km Inicial.")
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
                        st.success(f"Viagem {rv_selecionado} atualizada com sucesso.")
                        st.rerun()

    # =========================================================================
    # PÁGINA 4: USUÁRIOS
    # =========================================================================
    elif st.session_state["pagina_selecionada"] == opcoes_menu[3]:
        tab_lista, tab_novo = st.tabs(["Usuários Cadastrados", "Novo Usuário"])

        with tab_lista:
            st.dataframe(
                df_usuarios[["nome", "usuario"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "nome": st.column_config.TextColumn("Nome Completo / Condutor", width="large"),
                    "usuario": st.column_config.TextColumn("Login de Acesso", width="medium"),
                }
            )
            st.caption(f"Total: {len(df_usuarios)} registro(s).")

        with tab_novo:
            with st.form("form_cadastrar_usuario"):
                u_col1, u_col2 = st.columns(2)
                with u_col1:
                    novo_nome = st.text_input("Nome Completo:", placeholder="Ex: Roberto Silva")
                    novo_login = st.text_input("Login:", placeholder="Ex: roberto.silva").strip().lower()
                
                with u_col2:
                    nova_senha = st.text_input("Senha Inicial:", type="password", placeholder="Digite a senha")
                    confirma_senha = st.text_input("Confirmação de Senha:", type="password", placeholder="Repita a senha")

                btn_cadastrar = st.form_submit_button("Cadastrar Usuário")

                if btn_cadastrar:
                    if not novo_nome or not novo_login or not nova_senha:
                        st.error("Preencha todos os campos obrigatórios.")
                    elif nova_senha != confirma_senha:
                        st.error("As senhas informadas não conferem.")
                    elif novo_login in df_usuarios["usuario"].values:
                        st.error("Este nome de login já está cadastrado.")
                    else:
                        novo_reg = {
                            "usuario": novo_login,
                            "senha": nova_senha,
                            "nome": novo_nome
                        }
                        if "novos_usuarios_sessao" not in st.session_state:
                            st.session_state["novos_usuarios_sessao"] = []
                        st.session_state["novos_usuarios_sessao"].append(novo_reg)
                        st.success(f"Usuário {novo_nome} ({novo_login}) cadastrado com sucesso.")
                        st.rerun()

if __name__ == "__main__":
    main()