# Cartella. Una utility che salva in txt il contenuto di un albero di directories.
# Data concepimento: giovedì 27 febbraio 2020.
# 28 giugno 2024, pubblicato su GitHub
# Refactoring GUI: martedì 3 febbraio 2026

import wx
import os
import sys
import datetime

# --- CONFIGURAZIONE E LOGICA ---
VERSIONE = "4.0.0, del 3 febbraio 2026."
ESCLUSIONIPERMANENTI = ["cartella.py", "cartella.app", "cartella", "Cartella.txt", "cartella.exe", "desktop.ini"]
NONINIZIACON = [".", "_"]
BYTESGIGABYTES = 1073741824

def genera_report(cartellabase, output_filename, numerazione=True, indentazione=True, estensione=True, filtro=None):
    """Genera il file di report."""
    if filtro is None:
        filtro = []
    filtrati = len(filtro) > 0

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
        # Calcolo livello
        b = base.split(os.path.sep)
        l = len(b) - elementiincartellabase
        
        # Formattazione Directory
        i = l * 2 if indentazione else 0
        nc = f"{l}. " if numerazione else ""
        
        dirname = b[-1]
        if dirname and dirname[0] not in NONINIZIACON:
             f.write(f"{ ' '*i}{nc}[{dirname}]...\n")
        
        c = 1
        for fil in files:
            original_fil = fil
            
            # Controllo file nascosti o di sistema
            if not original_fil or original_fil in ESCLUSIONIPERMANENTI or original_fil[0] in NONINIZIACON:
                continue

            # Gestione estensione e filtri
            nome_base, est_raw = os.path.splitext(original_fil)
            ext_pulita = est_raw.lstrip(".").lower() # Rimuove il punto iniziale per confronto pulito
            
            if filtrati and ext_pulita in filtro:
                continue
            
            # Formattazione File
            i = (l + 1) * 2 if indentazione else 0
            
            n = ""
            if numerazione:
                n = f"{l+1}.{c}. "
                c += 1
            
            nome_visualizzato = original_fil if estensione else nome_base
            
            # Scrittura
            f.write(f"{ ' '*i}{n}{nome_visualizzato}\n")
            
            # Aggiornamento statistiche (SOLO SE SCRITTO)
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
        if getattr(sys, 'frozen', False):
            # Se compilato, cerchiamo README.md accanto all'eseguibile
            base_path = os.path.dirname(sys.executable)
        else:
            # Se script, cerchiamo README.md accanto allo script
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        path = os.path.join(base_path, "README.md")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return f"Manuale (README.md) non trovato in:\n{base_path}"
    except Exception as e:
        return f"Errore nel caricamento del manuale: {e}"

# --- INTERFACCIA GRAFICA (GUI) ---
class CartellaFrame(wx.Frame):
    def __init__(self, parent, title):
        super(CartellaFrame, self).__init__(parent, title=title, size=(800, 600))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # --- Sezione Navigazione (Superiore) ---
        self.dir_ctrl = wx.GenericDirCtrl(panel, -1, dir=os.getcwd(), style=wx.DIRCTRL_SHOW_FILTERS, filter="All files (*.*)|*.*")
        
        self.tree = self.dir_ctrl.GetTreeCtrl()
        self.tree.Bind(wx.EVT_KEY_DOWN, self.on_tree_key_down)

        vbox.Add(self.dir_ctrl, 2, wx.EXPAND | wx.ALL, 5)

        # --- Sezione Opzioni (Centrale) ---
        hbox_opts = wx.BoxSizer(wx.HORIZONTAL)
        
        self.chk_numerazione = wx.CheckBox(panel, label="Numerazione")
        self.chk_numerazione.SetValue(True)
        self.chk_indentazione = wx.CheckBox(panel, label="Indentazione")
        self.chk_indentazione.SetValue(True)
        self.chk_estensione = wx.CheckBox(panel, label="Estensione")
        self.chk_estensione.SetValue(True)

        hbox_opts.Add(self.chk_numerazione, 0, wx.ALL, 5)
        hbox_opts.Add(self.chk_indentazione, 0, wx.ALL, 5)
        hbox_opts.Add(self.chk_estensione, 0, wx.ALL, 5)

        vbox.Add(hbox_opts, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # --- Sezione Manuale (Inferiore) ---
        self.txt_manual = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.txt_manual.SetValue(get_manuale_text())
        
        vbox.Add(self.txt_manual, 1, wx.EXPAND | wx.ALL, 5)

        # --- Binding Generali ---
        panel.SetSizer(vbox)
        
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_hook)

        self.Center()
        self.Show()
        self.tree.SetFocus()

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

        num = self.chk_numerazione.GetValue()
        ind = self.chk_indentazione.GetValue()
        ext = self.chk_estensione.GetValue()
        
        output_file = "Cartella.txt" 
        
        wx.BeginBusyCursor()
        try:
            successo, msg, obj, bytes_tot, tempo = genera_report(
                path, output_file, num, ind, ext
            )
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