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
        .status-box {
            background-color: #1E293B;
            border: 1px solid #334155;
            padding: 14px;
            border-radius: 8px;
            margin-bottom: 1.2rem;
            color: #F8FAFC;
            line-height: 1.6;
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
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwQJfe1H2OHTAYGOPZhoOGRl8zazwK4SXf-RvKRMMkQhqJHbmyg4mHBT7AVRLubKOWzbQ/exec"
SPREADSHEET_ID = "1-Bn0VBnRV1zp_f7QrKTldKB03L9_k7DyRO3YslGMnnU"

GID_USUARIOS = "426012097"       # Aba com Login / Condutores
GID_VEICULOS = "0"               # Aba com a lista de veículos da frota
GID_LANCAMENTOS = "379222602"    # Aba onde serão gravados os registros de frota

# -------------------------------------------------------------
# 3. GESTÃO DE PERSISTÊNCIA DA VIAGEM (CONTRA REFRESH / F5)
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
# 4. FUNÇÕES DE SUPORTE E LEITURA DA PLANILHA
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
    """Envia o lançamento completo para o Webhook do Google Apps Script."""
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
# 5. TELA DE LOGIN
# -------------------------------------------------------------
def tela_login(df_usuarios):
    st.markdown('<div class="main-header"><h2>Master Café ☕</h2><p>Controle de Gestão de Frota</p></div>', unsafe_allow_html=True)
    
    with st.form("form_login"):
        st.subheader("Condutor")
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
# 6. APLICATIVO PRINCIPAL
# -------------------------------------------------------------
def main():
    df_usuarios = carregar_usuarios()

    # Recupera sessão por parâmetro da URL se recarregou
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

    # Verifica se há viagem em andamento (recuperação de refresh)
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
        if st.session_state["viagem_ativa"]:
            st.warning("⚠️ Há uma viagem em andamento para este login.")
        if st.button("🚪 Cancelar e Sair"):
            limpar_viagem_em_andamento(usuario_atual)
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

    st.markdown('<div class="main-header"><h2>Master Café ☕</h2><p>Controle de Gestão de Frota</p></div>', unsafe_allow_html=True)

    agora = obter_agora_brasil()

    # =========================================================================
    # ETAPA 1: SELEÇÃO DO VEÍCULO E START INICIAL (SAÍDA)
    # =========================================================================
    if not st.session_state["viagem_ativa"]:
        df_veiculos = carregar_veiculos()

        if df_veiculos.empty:
            st.error("Nenhum veículo disponível na base. Verifique a planilha.")
            if st.button("🔄 Recarregar Base"):
                st.cache_data.clear()
                st.rerun()
            return

        st.subheader("1. Selecione o Veículo")
        
        # Opções com placeholder inicial vazio para só exibir o restante após escolher
        opcoes = ["-- Selecione um veículo --"] + (df_veiculos["placa"] + " - " + df_veiculos["veiculo"]).tolist()
        veiculo_escolhido = st.selectbox("Veículo da Frota:", options=opcoes, key="select_veiculo")

        # Os outros campos só aparecem depois que o veículo é escolhido
        if veiculo_escolhido != "-- Selecione um veículo --":
            dados_veiculo = df_veiculos[
                (df_veiculos["placa"] + " - " + df_veiculos["veiculo"]) == veiculo_escolhido
            ].iloc[0]
            placa = dados_veiculo["placa"]
            modelo = dados_veiculo["veiculo"]

            st.markdown(f"""
                <div class="info-card">
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
                destino_ini = st.text_input("Destino / Rota planejada:", placeholder="Ex: Clientes Araraquara, São Carlos...")

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
                st.success("✅ Start Inicial registrado! Viagem iniciada com sucesso.")
                st.rerun()

    # =========================================================================
    # ETAPA 2: START FINAL (RETORNO E FINALIZAÇÃO DO LOGIN)
    # =========================================================================
    else:
        dados_ativos = st.session_state["dados_viagem"]

        st.subheader("Viagem em Andamento")
        st.markdown(f"""
            <div class="status-box">
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

            with st.spinner("Gravando registro e finalizando sessão..."):
                sucesso, msg = salvar_lancamento_frota(payload_completo)

            # Grava no backup local CSV
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

            # Limpa o arquivo de sessão da viagem em andamento
            limpar_viagem_em_andamento(usuario_atual)

            # Limpa todo o estado da sessão (dados limpos para o próximo login)
            st.session_state.clear()
            st.query_params.clear()

            if sucesso:
                st.success("✅ Viagem concluída e registrada com sucesso na planilha!")
            else:
                st.warning(f"⚠️ {msg} (Os dados foram preservados no backup local).")

            st.info("Sessão finalizada. Redirecionando para a tela de login...")
            st.rerun()

if __name__ == "__main__":
    main()