# Guida Deployment PythonAnywhere
## Social Media Scheduler - Labirintoambientale.it

Questa guida ti accompagna passo-passo nel deployment della tua applicazione Flask su PythonAnywhere.

---

## PARTE 1: Setup Iniziale PythonAnywhere (15 minuti)

### Step 1: Accesso e Console

1. Accedi al tuo account PythonAnywhere: https://www.pythonanywhere.com
2. Vai alla dashboard
3. Clicca su **"Consoles"** → **"Bash"** per aprire una console

### Step 2: Upload Files

**Opzione A: Upload tramite Web Interface (più semplice)**

1. Vai su **"Files"** nella dashboard
2. Clicca **"Upload a file"**
3. Carica tutti i file del progetto uno per uno:
   - `app.py`
   - `config.py`
   - `models.py`
   - `late_api.py`
   - `publish_scheduled_posts.py`
   - `requirements.txt`

4. Crea directory `templates` e `static`:
   - Clicca **"New directory"** → nome: `templates`
   - Clicca **"New directory"** → nome: `static`
   - Dentro `static` crea: `css`, `js`, `uploads`

**Opzione B: Upload tramite Git (consigliato per futuro)**

Nella console Bash:

```bash
# Clone del repository (se hai già creato un repo Git)
cd ~
git clone https://github.com/tuousername/labirintoambientale-social.git
cd labirintoambientale-social

# Oppure crea directory manualmente e usa upload
mkdir labirintoambientale-social
cd labirintoambientale-social
```

### Step 3: Installazione Dipendenze

Nella console Bash:

```bash
# Naviga nella directory progetto
cd ~/labirintoambientale-social

# Installa dipendenze (usa --user per piano free)
pip3.10 install --user -r requirements.txt

# Verifica installazione
pip3.10 list | grep Flask
```

**Output atteso:**
```
Flask                 3.0.0
Flask-SQLAlchemy      3.1.1
```

### Step 4: Configurazione API Keys

Modifica `config.py` con le tue credenziali:

```bash
# Apri editor
nano config.py

# Oppure usa l'editor web: Files → config.py → Edit
```

**Modifica questi valori:**

```python
# LATE API Key (ottienila da https://getlate.dev/dashboard/settings/api)
LATE_API_KEY = 'la_tua_chiave_api_late_qui'

# Account IDs da LATE Dashboard
SOCIAL_ACCOUNTS = {
    'facebook': 'fb_account_id_qui',
    'instagram': 'ig_account_id_qui',
    'linkedin': 'li_account_id_qui',
    'twitter': 'tw_account_id_qui',
    'pinterest': 'pi_account_id_qui'
}

# Pinterest board ID
PINTEREST_DEFAULT_BOARD = 'board_id_qui'
```

**Come ottenere Account IDs da LATE:**
1. Vai su https://getlate.dev/dashboard
2. Clicca su **"Accounts"**
3. Per ogni account connesso, copia l'**Account ID**

### Step 5: Inizializza Database

Nella console Bash:

```bash
cd ~/labirintoambientale-social

# Crea directory data
mkdir -p data

# Inizializza database con Python
python3.10 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database creato con successo!")
EOF
```

**Output atteso:**
```
✅ Database creato con successo!
```

Verifica:
```bash
ls -lh data/
# Dovresti vedere: posts.db
```

---

## PARTE 2: Configurazione Web App (10 minuti)

### Step 6: Crea Web App

1. Dashboard PythonAnywhere → **"Web"**
2. Clicca **"Add a new web app"**
3. Seleziona:
   - **Framework**: Manual configuration
   - **Python version**: Python 3.10

### Step 7: Configurazione WSGI

1. Nella pagina Web app, trova **"WSGI configuration file"**
2. Clicca sul link (es: `/var/www/tuousername_pythonanywhere_com_wsgi.py`)
3. **Cancella tutto** il contenuto del file
4. Sostituisci con:

```python
# /var/www/tuousername_pythonanywhere_com_wsgi.py
import sys
import os

# Aggiungi directory progetto al path
project_home = '/home/tuousername/labirintoambientale-social'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Importa app Flask
from app import app as application
```

**⚠️ IMPORTANTE:** Sostituisci `tuousername` con il tuo username PythonAnywhere!

### Step 8: Configurazione Virtualenv (Opzionale ma consigliato)

Se hai creato un virtualenv:

1. Nella pagina Web, trova **"Virtualenv"**
2. Inserisci path: `/home/tuousername/.virtualenvs/myenv`

Altrimenti lascia vuoto (userai dipendenze --user).

### Step 9: Static Files

Nella sezione **"Static files"**:

1. Clicca **"Enter URL"**: `/static/`
2. **"Enter path"**: `/home/tuousername/labirintoambientale-social/static`

3. Aggiungi un'altra entry:
   - **URL**: `/static/uploads/`
   - **Path**: `/home/tuousername/labirintoambientale-social/static/uploads`

### Step 10: Reload Web App

1. Scorri in alto nella pagina Web
2. Clicca il grande pulsante verde **"Reload tuousername.pythonanywhere.com"**
3. Attendi 10-15 secondi

### Step 11: Testa Applicazione

1. Clicca sul link: `http://tuousername.pythonanywhere.com`
2. Dovresti vedere la dashboard del Social Media Scheduler!

**Se vedi errori:**
1. Controlla **"Error log"** nella pagina Web
2. Controlla **"Server log"**
3. Verifica che tutti i file siano stati caricati
4. Verifica che le API keys siano configurate

---

## PARTE 3: Configurazione Scheduled Task (15 minuti)

Questo è il cuore dell'automazione: lo script che pubblica i post programmati.

### Step 12: Crea Scheduled Task

1. Dashboard → **"Tasks"**
2. Nella sezione **"Scheduled tasks"** clicca **"Create one"**
3. Configura:

**Orario esecuzione:**
```
09:00 UTC
```
(Corrisponde alle 10:00 CET in inverno, 11:00 in estate)

**Command:**
```bash
/usr/bin/python3.10 /home/tuousername/labirintoambientale-social/publish_scheduled_posts.py >> /home/tuousername/logs/social_scheduler.log 2>&1
```

**⚠️ Sostituisci `tuousername`!**

4. Clicca **"Create"**

### Step 13: Crea Directory Log

```bash
mkdir -p ~/logs
```

### Step 14: Test Manuale Scheduled Task

Testa lo script manualmente prima di aspettare il task automatico:

```bash
cd ~/labirintoambientale-social
python3.10 publish_scheduled_posts.py
```

**Output atteso (se nessun post da pubblicare):**
```
============================================================
🚀 Social Media Scheduler - Labirintoambientale.it
📅 Esecuzione: 2025-11-12 09:00:00
============================================================

ℹ️  Nessun post da pubblicare al momento
```

**Output con post da pubblicare:**
```
============================================================
🚀 Social Media Scheduler - Labirintoambientale.it
📅 Esecuzione: 2025-11-12 09:00:00
============================================================

📋 Trovati 2 post da pubblicare

📤 Pubblicazione post #1...
   Piattaforme: facebook,linkedin,twitter
   Schedulato per: 2025-11-12 08:50:00
✅ Post 1 pubblicato con successo su facebook, linkedin, twitter

📤 Pubblicazione post #2...
   Piattaforme: instagram,pinterest
   Schedulato per: 2025-11-12 08:55:00
✅ Post 2 pubblicato con successo su instagram, pinterest

============================================================
✅ Pubblicati con successo: 2
❌ Falliti: 0
============================================================
```

### Step 15: Verifica Log

Dopo l'esecuzione del task (manuale o automatico), controlla il log:

```bash
cat ~/logs/social_scheduler.log
```

---

## PARTE 4: Utilizzo Applicazione (Workflow Quotidiano)

### Creare un Post

1. Vai su `http://tuousername.pythonanywhere.com`
2. Clicca **"Nuovo Post"**
3. Compila il form:
   - **Contenuto**: Testo del post
   - **Piattaforme**: Seleziona Facebook, LinkedIn, Instagram, X, Pinterest
   - **Data**: Scegli data futura
   - **Ora**: Scegli ora (formato 24h)
   - **Immagine**: Upload (opzionale)
   - **Note**: Note personali (non pubblicate)

4. Clicca **"Programma Post"**

### Utilizzare Template Predefiniti

L'applicazione include 5 template specifici per labirintoambientale.it:

1. **Nuovo Impianto Rifiuti**
2. **Aggiornamento Normativo**
3. **Consiglio Settimanale**
4. **Focus Codice CER**
5. **ISO 14001**

Per usarli:
1. Nel form di creazione post
2. Seleziona template dal menu dropdown
3. Il contenuto viene pre-compilato
4. Personalizza con i tuoi dati
5. Programma

### Calendario Visuale

1. Clicca **"Calendario"** nel menu
2. Vedi tutti i post programmati per data
3. Clicca su un post per modificarlo
4. Drag & drop per spostare date (feature futura)

### Monitoraggio

**Dashboard principale:**
- Statistiche post (totali, programmati, pubblicati, falliti)
- Prossimi 10 post in arrivo
- Ultimi 10 post pubblicati

**Dettagli post:**
- Clicca su un post per vedere:
  - Status pubblicazione
  - Log per ogni piattaforma
  - Eventuali errori
  - Link ai post pubblicati

---

## PARTE 5: Manutenzione e Troubleshooting

### Aggiornare l'Applicazione

Quando modifichi il codice:

```bash
cd ~/labirintoambientale-social

# Se usi Git
git pull origin main

# Altrimenti ri-upload file modificati via Files

# Reload web app
# Dashboard Web → pulsante "Reload"
```

### Visualizzare Log Errori

**Web app errors:**
```bash
tail -f ~/labirintoambientale-social/flask_errors.log
```

**Scheduled task log:**
```bash
tail -f ~/logs/social_scheduler.log
```

**PythonAnywhere error log:**
- Dashboard Web → **"Error log"** (click per visualizzare)

### Test Connessione LATE API

Nella console Bash:

```bash
cd ~/labirintoambientale-social

python3.10 << EOF
from config import Config
from late_api import LateAPI

api = LateAPI(Config.LATE_API_KEY)
result = api.get_accounts()

if result['success']:
    print("✅ Connessione LATE OK!")
    print(f"Account connessi: {len(result['accounts'])}")
    for acc in result['accounts']:
        print(f"  - {acc.get('platform')}: {acc.get('username')}")
else:
    print("❌ Errore connessione LATE")
    print(result['error'])
EOF
```

### Database Backup

**Backup manuale:**
```bash
cp ~/labirintoambientale-social/data/posts.db ~/posts_backup_$(date +%Y%m%d).db
```

**Backup automatico giornaliero:**

1. Dashboard → **"Tasks"**
2. Crea nuovo scheduled task:
   - **Orario**: 03:00 UTC
   - **Command**:
```bash
cp /home/tuousername/labirintoambientale-social/data/posts.db /home/tuousername/backups/posts_$(date +\%Y\%m\%d).db
```

### Risolvere Problemi Comuni

**"Module not found" errors:**
```bash
pip3.10 install --user nome_modulo
# Poi Reload web app
```

**Database locked:**
```bash
# Chiudi tutte le connessioni al database
# Reload web app
```

**Scheduled task non esegue:**
- Verifica orario UTC (non CET!)
- Controlla log: `cat ~/logs/social_scheduler.log`
- Verifica permessi script: `chmod +x publish_scheduled_posts.py`

**Post non si pubblica:**
1. Verifica LATE API key in `config.py`
2. Verifica Account IDs corretti
3. Controlla log pubblicazione nel database
4. Testa manualmente: `python3.10 publish_scheduled_posts.py`

---

## PARTE 6: Upgrade da Free a Paid (Opzionale)

Se in futuro avrai bisogno di più risorse:

**Piano Hacker ($5/mese):**
- Scheduled tasks ogni ora (invece di 1/giorno)
- Più CPU quota
- 1GB storage
- Supporto prioritario

**Quando fare upgrade:**
- Quando pubblichi più di 20-30 post/giorno
- Quando hai bisogno di task orari
- Quando superi 512MB storage

**Come fare upgrade:**
1. Dashboard → **"Account"**
2. **"Upgrade"**
3. Scegli piano
4. Configura pagamento

---

## Contatti e Supporto

**PythonAnywhere Support:**
- Forum: https://www.pythonanywhere.com/forums/
- Email: support@pythonanywhere.com

**LATE API Support:**
- Docs: https://getlate.dev/docs
- Email: support@getlate.dev

---

## Checklist Finale

Prima di considerare il setup completo, verifica:

- [ ] Web app accessibile e funzionante
- [ ] Tutti i 5 social account connessi su LATE
- [ ] Account IDs configurati in `config.py`
- [ ] Database creato e accessibile
- [ ] Scheduled task configurato e testato
- [ ] Log directory creata
- [ ] Test creazione post completato
- [ ] Test pubblicazione post completato
- [ ] Backup database configurato

**🎉 Se tutti i check sono ✅ sei pronto per andare in produzione!**

---

## Prossimi Step Suggeriti

1. **Popola database con 10-15 post** per la prima settimana
2. **Monitora log** giornalmente per i primi 7 giorni
3. **Testa diversi orari** di pubblicazione per ogni piattaforma
4. **Crea template personalizzati** per contenuti ricorrenti
5. **Integra con WordPress** (feature futura) per auto-post

**Buona pubblicazione automatizzata! 🚀**