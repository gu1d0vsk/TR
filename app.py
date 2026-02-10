import streamlit as st
from docxtpl import DocxTemplate
from io import BytesIO
from datetime import date

# Configuração da Página
st.set_page_config(page_title="Gerador de TR - Finep", page_icon="📄", layout="wide")

st.title("📄 Gerador de Termo de Referência (TR)")
st.markdown("Preencha os campos abaixo para gerar o TR no padrão **Finep**.")

# --- BARRA LATERAL (Setup) ---
with st.sidebar:
    st.header("Configurações Gerais")
    depto = st.selectbox("Unidade Demandante", 
        ["Departamento de TI", "Departamento de RH", "Departamento de Compras", "Operações", "Jurídico"])
    
    tipo_contratacao = st.radio("Tipo de Contratação", ["Aquisição de Bem", "Prestação de Serviço"])
    
    st.divider()
    st.info("ℹ️ Certifique-se de que o arquivo 'modelo_tr.docx' está na mesma pasta deste script.")

# --- FORMULÁRIO PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["📝 Detalhes do Objeto", "⚙️ Condições de Execução", "⚖️ Cláusulas Opcionais"])

dados = {} # Dicionário que vai guardar todas as respostas

with tab1:
    st.subheader("1. Objeto e Justificativa")
    
    # Montando o texto do objeto dinamicamente
    verbo = "Aquisição de" if tipo_contratacao == "Aquisição de Bem" else "Contratação de empresa para prestação de serviços de"
    item_nome = st.text_input("Nome curto do Item/Serviço", placeholder="Ex: Notebooks de alto desempenho ou Limpeza Predial")
    
    dados['objeto_completo'] = f"{verbo} {item_nome}, conforme condições, quantidades e exigências estabelecidas neste instrumento."
    st.caption(f"Previsão do texto no TR: *{dados['objeto_completo']}*")
    
    dados['justificativa'] = st.text_area("2. Justificativa (Objetivo)", 
        placeholder="Descreva a necessidade da contratação (Ex: Substituição de equipamentos obsoletos...)")
    
    dados['especificacao_tecnica'] = st.text_area("3. Especificação Técnica Detalhada", height=150,
        placeholder="Cole aqui a descrição técnica, requisitos mínimos, voltagem, cor, dimensões, etc.")

with tab2:
    st.subheader("Locais e Prazos")
    col1, col2 = st.columns(2)
    
    prazo = col1.number_input("Prazo de Entrega/Execução (dias)", min_value=1, value=30)
    local = col2.text_input("Local de Entrega/Execução", value="Sede da Finep - Praia do Flamengo, 200")
    
    dados['local_prazo_entrega'] = f"O objeto deverá ser entregue/executado no endereço {local}, no prazo máximo de {prazo} dias corridos após o recebimento da Ordem de Compra/Serviço."
    
    vigencia = st.selectbox("Vigência do Contrato", ["12 meses", "24 meses", "36 meses", "Vigência atrelada à garantia"])
    dados['vigencia_texto'] = vigencia

with tab3:
    st.subheader("Selecione o que deve aparecer no TR")
    
    col_a, col_b, col_c = st.columns(3)
    
    # Checkboxes que controlam os {% if %} no Word
    dados['tem_vistoria'] = col_a.toggle("Exigir Vistoria Técnica?", value=False)
    dados['tem_amostra'] = col_b.toggle("Exigir Amostra/PoC?", value=False)
    dados['tem_garantia'] = col_c.toggle("Exigir Garantia Contratual?", value=False)
    
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

if st.button("🚀 Gerar Termo de Referência (.docx)", type="primary"):
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
            file_name=f"TR_{item_nome.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        st.error(f"Erro ao gerar documento: {e}")
        st.info("Verifique se o arquivo 'modelo_tr.docx' está na pasta e se as tags {{ }} estão corretas.")

# Debug (Opcional - para ver o que está sendo enviado)
with st.expander("Ver dados brutos (Debug)"):
    st.write(dados)
