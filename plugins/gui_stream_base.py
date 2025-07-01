# plugins/gui_stream_base.py

import tkinter as tk
from tkinter import ttk

def apply_dark_theme(root):
    """
    Wendett ein dunkles Thema auf die Tkinter-Anwendung an.
    """
    style = ttk.Style(root)
    
    # Versucht, ein dunkles Thema zu verwenden, falls verfügbar
    if "clam" in style.theme_names():
        style.theme_use("clam")
    elif "alt" in style.theme_names():
        style.theme_use("alt")
    else:
        print("WARNUNG: Kein geeignetes dunkles Thema gefunden, verwende Standard.")

    # Allgemeine Hintergrund- und Vordergrundfarben für das dunkle Thema
    bg_color = "#222222"  # Dunkelgrau
    fg_color = "#00FF00"  # Helles Grün (Matrix-Stil)
    accent_color = "#00FFCC" # Türkis für Akzente
    border_color = "#008080" # Teal für Ränder

    # Konfiguration für TFrame
    style.configure("TFrame", background=bg_color)
    
    # Konfiguration für TLabel
    style.configure("TLabel", background=bg_color, foreground=fg_color)

    # Konfiguration für TButton
    style.configure("TButton", 
                    background=accent_color, 
                    foreground=bg_color, 
                    font=("Consolas", 10, "bold"),
                    relief="raised",
                    borderwidth=2,
                    focusthickness=3,
                    focuscolor=fg_color)
    style.map("TButton", 
              background=[("active", fg_color)], # Hintergrund bei Hover
              foreground=[("active", bg_color)]) # Textfarbe bei Hover

    # Konfiguration für TEntry
    style.configure("TEntry", 
                    fieldbackground="#333333", # Dunkleres Feld
                    foreground=fg_color, 
                    insertbackground=fg_color, # Cursorfarbe
                    bordercolor=border_color,
                    borderwidth=1)

    # Konfiguration für TCombobox
    style.configure("TCombobox", 
                    fieldbackground="#333333", 
                    background=bg_color, 
                    foreground=fg_color,
                    selectbackground=accent_color, # Hintergrund der Auswahl
                    selectforeground=bg_color,    # Text der Auswahl
                    bordercolor=border_color,
                    arrowcolor=fg_color) # Farbe des Dropdown-Pfeils
    style.map("TCombobox", 
              background=[("readonly", bg_color)],
              fieldbackground=[("readonly", "#333333")]) # Hintergrund des Textfeldes

    # Konfiguration für TCheckbutton
    style.configure("TCheckbutton", 
                    background=bg_color, 
                    foreground=fg_color,
                    indicatorcolor=accent_color, # Farbe des Häkchens
                    indicatorbackground="#333333") # Hintergrund des Kästchens
    style.map("TCheckbutton", 
              background=[("active", bg_color)],
              foreground=[("active", fg_color)])

    # Konfiguration für TScrollbar (vertikal und horizontal)
    style.configure("Vertical.TScrollbar", 
                    background=bg_color, 
                    troughcolor="#333333", 
                    bordercolor=border_color,
                    arrowcolor=accent_color)
    style.map("Vertical.TScrollbar", 
              background=[("active", accent_color)],
              troughcolor=[("active", "#444444")])

    style.configure("Horizontal.TScrollbar", 
                    background=bg_color, 
                    troughcolor="#333333", 
                    bordercolor=border_color,
                    arrowcolor=accent_color)
    style.map("Horizontal.TScrollbar", 
              background=[("active", accent_color)],
              troughcolor=[("active", "#444444")])

    # Konfiguration für TNotebook (Tabs)
    style.configure("TNotebook", 
                    background=bg_color, 
                    bordercolor=border_color)
    style.configure("TNotebook.Tab", 
                    background="#333333", 
                    foreground=accent_color, 
                    font=("Consolas", 10, "bold"),
                    padding=[8, 4]) # Polsterung des Tabs
    style.map("TNotebook.Tab", 
              background=[("selected", bg_color)], # Hintergrund des aktiven Tabs
              foreground=[("selected", fg_color)], # Textfarbe des aktiven Tabs
              expand=[("selected", [1, 1, 1, 0])]) # Rand des aktiven Tabs

    # Konfiguration für Treeview
    style.configure("Treeview", 
                    background="#1e1e1e", # Hintergrund der Zeilen
                    foreground=fg_color, 
                    fieldbackground="#1e1e1e", # Hintergrund des gesamten Treeviews
                    bordercolor=border_color,
                    borderwidth=1,
                    rowheight=25) # Zeilenhöhe
    style.map("Treeview", 
              background=[("selected", accent_color)], # Hintergrund der ausgewählten Zeile
              foreground=[("selected", bg_color)]) # Textfarbe der ausgewählten Zeile

    style.configure("Treeview.Heading", 
                    background="#333333", 
                    foreground="#00FFCC", 
                    font=("Consolas", 10, "bold"),
                    relief="raised",
                    borderwidth=1,
                    bordercolor=border_color)
    style.map("Treeview.Heading", 
              background=[("active", "#444444")]) # Hintergrund bei Hover


class GUIStreamPluginBase:
    """
    Basisklasse für alle Tesseract GUI-Plugins, die im Metavisualizer angezeigt werden.
    Definiert die grundlegende Schnittstelle und Funktionalität.
    """
    # Metadaten des Plugins (müssen von abgeleiteten Klassen überschrieben werden)
    name = "Base Plugin"
    type = "generic"
    stream_type = "none" # Z.B. "network_scan", "code_analysis", "system_log"
    description = "Eine generische Basisklasse für Tesseract GUI-Plugins."
    author = "Tesseract Core Team"
    version = "0.1"

    def __init__(self):
        self.gui_frame = None # Der Tkinter-Frame für die GUI des Plugins
        self.is_running = False

    def create_gui(self, parent):
        """
        Erstellt das Tkinter-Frame und die Widgets für die GUI des Plugins.
        Muss von abgeleiteten Klassen implementiert werden.
        
        Args:
            parent: Das übergeordnete Tkinter-Widget (z.B. ein ttk.Notebook).
            
        Returns:
            Ein ttk.Frame, das die GUI des Plugins enthält.
        """
        self.gui_frame = ttk.Frame(parent, style="TFrame", padding="10")
        # Standard-Layout für den Frame, kann von abgeleiteten Klassen angepasst werden
        self.gui_frame.columnconfigure(0, weight=1)
        self.gui_frame.rowconfigure(0, weight=1)
        
        # Beispiel-Label für die Basisklasse
        # ttk.Label(self.gui_frame, text=f"Dies ist das {self.name} Plugin.", 
        #           font=("Consolas", 12), foreground="#00FFCC", background="#222222").pack(pady=20)
        
        return self.gui_frame

    def run(self, **kwargs):
        """
        Wird aufgerufen, wenn das Plugin gestartet oder aktiviert wird.
        Hier kann die Hauptlogik des Plugins gestartet werden (z.B. Threads, Timer).
        """
        print(f"INFO: Plugin '{self.name}' gestartet.")
        self.is_running = True

    def stop(self):
        """
        Wird aufgerufen, wenn das Plugin gestoppt oder deaktiviert wird.
        Hier sollte die laufende Logik sauber beendet werden.
        """
        print(f"INFO: Plugin '{self.name}' gestoppt.")
        self.is_running = False

    def update_gui(self):
        """
        Wird regelmäßig vom Metavisualizer aufgerufen, um die GUI zu aktualisieren.
        Kann von abgeleiteten Klassen überschrieben werden, um Daten anzuzeigen.
        """
        pass # Standardmäßig tut es nichts. Abgeleitete Klassen implementieren dies.

    def get_status(self):
        """
        Gibt den aktuellen Status des Plugins zurück.
        """
        return {"name": self.name, "is_running": self.is_running, "type": self.type}

# Beispielnutzung (nur zur Veranschaulichung, wird normalerweise vom PluginManager geladen)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("GUIStreamPluginBase Test")
    apply_dark_theme(root)

    # Erstelle eine Instanz der Basisklasse
    base_plugin = GUIStreamPluginBase()
    
    # Erstelle den GUI-Frame und zeige ihn an
    plugin_frame = base_plugin.create_gui(root)
    plugin_frame.pack(fill="both", expand=True)
    
    # Starte das Plugin
    base_plugin.run()

    root.mainloop()
