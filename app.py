# -*- coding: utf-8 -*-
"""
nano app.pyFlask Application principale - Social Media Scheduler
Labirintoambientale.it
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import pytz

from models import db, Post, PublicationLog, AccountSettings, PostTemplate
from late_api import LateAPI, validate_content_length
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Inizializza database
db.init_app(app)

# Crea directory necessarie
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['BASE_DIR'], 'data'), exist_ok=True)

# Inizializza LATE API client
late_api = LateAPI(app.config['LATE_API_KEY'])

def allowed_file(filename):
    """Verifica se file è consentito"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Dashboard principale"""
    # Statistiche
    total_posts = Post.query.count()
    scheduled_posts = Post.query.filter_by(status='scheduled').count()
    published_posts = Post.query.filter_by(status='published').count()
    failed_posts = Post.query.filter_by(status='failed').count()
    
    # Prossimi post programmati
    upcoming_posts = Post.query.filter_by(status='scheduled')\
        .order_by(Post.scheduled_date.asc())\
        .limit(10).all()
    
    # Ultimi post pubblicati
    recent_posts = Post.query.filter_by(status='published')\
        .order_by(Post.published_at.desc())\
        .limit(10).all()
    
    return render_template('dashboard.html',
                         total_posts=total_posts,
                         scheduled_posts=scheduled_posts,
                         published_posts=published_posts,
                         failed_posts=failed_posts,
                         upcoming_posts=upcoming_posts,
                         recent_posts=recent_posts)

@app.route('/posts')
def posts_list():
    """Lista tutti i post"""
    status_filter = request.args.get('status', 'all')
    
    query = Post.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    posts = query.order_by(Post.created_at.desc()).all()
    
    return render_template('posts_list.html', posts=posts, status_filter=status_filter)

@app.route('/post/create', methods=['GET', 'POST'])
def create_post():
    """Crea nuovo post"""
    if request.method == 'POST':
        # Recupera dati form
        content = request.form.get('content')
        platforms = request.form.getlist('platforms')
        scheduled_date_str = request.form.get('scheduled_date')
        scheduled_time_str = request.form.get('scheduled_time')
        template_name = request.form.get('template_name')
        notes = request.form.get('notes')
        pinterest_link = request.form.get('pinterest_link')
        
        # Validazione
        if not content or not platforms:
            flash('Contenuto e piattaforme sono obbligatori', 'error')
            return redirect(url_for('create_post'))
        
        # Valida lunghezza contenuto per ogni piattaforma
        for platform in platforms:
            is_valid, message = validate_content_length(
                content, platform, app.config['MAX_POST_LENGTH']
            )
            if not is_valid:
                flash(message, 'error')
                return redirect(url_for('create_post'))
        
        # Parse data/ora scheduling
        try:
            rome_tz = pytz.timezone('Europe/Rome')
            scheduled_datetime = datetime.strptime(
                f"{scheduled_date_str} {scheduled_time_str}", 
                "%Y-%m-%d %H:%M"
            )
            scheduled_datetime = rome_tz.localize(scheduled_datetime)
            scheduled_datetime_utc = scheduled_datetime.astimezone(pytz.UTC).replace(tzinfo=None)
        except ValueError:
            flash('Data/ora non valida', 'error')
            return redirect(url_for('create_post'))
        
        # Upload immagine se presente
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Aggiungi timestamp per unicità
                filename = f"{int(datetime.now().timestamp())}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                # URL relativo per accesso web
                image_url = f"/static/uploads/{filename}"
        
        # Crea post
        post = Post(
            content=content,
            platforms=','.join(platforms),
            scheduled_date=scheduled_datetime_utc,
            template_name=template_name if template_name else None,
            notes=notes,
            image_url=image_url,
            pinterest_link=pinterest_link if 'pinterest' in platforms else None,
            status='scheduled'
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash(f'Post programmato con successo per {scheduled_datetime.strftime("%d/%m/%Y %H:%M")}', 'success')
        return redirect(url_for('index'))
    
    # GET - mostra form
    templates = PostTemplate.query.all()
    return render_template('create_post.html', 
                         templates=templates,
                         post_templates=app.config['POST_TEMPLATES'])
                         now=datetime.now())
@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    """Modifica post esistente"""
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.content = request.form.get('content')
        post.platforms = ','.join(request.form.getlist('platforms'))
        post.notes = request.form.get('notes')
        
        # Aggiorna scheduling solo se non ancora pubblicato
        if post.status == 'scheduled':
            scheduled_date_str = request.form.get('scheduled_date')
            scheduled_time_str = request.form.get('scheduled_time')
            
            rome_tz = pytz.timezone('Europe/Rome')
            scheduled_datetime = datetime.strptime(
                f"{scheduled_date_str} {scheduled_time_str}",
                "%Y-%m-%d %H:%M"
            )
            scheduled_datetime = rome_tz.localize(scheduled_datetime)
            post.scheduled_date = scheduled_datetime.astimezone(pytz.UTC).replace(tzinfo=None)
        
        db.session.commit()
        flash('Post aggiornato con successo', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_post.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Elimina post"""
    post = Post.query.get_or_404(post_id)
    
    # Se programmato su LATE, elimina anche da lì
    if post.late_post_id and post.status == 'scheduled':
        late_api.delete_scheduled_post(post.late_post_id)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Post eliminato', 'success')
    return redirect(url_for('index'))

@app.route('/calendar')
def calendar():
    """Calendario visuale post programmati"""
    posts = Post.query.filter_by(status='scheduled').all()
    
    # Converte post in formato eventi calendario
    events = []
    for post in posts:
        rome_tz = pytz.timezone('Europe/Rome')
        scheduled_rome = pytz.UTC.localize(post.scheduled_date).astimezone(rome_tz)
        
        events.append({
            'id': post.id,
            'title': post.content[:50] + '...' if len(post.content) > 50 else post.content,
            'start': scheduled_rome.isoformat(),
            'platforms': post.get_platforms_list(),
            'url': url_for('edit_post', post_id=post.id)
        })
    
    return render_template('calendar.html', events=events)

@app.route('/templates')
def templates_list():
    """Gestione template"""
    templates = PostTemplate.query.all()
    config_templates = app.config['POST_TEMPLATES']
    
    return render_template('templates.html', 
                         templates=templates,
                         config_templates=config_templates)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Impostazioni account e configurazione"""
    if request.method == 'POST':
        # Aggiorna impostazioni
        for platform in ['facebook', 'instagram', 'linkedin', 'twitter', 'pinterest']:
            account_id = request.form.get(f'{platform}_account_id')
            if account_id:
                app.config['SOCIAL_ACCOUNTS'][platform] = account_id
        
        flash('Impostazioni aggiornate', 'success')
        return redirect(url_for('settings'))
    
    # Recupera account connessi da LATE
    accounts_response = late_api.get_accounts()
    late_accounts = accounts_response.get('accounts', []) if accounts_response['success'] else []
    
    return render_template('settings.html',
                         social_accounts=app.config['SOCIAL_ACCOUNTS'],
                         late_accounts=late_accounts)

@app.route('/api/template/<template_name>')
def get_template(template_name):
    """API per recuperare contenuto template"""
    templates = app.config['POST_TEMPLATES']
    
    if template_name in templates:
        return jsonify(templates[template_name])
    
    return jsonify({'error': 'Template non trovato'}), 404


@app.route('/publish-now/<int:post_id>', methods=['POST'])
def publish_now(post_id):
    """Pubblica immediatamente un post programmato"""
    post = Post.query.get_or_404(post_id)
    
    if post.status != 'scheduled':
        return jsonify({'error': 'Post già pubblicato o non programmato'}), 400
    
    # Usa lo script di pubblicazione
    from publish_scheduled_posts import publish_post
    
    success = publish_post(post, late_api)
    db.session.commit()
    
    if success:
        return jsonify({'success': True, 'message': 'Post pubblicato'})
    else:
        return jsonify({'success': False, 'error': post.error_message}), 500

# Inizializza database al primo avvio
with app.app_context():
    db.create_all()
    print("✅ Database inizializzato")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
