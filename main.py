import tkinter as tk
from tkinter import ttk, messagebox
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
from PIL import Image, ImageTk
import io
import urllib.request
import os
import dotenv
import sys

# API settings
dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")
VILLE = os.getenv("VILLE")

class AppMeteo:
    def __init__(self, root):
        self.root = root
        self.root.title("Application Météo")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")
        
        # Make the root window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Paramètres API
        self.api_key = API_KEY
        self.ville_actuelle = VILLE
        
        # Variables pour stocker les données
        self.meteo_actuelle = None
        self.previsions = None
        
        # Add refresh interval in milliseconds (5 minutes = 300000ms)
        self.refresh_interval = 300000
        self._refresh_job = None  # Pour garder la référence du job after
        
        # Mise en place de l'interface
        self.creer_interface()
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_change)

        # Initialiser le scroll wheel
        self.forecast_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Start auto-refresh
        self.start_auto_refresh()
    
    def start_auto_refresh(self):
        """Start the automatic refresh timer"""
        self.refresh_data()
        # Cancel previous job if any
        if self._refresh_job is not None:
            self.root.after_cancel(self._refresh_job)
        self._refresh_job = self.root.after(self.refresh_interval, self.start_auto_refresh)
    
    def set_refresh_interval(self, event=None):
        """Set refresh interval from dropdown and restart timer"""
        interval_str = self.refresh_interval_var.get()
        interval_map = {
            "30 sec": 30000,
            "1 min": 60000,
            "5 min": 300000,
            "10 min": 600000,
            "30 min": 1800000,
            "1 h": 3600000
        }
        self.refresh_interval = interval_map.get(interval_str, 300000)
        # Restart auto-refresh with new interval
        self.start_auto_refresh()
    
    def refresh_data(self):
        """Refresh weather data"""
        if self.ville_actuelle:
            # Update status bar
            self.status_bar.config(text=f"Actualisation des données pour {self.ville_actuelle}...")
            self.root.update()
            
            try:
                # Get new data
                self.meteo_actuelle = self.obtenir_meteo_actuelle(self.ville_actuelle)
                self.previsions = self.obtenir_previsions(self.ville_actuelle)
                
                # Update display
                if self.meteo_actuelle and self.previsions:
                    self.afficher_meteo_actuelle()
                    self.afficher_previsions()
                    self.creer_graphiques()
                    current_time = datetime.now().strftime("%H:%M:%S")
                    self.status_bar.config(text=f"Données actualisées à {current_time}")
                else:
                    self.status_bar.config(text="Erreur lors de l'actualisation des données")
            
            except Exception as e:
                self.status_bar.config(text=f"Erreur lors de l'actualisation: {str(e)}")
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.forecast_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_tab_change(self, event):
        """Handle tab changes and mousewheel binding"""
        tab = self.notebook.select()
        if self.notebook.index(tab) == 0:  # Si c'est l'onglet des prévisions
            self.forecast_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:
            self.forecast_canvas.unbind_all("<MouseWheel>")
    
    def creer_interface(self):
        # --- Use grid on root to separate content and status bar ---
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        # Main vertical container (row 0)
        self.vertical_container = tk.Frame(self.root, bg="#f0f0f0")
        self.vertical_container.grid(row=0, column=0, sticky="nsew")

        # Frame principale (inside vertical_container)
        main_frame = tk.Frame(self.vertical_container, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame supérieure pour la recherche et la météo actuelle
        top_frame = tk.Frame(main_frame, bg="#f0f0f0")
        top_frame.pack(fill=tk.X, pady=10)
        
        # Zone de recherche
        search_frame = tk.Frame(top_frame, bg="#f0f0f0")
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.search_entry = tk.Entry(search_frame, width=30, font=("Arial", 12))
        self.search_entry.insert(0, self.ville_actuelle)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        search_button = tk.Button(search_frame, text="Rechercher", command=self.rechercher_ville, 
                                 bg="#4a7abc", fg="white", font=("Arial", 10, "bold"))
        search_button.pack(side=tk.LEFT, padx=5)

        # --- Ajout du menu déroulant pour l'intervalle de rafraîchissement ---
        tk.Label(search_frame, text="Rafraîchissement :", bg="#f0f0f0", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 2))
        self.refresh_interval_var = tk.StringVar()
        self.refresh_interval_var.set("5 min")
        refresh_options = ["30 sec", "1 min", "5 min", "10 min", "30 min", "1 h"]
        refresh_menu = ttk.Combobox(search_frame, textvariable=self.refresh_interval_var, values=refresh_options, width=7, state="readonly")
        refresh_menu.pack(side=tk.LEFT, padx=2)
        refresh_menu.bind("<<ComboboxSelected>>", self.set_refresh_interval)
        # ---------------------------------------------------------------

        # Frame pour la météo actuelle - modified to center content
        self.current_weather_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.GROOVE)
        self.current_weather_frame.pack(fill=tk.X, pady=10)
        
        # Container frame for centering
        center_container = tk.Frame(self.current_weather_frame, bg="white")
        center_container.pack(expand=True)
        
        # Titre pour la météo actuelle
        self.current_title = tk.Label(center_container, text="", font=("Arial", 14, "bold"), bg="white")
        self.current_title.pack(pady=5)
        
        # Contenu de la météo actuelle (sera rempli dynamiquement)
        self.current_content = tk.Frame(center_container, bg="white")
        self.current_content.pack(padx=10, pady=5)
        
        # Frame pour l'icône et la température
        self.icon_temp_frame = tk.Frame(self.current_content, bg="white")
        self.icon_temp_frame.pack(side=tk.LEFT, padx=10)
        
        self.weather_icon = tk.Label(self.icon_temp_frame, bg="white")
        self.weather_icon.pack()
        
        self.temp_label = tk.Label(self.icon_temp_frame, text="", font=("Arial", 24), bg="white")
        self.temp_label.pack()
        
        # Frame pour les détails météo
        self.details_frame = tk.Frame(self.current_content, bg="white")
        self.details_frame.pack(side=tk.LEFT, padx=20)
        
        # Notebook pour les prévisions et graphiques
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Onglet pour les prévisions des 5 prochains jours
        self.forecast_frame = tk.Frame(self.notebook)
        self.notebook.add(self.forecast_frame, text="Prévisions 5 jours")
        
        # Make forecast_frame responsive
        self.forecast_frame.grid_rowconfigure(0, weight=1)
        self.forecast_frame.grid_columnconfigure(0, weight=1)
        
        # Create main container for centering with grid
        forecast_container = tk.Frame(self.forecast_frame, bg="white")
        forecast_container.grid(row=0, column=0, sticky="nsew")
        forecast_container.grid_rowconfigure(0, weight=1)
        forecast_container.grid_columnconfigure(0, weight=1)
        
        # Create a canvas with scrollbar for the forecast
        self.forecast_canvas = tk.Canvas(forecast_container, bg="white")
        forecast_scrollbar = ttk.Scrollbar(forecast_container, orient="vertical", command=self.forecast_canvas.yview)
        
        # Use grid for both canvas and scrollbar
        self.forecast_canvas.grid(row=0, column=0, sticky="nsew")
        forecast_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.forecast_canvas.configure(yscrollcommand=forecast_scrollbar.set)
        
        # Create a frame inside canvas to hold the content
        self.forecast_inner_frame = tk.Frame(self.forecast_canvas, bg="white")
        self.forecast_canvas_window = self.forecast_canvas.create_window(
            (0, 0), 
            window=self.forecast_inner_frame, 
            anchor='nw',
            tags='inner_frame'
        )
        
        # Make the inner frame expand
        self.forecast_inner_frame.grid_columnconfigure(0, weight=1)
        
        # Configure the canvas to resize with the window
        def configure_canvas(event):
            # Update the width of canvas
            canvas_width = event.width
            self.forecast_canvas.itemconfig(
                self.forecast_canvas_window,
                width=canvas_width
            )
        
        def configure_scroll_region(event):
            self.forecast_canvas.configure(scrollregion=self.forecast_canvas.bbox("all"))
        
        self.forecast_canvas.bind('<Configure>', configure_canvas)
        self.forecast_inner_frame.bind('<Configure>', configure_scroll_region)
        
        # Onglet pour les graphiques
        self.graph_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.graph_frame, text="Graphiques")
        
        # Statut bar (row 1, always visible at the bottom)
        self.status_bar = tk.Label(
            self.root,
            text="Prêt",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#e0e0e0",
            font=("Arial", 10)
        )
        self.status_bar.grid(row=1, column=0, sticky="ew")

        # Charger les données initiales
        self.rechercher_ville()
    
    def rechercher_ville(self):
        """Récupère les données météo pour la ville saisie"""
        ville = self.search_entry.get()
        if not ville:
            messagebox.showerror("Erreur", "Veuillez entrer un nom de ville.")
            return
        
        self.ville_actuelle = ville
        self.refresh_data()
    
    def obtenir_meteo_actuelle(self, ville):
        """Récupère les données météo actuelles via l'API"""
        url = f"https://api.openweathermap.org/data/2.5/weather?q={ville}&appid={self.api_key}&units=metric&lang=fr"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur lors de la récupération des données actuelles: {response.status_code}")
            return None
    
    def obtenir_previsions(self, ville):
        """Récupère les prévisions sur 5 jours via l'API"""
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={ville}&appid={self.api_key}&units=metric&lang=fr"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur lors de la récupération des prévisions: {response.status_code}")
            return None
    
    def afficher_meteo_actuelle(self):
        """Affiche les données météo actuelles dans l'interface"""
        if not self.meteo_actuelle:
            return
        
        # Nettoyer les widgets existants
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Mettre à jour le titre
        self.current_title.config(text=f"Météo actuelle à {self.meteo_actuelle['name']}, {self.meteo_actuelle.get('sys', {}).get('country', '')}")
        
        # Mettre à jour l'icône météo
        icon_code = self.meteo_actuelle['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        try:
            with urllib.request.urlopen(icon_url) as u:
                raw_data = u.read()
            img = Image.open(io.BytesIO(raw_data))
            img = img.resize((100, 100), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.weather_icon.config(image=photo)
            self.weather_icon.image = photo  # Garder une référence
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône: {e}")
            self.weather_icon.config(image="")
        
        # Mettre à jour la température
        self.temp_label.config(text=f"{self.meteo_actuelle['main']['temp']:.1f}°C")
        
        # Ajouter les détails météo
        details = [
            ("Condition", self.meteo_actuelle['weather'][0]['description'].capitalize()),
            ("Ressenti", f"{self.meteo_actuelle['main']['feels_like']:.1f}°C"),
            ("Min/Max", f"{self.meteo_actuelle['main']['temp_min']:.1f}°C / {self.meteo_actuelle['main']['temp_max']:.1f}°C"),
            ("Humidité", f"{self.meteo_actuelle['main']['humidity']}%"),
            ("Pression", f"{self.meteo_actuelle['main']['pressure']} hPa"),
            ("Vent", f"{self.meteo_actuelle['wind']['speed']} m/s"),
            ("Visibilité", f"{self.meteo_actuelle.get('visibility', 0) / 1000:.1f} km")
        ]
        
        # Si disponible, ajouter les précipitations
        if 'rain' in self.meteo_actuelle:
            details.append(("Pluie (1h)", f"{self.meteo_actuelle['rain'].get('1h', 0)} mm"))
        if 'snow' in self.meteo_actuelle:
            details.append(("Neige (1h)", f"{self.meteo_actuelle['snow'].get('1h', 0)} mm"))
        
        # Afficher les détails
        for i, (label, value) in enumerate(details):
            tk.Label(self.details_frame, text=f"{label}:", font=("Arial", 10, "bold"), bg="white").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            tk.Label(self.details_frame, text=value, font=("Arial", 10), bg="white").grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
    
    def traiter_previsions(self):
        """Traite les données de prévisions pour l'affichage et les graphiques"""
        if not self.previsions:
            return None
        
        liste_previsions = self.previsions['list']
        resultats = []
        
        for prevision in liste_previsions:
            date = datetime.fromtimestamp(prevision['dt'])
            temp = prevision['main']['temp']
            ressenti = prevision['main']['feels_like']
            description = prevision['weather'][0]['description']
            icon = prevision['weather'][0]['icon']
            humidite = prevision['main']['humidity']
            pression = prevision['main']['pressure']
            vitesse_vent = prevision['wind']['speed']
            direction_vent = prevision['wind'].get('deg', 0)
            
            # Précipitations (si disponibles)
            pluie = prevision.get('rain', {}).get('3h', 0) if 'rain' in prevision else 0
            neige = prevision.get('snow', {}).get('3h', 0) if 'snow' in prevision else 0
            
            resultats.append({
                'date': date,
                'temperature': temp,
                'ressenti': ressenti,
                'description': description,
                'icon': icon,
                'humidite': humidite,
                'pression': pression,
                'vitesse_vent': vitesse_vent,
                'direction_vent': direction_vent,
                'pluie': pluie,
                'neige': neige
            })
        
        df = pd.DataFrame(resultats)
        df['jour'] = df['date'].dt.date
        df['heure'] = df['date'].dt.hour
        
        return df
    
    def afficher_previsions(self):
        """Affiche les prévisions dans l'onglet des prévisions"""
        # Nettoyer les widgets existants
        for widget in self.forecast_inner_frame.winfo_children():
            widget.destroy()
        
        # Traitement des prévisions
        df = self.traiter_previsions()
        if df is None:
            return
        
        # Obtenir les jours uniques pour l'affichage
        jours_uniques = df['jour'].unique()
        
        # Container principal avec grid
        main_container = tk.Frame(self.forecast_inner_frame, bg="white")
        main_container.grid(row=0, column=0, sticky="nsew", padx=20)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Créer une frame pour chaque jour
        for i, jour in enumerate(jours_uniques):
            # Frame pour ce jour
            jour_frame = tk.Frame(main_container, bg="white", bd=1, relief=tk.RIDGE)
            jour_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            jour_frame.grid_columnconfigure(0, weight=1)
            
            # Afficher la date
            date_str = jour.strftime("%A %d %B").capitalize()
            date_label = tk.Label(jour_frame, text=date_str, font=("Arial", 12, "bold"), bg="white")
            date_label.pack(fill=tk.X, padx=5, pady=5)
            
            # Frame pour contenir les heures avec centrage
            heures_container = tk.Frame(jour_frame, bg="white")
            heures_container.pack(fill=tk.X, padx=5, pady=5)
            
            heures_frame = tk.Frame(heures_container, bg="white")
            heures_frame.pack(expand=True, anchor='center')
            
            # Filtrer pour ce jour
            df_jour = df[df['jour'] == jour]
            
            # Ajouter les prévisions pour chaque tranche horaire
            for j, (_, prevision) in enumerate(df_jour.iterrows()):
                heure_frame = tk.Frame(heures_frame, bg="white", width=100)
                heure_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
                
                # Heure
                heure_label = tk.Label(heure_frame, text=f"{prevision['date'].strftime('%H:%M')}", font=("Arial", 10), bg="white")
                heure_label.pack()
                
                # Icône météo
                icon_code = prevision['icon']
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
                try:
                    with urllib.request.urlopen(icon_url) as u:
                        raw_data = u.read()
                    img = Image.open(io.BytesIO(raw_data))
                    img = img.resize((50, 50), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    icon_label = tk.Label(heure_frame, image=photo, bg="white")
                    icon_label.image = photo  # Garder une référence
                    icon_label.pack()
                except Exception as e:
                    print(f"Erreur lors du chargement de l'icône: {e}")
                    
                # Température
                temp_label = tk.Label(heure_frame, text=f"{prevision['temperature']:.1f}°C", font=("Arial", 10), bg="white")
                temp_label.pack()
                
                # Description
                desc_label = tk.Label(heure_frame, text=prevision['description'], font=("Arial", 8), bg="white", wraplength=80)
                desc_label.pack()
            
            # Ajouter un résumé du jour
            resume_frame = tk.Frame(jour_frame, bg="#f5f5f5")
            resume_frame.pack(fill=tk.X, padx=5, pady=5)
            
            temp_min = df_jour['temperature'].min()
            temp_max = df_jour['temperature'].max()
            conditions = df_jour['description'].value_counts().idxmax()
            
            resume_label = tk.Label(
                resume_frame,
                text=f"Résumé : {conditions.capitalize()} - Min {temp_min:.1f}°C / Max {temp_max:.1f}°C",
                font=("Arial", 10, "italic"),
                bg="#f5f5f5"
            )
            resume_label.pack()
    
    def creer_graphiques(self):
        """Crée les graphiques météo dans l'onglet Graphiques"""
        # Nettoyer les anciens graphiques
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        df = self.traiter_previsions()
        if df is None:
            return
        
        # Préparer la figure matplotlib
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.tight_layout(pad=4)
        
        # Graphique Température
        axs[0, 0].plot(df['date'], df['temperature'], label='Température (°C)', color='tab:red')
        axs[0, 0].plot(df['date'], df['ressenti'], label='Ressenti (°C)', color='tab:orange', linestyle='--')
        axs[0, 0].set_title("Évolution de la température")
        axs[0, 0].set_xlabel("Date/Heure")
        axs[0, 0].set_ylabel("Température (°C)")
        axs[0, 0].legend()
        axs[0, 0].grid(True)
        
        # Graphique Humidité
        axs[0, 1].plot(df['date'], df['humidite'], label='Humidité (%)', color='tab:blue')
        axs[0, 1].set_title("Évolution de l'humidité")
        axs[0, 1].set_xlabel("Date/Heure")
        axs[0, 1].set_ylabel("Humidité (%)")
        axs[0, 1].grid(True)
        
        # Graphique Vent
        axs[1, 0].plot(df['date'], df['vitesse_vent'], label='Vitesse du vent (m/s)', color='tab:green')
        axs[1, 0].set_title("Vitesse du vent")
        axs[1, 0].set_xlabel("Date/Heure")
        axs[1, 0].set_ylabel("Vitesse (m/s)")
        axs[1, 0].grid(True)
        
        # Graphique Pluie/Neige
        axs[1, 1].bar(df['date'], df['pluie'], label='Pluie (mm)', color='tab:cyan')
        axs[1, 1].bar(df['date'], df['neige'], label='Neige (mm)', color='tab:gray', bottom=df['pluie'])
        axs[1, 1].set_title("Précipitations")
        axs[1, 1].set_xlabel("Date/Heure")
        axs[1, 1].set_ylabel("Quantité (mm)")
        axs[1, 1].legend()
        axs[1, 1].grid(True)
        
        # Embedding de la figure matplotlib dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Lancement de l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = AppMeteo(root)
    def on_closing():
        root.destroy()
        sys.exit()
    root.protocol('WM_DELETE_WINDOW', on_closing)
    root.mainloop()