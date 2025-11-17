# -*- coding: utf-8 -*-
"""
Script per pubblicazione automatica post programmati
Da eseguire come scheduled task giornaliero su PythonAnywhere

Labirintoambientale.it Social Media Scheduler
"""
import os
import sys
from datetime import datetime, timedelta
import pytz

# Aggiungi directory progetto al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from models import db, Post, PublicationLog
from late_api import LateAPI
from config import Config

def setup_app():
    """Setup Flask app context per accesso database"""
    from flask import Flask
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    return app

def get_posts_to_publish():
    """
    Recupera tutti i post schedulati pronti per pubblicazione
    
    Returns:
        list: Lista oggetti Post da pubblicare
    """
    now = datetime.utcnow()
    
    # Trova post schedulati con data/ora <= now
    posts = Post.query.filter(
        Post.status == 'scheduled',
        Post.scheduled_date <= now
    ).all()
    
    return posts

def publish_post(post, late_api):
    """
    Pubblica singolo post tramite LATE API
    
    Args:
        post (Post): Oggetto Post da pubblicare
        late_api (LateAPI): Istanza client LATE API
    
    Returns:
        bool: True se successo, False altrimenti
    """
    try:
        # Prepara configurazione piattaforme
        platforms = post.get_platforms_list()
        account_ids = Config.SOCIAL_ACCOUNTS
        
        # Media URLs
        media_urls = []
        if post.image_url:
            # Se è URL relativo, costruisci URL completo
            if post.image_url.startswith('/'):
                # In produzione su PythonAnywhere
                base_url = 'http://labirintoambientale.pythonanywhere.com'
                media_urls.append(base_url + post.image_url)
            else:
                media_urls.append(post.image_url)
                
        if post.video_url:
            media_urls.append(post.video_url)
        
        # Configurazione Pinterest
        pinterest_config = None
        if 'pinterest' in platforms:
            pinterest_config = {
                'board_id': post.pinterest_board_id or Config.PINTEREST_DEFAULT_BOARD,
                'link': post.pinterest_link or 'https://labirintoambientale.it'
            }
        
        # Chiama LATE API per pubblicare
        result = late_api.create_post(
            content=post.content,
            platforms=platforms,
            account_ids=account_ids,
            media_urls=media_urls if media_urls else None,
            scheduled_time=None,  # Pubblica immediatamente
            pinterest_config=pinterest_config
        )
        
        if result['success']:
            # Aggiorna stato post
            post.status = 'published'
            post.published_at = datetime.utcnow()
            post.late_post_id = result['data'].get('id')
            
            # Crea log successo per ogni piattaforma
            for platform in platforms:
                log = PublicationLog(
                    post_id=post.id,
                    platform=platform,
                    status='success',
                    late_response=str(result['data'])
                )
                db.session.add(log)
            
            print(f"✅ Post {post.id} pubblicato con successo su {', '.join(platforms)}")
            return True
            
        else:
            # Errore pubblicazione
            post.status = 'failed'
            post.error_message = str(result.get('error'))
            
            # Crea log errore
            for platform in platforms:
                log = PublicationLog(
                    post_id=post.id,
                    platform=platform,
                    status='failed',
                    error_message=post.error_message
                )
                db.session.add(log)
            
            print(f"❌ Errore pubblicazione post {post.id}: {post.error_message}")
            return False
            
    except Exception as e:
        post.status = 'failed'
        post.error_message = str(e)
        print(f"❌ Eccezione durante pubblicazione post {post.id}: {str(e)}")
        return False

def main():
    """Funzione principale dello script"""
    print(f"\n{'='*60}")
    print(f"🚀 Social Media Scheduler - Labirintoambientale.it")
    print(f"📅 Esecuzione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Setup Flask app e database
    app = setup_app()
    
    with app.app_context():
        # Verifica configurazione LATE API
        if Config.LATE_API_KEY == 'your_late_api_key_here':
            print("⚠️  ERRORE: LATE_API_KEY non configurata!")
            print("Configura la chiave API in config.py o come variabile ambiente")
            return
        
        # Inizializza client LATE
        late_api = LateAPI(Config.LATE_API_KEY)
        
        # Recupera post da pubblicare
        posts_to_publish = get_posts_to_publish()
        
        if not posts_to_publish:
            print("ℹ️  Nessun post da pubblicare al momento")
            return
        
        print(f"📋 Trovati {len(posts_to_publish)} post da pubblicare\n")
        
        # Pubblica ogni post
        success_count = 0
        failed_count = 0
        
        for post in posts_to_publish:
            print(f"📤 Pubblicazione post #{post.id}...")
            print(f"   Piattaforme: {post.platforms}")
            print(f"   Schedulato per: {post.scheduled_date}")
            
            if publish_post(post, late_api):
                success_count += 1
            else:
                failed_count += 1
            
            # Salva modifiche database
            db.session.commit()
            print()
        
        # Riepilogo
        print(f"{'='*60}")
        print(f"✅ Pubblicati con successo: {success_count}")
        print(f"❌ Falliti: {failed_count}")
        print(f"{'='*60}\n")

if __name__ == '__main__':
    main()