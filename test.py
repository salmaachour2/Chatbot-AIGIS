import requests
import os
from dotenv import load_dotenv
import json

# Charger la clé API depuis .env
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError("Clé API OpenRouter absente. Ajoute OPENROUTER_API_KEY dans .env")

def ask_openrouter(prompt, image_url=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Construire le contenu user selon qu'il y ait une image ou non
    if image_url:
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    else:
        user_content = [
            {"type": "text", "text": prompt}
        ]

    data = {
        "model": "qwen/qwen2.5-vl-72b-instruct:free",
        "messages": [
            {"role": "user", "content": user_content}
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Erreur API: {response.status_code} {response.text}"


if __name__ == "__main__":
    # Test texte seul
    texte = "Bonjour, peux-tu me donner des conseils sur l'entretien des bâtiments ?"
    print("Test texte seul :")
    print(ask_openrouter(texte))

    # Test texte + image
    texte_image = "Analyse cette image pour détecter les fissures et corrosion."
    image = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    print("\nTest texte + image :")
    print(ask_openrouter(texte_image, image_url=image))
