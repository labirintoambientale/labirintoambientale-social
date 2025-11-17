# -*- coding: utf-8 -*-
"""
Configurazione applicazione Social Media Scheduler
Labirintoambientale.it
"""
import os
from datetime import timedelta

class Config:
    """Configurazione base dell'applicazione"""
    
    # Secret key per sessioni Flask (CAMBIALA!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chiave-segreta-da-cambiare-assolutamente'
    
    # Database SQLite
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'data', 'posts.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LATE API Configuration
    # Ottieni la tua API key da: https://getlate.dev/dashboard/settings/api
    LATE_API_KEY = os.environ.get('LATE_API_KEY') or 'your_late_api_key_here'
    LATE_API_URL = 'https://api.getlate.dev/v1'
    
    # Account IDs per ogni piattaforma (li ottieni dopo aver connesso gli account su LATE)
    # Dashboard LATE → Accounts → copia gli ID
    SOCIAL_ACCOUNTS = {
        'facebook': os.environ.get('FACEBOOK_ACCOUNT_ID') or '',
        'instagram': os.environ.get('INSTAGRAM_ACCOUNT_ID') or '',
        'linkedin': os.environ.get('LINKEDIN_ACCOUNT_ID') or '',
        'twitter': os.environ.get('TWITTER_ACCOUNT_ID') or '',  # X/Twitter
        'pinterest': os.environ.get('PINTEREST_ACCOUNT_ID') or ''
    }
    
    # Pinterest board ID di default
    PINTEREST_DEFAULT_BOARD = os.environ.get('PINTEREST_BOARD_ID') or ''
    
    # Configurazione upload immagini
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}
    
    # Timezone
    TIMEZONE = 'Europe/Rome'
    
    # Configurazione post
    MAX_POST_LENGTH = {
        'twitter': 280,
        'facebook': 63206,
        'linkedin': 3000,
        'instagram': 2200,
        'pinterest': 500
    }
    
    # Template post predefiniti per labirintoambientale.it
    POST_TEMPLATES = {
        'nuovo_impianto': {
            'title': 'Nuovo Impianto Rifiuti',
            'content': '''🏭 Nuovo impianto nel database labirintoambientale.it!

📍 {nome_impianto} - {citta}, {regione}
♻️ Specializzato in: {tipo_rifiuti}
📋 Codici CER autorizzati: {codici_cer}

Scopri tutti i dettagli → {link}

#rifiuti #gestionerifiuti #{regione_tag} #economiacircolare''',
            'platforms': ['facebook', 'linkedin', 'twitter', 'instagram', 'pinterest']
        },
        'aggiornamento_normativo': {
            'title': 'Aggiornamento Normativo',
            'content': '''⚖️ Aggiornamento normativo: {titolo_normativa}

📅 In vigore dal: {data}
📌 Cosa cambia: {sintesi}

Consulta la guida completa su labirintoambientale.it

#normativa #dlgs152 #ambiente #consulenza''',
            'platforms': ['facebook', 'linkedin', 'twitter']
        },
        'consiglio_settimanale': {
            'title': 'Consiglio Settimanale',
            'content': '''💡 Consiglio della settimana

{tip_breve}

Vuoi approfondire? 
👉 labirintoambientale.it

#tips #gestionerifiuti #sostenibilità #ambiente''',
            'platforms': ['facebook', 'linkedin', 'instagram', 'pinterest']
        },
        'codice_cer': {
            'title': 'Focus Codice CER',
            'content': '''📋 Codice CER {codice_cer}

📝 Descrizione: {descrizione}
⚠️ Classificazione: {classificazione}
♻️ Modalità smaltimento: {modalita}

Trova impianti autorizzati su labirintoambientale.it

#CER #classificazionerifiuti #normativa''',
            'platforms': ['facebook', 'linkedin', 'twitter', 'pinterest']
        },
        'iso_14001': {
            'title': 'ISO 14001',
            'content': '''🌱 ISO 14001:2015 - Sistema di Gestione Ambientale

{contenuto}

Supporto per implementazione e consulenza su labirintoambientale.it

#ISO14001 #SGA #certificazione #ambiente''',
            'platforms': ['facebook', 'linkedin', 'twitter']
        }
    }
    
    # Orari ottimali per pubblicazione (ora locale CET)
    OPTIMAL_POSTING_TIMES = {
        'monday': ['09:00', '15:00', '18:00'],
        'tuesday': ['09:00', '15:00', '18:00'],
        'wednesday': ['09:00', '15:00', '18:00'],
        'thursday': ['09:00', '15:00', '18:00'],
        'friday': ['09:00', '15:00', '18:00'],
        'saturday': ['11:00', '17:00'],
        'sunday': ['11:00', '17:00']
    }
    
    # Hashtag strategici per labirintoambientale.it
    STRATEGIC_HASHTAGS = {
        'generale': ['#gestionerifiuti', '#ambiente', '#sostenibilità', '#economiacircolare'],
        'normativa': ['#dlgs152', '#normativaambientale', '#consulenza', '#compliance'],
        'tecnico': ['#CER', '#classificazionerifiuti', '#smaltimento', '#recupero'],
        'certificazione': ['#ISO14001', '#SGA', '#certificazione', '#qualità'],
        'impianti': ['#impiantirifiuti', '#riciclaggio', '#trattamento', '#recuperoenergetico']
    }