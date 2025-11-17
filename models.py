# -*- coding: utf-8 -*-
"""
Database Models per Social Media Scheduler
Labirintoambientale.it
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Post(db.Model):
    """Modello per i post social media"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Contenuto post
    content = db.Column(db.Text, nullable=False)
    
    # Piattaforme target (salvate come stringa separata da virgole)
    platforms = db.Column(db.String(200), nullable=False)  # es: "facebook,linkedin,twitter"
    
    # Media
    image_url = db.Column(db.String(500))  # URL locale o remoto dell'immagine
    video_url = db.Column(db.String(500))  # URL del video (opzionale)
    
    # Scheduling
    scheduled_date = db.Column(db.DateTime, nullable=False)  # Data/ora programmata
    timezone = db.Column(db.String(50), default='Europe/Rome')
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  
    # Possibili valori: 'draft', 'scheduled', 'published', 'failed'
    
    # Metadati pubblicazione
    published_at = db.Column(db.DateTime)  # Data/ora effettiva pubblicazione
    late_post_id = db.Column(db.String(100))  # ID ritornato da LATE API
    error_message = db.Column(db.Text)  # Eventuale messaggio di errore
    
    # Pinterest specifico
    pinterest_board_id = db.Column(db.String(100))  # Board Pinterest
    pinterest_link = db.Column(db.String(500))  # Link associato al Pin
    
    # Template utilizzato (opzionale)
    template_name = db.Column(db.String(100))  # es: 'nuovo_impianto', 'codice_cer'
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Note personali (non pubblicate)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Post {self.id}: {self.status} - {self.scheduled_date}>'
    
    def get_platforms_list(self):
        """Ritorna lista delle piattaforme"""
        return [p.strip() for p in self.platforms.split(',') if p.strip()]
    
    def set_platforms_list(self, platforms_list):
        """Imposta piattaforme da lista"""
        self.platforms = ','.join(platforms_list)
    
    def is_ready_to_publish(self):
        """Verifica se il post è pronto per pubblicazione"""
        now = datetime.utcnow()
        return (
            self.status == 'scheduled' and 
            self.scheduled_date <= now and
            self.content and
            self.platforms
        )
    
    def to_dict(self):
        """Converte il post in dizionario per JSON"""
        return {
            'id': self.id,
            'content': self.content,
            'platforms': self.get_platforms_list(),
            'image_url': self.image_url,
            'video_url': self.video_url,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'late_post_id': self.late_post_id,
            'template_name': self.template_name,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


class PublicationLog(db.Model):
    """Log delle pubblicazioni effettuate"""
    __tablename__ = 'publication_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    
    # Dettagli pubblicazione
    platform = db.Column(db.String(50), nullable=False)  # Singola piattaforma
    status = db.Column(db.String(20), nullable=False)  # 'success' o 'failed'
    
    # Risposta API
    late_response = db.Column(db.Text)  # JSON response da LATE
    error_message = db.Column(db.Text)
    
    # URL post pubblicato (se disponibile)
    published_url = db.Column(db.String(500))
    
    # Timestamp
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazione con Post
    post = db.relationship('Post', backref=db.backref('logs', lazy=True))
    
    def __repr__(self):
        return f'<Log {self.id}: {self.platform} - {self.status}>'


class AccountSettings(db.Model):
    """Impostazioni account social collegati"""
    __tablename__ = 'account_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), unique=True, nullable=False)
    
    # Account info da LATE
    account_id = db.Column(db.String(100), nullable=False)
    account_username = db.Column(db.String(200))
    
    # Configurazioni specifiche
    is_active = db.Column(db.Boolean, default=True)  # Abilita/disabilita piattaforma
    default_hashtags = db.Column(db.Text)  # Hashtag di default separati da virgola
    
    # Pinterest specifico
    pinterest_default_board = db.Column(db.String(100))
    
    # Metadata
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_post_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Account {self.platform}: {self.account_username}>'


class PostTemplate(db.Model):
    """Template salvati per creazione rapida post"""
    __tablename__ = 'post_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))
    
    # Contenuto template
    content_template = db.Column(db.Text, nullable=False)  # Con placeholder {variabile}
    
    # Piattaforme suggerite
    suggested_platforms = db.Column(db.String(200))
    
    # Categoria
    category = db.Column(db.String(50))  # es: 'impianti', 'normativa', 'cer', 'iso14001'
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_count = db.Column(db.Integer, default=0)  # Quante volte è stato usato
    
    def __repr__(self):
        return f'<Template {self.name}>'
    
    def get_suggested_platforms_list(self):
        """Ritorna lista piattaforme suggerite"""
        if not self.suggested_platforms:
            return []
        return [p.strip() for p in self.suggested_platforms.split(',') if p.strip()]