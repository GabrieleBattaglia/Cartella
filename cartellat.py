import datetime
import os
from os.path import split
from GBUtils import dgt

VERSIONE = "3.2.8, del 16 gennaio 2024."
ESCLUSIONIPERMANENTI = ["cartella.py", "cartella.app", "cartella", "Cartella.txt", "cartella.exe", "desktop.ini"]
NONINIZIACON = [".", "_"]
BYTESGIGABYTES = 1073741824

filtrati, indentazione, numerazione, estensione = False, False, False, False

def Manuale():
	man = ("Benvenuti nel manuale di CARTELLA.\n"
		   "Questa semplice applicazione svolge il compito di salvare, in un file di testo,\n"
		   "il contenuto della cartella in cui si trova e di tutto il contenuto delle relative sottocartelle.\n"
		   "Usare CARTELLA sarà perciò estremamente facile: basterà incollare cartella.exe nel percorso desiderato,\n"
		   "lanciarlo ed attendere pochi istanti.\n"
		   "Il risultato verrà scritto nel file cartella.txt che troverete dove avete salvato cartella.exe.\n\n"
		   "Attenzione: se cartella.txt esiste già nella posizione da cui eseguite il programma,\n"
		   "questo verrà sovrascritto con la nuova versione.\n\n"
		   "Scrivendo 'opzioni' quando richiesto, potrete modificare le opzioni di cartella.\n"
		   "Cartella possiede 3 opzioni impostate a 'sì' di default. Esse sono:\n"
		   "numerazione: indica se cartella deve indicare il livello di sottocartella cui appartengono i file e le cartelle riportate nel file dei risultati.\n"
		   "indentazione: specifica se i risultati debbano essere rientrati nel file, in base al loro livello di appartenenza.\n"
		   "estensione: lascia scegliere all'utente se i risultati devono includere anche le estensioni dei file.\n"
		   "Digitando filtro, al prompt, potrete indicare una serie di estensioni di file che Cartella non includerà nell'elenco,\n"
		   "questa funzione è utile nel caso in cui vogliate, ad esempio, evitare la visualizzazione di file temporanei.\n")
	print(man)

# main
def main():
	TEMPO = datetime.datetime.now()
	try:
		with open("Cartella.txt", "wt", encoding="utf-8") as f:
			f.write(f"File generato da CARTELLA, versione: {VERSIONE}".center(80, "-") + "\n")
			strutturafilesystem = os.walk(os.getcwd())
			cartellabase = os.getcwd()
			totaleoggetti = 0
			totalebytes = 0
			f.write(f"CARTELLA base: {cartellabase}.".center(80, "-") + '\n')
			n = ""
			elementiincartellabase = len(cartellabase.split(os.path.sep))

			for base, cartelle, files in strutturafilesystem:
				b = base.split(os.path.sep)
				l = len(b) - elementiincartellabase
				i = l * 2 if indentazione else 0
				nc = f"{l}. " if numerazione else ""
				if b[-1][0] not in NONINIZIACON:
					f.write(f"{' ' * i}{nc}[{b[-1]}]...\n")
				c = 1
				for fil in files:
					i = (l + 1) * 2 if indentazione else 0
					n = f"{l + 1}.{c}. " if numerazione else ""
					c += 1
					fil_name, fil_ext = os.path.splitext(fil)
					if not estensione:
						fil = fil_name
					if filtrati:
						est = fil_ext.lower()
						if est not in filtro:
							if fil not in ESCLUSIONIPERMANENTI and fil[0] not in NONINIZIACON:
								f.write(f"{' ' * i}{n}{fil}\n")
					else:
						if fil not in ESCLUSIONIPERMANENTI and fil[0] not in NONINIZIACON:
							f.write(f"{' ' * i}{n}{fil}\n")
					totaleoggetti += 1
					fp = os.path.join(base, fil)
					if not os.path.islink(fp):
						totalebytes += os.path.getsize(fp)

			print(f"Fatto! Troverai cartella.txt in: [{cartellabase}]")
			print(f"Arrivederci da CARTELLA, versione {VERSIONE}.")
			t = datetime.datetime.now() - TEMPO
			f.write("\n")
			f.write("scritto in Python 3, da Gabriele Battaglia.".center(80, "-") + "\n")
			f.write(f"Totale oggetti listati: {totaleoggetti}.".center(80, "-") + "\n")
			f.write(f"Dimensione Totale oggetti listati: {totalebytes / BYTESGIGABYTES:.4f} GigaBytes.".center(80, "-") + "\n")
			f.write((f"Tempo di generazione: {t.seconds} secondi e {t.microseconds} microsecondi.").center(80, "-"))
	except Exception as e:
		print(f"Errore durante l'esecuzione: {e}")

	input("Premi INVIO per chiudere.")

if __name__ == "__main__":
	main()
