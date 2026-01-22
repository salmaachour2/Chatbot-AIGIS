from datetime import datetime
import uuid
import streamlit as st
from backend import update_conversation_title
from backend import add_message, analyze_question, analyze_image, OPENROUTER_API_KEY, create_conversation, get_conversations, get_messages, delete_conversation
import base64
from io import BytesIO
from PIL import Image, UnidentifiedImageError

# ----------------------
# Configuration
# ----------------------
st.set_page_config(
    page_title="AIGIS | AI Structural Expert",
    layout="wide",
    page_icon="🔬",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# ----------------------
# CSS Professionnel Optimisé
# ----------------------
st.markdown("""
<style>
/* ============================================ VARIABLES ET CONFIGURATION GLOBALE ============================================ */
:root {
    --blue-dark: #1e3a8a;
    --blue-medium: #2563eb;
    --blue-light: #3b82f6;
    --blue-lighter: #60a5fa;
    --white: #ffffff;
    --gray-50: #f8fafc;
    --gray-100: #f1f5f9;
    --gray-200: #e2e8f0;
    --gray-300: #cbd5e1;
    --gray-700: #334155;
    --gray-900: #0f172a;
    --gradient-primary: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    --gradient-light: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
    --shadow-sm: 0 2px 8px rgba(30, 58, 138, 0.08);
    --shadow-md: 0 4px 16px rgba(30, 58, 138, 0.12);
    --shadow-lg: 0 8px 24px rgba(30, 58, 138, 0.16);
    --radius: 12px;
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Reset et Base */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--gradient-primary) !important;
    color: var(--white);
}

/* Suppression des espacements par défaut */
.stApp, main, header {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
header[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.98) !important;
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--gray-200) !important;
    height: 3.5rem !important;
}

/* Header Sidebar */
.sidebar-header {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--gray-200);
    display: flex;
     
    padding-left: 37px;               
}
.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.5rem;
            
}
.logo-icon {
    width: 44px;
    height: 44px;
    background: var(--gradient-primary);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: var(--shadow-md);
}
.logo-text {
    font-size: 24px;
    font-weight: 700;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

/* Titre de section */
.section-title {
    color: var(--gray-700);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 1.2rem 0 0.5rem;
    display: flex;
    align-items: center;
    gap: 8px;
    opacity: 0.8;
}

/* Container pour les conversations */
.conversation-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

/* Boutons de conversation */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
    margin-bottom: 2px !important;
    color: var(--gray-700) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    text-align: left !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
    position: relative;
    overflow: hidden;
}

/* ============================== SURVOL DES BOUTONS SIDEBAR ============================== */
/* Bouton Nouvelle Analyse */
.stSidebar .stButton > button:has(span:contains("Nouvelle Analyse")) {
    background: rgba(128,128,128,0.2) !important;
    border-radius: 12px !important;
    padding: 10px 12px !important;
    font-weight: 600 !important;
    text-align: left !important;
    transition: all 0.2s ease !important;
}
.stSidebar .stButton > button:has(span:contains("Nouvelle Analyse")):hover {
    background: rgba(128,128,128,0.3) !important;
}

/* Boutons de conversation */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: transparent !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(128,128,128,0.2) !important;
    border-radius: 12px !important;
}

/* Conversation sélectionnée */
/* Bouton sélectionné */
[data-testid="stSidebar"] [data-testid="stButton"] > button:focus-visible {
    background: rgba(128, 128, 128, 0.22) !important;
    border-radius: 12px !important;
    padding: 10px 12px !important;
    color: var(--gray-900) !important;
    font-weight: 600 !important;
    outline: none !important;
}
/* Empêche disparition au hover */
[data-testid="stSidebar"] [data-testid="stButton"] > button:focus-visible:hover {
    background: rgba(128, 128, 128, 0.22) !important;
}

/* Badges date/heure - Design minimaliste */
.conversation-meta {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-top: 4px;
    padding-left: 12px;
}
.time-badge, .date-badge {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 10px;
    padding: 0;
    color: var(--gray-700);
    opacity: 0.7;
    font-weight: 400;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid var(--gray-200);
    margin: 1rem 0;
}

/* ============================================ CONTENU PRINCIPAL ============================================ */
.main-header {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
}
.main-title {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    letter-spacing: -1px;
}
.main-subtitle {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.1rem;
    font-weight: 500;
}

/* Badges Eurocode */
.eurocode-container {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.eurocode-badge {
    background: rgba(255, 255, 255, 0.2);
    color: var(--white);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(5px);
}

/* Panneau de saisie */
.input-panel {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.25);
    box-shadow: var(--shadow-lg);
    margin-bottom: 1.5rem;
}
.input-title {
    color: var(--white);
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Champs de formulaire */
.stTextArea textarea {
    background: rgba(255, 255, 255, 0.95) !important;
    color: var(--gray-900) !important;
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: var(--radius) !important;
    font-size: 15px !important;
    padding: 12px !important;
}
.stTextArea textarea:focus {
    border-color: var(--white) !important;
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.2) !important;
}
.stFileUploader {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 2px dashed rgba(255, 255, 255, 0.5) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}
.stFileUploader:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: var(--white) !important;
}
.stFileUploader button {
    background: rgba(255, 255, 255, 0.85) !important;
    color: #000000 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    padding: 6px 14px !important;
    font-size: 13px !important;
    transition: background 0.2s ease, transform 0.2s ease !important;
}
.stFileUploader button:hover {
    background: rgba(255, 255, 255, 0.95) !important;
    transform: translateY(-1px);
}

/* ============================================ BULLES DE CHAT ============================================ */
.chat-bubble {
    padding: 1.25rem 1.5rem;
    margin: 1.25rem 0;
    border-radius: 18px;
    max-width: 85%;
    line-height: 1.6;
    animation: slideIn 0.4s ease-out;
    position: relative;
}
@keyframes slideIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.user-bubble {
    background: rgba(255, 255, 255, 0.95) !important;
    color: var(--gray-900) !important;
    border: 1px solid rgba(255, 255, 255, 0.3);
    margin-left: auto;
    box-shadow: var(--shadow-md);
}
.assistant-bubble {
    background: rgba(255, 255, 255, 0.98) !important;
    color: var(--gray-900) !important;
    border-left: 4px solid var(--blue-light);
    margin-right: auto;
    box-shadow: var(--shadow-lg);
}
.message-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--gray-200);
}
.message-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    background: var(--gradient-primary);
    color: var(--white);
}
.message-author {
    font-weight: 600;
    color: var(--gray-900);
    font-size: 15px;
}
.chat-image {
    max-width: 200px;
    border-radius: var(--radius);
    margin-top: 12px;
    border: 2px solid var(--gray-200);
    box-shadow: var(--shadow-md);
}

/* ============================================ SCROLLBAR ============================================ */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
}

/* ============================================ FOOTER ============================================ */
.footer {
    text-align: center;
    padding: 2rem 1rem;
    color: rgba(255, 255, 255, 0.7);
    font-size: 13px;
    margin-top: 3rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}
.footer-title {
    font-weight: 600;
    margin-bottom: 0.5rem;
}

/* ============================================ RESPONSIVE ============================================ */
@media (max-width: 768px) {
    .main-title {
        font-size: 2rem;
    }
    .chat-bubble {
        max-width: 95%;
    }
}

/* Popup de suppression */
.popup-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}
.popup-content {
    background: var(--white);
    border-radius: 20px;
    padding: 2rem;
    max-width: 400px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.popup-title {
    color: var(--gray-900);
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
}
.popup-message {
    color: var(--gray-700);
    margin-bottom: 1.5rem;
    line-height: 1.6;
}

/* ============================================ BOUTON 🚀 ANALYSER AVEC AIGIS (BLANC / TEXTE NOIR) ============================================ */
.stButton > button[kind="primary"] {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-size: 16px !important;
    border: none !important;
    width: 100% !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
    transition: all 0.25s ease !important;
    cursor: pointer;
    backdrop-filter: blur(6px);
}
.stButton > button[kind="primary"]:hover {
    background-color: rgba(255, 255, 255, 0.3) !important;
    color: #ffffff !important;
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.18) !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------
# Initialisation du State
# ----------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis AIGIS, votre expert en pathologies structurelles. Décrivez un problème ou téléversez une image pour une analyse technique conforme aux Eurocodes."}
    ]
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = None
if "conversations" not in st.session_state:
    st.session_state.conversations = get_conversations()
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = str(uuid.uuid4())
if "text_area_key" not in st.session_state:
    st.session_state.text_area_key = str(uuid.uuid4())
if "delete_popup_opened" not in st.session_state:
    st.session_state.delete_popup_opened = False
if "conversation_to_delete" not in st.session_state:
    st.session_state.conversation_to_delete = None
if "sidebar_visible" not in st.session_state:
    st.session_state.sidebar_visible = True
if "show_search" not in st.session_state:
    st.session_state.show_search = False

if "search_query" not in st.session_state:
    st.session_state.search_query = ""


# ----------------------
# Fonctions utilitaires
# ----------------------
def create_new_conversation():
    new_convo_id = create_conversation("Nouvelle conversation")
    st.session_state.current_conversation = new_convo_id
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis AIGIS, votre expert en pathologies structurelles. Décrivez un problème ou téléversez une image pour une analyse technique conforme aux Eurocodes."}
    ]
    st.session_state.uploaded_image = None
    st.session_state.file_uploader_key = str(uuid.uuid4())
    st.session_state.conversations = get_conversations()
    st.rerun()
# ----------------------
# Sidebar
# ----------------------
with st.sidebar:
    # Header avec logo
    st.markdown("""
    <div class="sidebar-header">
        <div class="logo">
            <div class="logo-icon">🔬</div>
            <div class="logo-text">AIGIS</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Bouton nouvelle conversation
    if st.button("➕ Nouvelle Analyse", key="new_convo", use_container_width=True, type="secondary"):
        create_new_conversation()
    # Bouton recherche
    if st.button("🔍 Recherche chats", key="search_toggle", use_container_width=True, type="secondary"):
        st.session_state.delete_popup_opened = False
        st.session_state.show_search = not st.session_state.show_search
        

    
    
    st.markdown("<hr>", unsafe_allow_html=True)

    # Champ de recherche
    if st.session_state.show_search:
        st.session_state.search_query = st.text_input(
            "",
        placeholder="🔍 Rechercher par titre...",
        value=st.session_state.search_query,
        label_visibility="collapsed"
    )
    # Liste des conversations
    st.markdown('<div class="section-title">📁 Historique</div>', unsafe_allow_html=True)
    conversations = st.session_state.conversations
    if st.session_state.search_query:
        conversations = [
            conv for conv in conversations
            if st.session_state.search_query.lower() in (conv[1] or "").lower()
        ]
    if conversations:
        for conv_id, title, created_at in conversations:
            try:
                date_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                time_str = date_obj.strftime("%H:%M")
                date_str = date_obj.strftime("%d/%m")
            except:
                time_str = "00:00"
                date_str = "Aujourd\'hui"

            is_active = st.session_state.current_conversation == conv_id
            col1, col2 = st.columns([8, 2])
            with col1:
                button_type = "secondary"
                if st.button(title, key=f"conv_{conv_id}", use_container_width=True, type=button_type):
                    st.session_state.current_conversation = conv_id
                    st.session_state.show_search = False
                    st.session_state.search_query = ""
                    messages = get_messages(conv_id)
                    st.session_state.messages = [{"role": role, "content": content, "image": image} for role, content, image in messages]
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{conv_id}", type="tertiary", help="Supprimer"):
                    st.session_state.delete_popup_opened = True
                    st.session_state.conversation_to_delete = conv_id


            # Métadonnées en ligne
            st.markdown(f'''
            <div class="conversation-meta">
                <span class="time-badge">🕒 {time_str}</span>
                <span style="color: var(--gray-300);">•</span>
                <span class="date-badge">📅 {date_str}</span>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("Aucune conversation pour le moment.")

# ----------------------
# Popup de suppression
# ----------------------
if st.session_state.delete_popup_opened:

    @st.dialog("⚠️ Confirmer la suppression")
    def confirm_delete():
        st.markdown(
            "Êtes-vous sûr de vouloir supprimer cette conversation ?  \n"
            "**Cette action est irréversible.**"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Supprimer", use_container_width=True):
                delete_conversation(st.session_state.conversation_to_delete)
                st.session_state.conversations = get_conversations()

                if st.session_state.current_conversation == st.session_state.conversation_to_delete:
                    create_new_conversation()

                st.session_state.delete_popup_opened = False
                st.session_state.conversation_to_delete = None
                st.rerun()

        with col2:
            if st.button("❌ Annuler", use_container_width=True):
                st.session_state.delete_popup_opened = False
                st.session_state.conversation_to_delete = None
                st.rerun()

    confirm_delete()

    # 🔐 IMPORTANT : empêcher réouverture automatique
    st.session_state.delete_popup_opened = False




# ----------------------
# Contenu Principal
# ----------------------
# Header
st.markdown("""
<div class="main-header">
    <div class="main-title">🏗️ AIGIS</div>
    <div class="main-subtitle">Intelligence Structurelle pour Pathologies du Bâtiment</div>
    <div class="eurocode-container">
        <span class="eurocode-badge">EUROCODE 2</span>
        <span class="eurocode-badge">EUROCODE 6</span>
        <span class="eurocode-badge">EUROCODE 8</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Zone de saisie
st.markdown("""
<div class="input-panel">
    <div class="input-title">🔍 Analyse de Pathologie Structurelle</div>
</div>
""", unsafe_allow_html=True)

user_input = st.text_area(
    "Description",
    value="",
    placeholder="Décrivez la pathologie structurelle observée (fissures, corrosion, déformation, etc.)...",
    key=st.session_state.text_area_key,
    label_visibility="collapsed",
    height=120
)

uploaded_file = st.file_uploader(
    "Image",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=False,
    key=st.session_state.file_uploader_key,
    label_visibility="collapsed"
)

if uploaded_file is not None:
    try:
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()
        Image.open(BytesIO(image_bytes)).verify()
        st.session_state.uploaded_image = uploaded_file
        col_img, col_info = st.columns([1,3])
        with col_img:
            st.image(image_bytes, width=150)
        with col_info:
            st.success("✅ Image prête pour l'analyse")
    except Exception as e:
        st.error(f"❌ Erreur de lecture d'image: {str(e)}")
        st.session_state.uploaded_image = None

# Bouton Analyser
if st.button("🚀 Analyser avec AIGIS", key="send_button", use_container_width=True, type="primary"):
    if user_input or uploaded_file is not None:
        with st.spinner("🔮 Analyse en cours..."):
            try:
                if "current_conversation" not in st.session_state:
                    st.session_state["current_conversation"] = create_conversation()
                conv_id = st.session_state["current_conversation"]
                preview_title = None
                if user_input:
                    preview_title = user_input.strip().split("\n")[0][:40]
                elif uploaded_file:
                    preview_title = "Analyse d'image"
                if preview_title:
                    update_conversation_title(conv_id, preview_title)
                
                if uploaded_file is not None:
                    uploaded_file.seek(0)
                    image_bytes = uploaded_file.read()
                    base64_str = base64.b64encode(image_bytes).decode("utf-8")
                    image_url = f"data:image/jpeg;base64,{base64_str}"
                    user_text = user_input if user_input else "Analyse cette image pour détecter les pathologies structurelles."
                    add_message(st.session_state.current_conversation, "user", user_text, base64_str)
                    analysis = analyze_image(image_url, user_text)
                    add_message(st.session_state.current_conversation, "assistant", analysis)
                elif user_input:
                    add_message(st.session_state.current_conversation, "user", user_input)
                    content = analyze_question(user_input)
                    add_message(st.session_state.current_conversation, "assistant", content)

                messages = get_messages(st.session_state.current_conversation)
                st.session_state.messages = [{"role": role, "content": content, "image": image} for role, content, image in messages]
                st.session_state.text_area_key = str(uuid.uuid4())
                st.session_state.file_uploader_key = str(uuid.uuid4())
                st.session_state.uploaded_image = None
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    else:
        st.warning("⚠️ Veuillez saisir du texte ou télécharger une image.")

# ----------------------
# Affichage des messages
# ----------------------
st.markdown("<div style='margin-top: 2rem'></div>", unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        content_html = f"<p>{msg['content']}</p>"
        if msg.get("image"):
            content_html += f'<img src="data:image/jpeg;base64,{msg["image"]}" class="chat-image">'
        st.markdown(f"""
        <div class='chat-bubble user-bubble'>
            <div class='message-header'>
                <div class='message-avatar'>👤</div>
                <div class='message-author'>Ingénieur</div>
            </div>
            {content_html}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='chat-bubble assistant-bubble'>
            <div class='message-header'>
                <div class='message-avatar'>🏗️</div>
                <div class='message-author'>AIGIS Expert</div>
            </div>
            <div>{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

# ----------------------
# Footer
# ----------------------
st.markdown("""
<div class="footer">
    <div class="footer-title">AIGIS • Système Expert en Pathologies Structurelles</div>
    <div>🔒 Analyse sécurisée • 📊 Rapports techniques • 🏗️ Conformité Eurocode</div>
</div>
""", unsafe_allow_html=True)
