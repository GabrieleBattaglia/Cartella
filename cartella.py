# Cartella. Una utility che salva in txt il contenuto di un albero di directories.
# Data concepimento: giovedì 27 febbraio 2020.
# 28 giugno 2024, pubblicato su GitHub
# Refactoring GUI: martedì 3 marzo 2026

import wx
import os
import sys
import datetime
import json
import fnmatch

# --- CONFIGURAZIONE ---
VERSIONE = "4.1.2, del 3 marzo 2026."
ESCLUSIONIPERMANENTI = ["cartella.py", "cartella.app", "cartella", "Cartella.txt", "cartella.exe", "desktop.ini", "cartella_settings.json"]
NONINIZIACON = [".", "_"]
BYTESGIGABYTES = 1073741824

def get_base_path():
    """Ritorna il percorso base, che sia lo script o l'eseguibile PyInstaller."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def carica_impostazioni():
    path = os.path.join(get_base_path(), "cartella_settings.json")
    default = {
        "numerazione": True,
        "indentazione": True,
        "estensione": True,
        "filtro_nomi": [],
        "filtro_estensioni": []
    }
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return {**default, **json.load(f)}
        except:
            return default
    return default

def salva_impostazioni(settings):
    path = os.path.join(get_base_path(), "cartella_settings.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Errore nel salvataggio impostazioni: {e}")

def genera_report(cartellabase, output_filename, settings):
    """Genera il file di report."""
    numerazione = settings.get("numerazione", True)
    indentazione = settings.get("indentazione", True)
    estensione = settings.get("estensione", True)
    filtro_nomi = settings.get("filtro_nomi", [])
    filtro_estensioni = settings.get("filtro_estensioni", [])

    TEMPO = datetime.datetime.now()
    
    try:
        f = open(output_filename, "wt", encoding="utf-8")
    except IOError as e:
        return False, f"Errore critico: impossibile scrivere il file {output_filename}. {e}", 0, 0, datetime.timedelta(0)

    f.write(f"File generato da CARTELLA, versione: {VERSIONE}".center(80, "-") + "\n")
    
    if not cartellabase:
        cartellabase = os.getcwd()
        
    strutturafilesystem = os.walk(cartellabase)
    
    totaleoggetti = 0
    totalebytes = 0
    
    f.write(f"CARTELLA base: {cartellabase}.".center(80, "-") + '\n')
    
    elementiincartellabase = len(cartellabase.split(os.path.sep))
    for base, cartelle, files in strutturafilesystem:
        # 0. Filtriamo le sottocartelle per evitare di entrarci e di listarle
        # Modifichiamo la lista in-place come richiesto da os.walk
        cartelle[:] = [d for d in cartelle if d[0] not in NONINIZIACON and 
                       not any(fnmatch.fnmatch(d, p) for p in filtro_nomi) and 
                       d not in ESCLUSIONIPERMANENTI]

        # 1. Calcolo livello
        b = base.split(os.path.sep)
        l = len(b) - elementiincartellabase

        # 2. Formattazione Directory
        i = l * 2 if indentazione else 0
        nc = f"{l}. " if numerazione else ""

        dirname = b[-1]
        if dirname:
             f.write(f"{' '*i}{nc}[{dirname}]...\n")
        
        c = 1
        for fil in files:
            original_fil = fil
            
            # 1. Esclusioni di sistema
            if not original_fil or original_fil in ESCLUSIONIPERMANENTI or original_fil[0] in NONINIZIACON:
                continue

            nome_base, est_raw = os.path.splitext(original_fil)
            est_pulita = est_raw.lstrip(".").lower()

            # 2. Filtro Nomi (con jolly)
            skip = False
            for pattern in filtro_nomi:
                if fnmatch.fnmatch(original_fil, pattern):
                    skip = True
                    break
            if skip: continue

            # 3. Filtro Estensioni (con jolly)
            for pattern in filtro_estensioni:
                # Confrontiamo con l'estensione pulita (senza punto)
                p_clean = pattern.lstrip(".").lower()
                if fnmatch.fnmatch(est_pulita, p_clean):
                    skip = True
                    break
            if skip: continue
            
            # Formattazione e Scrittura
            i = (l + 1) * 2 if indentazione else 0
            n = f"{l+1}.{c}. " if numerazione else ""
            if numerazione: c += 1
            
            nome_visualizzato = original_fil if estensione else nome_base
            f.write(f"{' '*i}{n}{nome_visualizzato}\n")
            
            totaleoggetti += 1
            fp = os.path.join(base, original_fil)
            if not os.path.islink(fp) and os.path.exists(fp):
                try:
                    totalebytes += os.path.getsize(fp)
                except OSError:
                    pass

    t = datetime.datetime.now() - TEMPO
    f.write("\n")
    f.write("scritto in Python 3, da Gabriele Battaglia.".center(80, "-") + "\n")
    f.write(f"Totale oggetti listati: {totaleoggetti}.".center(80, "-") + "\n")
    f.write(f"Dimensione Totale oggetti listati: {totalebytes/BYTESGIGABYTES:.4f} GigaBytes.".center(80, "-") + "\n")
    f.write((f"Tempo di generazione: {t.seconds} secondi e {t.microseconds} microsecondi.").center(80, "-"))
    f.close()
    
    return True, "Fatto!", totaleoggetti, totalebytes, t

def get_manuale_text():
    try:
        path = os.path.join(get_base_path(), "README.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return f"Manuale (README.txt) non trovato in:\n{get_base_path()}"
    except Exception as e:
        return f"Errore nel caricamento del manuale: {e}"

# --- FINESTRE DI DIALOGO ---
class FilterDialog(wx.Dialog):
    def __init__(self, parent, settings):
        super(FilterDialog, self).__init__(parent, title="Impostazioni Filtri", size=(500, 450))
        self.settings = settings
        
        main_vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Filtro Nomi
        lbl_nomi = wx.StaticText(self, label="Escludi file per nome (es: backup*, temp_?):")
        main_vbox.Add(lbl_nomi, 0, wx.ALL, 10)
        
        hbox_nomi = wx.BoxSizer(wx.HORIZONTAL)
        self.list_nomi = wx.ListBox(self, choices=self.settings["filtro_nomi"], style=wx.LB_SINGLE)
        hbox_nomi.Add(self.list_nomi, 1, wx.EXPAND | wx.LEFT, 10)
        
        vbox_btn_nomi = wx.BoxSizer(wx.VERTICAL)
        btn_add_nome = wx.Button(self, label="Aggiungi...")
        btn_del_nome = wx.Button(self, label="Rimuovi")
        vbox_btn_nomi.Add(btn_add_nome, 0, wx.BOTTOM, 5)
        vbox_btn_nomi.Add(btn_del_nome, 0)
        hbox_nomi.Add(vbox_btn_nomi, 0, wx.LEFT | wx.RIGHT, 10)
        main_vbox.Add(hbox_nomi, 1, wx.EXPAND)

        # Filtro Estensioni
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

        # OK/Cancel
        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        main_vbox.Add(btnsizer, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        
        self.SetSizer(main_vbox)
        
        # Binding
        btn_add_nome.Bind(wx.EVT_BUTTON, lambda e: self.on_add(self.list_nomi, "Filtro Nome"))
        btn_del_nome.Bind(wx.EVT_BUTTON, lambda e: self.on_remove(self.list_nomi))
        btn_add_est.Bind(wx.EVT_BUTTON, lambda e: self.on_add(self.list_est, "Filtro Estensione"))
        btn_del_est.Bind(wx.EVT_BUTTON, lambda e: self.on_remove(self.list_est))

    def on_add(self, listbox, title):
        dlg = wx.TextEntryDialog(self, "Inserisci il pattern (usa * e ?):", title)
        if dlg.ShowModal() == wx.ID_OK:
            val = dlg.GetValue().strip()
            if val:
                listbox.Append(val)
        dlg.Destroy()

    def on_remove(self, listbox):
        sel = listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            listbox.Delete(sel)

    def get_data(self):
        return {
            "filtro_nomi": list(self.list_nomi.GetStrings()),
            "filtro_estensioni": list(self.list_est.GetStrings())
        }

# --- INTERFACCIA PRINCIPALE ---
class CartellaFrame(wx.Frame):
    def __init__(self, parent, title):
        super(CartellaFrame, self).__init__(parent, title=title, size=(800, 650))
        
        self.settings = carica_impostazioni()

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Sezione Navigazione
        self.dir_ctrl = wx.GenericDirCtrl(panel, -1, dir=os.getcwd(), style=wx.DIRCTRL_SHOW_FILTERS, filter="All files (*.*)|*.*")
        self.tree = self.dir_ctrl.GetTreeCtrl()
        self.tree.Bind(wx.EVT_KEY_DOWN, self.on_tree_key_down)
        vbox.Add(self.dir_ctrl, 2, wx.EXPAND | wx.ALL, 5)

        # Sezione Opzioni
        hbox_opts = wx.BoxSizer(wx.HORIZONTAL)
        self.chk_numerazione = wx.CheckBox(panel, label="Numerazione")
        self.chk_indentazione = wx.CheckBox(panel, label="Indentazione")
        self.chk_estensione = wx.CheckBox(panel, label="Estensione")
        
        # Applica settings caricati
        self.chk_numerazione.SetValue(self.settings["numerazione"])
        self.chk_indentazione.SetValue(self.settings["indentazione"])
        self.chk_estensione.SetValue(self.settings["estensione"])

        self.btn_filtri = wx.Button(panel, label="Impostazioni Filtri")

        hbox_opts.Add(self.chk_numerazione, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox_opts.Add(self.chk_indentazione, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox_opts.Add(self.chk_estensione, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox_opts.AddStretchSpacer()
        hbox_opts.Add(self.btn_filtri, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        vbox.Add(hbox_opts, 0, wx.EXPAND | wx.ALL, 5)

        # Sezione Manuale
        self.txt_manual = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.txt_manual.SetValue(get_manuale_text())
        vbox.Add(self.txt_manual, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(vbox)
        
        # Binding
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_hook)
        self.btn_filtri.Bind(wx.EVT_BUTTON, self.on_apri_filtri)
        
        self.chk_numerazione.Bind(wx.EVT_CHECKBOX, self.on_opt_change)
        self.chk_indentazione.Bind(wx.EVT_CHECKBOX, self.on_opt_change)
        self.chk_estensione.Bind(wx.EVT_CHECKBOX, self.on_opt_change)

        self.Center()
        self.Show()
        self.tree.SetFocus()

    def on_opt_change(self, event):
        self.settings["numerazione"] = self.chk_numerazione.GetValue()
        self.settings["indentazione"] = self.chk_indentazione.GetValue()
        self.settings["estensione"] = self.chk_estensione.GetValue()
        salva_impostazioni(self.settings)

    def on_apri_filtri(self, event):
        dlg = FilterDialog(self, self.settings)
        if dlg.ShowModal() == wx.ID_OK:
            nuovi_filtri = dlg.get_data()
            self.settings.update(nuovi_filtri)
            salva_impostazioni(self.settings)
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
        elif keycode == wx.WXK_RETURN:
            self.avvia_processo()
        else:
            event.Skip()

    def avvia_processo(self):
        path = self.dir_ctrl.GetPath()
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if not os.path.isdir(path):
             wx.MessageBox("Seleziona una cartella valida!", "Errore", wx.OK | wx.ICON_ERROR)
             return

        output_file = "Cartella.txt" 
        wx.BeginBusyCursor()
        try:
            successo, msg, obj, bytes_tot, tempo = genera_report(path, output_file, self.settings)
        finally:
            wx.EndBusyCursor()
            
        if successo:
             wx.MessageBox(f"{msg}\nFile creato: {output_file}\nOggetti: {obj}\nDimensione: {bytes_tot/BYTESGIGABYTES:.4f} GB\nTempo: {tempo}", "Completato", wx.OK | wx.ICON_INFORMATION)
        else:
             wx.MessageBox(msg, "Errore", wx.OK | wx.ICON_ERROR)

if __name__ == "__main__":
    app = wx.App()
    frame = CartellaFrame(None, title=f"Cartella GUI - {VERSIONE}")
    app.MainLoop()
