# Social Media Scheduler - Labirintoambientale.it

Sistema automatizzato per la pubblicazione programmata di contenuti su 5 piattaforme social (Facebook, LinkedIn, Instagram, X/Twitter, Pinterest) tramite un'unica interfaccia web.

## 🎯 Caratteristiche Principali

- ✅ **Interfaccia web unica** per gestire tutti i social
- ✅ **Pubblicazione simultanea** su 5 piattaforme
- ✅ **Scheduling automatico** con task giornaliero
- ✅ **Template predefiniti** specifici per settore rifiuti/ambiente
- ✅ **Calendario visuale** per pianificazione contenuti
- ✅ **Database locale** SQLite per storico post
- ✅ **Upload immagini** e media
- ✅ **Log completo** pubblicazioni e errori
- ✅ **Costi minimi**: €0-13/mese

## 🏗️ Architettura

```
┌─────────────────────────────────────────────────────┐
│         Dashboard Web (Flask + Bootstrap)           │
│  Crea Post │ Calendario │ Template │ Statistiche   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Database SQLite      │
         │  - Post programmati   │
         │  - Log pubblicazioni  │
         │  - Template salvati   │
         └──────────┬────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Scheduled Task      │
         │  (1x giorno ore 9:00)│
         │  publish_scheduled   │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │    LATE API          │
         │  (Unified Social API)│
         └──────────┬───────────┘
                    │
      ┌─────────────┼─────────────────┬─────────────┐
      ▼             ▼                 ▼             ▼
  Facebook     Instagram          LinkedIn       X/Twitter
                                                   Pinterest
```

## 📦 Componenti

### File Principali

1. **app.py** - Applicazione Flask principale
   - Routes per dashboard, creazione post, calendario
   - Gestione upload immagini
   - API endpoints

2. **config.py** - Configurazioni
   - API keys LATE
   - Account IDs social
   - Template post predefiniti
   - Limiti caratteri per piattaforma
   - Hashtag strategici

3. **models.py** - Modelli database SQLAlchemy
   - `Post`: Post programmati
   - `PublicationLog`: Log pubblicazioni
   - `AccountSettings`: Configurazioni account
   - `PostTemplate`: Template salvati

4. **late_api.py** - Integrazione LATE API
   - Client API per pubblicazione
   - Validazione contenuti
   - Gestione errori
   - Formatting specifico per piattaforma

5. **publish_scheduled_posts.py** - Script automatico
   - Eseguito giornalmente da scheduled task
   - Recupera post da pubblicare dal database
   - Chiama LATE API per pubblicazione
   - Salva log risultati

## 🚀 Setup Rapido

### Prerequisiti

- Account PythonAnywhere (Free tier)
- Account LATE.dev (Free tier o Build €13/mese)
- Account social connessi su LATE (Facebook, Instagram, LinkedIn, X, Pinterest)

### Installazione (30 minuti)

1. **Registrazione servizi**
   ```
   - PythonAnywhere.com (piano Free)
   - getlate.dev (piano Free/Build)
   - Connetti i 5 account social su LATE
   ```

2. **Upload file**
   - Carica tutti i file su PythonAnywhere
   - Via web interface o Git

3. **Installa dipendenze**
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

4. **Configura API keys**
   - Modifica `config.py` con:
     - LATE_API_KEY
     - Account IDs per ogni social

5. **Inizializza database**
   ```bash
   python3.10 -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

6. **Configura web app**
   - Crea Flask web app su PythonAnywhere
   - Configura WSGI file
   - Reload app

7. **Configura scheduled task**
   - Task giornaliero ore 09:00 UTC
   - Esegue `publish_scheduled_posts.py`

📖 **Guida dettagliata completa**: Vedi `DEPLOY-GUIDE.md`

## 💻 Utilizzo

### Creare un Post

1. Dashboard → **"Nuovo Post"**
2. Scrivi contenuto (supporta emoji, hashtag, link)
3. Seleziona piattaforme target (tutte o alcune)
4. Scegli data e ora pubblicazione
5. Upload immagine (opzionale)
6. **"Programma Post"**

### Usare Template

Il sistema include 5 template predefiniti per labirintoambientale.it:

1. **Nuovo Impianto Rifiuti**
   ```
   🏭 Nuovo impianto nel database!
   📍 {nome_impianto} - {citta}, {regione}
   ♻️ Specializzato in: {tipo_rifiuti}
   ```

2. **Aggiornamento Normativo**
   ```
   ⚖️ Aggiornamento normativo: {titolo}
   📅 In vigore dal: {data}
   ```

3. **Consiglio Settimanale**
   ```
   💡 Consiglio della settimana
   {tip_breve}
   ```

4. **Focus Codice CER**
   ```
   📋 Codice CER {codice}
   📝 Descrizione: {descrizione}
   ```

5. **ISO 14001**
   ```
   🌱 ISO 14001:2015
   {contenuto}
   ```

Seleziona template → personalizza → programma!

### Calendario

- Vista mensile post programmati
- Click su post per modificare
- Colori diversi per stato (programmato/pubblicato/fallito)

### Monitoraggio

Dashboard mostra:
- Totale post programmati
- Post pubblicati oggi
- Post falliti (con errori)
- Prossimi 10 post in arrivo
- Ultimi 10 post pubblicati

## 🔧 Configurazione Avanzata

### Orari Ottimali Pubblicazione

In `config.py` sono preconfigurati orari ottimali per ogni giorno:

```python
OPTIMAL_POSTING_TIMES = {
    'monday': ['09:00', '15:00', '18:00'],
    'tuesday': ['09:00', '15:00', '18:00'],
    # ...
}
```

### Hashtag Strategici

Hashtag già organizzati per categoria:

```python
STRATEGIC_HASHTAGS = {
    'generale': ['#gestionerifiuti', '#ambiente', ...],
    'normativa': ['#dlgs152', '#normativaambientale', ...],
    'tecnico': ['#CER', '#classificazionerifiuti', ...],
    'certificazione': ['#ISO14001', '#SGA', ...],
    'impianti': ['#impiantirifiuti', '#riciclaggio', ...]
}
```

### Limiti Caratteri per Piattaforma

Automaticamente gestiti:

- Twitter/X: 280 caratteri
- LinkedIn: 3000 caratteri
- Instagram: 2200 caratteri
- Facebook: 63206 caratteri
- Pinterest: 500 caratteri

## 📊 Costi Operativi

| Servizio | Piano | Costo Mensile |
|----------|-------|---------------|
| **PythonAnywhere** | Free | €0 |
| **LATE API** | Free (10 post/mese) | €0 |
| **LATE API** | Build (120 post/mese) | €13 |
| **LATE API** | Accelerate (illimitati) | €33 |
| **TOTALE** | Free tier | **€0** |
| **TOTALE** | Build tier | **€13** |

### Quando fare upgrade LATE

- **Free (€0)**: Test, massimo 10 post/mese
- **Build (€13)**: Uso normale, 120 post/mese = 4 post/giorno
- **Accelerate (€33)**: Uso intensivo, post illimitati

## 🔐 Sicurezza

### API Keys

Non committare mai API keys nel repository Git!

Usa variabili ambiente su PythonAnywhere:

```bash
# In ~/.bashrc su PythonAnywhere
export LATE_API_KEY="la_tua_chiave"
export SECRET_KEY="chiave_segreta_flask"
```

Poi in `config.py`:
```python
LATE_API_KEY = os.environ.get('LATE_API_KEY') or 'fallback_for_dev'
```

### Database

- SQLite locale protetto da filesystem PythonAnywhere
- Backup giornalieri automatici consigliati
- Nessun dato sensibile utenti (solo post)

## 🐛 Troubleshooting

### Post non si pubblica

1. Verifica LATE API key in `config.py`
2. Controlla Account IDs corretti
3. Testa connessione:
   ```bash
   python3.10 -c "from late_api import LateAPI; from config import Config; api=LateAPI(Config.LATE_API_KEY); print(api.get_accounts())"
   ```

### Scheduled task non esegue

1. Verifica orario task (deve essere UTC!)
2. Controlla log: `cat ~/logs/social_scheduler.log`
3. Test manuale: `python3.10 publish_scheduled_posts.py`

### Web app non carica

1. Controlla Error log in dashboard Web
2. Verifica WSGI configuration
3. Reload web app
4. Verifica dipendenze installate

## 📈 Roadmap Future Features

- [ ] **Bulk scheduling** da CSV
- [ ] **Analytics integrate** da ogni piattaforma
- [ ] **AI content generation** con OpenAI/Claude
- [ ] **Integrazione WordPress** per auto-post da articoli
- [ ] **Preview post** per ogni piattaforma prima pubblicazione
- [ ] **Drag & drop** calendario per re-scheduling
- [ ] **Webhook notifiche** Discord/Slack per pubblicazioni
- [ ] **Multi-utente** con ruoli (admin/editor/viewer)
- [ ] **Riciclo contenuti evergreen** automatico
- [ ] **Hashtag suggester** basato su AI

## 🤝 Supporto

### Documentazione

- **LATE API Docs**: https://getlate.dev/docs
- **PythonAnywhere Help**: https://help.pythonanywhere.com
- **Flask Docs**: https://flask.palletsprojects.com

### Community

- **LATE Discord**: Disponibile su getlate.dev
- **PythonAnywhere Forum**: https://www.pythonanywhere.com/forums/

## 📝 License

Progetto custom per Labirintoambientale.it - Tutti i diritti riservati

## 🙏 Crediti

- **Framework**: Flask (Python)
- **Database**: SQLAlchemy + SQLite
- **API**: LATE (getlate.dev)
- **Hosting**: PythonAnywhere
- **UI**: Bootstrap 5

---

**Sviluppato per Labirintoambientale.it**
Sistema di gestione rifiuti e consulenza ambientale in Italia

🌱 Automazione social media per un ambiente più pulito!