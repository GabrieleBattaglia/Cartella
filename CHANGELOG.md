# Changelog, Cartella

Tutti i cambiamenti e le novità introdotte nelle versioni di Cartella.
Il changelog nasce con la versione 5.0.0. Le novità delle versioni precedenti, che stavano dentro il manuale, sono riportate in fondo.

## [5.0.0] - 2026-09-08

Pubblicata su GitHub il 2026-09-08 come release `v5.0.0`, con il solo archivio `cartella_portable_v5.0.0.zip` in allegato. Verificato che l'auto updater la riconosca e ne riceva le note. Issue 1 chiusa.

Revisione 1 del refactoring generale, più la finestra di aggiornamento chiesta dalla issue 1.

### Aggiunto

- **Un file per ogni scansione**, chiamato con il nome della cartella scandita, la data e l'ora, come `Cartella (Belgio 2004) - 2026-09-08 - 16.55.txt`, accanto al programma. Prima il file era sempre `Cartella.txt` e ogni scansione cancellava la precedente. Per la radice di un disco il nome è la lettera del disco.
- **Numerazione gerarchica**: ogni elemento porta i numeri di tutte le cartelle attraversate, come 3.2.1, quindi il numero dice la strada per arrivarci e due righe con lo stesso numero non esistono. Prima il numero era livello e contatore, e si ripeteva uguale in tutte le cartelle dello stesso livello.
- Le **cartelle che non si sono potute leggere**, per esempio per un permesso negato, vengono raccolte e scritte in fondo all'elenco con il motivo, invece di sparire in silenzio. I file che non si sono potuti misurare vengono contati e la dimensione totale viene dichiarata come almeno.
- Il riepilogo dice **quanti elementi ha escluso ciascun filtro**, e quanti collegamenti a cartelle non ha seguito.
- **Le esclusioni predefinite sono visibili** nella finestra dei filtri, come voci che si possono togliere, con un pulsante che le rimette. Fino alla 4.2.1 sette nomi e due prefissi erano esclusi di nascosto dal codice, e i filtri dell'utente li ripetevano senza saperlo. Alla prima esecuzione i predefiniti mancanti entrano nei filtri salvati.
- **Finestra di aggiornamento** (issue 1): dice la versione disponibile e quella in uso, mostra le novità della release in un campo di testo che si scorre e si rilegge con le frecce, e offre i pulsanti Aggiorna adesso e Non adesso; escape vale come Non adesso.
- **Suoni** dalla collezione condivisa di GBUtils: uno all'avvio della scansione, uno alla fine, uno per gli errori e uno quando un invio viene rifiutato perché la scansione è già in corso. Senza GBUtils resta il segnale di sistema.
- La scansione gira in un **thread separato**: la finestra resta viva e lo screen reader non la dà per bloccata. Un secondo invio durante la scansione viene rifiutato, e la chiusura aspetta la fine.
- File di contorno finora assenti: `CHANGELOG.md`, `requirements.txt` e `ruff.toml`; `cartella.spec` è ora versionato.

### Cambiato

- **Via i separatori di trattini** dal file prodotto: intestazione e riepilogo sono frasi normali, una per riga, senza centratura.
- La **dimensione totale** si esprime nell'unità adatta alla grandezza, da byte a TB, con un decimale, invece che sempre in gigabyte con quattro decimali.
- Il **tempo di generazione** si dice a parole, per esempio due minuti e dodici secondi, con i decimi solo sotto il secondo. Prima il file diceva secondi e microsecondi e la finestra un orario grezzo.
- I file e le cartelle sono in ordine alfabetico, senza badare alle maiuscole; le cartelle non portano più i tre puntini dopo il nome.
- I confronti dei filtri non badano alle maiuscole, e i filtri per nome valgono per cartelle e file allo stesso modo.
- Invio dentro il manuale non avvia più la scansione.
- Versione, data di rilascio e autori stanno in tre costanti separate; a `update_checker` arriva la sola versione.
- Il manuale non contiene più le novità delle versioni, che stanno qui.
- `cartella_settings.json` non è più versionato in git: contiene l'ultima cartella visitata, che è un dato personale.

### Corretto

- **Livello sbagliato sulla radice di un disco**: con base come `E:\` la barra finale produceva un pezzo vuoto nel conteggio e tutto l'albero perdeva un livello. Il livello ora si calcola sul percorso relativo.
- **Una scansione fallita non lascia un elenco troncato**: si scrive su un file temporaneo che prende il nome definitivo solo a fine scrittura.
- Un file delle impostazioni illeggibile viene messo da parte con l'estensione `.rotto` e il programma lo dice, invece di riscriverlo in silenzio al primo cambiamento e perdere i filtri. I valori del tipo sbagliato tornano al predefinito.
- Le impostazioni si salvano anche quando il programma si chiude per applicare un aggiornamento.
- Il controllo aggiornamenti verifica che la finestra esista ancora prima di mostrare qualcosa, e un errore nel thread viene detto invece di sparire.
- I collegamenti a cartelle non vengono seguiti: uno che punta a un'antenata faceva girare la scansione per sempre.
- Il file prodotto termina con un ritorno a capo.
- Tolto il ramo morto che usava la directory di lavoro come base.
- Il codice passa `ruff` senza rilievi.

## Versioni precedenti

Riportate dal manuale, dove stavano fino alla 4.2.1.

### 4.2.0 e 4.2.1

- Memorizzazione dell'ultima cartella esplorata alla chiusura del programma.

### 4.1.0 e 4.1.1

- Interfaccia grafica completa con wxPython.
- Filtri personalizzati per nomi di file e per estensioni.
- Supporto ai caratteri jolly: `*` per più caratteri e `?` per un carattere singolo.
- Salvataggio automatico delle impostazioni nel file `cartella_settings.json`.
