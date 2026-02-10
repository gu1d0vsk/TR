import streamlit as st
from docxtpl import DocxTemplate
from io import BytesIO
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de TR - Finep", page_icon="📄", layout="wide")

# --- ESTILIZAÇÃO CSS (MANTENDO A IDENTIDADE DARK NEON) ---
page_bg_img = """
<style>
    /* Fundo Geral */
    [data-testid="stApp"] {
        background-image: linear-gradient(rgb(2, 45, 44) 0%, rgb(0, 21, 21) 100%);
        background-attachment: fixed;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(2, 45, 44, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Cabeçalho transparente */
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }

    /* Texto claro */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, div[data-testid="stCaptionContainer"] {
        color: #e0e0e0 !important;
    }
    
    /* Inputs arredondados */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stSelectbox"] > div > div { 
        background-color: rgba(12, 19, 14, 0.5) !important;
        color: #e0e0e0 !important;
        border-radius: 1.5rem !important; 
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding-left: 1rem;
    }
    
    /* Foco nos inputs */
    div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {
        border-color: rgb(221, 79, 5) !important;
        box-shadow: 0 0 10px rgba(221, 79, 5, 0.2);
    }

    /* Botões Neon */
    div[data-testid="stButton"] > button, div[data-testid="stDownloadButton"] > button { 
        border-radius: 4rem; 
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    /* Botão Verde */
    div[data-testid="stButton"] > button { 
        background-color: rgb(0, 80, 81) !important; 
        color: #FFFFFF !important; 
    }
    /* Botão Laranja (Download) */
    div[data-testid="stDownloadButton"] > button {
        background-color: rgb(221, 79, 5) !important; 
        color: #FFFFFF !important; 
    }
    
    /* Efeito Hover */
    div[data-testid="stButton"] > button:hover, div[data-testid="stDownloadButton"] > button:hover {
        transform: scale(1.02);
        filter: brightness(1.2);
    }

    /* Checkboxes */
    div[data-testid="stCheckbox"] label span {
        line-height: 1.5;
    }
    
    /* Esconde elementos padrão */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
dados = {} 

# --- SIDEBAR: CONFIGURAÇÕES E FLUXO ---
with st.sidebar:
    st.title("⚙️ Configurações")
    st.markdown("Defina a estrutura do seu TR aqui.")
    
    # 1. TIPO DE CONTRATAÇÃO
    st.caption("TIPO DE PROCESSO")
    tipo_contratacao = st.radio("O que será contratado?", ["Aquisição de Bem", "Prestação de Serviço"], label_visibility="collapsed")
    
    st.divider()
    
    # 2. SEÇÕES OPCIONAIS (Isso controla as abas)
    st.caption("ITENS ADICIONAIS DO TR")
    tem_vistoria = st.checkbox("Exigir Vistoria Técnica?", value=False)
    tem_amostra = st.checkbox("Exigir Amostra / PoC?", value=False)
    tem_garantia = st.checkbox("Exigir Garantia Contratual?", value=False)
    
    dados['tem_vistoria'] = tem_vistoria
    dados['tem_amostra'] = tem_amostra
    dados['tem_garantia'] = tem_garantia
    
    st.divider()
    st.info("ℹ️ Ao marcar uma opção acima, uma nova aba aparecerá para preenchimento.")

# --- CABEÇALHO DA PÁGINA ---
st.title("📄 Gerador de Termo de Referência")

# --- BLOCO 1: IDENTIFICAÇÃO (UNIDADES) ---
# --- BLOCO 1: IDENTIFICAÇÃO (UNIDADES) ---
with st.container():
    col_dem, col_req = st.columns(2)
    
    with col_dem:
        # Unidade Demandante
        unidade_demandante = st.text_input("Unidade Demandante", placeholder="Ex: Depto. de Comunicação")
        dados['unidade_demandante'] = unidade_demandante

    with col_req:
        # Unidade Requisitante (Opcional, sem explicação)
        tem_requisitante = st.checkbox("Existe Unidade Requisitante?")
        
        if tem_requisitante:
            unidade_requisitante = st.text_input("Nome da Unidade Requisitante", placeholder="Ex: Gestão Documental")
            dados['unidade_requisitante'] = unidade_requisitante
            dados['tem_requisitante'] = True
        else:
            dados['unidade_requisitante'] = ""
            dados['tem_requisitante'] = False

st.divider()

# --- BLOCO 2: ABAS DINÂMICAS ---
# Criamos a lista de nomes das abas baseada no que foi marcado na sidebar
abas_ativas = ["📝 Objeto & Justificativa", "📍 Locais e Prazos"]

if tem_vistoria: abas_ativas.append("🔍 Vistoria")
if tem_amostra: abas_ativas.append("📦 Amostra/PoC")
if tem_garantia: abas_ativas.append("🛡️ Garantia")

# Cria as abas no Streamlit
tabs = st.tabs(abas_ativas)

# Dicionário para acessar as abas pelo nome (facilita a lógica)
tab_map = dict(zip(abas_ativas, tabs))

# --- CONTEÚDO DAS ABAS ---

# 1. ABA OBJETO (Sempre existe)
with tab_map["📝 Objeto & Justificativa"]:
    col_obj1, col_obj2 = st.columns([3, 1])
    
    verbo = "Aquisição de" if tipo_contratacao == "Aquisição de Bem" else "Contratação de empresa para prestação de serviços de"
    
    with col_obj1:
        item_nome = st.text_input("Objeto Resumido", placeholder="Ex: Notebooks i7 ou Limpeza Predial")
    with col_obj2:
        qtd_estimada = st.text_input("Qtd / Estimativa", placeholder="Ex: 12 meses ou 50 un")

    if item_nome:
        dados['objeto_completo'] = f"{verbo} {item_nome}, conforme condições, quantidades e exigências estabelecidas neste instrumento."
        st.caption(f"Prévia do texto: *{dados['objeto_completo']}*")
    else:
        dados['objeto_completo'] = "..."

    dados['justificativa'] = st.text_area("Justificativa da Contratação", height=100, 
                                          placeholder="Por que essa compra é necessária para a Finep?")
    
    dados['especificacao_tecnica'] = st.text_area("Especificação Técnica Detalhada", height=150,
                                                  placeholder="Descreva voltagem, cor, requisitos de memória, escopo do serviço...")

# 2. ABA LOCAIS E PRAZOS (Sempre existe)
with tab_map["📍 Locais e Prazos"]:
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        prazo_entrega = st.number_input("Prazo de Entrega/Execução (dias úteis)", value=30, min_value=1)
    with col_p2:
        local_entrega = st.text_input("Local de Entrega", value="Edifício Sede da Finep - Praia do Flamengo, 200")
        
    dados['local_prazo_entrega'] = f"O objeto deve ser entregue em {local_entrega} no prazo de {prazo_entrega} dias úteis."
    
    vigencia = st.selectbox("Vigência do Contrato", ["12 meses", "24 meses", "30 meses", "60 meses", "Vigência vinculada à garantia"])
    dados['vigencia_texto'] = vigencia

# 3. ABAS OPCIONAIS (Só aparecem se ativadas na sidebar)

if tem_vistoria and "🔍 Vistoria" in tab_map:
    with tab_map["🔍 Vistoria"]:
        st.markdown("### Detalhes da Vistoria")
        obrigatoria = st.toggle("A vistoria é obrigatória para participar?", value=False)
        
        texto_vistoria = "A vistoria é facultativa."
        if obrigatoria:
            texto_vistoria = "A vistoria é obrigatória, sob pena de desclassificação."
            
        dados['texto_vistoria'] = texto_vistoria
        st.write(f"Configuração atual: **{texto_vistoria}**")

if tem_amostra and "📦 Amostra/PoC" in tab_map:
    with tab_map["📦 Amostra/PoC"]:
        st.markdown("### Critérios de Amostra")
        prazo_amostra = st.number_input("Prazo para entregar a amostra (dias)", value=5)
        dados['texto_amostra'] = f"A licitante provisoriamente vencedora deverá apresentar amostra no prazo de {prazo_amostra} dias úteis."

if tem_garantia and "🛡️ Garantia" in tab_map:
    with tab_map["🛡️ Garantia"]:
        st.markdown("### Garantia Contratual")
        percentual = st.slider("Percentual sobre o valor do contrato", 1, 5, 5)
        dados['texto_garantia'] = f"Será exigida garantia de execução contratual de {percentual}%."

# --- GERAÇÃO E DOWNLOAD ---
st.divider()

# Variáveis automáticas de data
meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
hoje = date.today()
dados['local_data'] = f"Rio de Janeiro, {hoje.day} de {meses[hoje.month-1]} de {hoje.year}."

col_vazio, col_btn, col_vazio2 = st.columns([1, 2, 1])

with col_btn:
    if st.button("🚀 Gerar Documento (.docx)", use_container_width=True):
        try:
            doc = DocxTemplate("modelo_tr.docx")
            doc.render(dados)
            
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            st.success("Documento gerado com sucesso!")
            st.download_button(
                label="📥 Baixar TR Editado",
                data=buffer,
                file_name=f"TR_{str(item_nome).strip().replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro: {e}")
            st.warning("Verifique se o arquivo 'modelo_tr.docx' está na pasta correta.")
