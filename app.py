import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date, time
try:
    from zoneinfo import ZoneInfo
    FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")
except Exception:
    FUSO_BRASIL = timezone(timedelta(hours=-3))

import os
import unicodedata
import requests
import json

def obter_agora_brasil():
    """Retorna datetime atual de Brasília."""
    return datetime.now(FUSO_BRASIL)

# -------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILO VISUAL (DARK MODE)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Master Café - Gestão de Frota",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        #MainMenu {visibility: visible !important;}
        footer {visibility: hidden; display: none !important;}
        .stDeployButton {display: none !important;}
        [data-testid="stToolbarActions"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}
        [data-testid="manage-app-button"] {display: none !important;}

        .stApp {
            background-color: #0F172A;
            color: #F8FAFC;
        }
        .main-header {
            text-align: center;
            padding: 14px;
            border-radius: 10px;
            background: linear-gradient(135deg, #1E3A8A, #0D6EFD);
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        .info-card {
            background-color: #1E293B;
            border-left: 4px solid #0D6EFD;
            padding: 12px 14px;
            border-radius: 4px 8px 8px 4px;
            margin: 12px 0;
            color: #E2E8F0;
        }
        div.stButton > button:first-child {
            width: 100%;
            border-radius: 8px;
            height: 48px;
            font-weight: bold;
            background-color: #0D6EFD;
            color: white;
            border: none;
        }
        div.stButton > button:first-child:hover {
            background-color: #0b5ed7;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. DEFINIÇÃO DAS VARIÁVEIS GLOBAIS E LINKS
# -------------------------------------------------------------
# Insira a URL do seu Webhook do Google Apps Script configurado para a nova planilha
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwQJfe1H2OHTAYGOPZhoOGRl8zazwK4SXf-RvKRMMkQhqJHbmyg4mHBT7AVRLubKOWzbQ/exec"

# ID da Planilha de Gestão de Frota
SPREADSHEET_ID = "1-Bn0VBnRV1zp_f7QrKTldKB03L9_k7DyRO3YslGMnnU"

# GIDs das Abas
GID_USUARIOS = "426012097"       # Aba com Login / Condutores
GID_VEICULOS = "0"               # Aba com a lista de veículos da frota
GID_LANCAMENTOS = "379222602"    # Aba onde serão gravados os registros de frota

# -------------------------------------------------------------
# 3. FUNÇÕES DE SUPORTE E LEITURA DA PLANILHA
# -------------------------------------------------------------
def normalizar_texto(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.strip().lower()

@st.cache_data(ttl=60)
def carregar_usuarios():
    """Carrega os logins e condutores a partir da aba GID 426012097."""
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

    # Fallback de teste
    return pd.DataFrame([{"usuario": "admin", "senha": "123", "nome": "Condutor Master Café"}])

@st.cache_data(ttl=30)
def carregar_veiculos():
    """
    Carrega veículos da aba GID 0:
    - Coluna B: Descrição / Nome do Veículo (Índice 1)
    - Coluna E: Placa (Índice 4)
    """
    urls = [
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_VEICULOS}",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_VEICULOS}"
    ]
    for url in urls:
        try:
            df_raw = pd.read_csv(url, engine="python", on_bad_lines="skip", dtype=str)
            if not df_raw.empty and len(df_raw.columns) >= 5:
                # Localiza as colunas B e E pelo índice posicional ou cabeçalho
                col_veiculo = df_raw.columns[1]  # Coluna B
                col_placa = df_raw.columns[4]    # Coluna E

                df_veiculos = pd.DataFrame()
                df_veiculos["placa"] = df_raw[col_placa].dropna().astype(str).str.strip().str.upper()
                df_veiculos["veiculo"] = df_raw[col_veiculo].fillna("Não informado").astype(str).str.strip()
                
                # Remove placas vazias ou inválidas
                df_veiculos = df_veiculos[df_veiculos["placa"].str.len() >= 5].drop_duplicates(subset=["placa"])
                return df_veiculos
        except Exception:
            continue

    return pd.DataFrame(columns=["placa", "veiculo"])

def salvar_lancamento_frota(dados):
    """Envia os dados de frota para o Google Apps Script Webhook."""
    try:
        headers = {"Content-Type": "text/plain;charset=utf-8"}
        corpo = json.dumps(dados)

        resposta = requests.post(
            WEBHOOK_URL,
            data=corpo,
            headers=headers,
            timeout=30,
            allow_redirects=True
        )

        if resposta.status_code == 200:
            try:
                ret = resposta.json()
                if ret.get("status") == "success":
                    return True, "Registro de frota salvo com sucesso!"
                elif ret.get("status") == "error":
                    return False, f"Aviso do Apps Script: {ret.get('message')}"
            except Exception:
                pass
            return True, "Lançamento registrado na planilha Google."
        else:
            return False, f"Erro HTTP {resposta.status_code}: {resposta.text[:150]}"
    except Exception as e:
        return False, f"Falha na comunicação: {str(e)}"

# -------------------------------------------------------------
# 4. TELA DE LOGIN
# -------------------------------------------------------------
def tela_login(df_usuarios):
    st.markdown('<div class="main-header"><h2>Master Café ☕</h2><p>Controle de Gestão de Frota</p></div>', unsafe_allow_html=True)
    
    with st.form("form_login"):
        st.subheader("Identificação do Condutor")
        usuario_digitado = st.text_input("Usuário:").strip().lower()
        senha_digitada = st.text_input("Senha:", type="password").strip()
        btn_login = st.form_submit_button("Entrar no Sistema")
        
        if btn_login:
            if df_usuarios.empty:
                st.error("Não foi possível carregar a lista de usuários da planilha.")
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
# 5. APLICATIVO PRINCIPAL
# -------------------------------------------------------------
def main():
    df_usuarios = carregar_usuarios()

    # Recupera sessão por parâmetro de URL se recarregou
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

    nome_condutor = st.session_state.get("nome_condutor", "Condutor")

    # Menu lateral
    with st.sidebar:
        st.write(f"🚗 **Condutor Autenticado:**\n### {nome_condutor}")
        if st.button("🚪 Sair do Sistema"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

    st.markdown('<div class="main-header"><h2>Master Café ☕</h2><p>Registro de Saída e Retorno de Veículo</p></div>', unsafe_allow_html=True)

    df_veiculos = carregar_veiculos()

    if df_veiculos.empty:
        st.warning("Nenhum veículo encontrado na aba de frotas. Verifique a planilha ou recarregue.")
        if st.button("🔄 Recarregar Veículos"):
            st.cache_data.clear()
            st.rerun()
        return

    # Mapeamento para o Selectbox: mostra "Placa - Nome do Veículo"
    df_veiculos["rotulo"] = df_veiculos["placa"] + " - " + df_veiculos["veiculo"]
    opcoes_veiculos = df_veiculos["rotulo"].tolist()

    agora = obter_agora_brasil()

    with st.form("form_gestao_frota"):
        st.subheader("1. Veículo e Condutor")
        
        # Condutor vinculado automaticamente ao Login
        condutor_selecionado = st.text_input("Condutor:", value=nome_condutor, disabled=True)

        veiculo_sel_rotulo = st.selectbox("Selecione o Veículo:", options=opcoes_veiculos)
        
        # Recupera a placa e veículo exatos
        dados_veiculo_linha = df_veiculos[df_veiculos["rotulo"] == veiculo_sel_rotulo].iloc[0]
        placa_selecionada = dados_veiculo_linha["placa"]
        veiculo_selecionado = dados_veiculo_linha["veiculo"]

        st.markdown(f"""
            <div class="info-card">
                <b>🚙 Veículo:</b> {veiculo_selecionado}<br>
                <b>🔢 Placa:</b> {placa_selecionada}<br>
                <b>👤 Condutor:</b> {nome_condutor}
            </div>
        """, unsafe_allow_html=True)

        st.subheader("2. Saída (Início)")
        col_di, col_hi = st.columns(2)
        with col_di:
            data_inicial = st.date_input("Data Inicial:", value=agora.date(), format="DD/MM/YYYY")
        with col_hi:
            horario_inicial = st.time_input("Horário Inicial:", value=agora.time().replace(microsecond=0))

        km_inicial = st.number_input("Km Inicial:", min_value=0.0, step=1.0, format="%.0f")

        st.subheader("3. Retorno (Fim) e Destino")
        col_df, col_hf = st.columns(2)
        with col_df:
            data_final = st.date_input("Data Final:", value=agora.date(), format="DD/MM/YYYY")
        with col_hf:
            horario_final = st.time_input("Horário Final:", value=agora.time().replace(microsecond=0))

        km_final = st.number_input("Km Final:", min_value=0.0, step=1.0, format="%.0f")

        destino = st.text_input("Destino / Rota percorrida:", placeholder="Ex: Clientes Araraquara, São Carlos, Manutenção...")

        btn_salvar = st.form_submit_button("💾 Gravar Registro de Frota")

    if btn_salvar:
        # Validações básicas
        if km_final > 0 and km_final < km_inicial:
            st.error("⚠️ O Km Final não pode ser menor que o Km Inicial.")
            return

        if not destino.strip():
            st.error("⚠️ Por favor, informe o Destino.")
            return

        km_percorrido = (km_final - km_inicial) if km_final >= km_inicial else 0

        # Estrutura do payload para enviar para a aba GID 379222602
        payload = {
            "gid_destino": GID_LANCAMENTOS,
            "data_inicial": data_inicial.strftime("%d/%m/%Y"),
            "horario_inicial": horario_inicial.strftime("%H:%M:%S"),
            "km_inicial": int(km_inicial),
            "data_final": data_final.strftime("%d/%m/%Y"),
            "horario_final": horario_final.strftime("%H:%M:%S"),
            "km_final": int(km_final),
            "km_percorrido": int(km_percorrido),
            "condutor": nome_condutor,
            "placa": placa_selecionada,
            "veiculo": veiculo_selecionado,
            "destino": destino.strip(),
            "data_registro": agora.strftime("%d/%m/%Y %H:%M:%S")
        }

        with st.spinner("Salvando lançamento na planilha..."):
            sucesso, msg = salvar_lancamento_frota(payload)

        # Backup local em CSV
        try:
            arquivo_backup = "historico_frotas.csv"
            df_hist = pd.DataFrame([payload])
            df_hist.to_csv(
                arquivo_backup,
                mode="a",
                header=not os.path.exists(arquivo_backup),
                index=False
            )
        except Exception:
            pass

        if sucesso:
            st.success(f"✅ Lançamento gravado com sucesso na aba de registros!")
            st.info(f"Distância percorrida calculada: **{km_percorrido:,.0f} km**")
        else:
            st.warning(f"⚠️ {msg} (Os dados foram preservados no backup local).")

if __name__ == "__main__":
    main()