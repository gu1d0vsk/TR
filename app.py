import streamlit as st
from docxtpl import DocxTemplate
from io import BytesIO
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de TR - Finep", page_icon="📄", layout="wide")

# --- ESTILIZAÇÃO CSS (IDENTIDADE VISUAL) ---
page_bg_img = """
<style>
    /* Fundo Geral da Aplicação */
    [data-testid="stApp"] {
        background-image: linear-gradient(rgb(2, 45, 44) 0%, rgb(0, 21, 21) 100%);
        background-attachment: fixed;
    }
    
    /* Ajuste da Sidebar para acompanhar o tema */
    [data-testid="stSidebar"] {
        background-color: rgba(2, 45, 44, 0.9);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Cabeçalho transparente */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }

    /* Força texto claro (já que o fundo é escuro) */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, label, span, div[data-testid="stCaptionContainer"] {
        color: #e0e0e0 !important;
    }
    
    /* --- ESTILIZAÇÃO DOS INPUTS --- */
    /* Deixa os inputs arredondados e translúcidos */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stSelectbox"] > div > div { 
        background-color: rgba(12, 19, 14, 0.5) !important;
        color: #e0e0e0 !important;
        border-radius: 1.5rem !important; 
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: left; 
        padding-left: 1rem;
    }
    
    /* Foco nos inputs */
    div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {
        border-color: rgb(221, 79, 5) !important;
        box-shadow: 0 0 10px rgba(221, 79, 5, 0.2);
    }

    /* --- ESTILIZAÇÃO DOS BOTÕES (NEON) --- */
    /* Botão Principal (Gerar TR) */
    div[data-testid="stButton"] > button { 
        background-color: rgb(0, 80, 81) !important; 
        color: #FFFFFF !important; 
        border-radius: 4rem; 
        border-color: transparent;
        font-weight: bold;
        transition: all 0.3s ease;
        padding: 0.5rem 2rem;
    }
    div[data-testid="stButton"] > button:hover {
        box-shadow: 0 0 12px rgba(0, 80, 81, 0.8), 0 0 20px rgba(0, 80, 81, 0.4); 
        transform: scale(1.02);
    }

    /* Botão de Download (Laranja Neon) */
    div[data-testid="stDownloadButton"] > button {
        background-color: rgb(221, 79, 5) !important; 
        color: #FFFFFF !important; 
        border-radius: 4rem; 
        border-color: transparent;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        box-shadow: 0 0 12px rgba(221, 79, 5, 0.8), 0 0 20px rgba(221, 79, 5, 0.4); 
        transform: scale(1.02);
    }

    /* Limpeza da Interface (Esconde rodapés e menus padrão) */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Abas (Tabs) */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #a0a0a0 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: rgb(221, 79, 5) !important;
        border-bottom-color: rgb(221, 79, 5) !important;
    }
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.title("📄 Gerador de Termo de Referência")
st.markdown('<p style="font-size: 1.1rem; opacity: 0.8;">Preencha os campos abaixo para gerar o documento no padrão <strong>Finep</strong>.</p>', unsafe_allow_html=True)
st.divider()

# --- BARRA LATERAL (Setup) ---
with st.sidebar:
    st.header("Configurações")
    depto = st.selectbox("Unidade Demandante", 
        ["Departamento de TI", "Departamento de RH", "Departamento de Compras", "Operações", "Jurídico"])
    
    tipo_contratacao = st.radio("Tipo de Contratação", ["Aquisição de Bem", "Prestação de Serviço"])
    
    st.markdown("---")
    st.caption("ℹ️ Certifique-se de que o arquivo `modelo_tr.docx` está na mesma pasta.")

# --- FORMULÁRIO PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["📝 Detalhes do Objeto", "⚙️ Condições de Execução", "⚖️ Cláusulas Opcionais"])

dados = {} # Dicionário que vai guardar todas as respostas

with tab1:
    st.subheader("1. Objeto e Justificativa")
    
    col_input1, col_input2 = st.columns([2, 1])
    
    verbo = "Aquisição de" if tipo_contratacao == "Aquisição de Bem" else "Contratação de empresa para prestação de serviços de"
    with col_input1:
        item_nome = st.text_input("Nome curto do Item/Serviço", placeholder="Ex: Notebooks de alto desempenho")
    
    with col_input2:
        qtd_estimada = st.number_input("Qtd. Estimada", min_value=1, value=1)

    # Montando o texto do objeto dinamicamente
    if item_nome:
        dados['objeto_completo'] = f"{verbo} {item_nome}, conforme condições, quantidades e exigências estabelecidas neste instrumento."
        st.info(f"📌 **Prévia do Objeto:** {dados['objeto_completo']}")
    else:
        dados['objeto_completo'] = "..."

    dados['justificativa'] = st.text_area("2. Justificativa (Objetivo)", 
        placeholder="Descreva a necessidade da contratação...", height=100)
    
    dados['especificacao_tecnica'] = st.text_area("3. Especificação Técnica Detalhada", height=150,
        placeholder="Cole aqui a descrição técnica, requisitos mínimos, voltagem, cor, dimensões, etc.")

with tab2:
    st.subheader("Locais e Prazos")
    col1, col2 = st.columns(2)
    
    with col1:
        prazo = st.number_input("Prazo de Entrega/Execução (dias)", min_value=1, value=30)
    with col2:
        local = st.text_input("Local de Entrega/Execução", value="Sede da Finep - Praia do Flamengo, 200")
    
    dados['local_prazo_entrega'] = f"O objeto deverá ser entregue/executado no endereço {local}, no prazo máximo de {prazo} dias corridos após o recebimento da Ordem de Compra/Serviço."
    
    vigencia = st.selectbox("Vigência do Contrato", ["12 meses", "24 meses", "36 meses", "Vigência atrelada à garantia"])
    dados['vigencia_texto'] = vigencia

with tab3:
    st.subheader("Selecione o que deve aparecer no TR")
    
    col_a, col_b, col_c = st.columns(3)
    
    # Checkboxes estilizados
    dados['tem_vistoria'] = col_a.checkbox("Exigir Vistoria Técnica?", value=False)
    dados['tem_amostra'] = col_b.checkbox("Exigir Amostra/PoC?", value=False)
    dados['tem_garantia'] = col_c.checkbox("Exigir Garantia Contratual?", value=False)
    
    if dados['tem_vistoria']:
        st.warning("⚠️ A seção '11. DA VISTORIA' será incluída no documento.")
    
    if dados['tem_garantia']:
        percentual = st.slider("Percentual da Garantia", 1, 5, 5)
        dados['texto_garantia'] = f"Será exigida garantia contratual de {percentual}% sobre o valor total."
    else:
        dados['texto_garantia'] = "Não será exigida garantia contratual."

# --- GERAÇÃO DO DOCUMENTO ---
st.divider()

# Dados automáticos
dados['unidade_demandante'] = depto
meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
hoje = date.today()
dados['local_data'] = f"Rio de Janeiro, {hoje.day} de {meses[hoje.month-1]} de {hoje.year}."

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    if st.button("🚀 Gerar Termo de Referência (.docx)", use_container_width=True):
        try:
            # 1. Carrega o modelo
            doc = DocxTemplate("modelo_tr.docx")
            
            # 2. Renderiza (Substitui as tags pelos dados)
            doc.render(dados)
            
            # 3. Salva na memória (Buffer) para download
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            st.success("TR gerado com sucesso! Baixe abaixo:")
            
            st.download_button(
                label="📥 Baixar TR Preenchido",
                data=buffer,
                file_name=f"TR_{str(item_nome).replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Erro ao gerar documento: {e}")
            st.warning("Verifique se o arquivo 'modelo_tr.docx' está na mesma pasta do script.")

# Debug (Opcional - para ver o que está sendo enviado)
# with st.expander("Ver dados brutos (Debug)"):
#    st.write(dados)
