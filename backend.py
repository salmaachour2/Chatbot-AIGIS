import os
import mimetypes
import json
import base64
from dotenv import load_dotenv  # variable d'environnement (api)
import logging  # debug et suivi
import requests
import sqlite3
from datetime import datetime
import uuid  # Génération d’identifiants uniques pour les conversations/messages.

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger la clé OpenRouter depuis .env
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("Clé API OpenRouter absente. Ajoute OPENROUTER_API_KEY dans .env")

# Chargement des bases de connaissances
def load_json_kb(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

EUROCODES_KB = load_json_kb("knowledge_bases/eurocodes_kb.json")
ANOMALY_KB = load_json_kb("knowledge_bases/anomaly_kb.json")

AIGIS_SYSTEM_PROMPT = """
Tu es AIGIS, un chatbot spécialisé dans la santé des bâtiments et infrastructures.
Ta fonction principale est de détecter les anomalies (corrosion, fissures, béton écaillé, etc.)
et de fournir des conseils techniques conformes aux normes Eurocode.
Réponds toujours en français sauf si on te le demande autrement.
"""

def format_knowledge(kb):
    if not kb:
        return "Aucune information disponible."
    formatted = []
    for item in kb:
        if isinstance(item, dict):
            if 'type' in item and 'description' in item:
                formatted.append(f"{item['type']}: {item['description']}")
            elif 'name' in item and 'description' in item:
                formatted.append(f"{item['name']}: {item['description']}")
            elif 'title' in item and 'content' in item:
                formatted.append(f"{item['title']}: {item['content']}")
        elif isinstance(item, str):
            formatted.append(item)
    return "\n".join(formatted)

# -------------------
# Fonction pour interroger OpenRouter (texte ou texte+image)
# -------------------
def ask_openrouter(prompt, image_url=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    # Construire le contenu user selon qu'il y ait une image ou non
    if image_url:
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    else:
        user_content = [{"type": "text", "text": prompt}]
    data = {
        "model": "qwen/qwen-2.5-vl-7b-instruct:free",
        "messages": [
            {"role": "user", "content": user_content}
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        logger.error(f"Erreur API OpenRouter: {response.status_code} {response.text}")
        return f"Erreur API OpenRouter: {response.status_code} {response.text}"

# -------------------
# Chat texte seul avec intégration des bases de connaissances
# -------------------
def analyze_question(user_input=None):
    try:
        anomaly_knowledge = format_knowledge(ANOMALY_KB)
        eurocode_knowledge = format_knowledge(EUROCODES_KB)
        prompt = f"{AIGIS_SYSTEM_PROMPT}\nANOMALIES:\n{anomaly_knowledge}\nEUROCODES:\n{eurocode_knowledge}\nQUESTION:\n{user_input}"
        return ask_openrouter(prompt)
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {e}")
        return f"Erreur technique: {str(e)}"

# -------------------
# Analyse image avec texte
# -------------------
def analyze_image(image_path_or_url, user_text="Analyse cette image pour détecter les fissures et corrosion."):
    try:
        anomaly_knowledge = format_knowledge(ANOMALY_KB)
        eurocode_knowledge = format_knowledge(EUROCODES_KB)
        prompt = f"{AIGIS_SYSTEM_PROMPT}\nANOMALIES:\n{anomaly_knowledge}\nEUROCODES:\n{eurocode_knowledge}\n{user_text}"
        # Si c'est un chemin local, encoder en base64
        if os.path.isfile(image_path_or_url):
            with open(image_path_or_url, "rb") as img_file:
                img_bytes = img_file.read()
            mime_type, _ = mimetypes.guess_type(image_path_or_url)
            if mime_type is None:
                mime_type = "image/png"  # fallback si inconnu
            base64_str = base64.b64encode(img_bytes).decode("utf-8")
            image_url = f"data:{mime_type};base64,{base64_str}"
        else:
            image_url = image_path_or_url  # déjà une URL
        return ask_openrouter(prompt, image_url=image_url)
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse image: {e}")
        return None

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('aigis_chat.db')
    c = conn.cursor()
    # Table des conversations
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Table des messages
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            image BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    ''')
    conn.commit()
    conn.close()

# Créer une nouvelle conversation
def create_conversation(title="Nouvelle conversation"):
    conn = sqlite3.connect('aigis_chat.db')
    c = conn.cursor()
    conversation_id = str(uuid.uuid4())
    if not title:
        title = "Nouvelle conversation"
    c.execute('INSERT INTO conversations (id, title) VALUES (?, ?)', (conversation_id, title))
    conn.commit()
    conn.close()
    return conversation_id

# Nouvelle fonction pour mettre à jour le titre
def update_conversation_title(conversation_id, new_title):
    conn = sqlite3.connect("aigis_chat.db")
    cur = conn.cursor()
    cur.execute("UPDATE conversations SET title=? WHERE id=?", (new_title, conversation_id))
    conn.commit()
    conn.close()

# Ajouter un message à une conversation
def add_message(conversation_id, role, content, image=None):
    conn = sqlite3.connect('aigis_chat.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO messages (conversation_id, role, content, image) VALUES (?, ?, ?, ?)
    ''', (conversation_id, role, content, image))
    conn.commit()
    conn.close()

# Récupérer toutes les conversations
def get_conversations():
    conn = sqlite3.connect('aigis_chat.db')
    c = conn.cursor()
    c.execute('SELECT id, title, created_at FROM conversations ORDER BY created_at DESC')
    conversations = c.fetchall()
    conn.close()
    return conversations

# Récupérer les messages d'une conversation
def get_messages(conversation_id):
    conn = sqlite3.connect('aigis_chat.db')
    c = conn.cursor()
    c.execute('SELECT role, content, image FROM messages WHERE conversation_id = ? ORDER BY created_at', (conversation_id,))
    messages = c.fetchall()
    conn.close()
    return messages

# Supprimer une conversation
def delete_conversation(conv_id):
    conn = sqlite3.connect("aigis_chat.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM conversations WHERE id=?", (conv_id,))
    cur.execute("DELETE FROM messages WHERE conversation_id=?", (conv_id,))
    conn.commit()
    conn.close()

# Initialiser la base de données au démarrage
init_db()
