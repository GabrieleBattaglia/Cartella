# Cartella
**Cartella** è una utility che genera un report testuale (`Cartella.txt`) contenente la struttura dell'albero di directory selezionato, utile per documentare contenuti di dischi o cartelle.

**Versione:** 4.0.0 (3 febbraio 2026)
**Autore:** Gabriele Battaglia

## Novità della Versione 4.0.0
- **Interfaccia Grafica (GUI):** Abbandonata l'interfaccia a riga di comando per una più comoda interfaccia visiva basata su `wxPython`.
- **Navigazione Semplificata:** Uso intuitivo delle frecce direzionali per esplorare le cartelle.
- **Manuale Integrato:** Le istruzioni sono visibili direttamente nella finestra principale.

## Installazione e Requisiti
Richiede Python 3 e la libreria `wxPython`.
```bash
pip install wxPython
```

## Utilizzo
Esegui lo script:
```bash
python cartella.py
```

### Comandi da Tastiera
L'interfaccia è progettata per essere usata rapidamente anche solo con la tastiera:

*   **Frecce Su/Giù:** Scorri l'elenco delle cartelle e dei file.
*   **Freccia Destra:** Entra in una cartella (Espande il nodo).
*   **Freccia Sinistra:** Esce dalla cartella corrente (Collassa il nodo o torna al livello superiore).
*   **Tab:** Sposta il focus tra l'albero delle cartelle, le opzioni e il manuale.
*   **Invio:** Avvia la creazione del file `Cartella.txt` basandosi sulla cartella attualmente selezionata.
*   **Esc:** Chiude il programma.

### Opzioni
*   **Numerazione:** Aggiunge una numerazione gerarchica ai file (es. 1.1, 1.2).
*   **Indentazione:** Rientra visivamente i nomi per rappresentare la struttura ad albero.
*   **Estensione:** Include l'estensione dei file nel report.

## Output
Il programma genererà un file chiamato `Cartella.txt` nella stessa directory dello script. Attenzione: se il file esiste già, verrà sovrascritto.
