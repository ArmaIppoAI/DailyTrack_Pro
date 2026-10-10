# DailyTrack Pro — Python + Flet

Tracker personale con dashboard, diario, idratazione, passi, alimentazione, stima calorie/macronutrienti, obiettivo proteine pari a 2 g/kg, storico e sessioni di camminata.

## Avvio desktop
Python 3.10+ consigliato.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Il database SQLite `dailytrack.db` viene creato automaticamente.

## Ricerca alimenti tramite API
L'app usa USDA FoodData Central. Per risultati completi, crea una chiave API gratuita:
https://fdc.nal.usda.gov/api-key-signup.html

Copia `.env.example` come `.env` e imposta `USDA_API_KEY=la_tua_chiave`.
In alternativa imposta la variabile d'ambiente `USDA_API_KEY`. Se non configurata, l'app prova con la chiave demo, soggetta a limiti.

La ricerca API richiede connessione internet. È una stima: i risultati variano in base al prodotto, alla voce selezionata e alla quantità. Controlla sempre etichetta e porzione. L'inserimento manuale resta disponibile.

## Android
La UI Flet è condivisa, ma una build Android richiede l'ambiente Android/Java configurato:
https://flet.dev/docs/publish/android/

Prima di distribuire su Android, sposta il DB in una directory dati persistente dell'app. Questa versione usa un percorso locale vicino al progetto per semplificare lo sviluppo desktop.

## Funzioni
- Dashboard con riepilogo di acqua, passi, calorie, proteine e diario.
- Acqua a incrementi rapidi.
- Peso corporeo e obiettivo proteine calcolato come 2 g/kg.
- Diario giornaliero.
- Alimenti aggiunti da ricerca API oppure manualmente.
- Totali stimati di kcal, proteine, carboidrati e grassi.
- Storico giornaliero.
- Sessione camminata con timer, distanza facoltativa e registrazione passi a fine sessione.

## Limite importante: contapassi automatico
La sessione di camminata tiene traccia del tempo e consente di salvare i passi della sessione, ma **non legge ancora il sensore pedometro del telefono**. Per contare automaticamente i passi mentre cammini serve un'integrazione Android nativa (sensore STEP_COUNTER/STEP_DETECTOR o Health Connect), permessi e test su dispositivo reale. Non viene simulato un conteggio automatico.
