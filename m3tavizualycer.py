# m3tavizualycer.py

import tkinter as tk
from tkinter import ttk
import os
import sys

# Fügen Sie das übergeordnete Verzeichnis zum Python-Pfad hinzu,
# damit db_manager_updated und plugin_manager gefunden werden.
# Dies ist wichtig, wenn Sie das Skript von einem anderen Ort aus starten.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importieren Sie die notwendigen Komponenten
from plugin_manager import PluginManager
from plugins.gui_stream_base import apply_dark_theme # Für das dunkle Thema
# Stellen Sie sicher, dass db_manager_updated.py im selben Verzeichnis ist
from db_manager_updated import DBManager 

class MetavisualizerApp:
    """
    Die Hauptanwendung des Tesseract Metavisualizers.
    Verwaltet die GUI, Tabs und lädt Plugins.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Tesseract Metavisualizer")
        self.root.geometry("1024x768") # Standardgröße
        
        # Dunkles Thema anwenden
        apply_dark_theme(self.root)

        self.db_manager = DBManager() # Initialisiert den DBManager und die DB-Tabellen
        self.plugin_manager = PluginManager()
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._create_tabs()
        self._load_and_integrate_plugins()

        # Optional: Regelmäßiges Update für Plugins, die das benötigen
        # self.root.after(5000, self._periodic_plugin_update)

    def _create_tabs(self):
        """Erstellt die grundlegenden Tabs im Metavisualizer."""
        
        # 1. Übersicht/OSI-Visualisierung Tab (Platzhalter für Proto-Release)
        self.overview_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.overview_frame, text="Übersicht/OSI")
        tk.Label(self.overview_frame, text="Hier entsteht die 3D-OSI-Visualisierung...", 
                 foreground="#00FFCC", background="#222222", font=("Consolas", 16)).pack(pady=50)
        tk.Label(self.overview_frame, text="Aktive Module, Netzwerk-Status, etc. werden hier visualisiert.", 
                 foreground="#00FFCC", background="#222222", font=("Consolas", 12)).pack(pady=10)

        # 2. Netzwerk-Scans Tab (Platzhalter)
        self.scan_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.scan_frame, text="Netzwerk-Scans")
        tk.Label(self.scan_frame, text="Hier werden Netzwerk-Scans gesteuert und angezeigt.", 
                 foreground="#00FFCC", background="#222222", font=("Consolas", 16)).pack(pady=50)
        
        # 3. Modul-Manager Tab (Platzhalter)
        self.module_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.module_frame, text="Modul-Manager")
        tk.Label(self.module_frame, text="Verwaltung der Tesseract-Module.", 
                 foreground="#00FFCC", background="#222222", font=("Consolas", 16)).pack(pady=50)

        # Der Jan's Eye Reports Tab wird dynamisch hinzugefügt
        # 4. System-Log Tab (Platzhalter)
        self.log_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.log_frame, text="System-Log")
        tk.Label(self.log_frame, text="Hier werden die System-Logs angezeigt (Midori-Integration).", 
                 foreground="#00FFCC", background="#222222", font=("Consolas", 16)).pack(pady=50)

    def _load_and_integrate_plugins(self):
        """
        Lädt Plugins und integriert ihre GUIs als neue Tabs.
        """
        self.plugin_manager.load_plugins()

        # Jan's Eye Report Viewer Plugin integrieren
        jan_eye_viewer_plugin = self.plugin_manager.get_plugin("Jan's Eye Reports")
        if jan_eye_viewer_plugin:
            # Erstellt den GUI-Frame des Plugins
            plugin_gui_frame = jan_eye_viewer_plugin.create_gui(self.notebook)
            # Fügt den Frame als neuen Tab hinzu
            self.notebook.add(plugin_gui_frame, text=jan_eye_viewer_plugin.name)
            # Startet das Plugin (führt initial update_gui aus)
            jan_eye_viewer_plugin.run()
            print(f"'{jan_eye_viewer_plugin.name}' Plugin-Tab hinzugefügt und gestartet.")
        else:
            print("WARNUNG: 'Jan's Eye Reports' Plugin nicht gefunden. Stellen Sie sicher, dass 'jan_eye_report_viewer.py' existiert.")
        
        # Hier können Sie weitere Plugins integrieren, z.B. den MetaPluginInspector
        # meta_inspector_plugin = self.plugin_manager.get_plugin("Meta Plugin Inspector")
        # if meta_inspector_plugin:
        #     plugin_gui_frame = meta_inspector_plugin.create_gui(self.notebook)
        #     self.notebook.add(plugin_gui_frame, text=meta_inspector_plugin.name)
        #     # Übergabe des PluginManagers an den MetaPluginInspector
        #     meta_inspector_plugin.run(plugin_manager=self.plugin_manager)
        #     print(f"'{meta_inspector_plugin.name}' Plugin-Tab hinzugefügt und gestartet.")


    def _periodic_plugin_update(self):
        """
        Führt regelmäßige Updates für Plugins aus, die dies benötigen.
        """
        # Beispiel: Wenn JanEyeReportViewer regelmäßige Updates benötigt
        jan_eye_viewer_plugin = self.plugin_manager.get_plugin("Jan's Eye Reports")
        if jan_eye_viewer_plugin:
            # jan_eye_viewer_plugin.update_gui() # Nur aufrufen, wenn wirklich nötig und nicht zu oft
            pass # Der JanEyeReportViewer hat bereits einen Refresh-Button

        self.root.after(5000, self._periodic_plugin_update) # Alle 5 Sekunden wiederholen


if __name__ == "__main__":
    # Stellen Sie sicher, dass die Datenbank initialisiert wird
    # (Der DBManager wird beim Instanziieren der App initialisiert)
    
    root = tk.Tk()
    app = MetavisualizerApp(root)
    root.mainloop()
