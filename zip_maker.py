# Cartella, utilita': prepara l'archivio per la distribuzione.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' auto).
# 04/09/2026: primo chiamante, il mestiere sta in crea_archivio_release di GBUtils V104.

"""Comprime il risultato di PyInstaller in un solo archivio.

Tutto il mestiere sta in GBUtils, cosi' la regola sulle esclusioni e' una
sola per tutti i progetti. Qui restano soltanto i nomi di Cartella.

Cartella si compila in un file unico, quindi dentro dist c'e' soltanto
l'eseguibile e tutto il resto viaggia dentro di lui. Le eccezioni sono
due: get_base_path, quando l'app e' congelata, restituisce la cartella
dell'eseguibile e non quella temporanea di PyInstaller, percio' README.txt
deve stare accanto al programma o la voce Manuale non trova niente. La
release 4.2.1 pubblicata contiene infatti cartella.exe, LICENSE e
README.txt, e questo script li rimette li' da se': era un passaggio a
mano, e i passaggi a mano prima o poi si dimenticano.

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
DIST = os.path.join(QUI, "dist")
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
        print("Archivio non creato: manca la cartella dist, compila prima.")
        return 1
    try:
        for nome in ACCANTO:
            shutil.copy2(os.path.join(QUI, nome), os.path.join(DIST, nome))
        crea_archivio_release("Cartella", cartella_dist="dist", archivio=f"cartella_portable_v{versione()}.zip", escludi=FUORI)
    except (FileNotFoundError, OSError, ValueError) as e:
        print(f"Archivio non creato: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
