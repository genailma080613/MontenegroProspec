import streamlit as st
import pandas as pd
from groq import Groq
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io
import urllib.parse

# 1. Configuração e Estilo
st.set_page_config(page_title="Montenegro Prospec", page_icon="🇲🇪", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background: radial-gradient(circle at 10% 20%, #1a2a6c 0%, #2a4858 40%, #ffffff 100%); background-attachment: fixed; }
    .main .block-container { background-color: white; padding: 40px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
    .section-title { color: #1a2a6c; font-weight: 700; border-left: 6px solid #1a2a6c; padding-left: 20px; margin-bottom: 30px; text-transform: uppercase; }
    .metric-card { background: #f9f9f9; padding: 25px; border-radius: 16px; border-bottom: 5px solid #1a2a6c; }
    .btn-share { display: inline-flex; align-items: center; justify-content: center; padding: 12px; border-radius: 8px; text-decoration: none; color: white !important; font-weight: 600; width: 100%; margin-top: 10px; }
    .btn-wa { background-color: #25d366; } .btn-mail { background-color: #1a2a6c; }
    </style>
    """, unsafe_allow_html=True)

# --- IDIOMAS ---
languages = {
    "Português": {"nav": "Navegação", "roi": "Dashboard ROI", "legal": "Scanner de Matrículas", "visto": "Visto & Residência", "val": "Valor do Ativo (€)", "alg": "Aluguel Mensal (€)", "total": "Investimento Total", "grafico": "Comparativo: Investimento vs Lucro/Ano"},
    "Español": {"nav": "Navegación", "roi": "Dashboard ROI", "legal": "Escáner de Títulos", "visto": "Visa y Residencia", "val": "Valor del Activo (€)", "alg": "Alquiler Mensual (€)", "total": "Inversión Total", "grafico": "Comparativo: Inversión vs Lucro/Año"},
    "Crnogorski": {"nav": "Navigacija", "roi": "ROI Dashboard", "legal": "Scanner Nepokretnosti", "visto": "Viza i Boravak", "val": "Vrijednost (€)", "alg": "Mjesečna kirija (€)", "total": "Ukupna investicija", "grafico": "Poređenje: Investicija naspram Dobiti/Godišnje"}
}

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center; color:white;'>🇲🇪 MONTENEGRO PROSPEC</h2>", unsafe_allow_html=True)
    senha = st.text_input("Credencial", type="password")
    if st.button("Acessar"):
        if senha == st.secrets["PASSWORD"]: st.session_state.auth = True; st.rerun()
else:
    st.sidebar.markdown("### <i class='fas fa-globe'></i> Idioma")
    sel_lang = st.sidebar.selectbox("", list(languages.keys()))
    t = languages[sel_lang]
    st.sidebar.markdown("---")
    menu = st.sidebar.radio(t["nav"], [t["roi"], t["legal"], t["visto"], "📤 Exportar Relatório"])

    if menu == t["roi"]:
        st.markdown(f"<div class='section-title'>{t['roi']}</div>", unsafe_allow_html=True)
        c1, col_form = st.columns([1, 1])
        with c1:
            v_aq = st.number_input(t["val"], value=250000.0)
            a_men = st.number_input(t["alg"], value=1200.0)
        
        total = v_aq + (v_aq * 0.03) + 1500
        lucro_anual = a_men * 12
        roi = (lucro_anual / total) * 100
        st.session_state.dados = {"total": total, "roi": roi, "lucro": lucro_anual}

        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-card'><b>{t['total']}</b><h2>€ {total:,.2f}</h2></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'><b>Renda Anual</b><h2>€ {lucro_anual:,.2f}</h2></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card' style='border-color:#28a745'><b>ROI</b><h2 style='color:#28a745'>{roi:.2f}%</h2></div>", unsafe_allow_html=True)

        # --- GRÁFICO EM TEMPO REAL (RESTAURADO) ---
        st.markdown(f"#### {t['grafico']}")
        chart_data = pd.DataFrame({
            "Valores": [total, lucro_anual],
            "Categoria": ["Investimento Total", "Lucro Bruto Anual"]
        }).set_index("Categoria")
        st.bar_chart(chart_data)

    elif menu == t["legal"]:
        st.markdown(f"<div class='section-title'>{t['legal']}</div>", unsafe_allow_html=True)
        doc_text = st.text_area("Texto em Sérvio (List Nepokretnosti):", height=200)
        if st.button("Analisar Ônus"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            chat = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "user", "content": f"Analise: {doc_text}"}])
            st.write(chat.choices[0].message.content)

    elif menu == "📤 Exportar Relatório":
        st.markdown("<div class='section-title'>Exportação Segura</div>", unsafe_allow_html=True)
        senha_pdf = st.text_input("Senha PDF", value=st.secrets["PASSWORD"], type="password")
        if st.button("Gerar PDF"):
            packet = io.BytesIO(); can = canvas.Canvas(packet); can.drawString(100, 800, f"ROI: {st.session_state.dados['roi']:.2f}%"); can.save()
            packet.seek(0); reader = PdfReader(packet); writer = PdfWriter(); writer.add_page(reader.pages[0]); writer.encrypt(senha_pdf)
            output = io.BytesIO(); writer.write(output); st.session_state.pdf_ready = output.getvalue(); st.success("PDF Pronto!")
        
        if "pdf_ready" in st.session_state:
            st.download_button("Baixar PDF", st.session_state.pdf_ready, "prospec.pdf")
            msg = urllib.parse.quote(f"Resumo Montenegro: ROI de {st.session_state.dados['roi']:.2f}%")
            st.markdown(f'<a href="https://wa.me/?text={msg}" class="btn-share btn-wa">WhatsApp</a>', unsafe_allow_html=True)
            st.markdown(f'<a href="mailto:?body={msg}" class="btn-share btn-mail">E-mail</a>', unsafe_allow_html=True)

    if st.sidebar.button("Sair"): st.session_state.auth = False; st.rerun()