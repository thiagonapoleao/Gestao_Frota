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
# 1. CONFIGURAÇÃO DA PÁGINA E CSS (SIDEBAR RESPONSIVA E OCULTÁVEL)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Painel de Frotas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        /* 1. MANTÉM O BOTÃO DE ABRIR/FECHAR A SIDEBAR 100% OPERACIONAL */
        [data-testid="collapsedControl"],
        button[kind="header"] {
            display: flex !important;
            visibility: visible !important;
            color: #0F172A !important;
            z-index: 1000000 !important;
        }

        /* Oculta apenas os menus de desenvolvimento e deploy do Streamlit */
        #MainMenu, footer, .stDeployButton, [data-testid="stToolbarActions"],
        [data-testid="manage-app-button"], div[data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Ajusta o topo para não cobrir o botão da sidebar */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
            height: 2.2rem !important;
        }

        .block-container,
        div[data-testid="stAppViewContainer"] > .main > .block-container {
            padding-top: 0.8rem !important;
            padding-bottom: 2rem !important;
            max-width: 96% !important;
        }

        /* 2. FORÇA TEMA CLARO NATIVO */
        :root, html, body {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
            color-scheme: light !important;
        }

        .stApp, [data-testid="stAppViewContainer"] {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }

        h1, h2, h3, h4, h5, p, span, label, div {
            color: #0F172A !important;
        }
        .stWidgetLabel p, label p {
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
        }

        /* 3. SIDEBAR COM RECOLHIMENTO NATURAL (SEM FORÇAR TRANSFORM) */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #1E293B !important;
        }

        /* Botões de rádio da barra lateral */
        div[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
            gap: 8px !important;
        }
        div[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label {
            background-color: #F8FAFC !important;
            border: 1px solid #CBD5E1 !important;
            padding: 10px 14px !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            font-weight: 600 !important;
            color: #0F172A !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        }
        div[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:hover {
            background-color: #EFF6FF !important;
            border-color: #2563EB !important;
        }

        /* Cabeçalho Compacto */
        .dash-header-container {
            background: #FFFFFF;
            padding: 16px 24px;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
            margin-bottom: 1.2rem;
            margin-top: 0px;
        }

        .dash-title {
            font-size: 1.45rem;
            font-weight: 800;
            color: #0F172A;
            margin: 0;
            letter-spacing: -0.02em;
        }
        .dash-subtitle {
            font-size: 0.88rem;
            color: #64748B;
            margin: 2px 0 0 0;
        }

        /* Painel de Filtros */
        .filter-panel {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 18px 20px 10px 20px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
            margin-bottom: 1.2rem;
        }

        /* KPI Cards */
        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .kpi-title {
            font-size: 0.80rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B;
            margin: 0;
        }
        .kpi-value {
            font-size: 1.85rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.1;
            margin: 0;
        }
        .kpi-caption {
            font-size: 0.78rem;
            color: #94A3B8;
            margin: 0;
        }

        .badge-open {
            background-color: #FEF3C7;
            color: #92400E;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.76rem;
            font-weight: 700;
            display: inline-block;
            border: 1px solid #FDE68A;
        }
        .badge-done {
            background-color: #DEF7EC;
            color: #03543F;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.76rem;
            font-weight: 700;
            display: inline-block;
            border: 1px solid #BCF0DA;
        }

        [data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 14px !important;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
            padding: 24px !important;
        }

        div[data-baseweb="input"],
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] > div,
        div[data-testid="stDateInput"] > div {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            color: #0F172A !important;
            border-radius: 8px !important;
        }
        input {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            -webkit-text-fill-color: #0F172A !important;
        }

        div.stButton > button {
            background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            border: none !important;
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.2) !important;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #1D4ED8, #1E40AF) !important;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0 !important;
            border-radius: 10px !important;
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

def renderizar_cabecalho_com_logo(subtitulo="Monitoramento em Tempo Real de Viagens e Quilometragem"):
    caminho_logo = obter_caminho_logotipo()
    agora = obter_agora_brasil()

    st.markdown('<div class="dash-header-container">', unsafe_allow_html=True)
    c_logo, c_texto, c_hora = st.columns([1.2, 5, 2.3])

    with c_logo:
        if caminho_logo:
            try:
                logo_img = Image.open(caminho_logo)
                st.image(logo_img, width=140)
            except Exception:
                st.markdown("### ☕")
        else:
            st.markdown("### ☕")

    with c_texto:
        st.markdown(f"""
            <div style="padding-left: 8px;">
                <div class="dash-title">Painel de Frotas</div>
                <div class="dash-subtitle">{subtitulo}</div>
            </div>
        """, unsafe_allow_html=True)

    with c_hora:
        st.markdown(f"""
            <div style="text-align: right; padding-top: 4px;">
                <span style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Sincronizado</span><br>
                <span style="font-size: 0.92rem; font-weight: 700; color: #0F172A;">{agora.strftime("%d/%m/%Y às %H:%M:%S")}</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def normalizar_texto(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.strip().lower()

# -------------------------------------------------------------
# 4. CARREGAMENTO E TRATAMENTO DOS DADOS (ETL)
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

# -------------------------------------------------------------
# 5. TELA DE LOGIN
# -------------------------------------------------------------
def tela_login(df_usuarios):
    caminho_logo = obter_caminho_logotipo()
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if caminho_logo:
            try:
                logo_img = Image.open(caminho_logo)
                st.image(logo_img, width=160)
            except Exception:
                st.markdown("<h2 style='text-align:center;'>☕</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='text-align:center;'>☕</h2>", unsafe_allow_html=True)

        st.markdown("<p style='text-align:center; color:#64748B; font-weight:500;'>Acesso ao Painel de Frotas</p>", unsafe_allow_html=True)

        with st.form("form_login_dash"):
            usuario_digitado = st.text_input("Usuário Gestor:", placeholder="Digite seu usuário").strip().lower()
            senha_digitada = st.text_input("Senha:", type="password", placeholder="Digite sua senha").strip()
            btn_login = st.form_submit_button("Acessar Painel Gerencial")

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
# 6. APLICATIVO DO DASHBOARD
# -------------------------------------------------------------
def main():
    df_usuarios = carregar_usuarios()

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

    opcoes_menu = ["📊 Visão Geral & KPIs", "🔍 Consulta & Filtros Avançados"]

    if "pagina_selecionada" not in st.session_state:
        st.session_state["pagina_selecionada"] = opcoes_menu[0]

    # BARRA LATERAL (COM CONTROLE LIVRE DE EXPANDIR/RECOLHER)
    with st.sidebar:
        caminho_logo = obter_caminho_logotipo()
        if caminho_logo:
            try:
                logo_img = Image.open(caminho_logo)
                st.image(logo_img, width=150)
            except Exception:
                st.markdown("### ☕")
        else:
            st.markdown("### ☕")

        st.markdown(f"👤 **Gestor:**\n**{nome_gestor}**")
        st.markdown("---")

        st.markdown("#### 📌 **Navegação**")
        idx_selecionado = opcoes_menu.index(st.session_state["pagina_selecionada"]) if st.session_state["pagina_selecionada"] in opcoes_menu else 0
        pagina_sidebar = st.radio(
            "Módulos:",
            options=opcoes_menu,
            index=idx_selecionado,
            key="radio_nav_sidebar"
        )
        st.session_state["pagina_selecionada"] = pagina_sidebar

        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔄 Atualizar"):
                st.cache_data.clear()
                st.rerun()
        with col_btn2:
            if st.button("🚪 Sair"):
                st.session_state.clear()
                st.query_params.clear()
                st.rerun()

    df_base = carregar_dados_viagens()

    if df_base.empty:
        st.warning("Nenhum registro de viagem encontrado na planilha.")
        return

    hoje_brasil = obter_agora_brasil().date()

    # =========================================================================
    # PÁGINA 1: VISÃO GERAL & KPIS
    # =========================================================================
    if st.session_state["pagina_selecionada"] == "📊 Visão Geral & KPIs":
        renderizar_cabecalho_com_logo("Visão Geral, Controle de Veículos em Trânsito e Indicadores")

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
                    <p class="kpi-value">{total_km_rodado:,.0f} <span style="font-size: 0.95rem; font-weight: 500;">km</span></p>
                    <p class="kpi-caption">Viagens concluídas</p>
                </div>
            """, unsafe_allow_html=True)

        with kpi4:
            st.markdown(f"""
                <div class="kpi-card" style="border-left: 4px solid #6366F1;">
                    <p class="kpi-title">Média Km / Viagem</p>
                    <p class="kpi-value">{media_km_geral:,.1f} <span style="font-size: 0.95rem; font-weight: 500;">km</span></p>
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

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

        # 2. VEÍCULOS EM ABERTO NO TOPO
        st.markdown("### 🚨 **Veículos em Aberto (Atualmente em Trânsito)**")
        if viagens_abertas_df.empty:
            st.success("✅ **Todos os veículos estão no pátio.** Nenhuma viagem em aberto no momento.")
        else:
            grid_abertos = st.columns(min(len(viagens_abertas_df), 3))
            for idx, (_, v_aberta) in enumerate(viagens_abertas_df.iterrows()):
                col_target = grid_abertos[idx % 3]
                with col_target:
                    st.markdown(f"""
                        <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-left: 4px solid #F59E0B; padding: 14px 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-weight: 800; font-size: 1.05rem; color: #92400E;">🚗 {v_aberta['placa']}</span>
                                <span class="badge-open">EM TRÂNSITO</span>
                            </div>
                            <div style="font-size: 0.88rem; color: #78350F; font-weight: 600;">{v_aberta['veiculo']}</div>
                            <hr style="margin: 8px 0; border: none; border-top: 1px solid #FEE382;">
                            <div style="font-size: 0.84rem; color: #451A03; line-height: 1.5;">
                                <b>Condutor:</b> {v_aberta['condutor']}<br>
                                <b>Saída:</b> {v_aberta['data_inicial']} às {v_aberta['horario_inicial']}<br>
                                <b>Km Saída:</b> {v_aberta['km_inicial']} km<br>
                                <b>Destino:</b> {v_aberta['destino'] or 'Não especificado'}<br>
                                <b>Código RV:</b> <code style="background: #FEF3C7; color: #92400E; padding: 2px 6px; border-radius: 4px; font-weight: 700;">{v_aberta['rv']}</code>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # 3. GRÁFICOS ACUMULATIVOS COM VALORES NAS BARRAS
        st.markdown("### 📈 **Quilometragem Acumulada da Frota**")
        g_col1, g_col2 = st.columns(2)

        with g_col1:
            st.markdown("##### 🏆 **Km Total Acumulado por Veículo**")
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
                    align="center",
                    baseline="bottom",
                    dy=-4,
                    fontSize=12,
                    fontWeight=700,
                    color="#1E3A8A"
                ).encode(
                    x=alt.X("Placa:N", sort="-y"),
                    y=alt.Y("Km_Total:Q"),
                    text="rotulo_km:N"
                )

                grafico_km_total = (bars1 + text1).properties(height=320)
                st.altair_chart(grafico_km_total, use_container_width=True)
            else:
                st.caption("Sem dados suficientes para calcular valores acumulados.")

        with g_col2:
            st.markdown("##### 🚙 **Média de Km por Veículo**")
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
                    align="center",
                    baseline="bottom",
                    dy=-4,
                    fontSize=12,
                    fontWeight=700,
                    color="#064E3B"
                ).encode(
                    x=alt.X("Placa:N", sort="-y"),
                    y=alt.Y("Media_Km:Q"),
                    text="rotulo_media:N"
                )

                grafico_media_km = (bars2 + text2).properties(height=320)
                st.altair_chart(grafico_media_km, use_container_width=True)
            else:
                st.caption("Sem dados suficientes para calcular médias.")

        st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

        # 4. CARROS UTILIZADOS NO DIA (HOJE)
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
                st.metric("Veículos Ativados no Dia", f"{qtd_carros_dia}")
            with m2:
                st.metric("Viagens Registradas no Dia", f"{len(df_carros_dia)}")
            with m3:
                st.metric("Km Total Rodado no Dia", f"{km_dia_total:,.0f} km")

            df_tabela_dia = df_carros_dia[[
                "rv", "status", "placa", "veiculo", "condutor",
                "horario_inicial", "km_inicial_num", "horario_final", "km_final_num",
                "km_percorrido_num", "destino"
            ]].copy()

            df_tabela_dia.columns = [
                "Registro (RV)", "Status", "Placa", "Veículo", "Condutor",
                "Hora Saída", "Km Saída", "Hora Retorno", "Km Retorno", "Km Rodado", "Destino"
            ]

            df_tabela_dia = df_tabela_dia.sort_values(by=["Status", "Hora Saída"], ascending=[True, False])

            st.dataframe(
                df_tabela_dia,
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

    # =========================================================================
    # PÁGINA 2: CONSULTA & FILTROS AVANÇADOS
    # =========================================================================
    elif st.session_state["pagina_selecionada"] == "🔍 Consulta & Filtros Avançados":
        renderizar_cabecalho_com_logo("Pesquisa Cruzada por Veículo, Condutor, Período e Status")

        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.95rem; font-weight:700; color:#0F172A; margin-bottom:8px;'>🎯 Parâmetros de Pesquisa</p>", unsafe_allow_html=True)
        
        f_col1, f_col2, f_col3, f_col4 = st.columns([1.2, 1.8, 1.8, 1.4])

        with f_col1:
            status_opcoes = ["Todos", "Em Aberto", "Concluída"]
            status_sel = st.selectbox("Status da Viagem:", status_opcoes)

        with f_col2:
            lista_veiculos = sorted([v for v in df_base["rotulo_veiculo"].unique() if v])
            veiculos_sel = st.multiselect(
                "Veículo(s):",
                options=lista_veiculos,
                placeholder="Todos os veículos..."
            )

        with f_col3:
            lista_condutores = sorted([c for c in df_base["condutor"].unique() if c and c.lower() != "nan"])
            condutores_sel = st.multiselect(
                "Condutor(es):",
                options=lista_condutores,
                placeholder="Todos os condutores..."
            )

        with f_col4:
            datas_validas = df_base["data_ini_dt"].dropna()
            min_d = datas_validas.min().date() if not datas_validas.empty else date.today() - timedelta(days=30)
            max_d = datas_validas.max().date() if not datas_validas.empty else date.today()
            periodo_sel = st.date_input(
                "Período de Saída:",
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
            st.metric("Viagens Localizadas", f"{qtd_res}")
        with r_col2:
            st.metric("Km Total no Filtro", f"{km_res:,.0f} km")
        with r_col3:
            st.metric("Média Km / Viagem", f"{media_km_res:,.1f} km")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
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
            with st.expander("📊 **Visualizar Matriz Cruzada: Km Total por Veículo e por Condutor**"):
                pivot_km = df_conc_consulta.pivot_table(
                    index="veiculo",
                    columns="condutor",
                    values="km_percorrido_num",
                    aggfunc="sum",
                    fill_value=0
                )
                st.dataframe(pivot_km.style.format("{:,.0f} km"), use_container_width=True)

if __name__ == "__main__":
    main()