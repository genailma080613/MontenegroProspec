import streamlit as st
from groq import Groq
import plotly.graph_objects as go 
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter 
import io

# 1. CONFIGURAÇÃO DE PÁGINA E IDIOMA
st.set_page_config(page_title="MONTENEGROPROSPEC", layout="wide")

if 'idioma_atual' not in st.session_state:
    st.session_state['idioma_atual'] = "Português"

# Dicionário Profissional de Tradução
DICIONARIO = {
    "Português": {
        "acesso": "Acesso Restrito", "senha": "Chave de Acesso Master", "entrar": "Autenticar",
        "idioma": "Idioma", "operador": "Operador", "sair": "Sair",
        "m1": "Análise de ROI", "m2": "Due Diligence Jurídica", "m3": "Visto & Residência", "m4": "Business Intelligence", "m5": "Relatórios Oficiais",
        "t1": "Análise de ROI em Tempo Real", "t2": "Due Diligence Jurídica", "t3": "Protocolos de Residência", "t4": "Business Intelligence", "t5": "Geração de Parecer Técnico"
    },
    "English": {
        "acesso": "Restricted Access", "senha": "Master Access Key", "entrar": "Authenticate",
        "idioma": "Language", "operador": "Operator", "sair": "Logout",
        "m1": "ROI Analysis", "m2": "Legal Due Diligence", "m3": "Visa & Residency", "m4": "Business Intelligence", "m5": "Official Reports",
        "t1": "Real-Time ROI Analysis", "t2": "Legal Due Diligence", "t3": "Residency Protocols", "t4": "Business Intelligence", "t5": "Technical Report Generation"
    },
    "Crnogorski": {
        "acesso": "Ograničen Pristup", "senha": "Glavna Pristupna Lozinka", "entrar": "Autentifikacija",
        "idioma": "Jezik", "operador": "Operator", "sair": "Odjavi se",
        "m1": "ROI Analiza", "m2": "Pravni Due Diligence", "m3": "Viza i Rezidencija", "m4": "Poslovna Inteligencija", "m5": "Zvanični Izvještaji",
        "t1": "ROI Analiza u Realnom Vremenu", "t2": "Pravni Due Diligence", "t3": "Protokoli za Rezidenciju", "t4": "Poslovna Inteligencija", "t5": "Generisanje Tehničkog Izvještaja"
    },
    "Español": {
        "acesso": "Acceso Restringido", "senha": "Clave de Acceso", "entrar": "Autenticar",
        "idioma": "Idioma", "operador": "Operador", "sair": "Salir",
        "m1": "Análisis de ROI", "m2": "Due Diligence Legal", "m3": "Visa y Residencia", "m4": "Inteligencia de Negocios", "m5": "Informes Oficiales",
        "t1": "Análisis de ROI en Tiempo Real", "t2": "Due Diligence Legal", "t3": "Protocolos de Residencia", "t4": "Inteligencia de Negocios", "t5": "Generación de Informe Técnico"
    }
}

# Carrega os textos do idioma selecionado
t = DICIONARIO[st.session_state['idioma_atual']]

# 2. ESTILO VISUAL (LIMPO E CORPORATIVO)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, label, .stMetric, .stSelectbox div, span { 
        color: #000000 !important; font-weight: 800 !important; 
    }
    .sidebar-title {
        font-size: 1.15rem !important; font-weight: 800 !important; color: #000000 !important; text-align: center; padding-bottom: 10px;
    }
    .stSidebar { background-color: #f1f5f9; border-right: 1px solid #cbd5e1; }
    .footer { text-align: center; padding: 20px; color: #000000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Função PDF 
def gerar_pdf(conteudo, titulo="Relatório Técnico", senha=""):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "MONTENEGROPROSPEC - Parecer Técnico")
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, f"Título: {titulo}")
    text_object = c.beginText(50, 750)
    text_object.setFont("Helvetica", 10)
    linhas = conteudo.split('\n')
    for line in linhas: text_object.textLine(line[:100])
    c.drawText(text_object)
    c.showPage()
    c.save()
    buffer.seek(0)
    if senha:
        reader = PdfReader(buffer)
        writer = PdfWriter()
        for page in reader.pages: writer.add_page(page)
        writer.encrypt(senha)
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output
    return buffer

# 3. SISTEMA DE LOGIN (TRADUZIDO)
def check_password():
    if "auth" not in st.session_state: st.session_state["auth"] = False
    if st.session_state["auth"]: return True
    st.markdown(f"<h2 style='text-align: center;'>{t['acesso']}</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        pwd = st.text_input(t['senha'], type="password")
        if st.button(t['entrar']):
            correct_pwd = st.secrets.get("PASSWORD", "mne2026")
            if pwd == correct_pwd:
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Erro")
    return False

if not check_password(): st.stop()

# 4. INICIALIZAÇÃO DA IA
try:
    api_key = st.secrets.get("GROQ_API_KEY")
    client = Groq(api_key=api_key)
except:
    st.error("Configure a chave GROQ_API_KEY nos Secrets.")

# 5. SIDEBAR (MOTOR DE IDIOMA ATIVADO)
st.sidebar.markdown('<div class="sidebar-title">MONTENEGROPROSPEC</div>', unsafe_allow_html=True)

# Lógica que aplica o idioma em tempo real
lista_idiomas = ["Português", "English", "Crnogorski", "Español"]
indice_atual = lista_idiomas.index(st.session_state['idioma_atual'])
novo_idioma = st.sidebar.selectbox(f"{t['idioma']}:", lista_idiomas, index=indice_atual)

if novo_idioma != st.session_state['idioma_atual']:
    st.session_state['idioma_atual'] = novo_idioma
    st.rerun()

st.sidebar.write(f"{t['operador']}: **Genailma Couto**")
st.sidebar.markdown("---")

menu = st.sidebar.radio("MENU", [t['m1'], t['m2'], t['m3'], t['m4'], t['m5']])

if st.sidebar.button(t['sair']):
    st.session_state["auth"] = False
    st.rerun()

# 6. CONTEÚDO DINÂMICO
if menu == t['m1']:
    st.title(t['t1'])
    v = st.number_input("Valor do Imóvel (€)", value=150000.0)
    imp = v * 0.03 if v <= 150000 else (4500 + (v-150000)*0.05)
    st.metric("Total", f"€ {v + imp + 1500:,.2f}")
    
    df = pd.DataFrame({'Mês': ['Jan', 'Fev', 'Mar', 'Abr'], 'Valor': [2800, 2850, 2900, 3050]})
    fig = go.Figure(go.Scatter(x=df['Mês'], y=df['Valor'], mode='lines+markers', line=dict(color='#10b981', width=3)))
    st.plotly_chart(fig, use_container_width=True)

elif menu == t['m2']:
    st.title(t['t2'])
    doc = st.text_area("List Nepokretnosti (Matrícula):", height=250)
    if st.button("Executar Auditoria IA"):
        if doc.strip():
            with st.spinner("..."):
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Realize análise técnica e jurídica deste imóvel em Montenegro: {doc}"}],
                    model="llama-3.1-8b-instant"
                )
                st.session_state['ultima_analise'] = res.choices[0].message.content
                st.markdown(st.session_state['ultima_analise'])

elif menu == t['m3']:
    st.title(t['t3'])
    servico = st.selectbox("Serviço:", ["Visto de Nômade Digital", "Cidadania por Investimento", "Abertura de Empresa (DOO)", "Compra de Imóveis"])
    st.info(f"Módulo: {servico} (2026).")

elif menu == t['m4']:
    st.title(t['t4'])
    dados_bi = pd.DataFrame({'Região': ['Budva', 'Tivat', 'Kotor'], 'ROI %': [7.5, 8.2, 6.9]})
    st.bar_chart(dados_bi.set_index('Região'))

elif menu == t['m5']:
    st.title(t['t5'])
    if 'ultima_analise' in st.session_state:
        senha_doc = st.text_input("Senha para o PDF (opcional):", type="password")
        pdf_data = gerar_pdf(st.session_state['ultima_analise'], senha=senha_doc)
        st.download_button(label="Baixar Relatório PDF", data=pdf_data, file_name="parecer_montenegro.pdf", mime="application/pdf")
        
        st.markdown("---")
        telefone = st.text_input("WhatsApp do Cliente:")
        if st.button("Enviar por WhatsApp"):
            if telefone:
                msg = "Parecer MontenegroProspec."
                if senha_doc: msg += f" Senha: {senha_doc}"
                link = f"https://wa.me/{telefone}?text={msg.replace(' ', '%20')}"
                st.markdown(f'<a href="{link}" target="_blank">Clique aqui para enviar</a>', unsafe_allow_html=True)
    else:
        st.warning("Realize a Due Diligence primeiro.")

# 7. RODAPÉ
st.markdown(f'<div class="footer">MONTENEGROPROSPEC | Desenvolvido por Genailma de Oliveira Couto • 2026</div>', unsafe_allow_html=True)