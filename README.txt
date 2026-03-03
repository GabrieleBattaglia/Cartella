CARTELLA
Utility per la generazione di report strutturati delle directory.

Versione: 4.1.2 (3 marzo 2026)
Autore: Gabriele Battaglia

DESCRIZIONE:
Cartella genera un file di testo (Cartella.txt) che contiene l'elenco di tutti i file e le sottocartelle presenti nel percorso selezionato.

NOVITA' VERSIONE 4.1.0/4.1.1:
- Interfaccia Grafica completa (GUI) con wxPython.
- Filtri personalizzati per nomi di file e per estensioni.
- Supporto ai caratteri jolly: * (molteplici caratteri) e ? (carattere singolo).
- Salvataggio automatico delle impostazioni nel file cartella_settings.json.

COMANDI DA TASTIERA:
- Frecce SU/GIU: Scorrono l'albero delle directory.
- Freccia DESTRA: Entra in una cartella (Espande).
- Freccia SINISTRA: Chiude la cartella corrente o risale al livello superiore.
- INVIO: Avvia la scansione della cartella attualmente selezionata.
- ESC: Chiude l'applicazione.

OPZIONI:
- Numerazione: Aggiunge i numeri di livello (es. 1.1, 1.2).
- Indentazione: Sposta i nomi a destra in base alla profondità.
- Estensione: Include le estensioni dei file (es. .txt, .exe) nel report.

FILTRI:
Tramite il pulsante "Impostazioni Filtri" e' possibile aggiungere pattern di esclusione.
Esempi:
- Nome: backup* (esclude tutti i file che iniziano per backup).
- Estensione: tmp (esclude tutti i file temporanei con quella estensione).

NOTE TECNICHE:
Il programma salva le preferenze in cartella_settings.json per mantenerle ad ogni riavvio.
Il manuale viene caricato direttamente da questo file README.txt.
