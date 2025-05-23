# 🌦️ Meteo-Weather

**Meteo-Weather** est une application web simple permettant de consulter la météo actuelle et les prévisions météo pour n'importe quelle ville dans le monde.  
Développée avec ❤️ par [Mathieux83](https://github.com/Mathieux83).

---

## 🚀 Fonctionnalités

- Recherche météo par nom de ville
- Affichage :
  - Température actuelle
  - Conditions météorologiques (ensoleillé, nuageux, pluie, etc.)
  - Température minimale et maximale
  - Vitesse du vent
  - Graphiques intégré
- Interface responsive et intuitive
- Données météo en temps réel via une API

---

## 📸 Screnshots
 
![Demo1](https://github.com/user-attachments/assets/bdbbb778-5bd1-434b-910d-89a92e5498c1)
![Demo2](https://github.com/user-attachments/assets/6a04ad03-e8b2-48d3-9506-e91df5365da0)
![Demo3](https://github.com/user-attachments/assets/a927fc6f-bb02-4faf-9ee8-a7680548153a)
![Demo4](https://github.com/user-attachments/assets/80ee492e-2fb3-4ec9-9a56-feb5b7398a92)



---

## 🛠️ Technologies utilisées

- Python
- [API OpenWeatherMap](https://openweathermap.org/api)

---

## 📦 Installation locale

1. **Clone le dépôt :**
   ```
   git clone https://github.com/Mathieux83/Meteo-Weather.git
   ```

2. **Accède au dossier du projet :**
   ```
   cd Meteo-Weather
   ```

3. **Executer `main.py` dans ton terminal avec Python.**

---

## 🔑 Configuration API

Le projet utilise l'API de **OpenWeatherMap**. Pour obtenir ta propre clé API :

1. Crée un compte sur [OpenWeatherMap](https://openweathermap.org/).
2. Récupère ta **clé API**.
3. Dans le fichier `.env`, remplace la clé existante par la tienne :
   ```
   API_KEY='VOTRE_CLE_API_ICI'
   ```
4. Faire parreil pour ta ville dans le même fichier :
   ```
   VILLE="TA_VILLE"
   ```
---

## Créer le .exe

Vous pouvez aussi créer un .exe avec `auto-py-to-exe`

1. Spécifier le script donc `main.py`
2. Choisir : `One File` et `Window Based`
3. Dans `Additionals Files` ajouter le fichier `.env` que vous avez configurer avec votre ``API`` et votre ``VILLE``
4. (Optional) Vous pouvez ajouter un fichier .ico pour l'icone de votre .exe que vous allez créer

---
## 📄 Licence

Ce projet est open-source sous licence [MIT](LICENSE).

---

## 🤝 Contribuer

Les contributions sont les bienvenues !  
N'hésite pas à ouvrir des **issues** ou à soumettre des **pull requests** pour améliorer le projet.

---

## 📬 Contact

Créé par **Mathieux83** — [Voir mon profil GitHub](https://github.com/Mathieux83)  
Pour toute question, suggestion ou collaboration, n'hésite pas à me contacter !
