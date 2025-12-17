# Cartella. Una utility che salva in txt il contenuto di un albero di directories.
# Data concepimento: giovedì 27 febbraio 2020.
# 28 giugno 2024, pubblicato su GitHub
# Refactoring: mercoledì 17 dicembre 2025

import datetime
import os
import sys

# QC
VERSIONE = "3.4.0, del 17 dicembre 2025."
ESCLUSIONIPERMANENTI = ["cartella.py", "cartella.app", "cartella", "Cartella.txt", "cartella.exe", "desktop.ini"]
NONINIZIACON = [".", "_"]
BYTESGIGABYTES = 1073741824


def dgt(prompt, smin=0, smax=100):
    """Gestisce l'input utente in modo sicuro."""
    while True:
        try:
            val = input(prompt)
            if smin <= len(val) <= smax:
                return val
            print(f"Input non valido. Lunghezza attesa tra {smin} e {smax}.")
        except EOFError:
            return ""
        except KeyboardInterrupt:
            print("\nOperazione annullata dall'utente.")
            sys.exit(0)


def Manuale():
    '''Visualizza il manuale'''
    man = ("Benvenuti nel manuale di CARTELLA.\n"
           "Questa semplice applicazione svolge il compito di salvare, in un file di testo,\n"
           "il contenuto della cartella in cui si trova e di tutto il contenuto\ndelle relative sottocartelle.\nUsare CARTELLA sarà perciò estremamente facile: basterà incollare cartella.exe\n"
           "nel percorso desiderato, lanciarlo ed attendere pochi istanti.\n"
           "Il risultato verrà scritto nel file cartella.txt che troverete dove avete\nsalvato cartella.exe.\n\n"
           "Attenzione: se cartella.txt esiste già nella posizione da cui eseguite il\n\tprogramma, questo verrà sovrascritto con la nuova versione.\n\n"
           "Scrivendo 'opzioni' quando richiesto, potrete modificare le opzioni di cartella\n"
           "cartella possiede 3 opzioni impostate a 'sì' di default. Esse sono:\n"
           "numerazione: indica se cartella deve indicare il livello di sottocartella cui\n\tappartengono i file e le cartelle riportate nel file dei risultati.\n"
           "indentazione: specifica se i risultati debbano essere rientrati nel file,\n\tin base al loro livello di appartenenza.\n"
           "estensione: lascia scegliere all'utente se i risultati devono includere anche\n\tle estensioni dei file.\n"
           "Digitando filtro, al prompt, potrete indicare una serie di estensioni di file che Cartella non includerà nell'elenco,\n"
           "questa funzione è utile nel caso in cui vogliate, ad esempio, evitare la visualizzazione di una determinata tipologia di file\n"
           "Buon divertimento. Gabriele Battaglia\n")
    print(man)
    return


def Opzioni():
    '''Stabilisce le opzioni del programma
    restituisce le booleane corrispondenti'''
    print("Cambio opzioni.")
    x = dgt("Vuoi che gli oggetti siano preceduti dal numero del loro livello di appartenenza? S/N ", smin=1, smax=1)
    numerazione = True if x.lower() == "s" else False
    
    x = dgt("Vuoi che il risultato sia formattato con indentazione? S/N ", smin=1, smax=1)
    indentazione = True if x.lower() == "s" else False
    
    x = dgt("Vuoi che i nomi degli oggetti siano completi di estensione? S/N ", smin=1, smax=1)
    estensione = True if x.lower() == "s" else False
    
    print("Grazie")
    return numerazione, indentazione, estensione


def Filtri():
    '''restituisce la lista delle estensioni da non visualizzare'''
    print("Bene, scrivi tutte le estensioni che determineranno i file da non includere nella lista.\nInserisci solo l'estensione, senza punto e seguita da invio.\nConcludi con un invio a vuoto.")
    f = []
    contatore = 1
    while True:
        a = dgt(f"{contatore}a estensione: > ", smax=20)
        if a == "":
            break
        f.append(a.lower())
        contatore += 1
    print("Ottimo, verranno esclusi tutti i file che hanno le seguenti estensioni:")
    for j in f:
        print(j, end=", ")
    print("\n")
    return f


def main():
    filtro = []
    filtrati, indentati, opzionati, estensionati = False, False, False, False
    print(f"Chiamato? Ciao! Sono CARTELLA {VERSIONE} e lavoro per te\n\tSe vuoi sapere come funziono, scrivi aiuto,\n\tSe vuoi cambiare le opzioni, scrivi opzioni,\nse vuoi attivare il filtro per escludere determinati file, scrivi filtro, altrimenti batti invio.")

    while True:
        print("Scegli: Aiuto, opzioni, filtro o invio a vuoto per proseguire.")
        a = dgt("...> ", smax=7)
        if a.lower() == "aiuto":
            Manuale()
        elif a.lower() == "opzioni":
            numerazione, indentazione, estensione = Opzioni()
            opzionati = True
        elif a.lower() == "filtro":
            filtro = Filtri()
            filtrati = True
        elif a == "":
            print("Proseguiamo!")
            break
    
    if not opzionati:
        indentazione, numerazione, estensione = True, True, True

    TEMPO = datetime.datetime.now()
    output_filename = "Cartella.txt"
    
    try:
        f = open(output_filename, "wt", encoding="utf-8")
    except IOError as e:
        print(f"Errore critico: impossibile scrivere il file {output_filename}. {e}")
        return

    f.write(f"File generato da CARTELLA, versione: {VERSIONE}".center(80, "-") + "\n")
    
    cartellabase = os.getcwd()
    strutturafilesystem = os.walk(cartellabase)
    
    totaleoggetti = 0
    totalebytes = 0
    
    f.write(f"CARTELLA base: {cartellabase}.".center(80, "-") + '\n')
    
    elementiincartellabase = len(cartellabase.split(os.path.sep))
    
    for base, cartelle, files in strutturafilesystem:
        # Calcolo livello
        b = base.split(os.path.sep)
        l = len(b) - elementiincartellabase
        
        # Formattazione Directory
        i = l * 2 if indentazione else 0
        nc = f"{l}. " if numerazione else ""
        
        dirname = b[-1]
        if dirname and dirname[0] not in NONINIZIACON:
             f.write(f"{' '*i}{nc}[{dirname}]...\n")
        
        c = 1
        for fil in files:
            original_fil = fil
            
            # Controllo file nascosti o di sistema
            if not original_fil or original_fil in ESCLUSIONIPERMANENTI or original_fil[0] in NONINIZIACON:
                continue

            # Gestione estensione e filtri
            nome_base, est_raw = os.path.splitext(original_fil)
            est = est_raw.lstrip(".").lower() # Rimuove il punto iniziale per confronto pulito
            
            if filtrati and est in filtro:
                continue
            
            # Formattazione File
            i = (l + 1) * 2 if indentazione else 0
            
            n = ""
            if numerazione:
                n = f"{l+1}.{c}. "
                c += 1
            
            nome_visualizzato = original_fil if estensione else nome_base
            
            # Scrittura
            f.write(f"{' '*i}{n}{nome_visualizzato}\n")
            
            # Aggiornamento statistiche (SOLO SE SCRITTO)
            totaleoggetti += 1
            fp = os.path.join(base, original_fil)
            if not os.path.islink(fp) and os.path.exists(fp):
                try:
                    totalebytes += os.path.getsize(fp)
                except OSError as e:
                    # Non stampare errore per ogni file inaccessibile, magari loggalo o ignoralo
                    pass

    print(f"Fatto! Troverai {output_filename} in: [{cartellabase}]")
    print(f"Arrivederci da CARTELLA, versione {VERSIONE}.")
    
    t = datetime.datetime.now() - TEMPO
    f.write("\n")
    f.write("scritto in Python 3, da Gabriele Battaglia.".center(80, "-") + "\n")
    f.write(f"Totale oggetti listati: {totaleoggetti}.".center(80, "-") + "\n")
    f.write(f"Dimensione Totale oggetti listati: {totalebytes/BYTESGIGABYTES:.4f} GigaBytes.".center(80, "-") + "\n")
    f.write((f"Tempo di generazione: {t.seconds} secondi e {t.microseconds} microsecondi.").center(80, "-"))
    f.close()
    
    input("Premi INVIO per chiudere.")

if __name__ == "__main__":
    main()