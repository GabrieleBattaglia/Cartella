CARTELLA
Scrive in un file di testo l'elenco di tutto cio' che sta in una cartella e nelle sue sottocartelle.
Versione 5.0.0 del 8 settembre 2026.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode).

COSA FA
Si sceglie una cartella nell'albero, si preme invio, e Cartella scrive accanto al programma un file di testo chiamato con il nome della cartella scandita, la data e l'ora, per esempio Cartella (Belgio 2004) - 2026-09-08 - 16.55.txt. Ogni scansione ha il proprio file, e gli elenchi precedenti restano. Il file comincia con la versione del programma, la data e l'ora della scansione e la cartella di partenza; poi viene l'elenco; in fondo il riepilogo.
Il file compare soltanto a scansione finita: se qualcosa va storto a meta', non resta un elenco troncato che sembra completo.

L'ELENCO
Ogni cartella sta fra parentesi quadre. Dentro ogni cartella vengono prima i file, in ordine alfabetico, poi le sottocartelle, ciascuna con il proprio contenuto.
Con la numerazione accesa ogni elemento porta un numero gerarchico: i file e le sottocartelle della cartella di partenza si numerano 1, 2, 3 e cosi' via; il contenuto della cartella numero 3 si numera 3.1, 3.2; il contenuto della cartella 3.2 si numera 3.2.1, 3.2.2. Il numero dice quindi la strada per arrivare all'elemento, e due righe con lo stesso numero non esistono.
Con l'indentazione accesa ogni livello sposta la riga di due spazi a destra.
Con l'estensione spenta i nomi dei file compaiono senza estensione.

IL RIEPILOGO
In fondo al file: gli oggetti elencati, la dimensione totale nell'unita' adatta, cioe' byte, KB, MB, GB o TB, il tempo di generazione a parole, gli elementi esclusi dai filtri con il conto per ciascun filtro, i collegamenti a cartelle non seguiti, e le cartelle che non si sono potute leggere, ciascuna con il motivo. Se qualche file non si e' potuto misurare, la dimensione totale e' dichiarata come almeno.
Lo stesso riepilogo compare nella finestra di fine scansione.

COMANDI DA TASTIERA
Frecce su e giu': scorrono l'albero delle cartelle.
Freccia destra: apre la cartella.
Freccia sinistra: chiude la cartella, oppure risale a quella superiore.
Invio: avvia la scansione della cartella selezionata. Non lo fa quando il cursore sta dentro questo manuale, dove invio serve a leggere.
Escape: chiude il programma.
Durante la scansione la finestra resta viva: un suono segna l'avvio e un altro la fine. Un secondo invio prima della fine viene rifiutato con un suono, e anche la chiusura aspetta che la scansione finisca.

OPZIONI
Numerazione, Indentazione ed Estensione sono tre caselle di controllo e si salvano subito.

FILTRI
Il pulsante Impostazioni filtri apre due elenchi: i filtri per nome, che valgono per le cartelle e per i file, e i filtri per estensione, che valgono per i soli file. Si usano i caratteri jolly: l'asterisco per una sequenza qualunque di caratteri, il punto interrogativo per un carattere solo. Le maiuscole non contano.
I filtri per nome predefiniti sono Cartella (*.txt, cartella.exe, cartella_settings.json, desktop.ini, .* e _*: escludono gli elenchi prodotti dal programma e i suoi file, il desktop.ini di Windows e tutto cio' che comincia per punto o per trattino basso, che di norma e' di servizio. Si tolgono come qualunque altro filtro, e il pulsante Rimetti i predefiniti li riporta.
Esempi: backup* esclude tutto cio' che comincia per backup; tmp, fra le estensioni, esclude i file temporanei.

IMPOSTAZIONI
Le impostazioni stanno in cartella_settings.json accanto al programma, con l'ultima cartella visitata. Si salvano a ogni cambiamento e alla chiusura. Se il file non si legge, il programma lo dice, riparte dai valori predefiniti e mette da parte il file rotto con l'estensione .rotto, cosi' i filtri si possono recuperare.

AGGIORNAMENTI
L'eseguibile controlla all'avvio se esiste una versione nuova. Se c'e', una finestra dice la versione disponibile e quella in uso, mostra le novita' in un campo di testo che si scorre con le frecce, e offre due pulsanti: Aggiorna adesso e Non adesso. Escape e la chiusura della finestra valgono come Non adesso. Se qualcosa va storto, l'errore finisce in auto_updater_error.log accanto al programma.

NOTE
Il manuale e' questo file README.txt, che deve stare accanto al programma.
L'eseguibile non e' firmato: al primo avvio Windows puo' mostrare l'avviso di SmartScreen, ed e' normale.
