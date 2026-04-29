import streamlit as st
from groq import Groq
import plotly.graph_objects as go 
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="MONTENEGROPROSPEC", page_icon="🇲🇪", layout="wide")

# 2. ESTILO VISUAL (CORREÇÃO DE LEGIBILIDADE E CONTRASTE)
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff; /* Fundo branco sólido para garantir leitura */
    }
    /* Força cor PRETA em todos os textos para máxima visibilidade */
    h1, h2, h3, p, label, .stMetric, .stSelectbox div, span { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    .stSidebar { background-color: #f1f5f9; border-right: 1px solid #cbd5e1; }
    .footer {
        text-align: center; padding: 20px; color: #000000; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Função para Gerar PDF
def gerar_pdf(conteudo, titulo="Relatório Técnico"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "MONTENEGROPROSPEC - Parecer Técnico")
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, f"Título: {titulo}")
    text_object = c.beginText(50, 750)
    text_object.setFont("Helvetica", 10)
    linhas = conteudo.split('\n')
    for line in linhas:
        text_object.textLine(line[:100])
    c.drawText(text_object)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# 3. SISTEMA DE LOGIN
def check_password():
    if "auth" not in st.session_state: st.session_state["auth"] = False
    if st.session_state["auth"]: return True
    st.markdown("<h2 style='text-align: center;'>Acesso Restrito</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        pwd = st.text_input("Chave de Acesso Master", type="password")
        if st.button("Autenticar"):
            correct_pwd = st.secrets.get("PASSWORD", "mne2026")
            if pwd == correct_pwd:
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Credencial inválida.")
    return False

if not check_password(): st.stop()

# 4. INICIALIZAÇÃO DA IA
try:
    api_key = st.secrets.get("GROQ_API_KEY")
    client = Groq(api_key=api_key)
except:
    st.error("Configure a chave GROQ_API_KEY nos Secrets.")

# 5. SIDEBAR (LIMPA E PROFISSIONAL)
st.sidebar.title("MONTENEGROPROSPEC")
st.sidebar.write("Idioma: Português")
st.sidebar.write(f"Operador: **Genailma Couto**")
st.sidebar.markdown("---")
menu = st.sidebar.radio("MENU", ["Análise de ROI", "Due Diligence Jurídica", "Visto & Residência", "Business Intelligence", "Relatórios Oficiais"])

if st.sidebar.button("Sair"):
    st.session_state["auth"] = False
    st.rerun()

# 6. CONTEÚDO
if menu == "Análise de ROI":
    st.title("📊 Análise de ROI em Tempo Real")
    v = st.number_input("Valor do Imóvel (€)", value=150000.0)
    imp = v * 0.03 if v <= 150000 else (4500 + (v-150000)*0.05)
    st.metric("Estimativa de Custo Total", f"€ {v + imp + 1500:,.2f}")
    
    df = pd.DataFrame({'Mês': ['Jan', 'Fev', 'Mar', 'Abr'], 'Valor': [2800, 2850, 2900, 3050]})
    fig = go.Figure(go.Scatter(x=df['Mês'], y=df['Valor'], mode='lines+markers', line=dict(color='#10b981', width=3)))
    fig.update_layout(title="Tendência de Valorização m²", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Due Diligence Jurídica":
    st.title("⚖️ Due Diligence Jurídica")
    doc = st.text_area("Texto do List Nepokretnosti (Matrícula):", height=250)
    if st.button("Executar Auditoria IA"):
        if doc.strip():
            with st.spinner("Analisando gravames..."):
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Realize análise técnica e jurídica deste imóvel em Montenegro: {doc}"}],
                    model="llama-3.1-8b-instant"
                )
                st.session_state['ultima_analise'] = res.choices[0].message.content
                st.info("Resultado da Análise:")
                st.markdown(st.session_state['ultima_analise'])
        else:
            st.warning("Por favor, cole o texto antes de analisar.")

elif menu == "Visto & Residência":
    st.title("🇲🇪 Protocolos de Residência")
    servico = st.selectbox("Selecione o Serviço:", ["Visto de Nômade Digital", "Cidadania por Investimento", "Abertura de Empresa (DOO)", "Compra de Imóveis"])
    
    if servico == "Compra de Imóveis":
        st.subheader("Aquisição e Direito à Residência")
        st.write("Qualquer imóvel edificado em Montenegro dá direito ao pedido de residência temporária.")
        st.info("Requisito: List Nepokretnosti sem ônus (Cista Svojina).")
    else:
        st.info(f"Módulo de {servico} configurado para as diretrizes de 2026.")

elif menu == "Business Intelligence":
    st.title("📈 Business Intelligence")
    st.write("Análise de Mercado e Demandas")
    dados_bi = pd.DataFrame({'Região': ['Budva', 'Tivat', 'Kotor'], 'ROI %': [7.5, 8.2, 6.9]})
    st.bar_chart(dados_bi.set_index('Região'))

elif menu == "Relatórios Oficiais":
    st.title("📄 Geração de Parecer Técnico")
    if 'ultima_analise' in st.session_state:
        pdf_data = gerar_pdf(st.session_state['ultima_analise'])
        st.download_button(label="📥 Baixar Relatório PDF", data=pdf_data, file_name="parecer_montenegro.pdf", mime="application/pdf")
    else:
        st.warning("Realize a Due Diligence primeiro.")

# 7. RODAPÉ
st.markdown(f'<div class="footer">MONTENEGROPROSPEC | Desenvolvido por Genailma de Oliveira Couto • 2026</div>', unsafe_allow_html=True)