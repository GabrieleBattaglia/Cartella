# Cartella, utilita': prepara l'archivio per la distribuzione.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' auto).
# 04/09/2026: primo chiamante, il mestiere sta in crea_archivio_release di GBUtils V104.

"""Comprime il risultato di PyInstaller in un solo archivio.

Tutto il mestiere sta in GBUtils, cosi' la regola sulle esclusioni e' una
sola per tutti i progetti. Qui restano soltanto i nomi di Cartella.

Dalla 5.1.2 Cartella si compila a cartella, come tutto il parco: in
dist, sottocartella cartella, ci sono l'eseguibile e _internal. Accanto all'eseguibile
vanno anche README.txt e LICENSE: get_base_path, quando l'app e'
congelata, restituisce la cartella dell'eseguibile, percio' senza il
manuale li' la voce Manuale non trova niente. Questo script ce li mette
da se': era un passaggio a mano, e i passaggi a mano prima o poi si
dimenticano. Fino alla 5.1.1 il pacchetto era un file unico, e dist
conteneva il solo eseguibile.

Il nome dell'archivio porta la versione, come le release gia' pubblicate,
e la versione si legge dal sorgente perche' deve stare in un posto solo.

Si lasciano fuori le impostazioni, l'elenco che Cartella scrive e il
desktop.ini di Windows: nascono provando l'eseguibile prima di comprimere.
"""

import os
import re
import shutil
import sys

from GBUtils import crea_archivio_release

QUI = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(QUI, "dist", "cartella")
ACCANTO = ["README.txt", "LICENSE"]
FUORI = ["cartella_settings.json", "cartella_settings.json.rotto", "desktop.ini", "auto_updater_error.log"]


def versione():
    """La versione sta in cartella.py e da li' si legge, non si duplica."""
    with open(os.path.join(QUI, "cartella.py"), encoding="utf-8") as f:
        sorgente = f.read()
    trovato = re.search(r'VERSIONE\s*=\s*["\']([\d.]+)', sorgente)
    if not trovato:
        raise ValueError("Versione non trovata in cartella.py")
    return trovato.group(1)


def main():
    if not os.path.isdir(DIST):
        print("Archivio non creato: manca la cartella dist\\cartella, compila prima.")
        return 1
    try:
        for nome in ACCANTO:
            shutil.copy2(os.path.join(QUI, nome), os.path.join(DIST, nome))
        crea_archivio_release("Cartella", cartella_dist=os.path.join("dist", "cartella"), archivio=f"cartella_portable_v{versione()}.zip", escludi=FUORI)
    except (FileNotFoundError, OSError, ValueError) as e:
        print(f"Archivio non creato: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
