# Cartella. Una utility che salva in txt il contenuto di un albero di directories.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode)
# Data concepimento: giovedi' 27 febbraio 2020.
# 28 giugno 2024, pubblicato su GitHub.
# Refactoring GUI: martedi' 3 marzo 2026.
# 08/09/2026: revisione 1 del refactoring generale, versione 5.0.0.

import contextlib
import datetime
import fnmatch
import json
import os
import sys
import threading
import time
import traceback

import wx

# GBUtils serve per i suoni, per l'aggiornamento e per scrivere le dimensioni.
# Da sorgente il programma deve partire anche dove manca: resta muto, senza
# controllo aggiornamenti e con le dimensioni in byte.
try:
    from GBUtils import Acusticator, cartella_applicazione, formatta_dimensione
except ImportError:
    Acusticator = None
    cartella_applicazione = None

    def formatta_dimensione(byte, **gusto):
        """Il ripiego di quando GBUtils non c'e': i byte, senza salire di
        unita'. Il rapporto esce lo stesso, con le dimensioni piu' scomode da
        leggere, invece di fermarsi con un errore."""
        return f"{int(byte)} byte"

APP_NAME = "cartella"
VERSIONE = "5.0.3"
RELEASE_DATE = "2026-09-14"
AUTORI = "Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode)"
API_RELEASE = "https://api.github.com/repos/GabrieleBattaglia/Cartella/releases/latest"
NOME_IMPOSTAZIONI = "cartella_settings.json"
NOME_MANUALE = "README.txt"
# Cio' che il programma esclude da se': dalla 5.0.0 sta fra i filtri
# visibili nella finestra, dove si puo' togliere, invece che nascosto nel
# codice. Le cartelle e i file che cominciano per punto o per trattino basso
# sono di norma di servizio.
FILTRI_PREDEFINITI = ["Cartella (*.txt", "cartella.exe", "cartella_settings.json", "desktop.ini", ".*", "_*"]
FORMATO_IMPOSTAZIONI = 2
UNITA = ("byte", "KB", "MB", "GB", "TB")
# Come Cartella scrive una dimensione: un decimale, la virgola e, sotto il
# chilo, i byte interi. La formula sta in GBUtils dalla V156, con la issue 9,
# perche' era riscritta in quattro programmi; qui resta soltanto il gusto.
COME_BYTE = {"decimali": 1, "separatore": ",", "unita": UNITA, "byte_interi": True}
SUONI = {
    "avvio_scansione": "partenza",
    "fine_scansione": "terminata",
    "errore": "errore_secco",
    "rifiutato": "rifiutato",
}
IMPOSTAZIONI_PREDEFINITE = {
    "formato": FORMATO_IMPOSTAZIONI,
    "numerazione": True,
    "indentazione": True,
    "estensione": True,
    "filtro_nomi": FILTRI_PREDEFINITI,
    "filtro_estensioni": [],
    "ultima_cartella": "",
}


def get_base_path():
    """Il percorso base, accanto allo script o all'eseguibile PyInstaller.
    La logica sta in GBUtils, come tutte le utilita' condivise. Le tre righe
    di riserva servono al caso, dichiarato in cima al file, di un avvio da
    sorgente dove GBUtils non c'e': il programma deve partire lo stesso."""
    if cartella_applicazione is not None:
        return cartella_applicazione()
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def suona(evento):
    """Un suono della collezione condivisa; senza GBUtils, il segnale di sistema."""
    nome = SUONI.get(evento)
    if Acusticator is not None and nome:
        Acusticator.play(nome)
    else:
        wx.Bell()


# Impostazioni.


def percorso_impostazioni():
    return os.path.join(get_base_path(), NOME_IMPOSTAZIONI)


def _lista_di_stringhe(valore):
    if not isinstance(valore, list):
        return None
    return [v.strip() for v in valore if isinstance(v, str) and v.strip()]


def normalizza_impostazioni(dati):
    """Tiene solo i valori del tipo giusto; il resto torna al predefinito.

    Un file scritto da una versione precedente non ha il campo formato: in
    quel caso le esclusioni che il codice applicava di nascosto entrano nei
    filtri visibili, senza doppioni.
    """
    impostazioni = {chiave: (list(valore) if isinstance(valore, list) else valore) for chiave, valore in IMPOSTAZIONI_PREDEFINITE.items()}
    for chiave in ("numerazione", "indentazione", "estensione"):
        if isinstance(dati.get(chiave), bool):
            impostazioni[chiave] = dati[chiave]
    for chiave in ("filtro_nomi", "filtro_estensioni"):
        lista = _lista_di_stringhe(dati.get(chiave))
        if lista is not None:
            impostazioni[chiave] = lista
    if isinstance(dati.get("ultima_cartella"), str):
        impostazioni["ultima_cartella"] = dati["ultima_cartella"]
    if dati.get("formato") != FORMATO_IMPOSTAZIONI:
        presenti = {f.lower() for f in impostazioni["filtro_nomi"]}
        impostazioni["filtro_nomi"].extend(f for f in FILTRI_PREDEFINITI if f.lower() not in presenti)
    impostazioni["formato"] = FORMATO_IMPOSTAZIONI
    return impostazioni


def carica_impostazioni():
    """Restituisce le impostazioni e un avviso, vuoto se e' andato tutto bene.

    Un file che non si legge viene messo da parte con un altro nome, cosi'
    il prossimo salvataggio non lo cancella e i filtri si possono recuperare.
    """
    percorso = percorso_impostazioni()
    if not os.path.exists(percorso):
        return normalizza_impostazioni({}), ""
    try:
        with open(percorso, encoding="utf-8") as f:
            dati = json.load(f)
        if not isinstance(dati, dict):
            raise ValueError("il contenuto non e' un dizionario")
    except (OSError, ValueError) as e:
        rotto = percorso + ".rotto"
        with contextlib.suppress(OSError):
            os.replace(percorso, rotto)
        avviso = (
            f"Le impostazioni salvate non si leggono: {e}.\n"
            "Riparto da quelle predefinite.\n"
            f"Il file rotto e' {os.path.basename(rotto)},\n"
            "accanto al programma."
        )
        return normalizza_impostazioni({}), avviso
    return normalizza_impostazioni(dati), ""


def salva_impostazioni(impostazioni):
    """Scrive su un file temporaneo e sostituisce solo a scrittura riuscita. Restituisce l'errore, o vuoto."""
    percorso = percorso_impostazioni()
    temporaneo = percorso + ".tmp"
    try:
        with open(temporaneo, "w", encoding="utf-8") as f:
            json.dump(impostazioni, f, indent=4, ensure_ascii=False)
        os.replace(temporaneo, percorso)
    except OSError as e:
        with contextlib.suppress(OSError):
            os.remove(temporaneo)
        return f"Impostazioni non salvate: {e}"
    return ""


# Formattazioni.


def formatta_durata(secondi):
    """Una durata a parole, con i decimi solo sotto il secondo."""
    if secondi < 1:
        return f"{secondi:.1f}".replace(".", ",") + " secondi"
    totale = round(secondi)
    ore, resto = divmod(totale, 3600)
    minuti, sec = divmod(resto, 60)
    parti = []
    if ore:
        parti.append(f"{ore} {'ora' if ore == 1 else 'ore'}")
    if minuti:
        parti.append(f"{minuti} {'minuto' if minuti == 1 else 'minuti'}")
    if sec or not parti:
        parti.append(f"{sec} {'secondo' if sec == 1 else 'secondi'}")
    if len(parti) == 3:
        return f"{parti[0]}, {parti[1]} e {parti[2]}"
    return " e ".join(parti)


def plurale(quanti, singolare, plurale_):
    return f"{quanti} {singolare if quanti == 1 else plurale_}"


def nome_report(base, quando):
    """Il nome del file prodotto: Cartella (nome della cartella scandita) - data - ora.txt.

    Ogni scansione ha cosi' il proprio file, e due inventari possono
    convivere. Per la radice di un disco il nome e' la lettera del disco.
    """
    nome = os.path.basename(base) or os.path.splitdrive(base)[0].rstrip(":") or base
    nome = "".join(ch for ch in nome if ch not in '<>:"/\\|?*').strip() or "radice"
    return f"Cartella ({nome}) - {quando.strftime('%Y-%m-%d')} - {quando.strftime('%H.%M')}.txt"


# Il report.


class Filtri:
    """I filtri dell'utente. I confronti non badano alle maiuscole."""

    def __init__(self, nomi, estensioni):
        self.nomi = [n for n in nomi if n.strip()]
        self.estensioni = [e.lstrip(".").lower() for e in estensioni if e.strip(".").strip()]

    def esclude_nome(self, nome):
        """Il filtro che esclude questo nome, oppure None."""
        minuscolo = nome.lower()
        for filtro in self.nomi:
            if fnmatch.fnmatchcase(minuscolo, filtro.lower()):
                return filtro
        return None

    def esclude_estensione(self, nome):
        """Il filtro di estensione che esclude questo file, oppure None."""
        estensione = os.path.splitext(nome)[1].lstrip(".").lower()
        for filtro in self.estensioni:
            if fnmatch.fnmatchcase(estensione, filtro):
                return filtro
        return None


class Risultato:
    """Cio' che la scansione ha prodotto e cio' che non ha potuto fare."""

    def __init__(self, base, percorso):
        self.base = base
        self.percorso = percorso
        self.oggetti = 0
        self.byte = 0
        self.non_misurati = 0
        self.non_letti = []
        self.esclusi = {}
        self.collegamenti = 0
        self.durata = 0.0

    def conta_escluso(self, regola):
        self.esclusi[regola] = self.esclusi.get(regola, 0) + 1

    @property
    def totale_esclusi(self):
        return sum(self.esclusi.values())

    def righe_riepilogo(self):
        """Il riepilogo in frasi, uguale in fondo al file e nella finestra finale."""
        righe = [f"Oggetti elencati: {self.oggetti}."]
        if self.non_misurati:
            righe.append(f"Dimensione totale: almeno {formatta_dimensione(self.byte, **COME_BYTE)},")
            righe.append(f"{plurale(self.non_misurati, 'file non misurato', 'file non misurati')}.")
        else:
            righe.append(f"Dimensione totale: {formatta_dimensione(self.byte, **COME_BYTE)}.")
        righe.append(f"Tempo di generazione: {formatta_durata(self.durata)}.")
        if self.esclusi:
            righe.append(f"Esclusi dai filtri: {plurale(self.totale_esclusi, 'elemento', 'elementi')}.")
        if self.collegamenti:
            righe.append(f"Collegamenti a cartelle non seguiti: {self.collegamenti}.")
        if self.non_letti:
            righe.append(f"Cartelle non lette: {len(self.non_letti)}.")
        return righe

    def righe_dettaglio(self):
        """Le righe che stanno solo in fondo al file: cosa ha escluso quale filtro, e cosa non si e' letto."""
        righe = []
        for regola, quanti in sorted(self.esclusi.items(), key=lambda voce: (-voce[1], voce[0])):
            righe.append(f"Filtro {regola}: {plurale(quanti, 'elemento', 'elementi')}.")
        for percorso, motivo in self.non_letti:
            righe.append(f"Non letta: {percorso}")
            righe.append(f"Motivo: {motivo}.")
        return righe


def _numero(prefisso, contatore):
    return f"{prefisso}.{contatore}" if prefisso else str(contatore)


def genera_report(cartellabase, output_filename, settings):
    """Scrive l'elenco su un file temporaneo e lo rinomina solo a fine scrittura.

    Cosi' un errore a meta' non lascia un file troncato che sembra completo.
    Solleva OSError se il file non si puo' scrivere.
    Le cartelle che os.walk non riesce ad aprire, per esempio per un permesso
    negato, vengono raccolte e scritte in fondo invece di sparire in silenzio.
    La numerazione e' gerarchica: ogni elemento porta i numeri di tutte le
    cartelle attraversate, quindi due righe con lo stesso numero non esistono.
    """
    inizio = time.perf_counter()
    numerazione = settings.get("numerazione", True)
    indentazione = settings.get("indentazione", True)
    estensione = settings.get("estensione", True)
    filtri = Filtri(settings.get("filtro_nomi", []), settings.get("filtro_estensioni", []))
    base = os.path.normpath(cartellabase)
    risultato = Risultato(base, output_filename)
    numeri = {base: ""}
    adesso = datetime.datetime.now()

    def non_letta(errore):
        percorso = getattr(errore, "filename", None) or base
        motivo = getattr(errore, "strerror", None) or str(errore)
        risultato.non_letti.append((str(percorso), motivo))

    def rientro(livello):
        return "  " * livello if indentazione else ""

    temporaneo = output_filename + ".tmp"
    try:
        with open(temporaneo, "w", encoding="utf-8") as f:
            f.write(f"Elenco generato da Cartella {VERSIONE}\n")
            f.write(f"il {adesso.strftime('%d/%m/%Y')} alle {adesso.strftime('%H:%M')}.\n")
            f.write(f"Cartella base: {base}\n")
            for percorso, cartelle, files in os.walk(base, onerror=non_letta):
                if percorso == base:
                    livello = 0
                    prefisso = ""
                    f.write(f"[{os.path.basename(base) or base}]\n")
                else:
                    livello = os.path.relpath(percorso, base).count(os.sep) + 1
                    prefisso = numeri.pop(percorso, "")
                    etichetta = f"{prefisso}. " if numerazione and prefisso else ""
                    f.write(f"{rientro(livello)}{etichetta}[{os.path.basename(percorso)}]\n")
                tenute = []
                for nome in sorted(cartelle, key=str.lower):
                    regola = filtri.esclude_nome(nome)
                    if regola:
                        risultato.conta_escluso(regola)
                    elif os.path.isjunction(os.path.join(percorso, nome)):
                        # Un collegamento a cartella puo' puntare a un'antenata
                        # e far girare la scansione per sempre: si conta e basta.
                        risultato.collegamenti += 1
                    else:
                        tenute.append(nome)
                cartelle[:] = tenute
                contatore = 0
                for nome in sorted(files, key=str.lower):
                    regola = filtri.esclude_nome(nome) or filtri.esclude_estensione(nome)
                    if regola:
                        risultato.conta_escluso(regola)
                        continue
                    contatore += 1
                    etichetta = f"{_numero(prefisso, contatore)}. " if numerazione else ""
                    mostrato = nome if estensione else os.path.splitext(nome)[0]
                    f.write(f"{rientro(livello + 1)}{etichetta}{mostrato}\n")
                    risultato.oggetti += 1
                    completo = os.path.join(percorso, nome)
                    if not os.path.islink(completo):
                        try:
                            risultato.byte += os.path.getsize(completo)
                        except OSError:
                            risultato.non_misurati += 1
                # Le sottocartelle continuano la numerazione dei file, cosi'
                # ogni elemento della cartella ha un numero suo.
                for nome in cartelle:
                    contatore += 1
                    numeri[os.path.join(percorso, nome)] = _numero(prefisso, contatore)
            risultato.durata = time.perf_counter() - inizio
            for riga in risultato.righe_riepilogo() + risultato.righe_dettaglio():
                f.write(riga + "\n")
        os.replace(temporaneo, output_filename)
    except BaseException:
        with contextlib.suppress(OSError):
            os.remove(temporaneo)
        raise
    return risultato


def get_manuale_text():
    percorso = os.path.join(get_base_path(), NOME_MANUALE)
    try:
        with open(percorso, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as e:
        return f"Manuale non disponibile.\nCercato in: {percorso}\nMotivo: {e}"


# Finestre di dialogo.


class FilterDialog(wx.Dialog):
    def __init__(self, parent, settings):
        super().__init__(parent, title="Impostazioni filtri", size=(520, 520))
        self.settings = settings
        main_vbox = wx.BoxSizer(wx.VERTICAL)
        lbl_nomi = wx.StaticText(self, label="Escludi cartelle e file per nome (es: backup*, temp_?):")
        main_vbox.Add(lbl_nomi, 0, wx.ALL, 10)
        hbox_nomi = wx.BoxSizer(wx.HORIZONTAL)
        self.list_nomi = wx.ListBox(self, choices=self.settings["filtro_nomi"], style=wx.LB_SINGLE)
        hbox_nomi.Add(self.list_nomi, 1, wx.EXPAND | wx.LEFT, 10)
        vbox_btn_nomi = wx.BoxSizer(wx.VERTICAL)
        btn_add_nome = wx.Button(self, label="Aggiungi...")
        btn_del_nome = wx.Button(self, label="Rimuovi")
        btn_predefiniti = wx.Button(self, label="Rimetti i predefiniti")
        vbox_btn_nomi.Add(btn_add_nome, 0, wx.BOTTOM, 5)
        vbox_btn_nomi.Add(btn_del_nome, 0, wx.BOTTOM, 5)
        vbox_btn_nomi.Add(btn_predefiniti, 0)
        hbox_nomi.Add(vbox_btn_nomi, 0, wx.LEFT | wx.RIGHT, 10)
        main_vbox.Add(hbox_nomi, 1, wx.EXPAND)
        lbl_est = wx.StaticText(self, label="Escludi file per estensione (es: exe, tmp, log*):")
        main_vbox.Add(lbl_est, 0, wx.ALL, 10)
        hbox_est = wx.BoxSizer(wx.HORIZONTAL)
        self.list_est = wx.ListBox(self, choices=self.settings["filtro_estensioni"], style=wx.LB_SINGLE)
        hbox_est.Add(self.list_est, 1, wx.EXPAND | wx.LEFT, 10)
        vbox_btn_est = wx.BoxSizer(wx.VERTICAL)
        btn_add_est = wx.Button(self, label="Aggiungi...")
        btn_del_est = wx.Button(self, label="Rimuovi")
        vbox_btn_est.Add(btn_add_est, 0, wx.BOTTOM, 5)
        vbox_btn_est.Add(btn_del_est, 0)
        hbox_est.Add(vbox_btn_est, 0, wx.LEFT | wx.RIGHT, 10)
        main_vbox.Add(hbox_est, 1, wx.EXPAND)
        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        main_vbox.Add(btnsizer, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        self.SetSizer(main_vbox)
        btn_add_nome.Bind(wx.EVT_BUTTON, lambda e: self.on_add(self.list_nomi, "Filtro per nome"))
        btn_del_nome.Bind(wx.EVT_BUTTON, lambda e: self.on_remove(self.list_nomi))
        btn_predefiniti.Bind(wx.EVT_BUTTON, self.on_predefiniti)
        btn_add_est.Bind(wx.EVT_BUTTON, lambda e: self.on_add(self.list_est, "Filtro per estensione"))
        btn_del_est.Bind(wx.EVT_BUTTON, lambda e: self.on_remove(self.list_est))

    def on_add(self, listbox, title):
        dlg = wx.TextEntryDialog(self, "Inserisci il pattern (usa * e ?):", title)
        if dlg.ShowModal() == wx.ID_OK:
            val = dlg.GetValue().strip()
            if val and val.lower() not in {s.lower() for s in listbox.GetStrings()}:
                listbox.Append(val)
        dlg.Destroy()

    def on_remove(self, listbox):
        sel = listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            listbox.Delete(sel)
            if listbox.GetCount():
                listbox.SetSelection(min(sel, listbox.GetCount() - 1))

    def on_predefiniti(self, event):
        """Rimette fra i filtri per nome i predefiniti che mancano."""
        presenti = {s.lower() for s in self.list_nomi.GetStrings()}
        for nome in FILTRI_PREDEFINITI:
            if nome.lower() not in presenti:
                self.list_nomi.Append(nome)

    def get_data(self):
        return {
            "filtro_nomi": list(self.list_nomi.GetStrings()),
            "filtro_estensioni": list(self.list_est.GetStrings()),
        }


class DialogoAggiornamento(wx.Dialog):
    """Propone la versione nuova con le sue novita' e due pulsanti espliciti.

    Le note si leggono in un campo di testo, dove si scorrono e rileggono con
    le frecce; escape e la chiusura della finestra valgono come non adesso.
    """

    def __init__(self, parent, versione_nuova, note):
        super().__init__(parent, title="Aggiornamento disponibile", size=(560, 480))
        vbox = wx.BoxSizer(wx.VERTICAL)
        testo = f"E' disponibile la versione {versione_nuova}. Tu hai la {VERSIONE}."
        vbox.Add(wx.StaticText(self, label=testo), 0, wx.ALL, 10)
        vbox.Add(wx.StaticText(self, label="Novita' di questa versione:"), 0, wx.LEFT | wx.RIGHT, 10)
        contenuto = (note or "").strip() or "Nessuna nota per questa versione."
        self.txt_note = wx.TextCtrl(self, value=contenuto, style=wx.TE_MULTILINE | wx.TE_READONLY)
        vbox.Add(self.txt_note, 1, wx.EXPAND | wx.ALL, 10)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        btn_si = wx.Button(self, wx.ID_YES, "Aggiorna adesso")
        btn_no = wx.Button(self, wx.ID_NO, "Non adesso")
        hbox.Add(btn_si, 0, wx.RIGHT, 10)
        hbox.Add(btn_no, 0)
        vbox.Add(hbox, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.SetSizer(vbox)
        btn_si.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_YES))
        btn_no.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_NO))
        self.SetAffirmativeId(wx.ID_YES)
        self.SetEscapeId(wx.ID_NO)
        self.txt_note.SetFocus()


# Interfaccia principale.


class CartellaFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(800, 650))
        self.settings, avviso_impostazioni = carica_impostazioni()
        self.scansione_in_corso = False
        self.chiusura_per_aggiornamento = False
        # L'attesa dello scaricamento: nasce quando l'utente dice di si' e
        # sparisce con l'esito. Vive qui perche' chi la apre e chi la chiude
        # sono due momenti diversi.
        self.attesa_aggiornamento = None
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        ultima = self.settings.get("ultima_cartella", "")
        if not ultima or not os.path.isdir(ultima):
            ultima = os.getcwd()
        self.dir_ctrl = wx.GenericDirCtrl(panel, -1, dir=ultima, style=wx.DIRCTRL_SHOW_FILTERS, filter="Tutti i file (*.*)|*.*")
        self.tree = self.dir_ctrl.GetTreeCtrl()
        self.tree.Bind(wx.EVT_KEY_DOWN, self.on_tree_key_down)
        vbox.Add(self.dir_ctrl, 2, wx.EXPAND | wx.ALL, 5)
        hbox_opts = wx.BoxSizer(wx.HORIZONTAL)
        self.chk_numerazione = wx.CheckBox(panel, label="Numerazione")
        self.chk_indentazione = wx.CheckBox(panel, label="Indentazione")
        self.chk_estensione = wx.CheckBox(panel, label="Estensione")
        self.chk_numerazione.SetValue(self.settings["numerazione"])
        self.chk_indentazione.SetValue(self.settings["indentazione"])
        self.chk_estensione.SetValue(self.settings["estensione"])
        self.btn_filtri = wx.Button(panel, label="Impostazioni filtri")
        hbox_opts.Add(self.chk_numerazione, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox_opts.Add(self.chk_indentazione, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox_opts.Add(self.chk_estensione, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox_opts.AddStretchSpacer()
        hbox_opts.Add(self.btn_filtri, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        vbox.Add(hbox_opts, 0, wx.EXPAND | wx.ALL, 5)
        self.txt_manual = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.txt_manual.SetValue(get_manuale_text())
        vbox.Add(self.txt_manual, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(vbox)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_hook)
        self.btn_filtri.Bind(wx.EVT_BUTTON, self.on_apri_filtri)
        self.chk_numerazione.Bind(wx.EVT_CHECKBOX, self.on_opt_change)
        self.chk_indentazione.Bind(wx.EVT_CHECKBOX, self.on_opt_change)
        self.chk_estensione.Bind(wx.EVT_CHECKBOX, self.on_opt_change)
        self.Center()
        self.Show()
        self.tree.SetFocus()
        if avviso_impostazioni:
            wx.CallAfter(wx.MessageBox, avviso_impostazioni, "Impostazioni", wx.OK | wx.ICON_WARNING, self)

    def salva(self):
        """Salva le impostazioni e, se non riesce, lo dice una volta."""
        errore = salva_impostazioni(self.settings)
        if errore:
            wx.MessageBox(errore, "Errore", wx.OK | wx.ICON_ERROR, self)

    def on_close(self, event):
        if self.scansione_in_corso and not self.chiusura_per_aggiornamento:
            suona("rifiutato")
            wx.MessageBox("Scansione in corso, aspetta che finisca.", "Cartella", wx.OK | wx.ICON_INFORMATION, self)
            event.Veto()
            return
        self.settings["ultima_cartella"] = self.dir_ctrl.GetPath()
        self.salva()
        if Acusticator is not None:
            Acusticator.close()
        event.Skip()

    def on_opt_change(self, event):
        self.settings["numerazione"] = self.chk_numerazione.GetValue()
        self.settings["indentazione"] = self.chk_indentazione.GetValue()
        self.settings["estensione"] = self.chk_estensione.GetValue()
        self.salva()

    def on_apri_filtri(self, event):
        dlg = FilterDialog(self, self.settings)
        if dlg.ShowModal() == wx.ID_OK:
            self.settings.update(dlg.get_data())
            self.salva()
        dlg.Destroy()

    def on_tree_key_down(self, event):
        keycode = event.GetKeyCode()
        item = self.tree.GetSelection()
        if keycode == wx.WXK_RIGHT:
            if item.IsOk() and self.tree.ItemHasChildren(item):
                self.tree.Expand(item)
            event.Skip()
        elif keycode == wx.WXK_LEFT:
            if item.IsOk():
                if self.tree.IsExpanded(item):
                    self.tree.Collapse(item)
                else:
                    parent = self.tree.GetItemParent(item)
                    if parent.IsOk():
                        self.tree.SelectItem(parent)
                        self.tree.EnsureVisible(parent)
        else:
            event.Skip()

    def on_key_hook(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.Close()
        elif keycode == wx.WXK_RETURN and self.FindFocus() is not self.txt_manual:
            # Invio dentro il manuale serve a leggerlo, non ad avviare la scansione.
            self.avvia_processo()
        else:
            event.Skip()

    def avvia_processo(self):
        """Avvia la scansione in un thread, cosi' la finestra resta viva e lo screen reader non la da' per bloccata."""
        if self.scansione_in_corso:
            suona("rifiutato")
            return
        path = self.dir_ctrl.GetPath()
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if not os.path.isdir(path):
            suona("errore")
            wx.MessageBox("Seleziona una cartella valida.", "Errore", wx.OK | wx.ICON_ERROR, self)
            return
        output_file = os.path.join(get_base_path(), nome_report(os.path.normpath(path), datetime.datetime.now()))
        self.scansione_in_corso = True
        suona("avvio_scansione")
        wx.BeginBusyCursor()
        threading.Thread(target=self._lavoro_scansione, args=(path, output_file), daemon=True).start()

    def _lavoro_scansione(self, path, output_file):
        try:
            risultato = genera_report(path, output_file, dict(self.settings))
        except OSError as e:
            wx.CallAfter(self.fine_scansione, None, f"Impossibile scrivere il file {output_file}.\n{e}")
        except Exception as e:  # noqa: BLE001 - un thread che muore in silenzio non direbbe niente a nessuno
            wx.CallAfter(self.fine_scansione, None, f"Errore interno: {e}\n{traceback.format_exc()}")
        else:
            wx.CallAfter(self.fine_scansione, risultato, None)

    def fine_scansione(self, risultato, errore):
        if not self:
            return
        self.scansione_in_corso = False
        wx.EndBusyCursor()
        if errore:
            suona("errore")
            wx.MessageBox(errore, "Errore", wx.OK | wx.ICON_ERROR, self)
            return
        suona("fine_scansione")
        righe = ["Fatto.", f"File: {risultato.percorso}", *risultato.righe_riepilogo()]
        if risultato.non_letti:
            righe.append("L'elenco delle cartelle non lette")
            righe.append("sta in fondo al file.")
        wx.MessageBox("\n".join(righe), "Completato", wx.OK | wx.ICON_INFORMATION, self)

    # Aggiornamento.

    def chiedi_aggiornamento(self, versione_attuale, versione_nuova, note):
        """La risposta dell'utente a gestisci_aggiornamento, che intanto aspetta.

        La domanda nasce nel thread del controllo, ma la finestra vive su
        quello principale: la si porta li' con CallAfter e si resta fermi
        finche' non si sa la risposta, perche' e' lei a dire se scaricare.
        Il parametro versione_attuale arriva per completezza; qui si usa la
        costante, che e' la stessa cosa scritta in un posto solo.
        """
        risposta = []
        risposto = threading.Event()

        def nella_finestra():
            try:
                if not self:
                    return
                dlg = DialogoAggiornamento(self, versione_nuova, note)
                scelta = dlg.ShowModal()
                dlg.Destroy()
                if scelta != wx.ID_YES:
                    return
                risposta.append(True)
                # Lo scaricamento comincia appena questa funzione risponde e
                # dura quanto dura: l'attesa si apre qui e la chiude l'esito,
                # che arriva sempre, riuscito o no.
                self.attesa_aggiornamento = wx.BusyInfo("Scarico l'aggiornamento, aspetta.", parent=self)
            finally:
                risposto.set()

        wx.CallAfter(nella_finestra)
        risposto.wait()
        return bool(risposta)

    def avvisa_aggiornamento(self, testo):
        """Gli esiti che gestisci_aggiornamento riferisce, pochi e tutti utili:
        il pacchetto non ancora pronto, lo scaricamento fallito, il programma
        che sta per chiudersi. Arrivano dal thread, quindi passano di qui."""
        wx.CallAfter(self.mostra_esito_aggiornamento, testo)

    def mostra_esito_aggiornamento(self, testo):
        # Rilasciare l'attesa la fa sparire: se non era aperta, non cambia nulla.
        self.attesa_aggiornamento = None
        if not self:
            return
        wx.MessageBox(testo, "Aggiornamento", wx.OK | wx.ICON_INFORMATION, self)

    def chiudi_per_aggiornamento(self):
        if not self:
            return
        # Le impostazioni si salvano passando da on_close, come a ogni uscita.
        self.chiusura_per_aggiornamento = True
        self.Close()


def avvia_controllo_aggiornamenti(frame):
    """Controlla in un thread se c'e' una versione nuova, solo per l'eseguibile.

    Dalla 5.0.3 il giro lo conduce gestisci_aggiornamento di GBUtils: qui
    restano la finestra, che e' la sola cosa che Cartella sappia fare meglio
    di lei, e il ponte fra il thread e la finestra. La funzione tace finche'
    non c'e' davvero un aggiornamento, quindi agli avvii normali, che sono
    quasi tutti, non compare niente.
    """
    if not getattr(sys, "frozen", False):
        return
    try:
        from GBUtils import gestisci_aggiornamento
    except ImportError:
        return

    def lavoro():
        # Un avviso senza aggiornamento vuol dire che qualcosa e' andato storto,
        # il pacchetto non ancora pronto o lo scaricamento fallito: e' il caso
        # in cui la 5.0.2 suonava l'errore, e continua a farlo.
        avvisi = []

        def avvisa(testo):
            avvisi.append(testo)
            frame.avvisa_aggiornamento(testo)

        try:
            pronto = gestisci_aggiornamento(
                APP_NAME, VERSIONE, API_RELEASE,
                proponi=frame.chiedi_aggiornamento, avvisa=avvisa)
        except Exception as e:  # noqa: BLE001 - un thread che muore in silenzio non direbbe niente a nessuno
            wx.CallAfter(frame.mostra_esito_aggiornamento, f"Controllo aggiornamenti non riuscito:\n{e}")
            return
        if pronto:
            wx.CallAfter(frame.chiudi_per_aggiornamento)
        elif avvisi:
            suona("errore")

    threading.Thread(target=lavoro, daemon=True).start()


if __name__ == "__main__":
    app = wx.App()
    frame = CartellaFrame(None, title=f"Cartella {VERSIONE}")
    if "--prova-aggiornamento" in sys.argv:
        # Il giro dell'aggiornamento con dati finti, per provarlo con lo screen
        # reader senza aspettare una release nuova. Gira in un thread come
        # quello vero, perche' la domanda aspetta la risposta e dal thread
        # principale bloccherebbe la finestra che deve mostrarla.
        note_di_prova = "Prima novita' di prova.\nSeconda novita' di prova, un po' piu' lunga, per vedere come si scorre il testo con le frecce.\nTerza e ultima."

        def prova_aggiornamento():
            if frame.chiedi_aggiornamento(VERSIONE, "9.9.9", note_di_prova):
                # Il tempo di sentire l'attesa, poi l'esito che la chiude.
                time.sleep(2)
                frame.avvisa_aggiornamento("Prova finita: qui il programma si chiuderebbe per applicare l'aggiornamento.")

        threading.Thread(target=prova_aggiornamento, daemon=True).start()
    else:
        avvia_controllo_aggiornamenti(frame)
    app.MainLoop()
