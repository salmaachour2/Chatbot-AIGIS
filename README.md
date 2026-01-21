# AIGIS - Assistant IA pour l'Analyse des Pathologies Structurelles

## Description

AIGIS est un assistant IA spécialisé dans l’analyse des pathologies structurelles du bâtiment, basé sur les normes Eurocodes et utilisant le modèle Google Gemini via LangChain.

---

## Structure du projet

- `aigis_core.py` : Contient la logique métier, les appels à l’API Google Gemini, la gestion des bases de connaissances.
- `app.py` : Interface utilisateur réalisée avec Streamlit, affichage, gestion des interactions.
- `knowledge_bases/` : Dossier contenant les fichiers JSON avec les bases de connaissance.

---

## Installation

1. Cloner ce dépôt
2. Créer un fichier `.env` avec votre clé API Google :

