# -*- coding: utf-8 -*-
"""
Integrazione LATE API per pubblicazione social media
Labirintoambientale.it
"""
import requests
import json
from datetime import datetime
import pytz

class LateAPI:
    """Classe per interagire con LATE API"""
    
    def __init__(self, api_key, api_url='https://api.getlate.dev/v1'):
        """
        Inizializza client LATE API
        
        Args:
            api_key (str): API key da LATE dashboard
            api_url (str): Base URL API LATE
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_post(self, content, platforms, account_ids, media_urls=None, 
                   scheduled_time=None, pinterest_config=None):
        """
        Crea e pubblica/programma un post su LATE
        
        Args:
            content (str): Testo del post
            platforms (list): Lista piattaforme ['facebook', 'instagram', 'twitter', 'linkedin', 'pinterest']
            account_ids (dict): Dizionario {platform: account_id}
            media_urls (list): Lista URL media da allegare
            scheduled_time (datetime): Datetime per scheduling (None = pubblica ora)
            pinterest_config (dict): Configurazione Pinterest {'board_id': '...', 'link': '...'}
        
        Returns:
            dict: Risposta API con dettagli pubblicazione
        """
        endpoint = f'{self.api_url}/posts'
        
        # Costruisci payload
        payload = {
            'content': content,
            'platforms': []
        }
        
        # Aggiungi configurazione per ogni piattaforma
        for platform in platforms:
            if platform not in account_ids or not account_ids[platform]:
                continue
            
            platform_config = {
                'platform': platform,
                'accountId': account_ids[platform]
            }
            
            # Configurazione specifica Pinterest
            if platform == 'pinterest' and pinterest_config:
                platform_config['boardId'] = pinterest_config.get('board_id')
                platform_config['link'] = pinterest_config.get('link')
            
            payload['platforms'].append(platform_config)
        
        # Aggiungi media se presenti
        if media_urls:
            payload['mediaItems'] = [
                {'type': 'image' if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')) else 'video',
                 'url': url}
                for url in media_urls
            ]
        
        # Scheduling
        if scheduled_time:
            # Converti in ISO 8601 UTC
            if scheduled_time.tzinfo is None:
                # Assume Europe/Rome se non specificato
                rome_tz = pytz.timezone('Europe/Rome')
                scheduled_time = rome_tz.localize(scheduled_time)
            
            utc_time = scheduled_time.astimezone(pytz.UTC)
            payload['scheduledFor'] = utc_time.isoformat()
            payload['timezone'] = 'Europe/Rome'
        
        # Chiamata API
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.json() if e.response.content else str(e)
            return {
                'success': False,
                'error': error_detail,
                'status_code': e.response.status_code if e.response else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': None
            }
    
    def get_post(self, post_id):
        """
        Recupera dettagli di un post da LATE
        
        Args:
            post_id (str): ID del post su LATE
        
        Returns:
            dict: Dettagli del post
        """
        endpoint = f'{self.api_url}/posts/{post_id}'
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_scheduled_post(self, post_id):
        """
        Elimina un post programmato (prima della pubblicazione)
        
        Args:
            post_id (str): ID del post su LATE
        
        Returns:
            dict: Risultato eliminazione
        """
        endpoint = f'{self.api_url}/posts/{post_id}'
        
        try:
            response = requests.delete(endpoint, headers=self.headers)
            response.raise_for_status()
            return {
                'success': True,
                'message': 'Post eliminato con successo'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_accounts(self):
        """
        Recupera lista account connessi su LATE
        
        Returns:
            dict: Lista account con IDs
        """
        endpoint = f'{self.api_url}/accounts'
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return {
                'success': True,
                'accounts': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_analytics(self, post_id):
        """
        Recupera analytics di un post pubblicato
        
        Args:
            post_id (str): ID del post su LATE
        
        Returns:
            dict: Analytics del post
        """
        endpoint = f'{self.api_url}/posts/{post_id}/analytics'
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return {
                'success': True,
                'analytics': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def validate_content_length(content, platform, max_lengths):
    """
    Valida lunghezza contenuto per piattaforma
    
    Args:
        content (str): Contenuto del post
        platform (str): Nome piattaforma
        max_lengths (dict): Dizionario limiti caratteri per piattaforma
    
    Returns:
        tuple: (is_valid, message)
    """
    content_length = len(content)
    max_length = max_lengths.get(platform, 10000)
    
    if content_length > max_length:
        return False, f'{platform} consente max {max_length} caratteri. Attuali: {content_length}'
    
    return True, 'OK'


def prepare_pinterest_content(content, max_length=500):
    """
    Prepara contenuto per Pinterest (limiti più stringenti)
    
    Args:
        content (str): Contenuto originale
        max_length (int): Lunghezza massima Pinterest
    
    Returns:
        str: Contenuto troncato se necessario
    """
    if len(content) <= max_length:
        return content
    
    # Tronca e aggiungi ellipsis
    return content[:max_length-3] + '...'


def extract_hashtags(content):
    """
    Estrae hashtag dal contenuto
    
    Args:
        content (str): Contenuto post
    
    Returns:
        list: Lista hashtag trovati
    """
    import re
    hashtag_pattern = r'#\w+'
    return re.findall(hashtag_pattern, content)


def format_content_for_platform(content, platform):
    """
    Formatta contenuto specifico per piattaforma
    
    Args:
        content (str): Contenuto base
        platform (str): Piattaforma target
    
    Returns:
        str: Contenuto formattato
    """
    # Instagram: più emoji, hashtag alla fine
    if platform == 'instagram':
        # Se non ci sono emoji, aggiungi alcune
        if not any(ord(char) > 127 for char in content):
            content = '✨ ' + content
    
    # Twitter: limita lunghezza
    elif platform == 'twitter':
        if len(content) > 280:
            content = content[:277] + '...'
    
    # LinkedIn: più professionale
    elif platform == 'linkedin':
        # Rimuovi emoji eccessive per LinkedIn se necessario
        pass
    
    # Pinterest: più corto con focus visual
    elif platform == 'pinterest':
        content = prepare_pinterest_content(content)
    
    return content