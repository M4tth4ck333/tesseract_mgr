# plugins/jan_eye_report_viewer.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
import sys
import os

# Fügen Sie das übergeordnete Verzeichnis zum Python-Pfad hinzu,
# damit db_manager_updated gefunden wird.
if '..' not in sys.path:
    sys.path.insert(0, '..')

from plugins.gui_stream_base import GUIStreamPluginBase
from db_manager_updated import DBManager, CodeAnalysisReport # Importieren Sie DBManager und das Modell

class JanEyeReportViewer(GUIStreamPluginBase):
    """
    Ein Tesseract GUI-Plugin zur Anzeige von CodeAnalysisReport-Daten
    aus der Datenbank.
    """
    name = "Jan's Eye Reports"
    type = "analysis_viewer"
    stream_type = "code_analysis"
    description = "Zeigt Berichte der Code-Analyse von Jan's Eye an."
    author = "Jan (M4tth4ck333)"
    version = "0.1"

    def __init__(self):
        super().__init__()
        self.db_manager = DBManager() # Initialisiert den DBManager
        self.reports_tree = None # Treeview-Widget für die Berichte

    def create_gui(self, parent):
        """
        Erstellt das Tkinter-Frame für das Jan's Eye Report Viewer Plugin.
        """
        # Erstellt einen Frame, der als Container für die Plugin-GUI dient
        frame = super().create_gui(parent)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1) # Die Tabelle soll sich ausdehnen

        # Titel-Label
        title_label = ttk.Label(frame, text="Jan's Eye Code Analysis Reports", font=("Consolas", 14, "bold"), foreground="#00FFCC", background="#222222")
        title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

        # Refresh Button
        refresh_button = ttk.Button(frame, text="Refresh Reports", command=self.refresh_reports)
        refresh_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        # Platzierung des Buttons rechts vom Titel, aber innerhalb des Grids

        # Treeview für die Berichte
        columns = ("ID", "File Path", "Issue Type", "Severity", "Description", "Line", "Snippet", "Date", "Status")
        self.reports_tree = ttk.Treeview(frame, columns=columns, show="headings", style="Treeview")

        # Spaltenüberschriften konfigurieren
        for col in columns:
            self.reports_tree.heading(col, text=col, anchor=tk.W)
            self.reports_tree.column(col, width=100, stretch=True) # Standardbreite

        # Spezifische Spaltenbreiten anpassen
        self.reports_tree.column("ID", width=40, minwidth=30, stretch=False)
        self.reports_tree.column("File Path", width=250, minwidth=150)
        self.reports_tree.column("Issue Type", width=100, minwidth=80)
        self.reports_tree.column("Severity", width=80, minwidth=60)
        self.reports_tree.column("Line", width=50, minwidth=40, stretch=False)
        self.reports_tree.column("Status", width=80, minwidth=60)

        self.reports_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Scrollbars hinzufügen
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.reports_tree.yview)
        vsb.grid(row=1, column=2, sticky="ns")
        self.reports_tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.reports_tree.xview)
        hsb.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.reports_tree.configure(xscrollcommand=hsb.set)

        # Event-Handler für Doppelklick auf einen Eintrag
        self.reports_tree.bind("<Double-1>", self.on_item_double_click)

        return frame

    def refresh_reports(self):
        """
        Lädt die Code-Analyse-Berichte aus der Datenbank neu und aktualisiert die Anzeige.
        """
        # Vorhandene Einträge löschen
        for item in self.reports_tree.get_children():
            self.reports_tree.delete(item)

        # Berichte aus der Datenbank abrufen
        reports = self.db_manager.get_all_code_analysis_reports()

        # Berichte in die Treeview einfügen
        for report in reports:
            # Formatieren des Datums für bessere Lesbarkeit
            analysis_date_str = report.analysis_date.strftime("%Y-%m-%d %H:%M:%S") if report.analysis_date else ""
            
            # Zeilennummer als String behandeln, falls None
            line_number_str = str(report.line_number) if report.line_number is not None else "N/A"

            self.reports_tree.insert("", "end", values=(
                report.id,
                report.file_path,
                report.issue_type,
                report.severity,
                report.description,
                line_number_str,
                report.code_snippet,
                analysis_date_str,
                report.status
            ))
        print(f"INFO: {len(reports)} Code-Analyse-Berichte geladen und angezeigt.")

    def on_item_double_click(self, event):
        """
        Behandelt Doppelklicks auf einen Berichtseintrag.
        Öffnet ein Detailfenster für den ausgewählten Bericht.
        """
        selected_item = self.reports_tree.selection()
        if not selected_item:
            return

        item_values = self.reports_tree.item(selected_item, "values")
        
        # Extrahieren der Daten
        report_id = item_values[0]
        file_path = item_values[1]
        issue_type = item_values[2]
        severity = item_values[3]
        description = item_values[4]
        line_number = item_values[5]
        code_snippet = item_values[6]
        analysis_date = item_values[7]
        status = item_values[8]

        # Detailfenster erstellen
        detail_window = tk.Toplevel(self.gui_frame)
        detail_window.title(f"Report Details: ID {report_id}")
        detail_window.transient(self.gui_frame.winfo_toplevel()) # Macht es modal zum Hauptfenster
        detail_window.grab_set() # Fängt alle Events ab
        detail_window.resizable(True, True) # Fenstergröße anpassbar machen

        # Stil für das Detailfenster (optional, für ein dunkleres Thema)
        detail_window.configure(bg="#1a1a1a")
        ttk.Style().theme_use("tesseract_dark") # Sicherstellen, dass das Thema angewendet wird

        detail_frame = ttk.Frame(detail_window, padding="15", style="TFrame")
        detail_frame.pack(fill="both", expand=True)

        # Layout mit Grid
        detail_frame.columnconfigure(1, weight=1) # Zweite Spalte dehnbar machen

        row_idx = 0
        def add_detail_row(label_text, value_text):
            nonlocal row_idx
            ttk.Label(detail_frame, text=f"{label_text}:", font=("Consolas", 10, "bold"), foreground="#00FFCC", background="#222222").grid(row=row_idx, column=0, sticky="nw", pady=2, padx=5)
            # Text-Widget für längere Inhalte, Label für kurze
            if label_text in ["Description", "Code Snippet"]:
                text_widget = tk.Text(detail_frame, wrap="word", height=5 if label_text == "Description" else 8, width=80,
                                      font=("Consolas", 10), bg="#181818", fg="#00FF00", bd=0, relief="flat",
                                      insertbackground="#00FF00")
                text_widget.insert("1.0", value_text)
                text_widget.config(state="disabled") # Nur lesbar
                text_widget.grid(row=row_idx, column=1, sticky="nsew", pady=2, padx=5)
                # Scrollbar für Text-Widgets
                text_scrollbar = ttk.Scrollbar(detail_frame, orient="vertical", command=text_widget.yview)
                text_scrollbar.grid(row=row_idx, column=2, sticky="ns", pady=2)
                text_widget.config(yscrollcommand=text_scrollbar.set)
            else:
                ttk.Label(detail_frame, text=value_text, font=("Consolas", 10), foreground="#00FF00", background="#222222").grid(row=row_idx, column=1, sticky="nw", pady=2, padx=5)
            row_idx += 1

        add_detail_row("ID", report_id)
        add_detail_row("File Path", file_path)
        add_detail_row("Issue Type", issue_type)
        add_detail_row("Severity", severity)
        add_detail_row("Description", description)
        add_detail_row("Line Number", line_number)
        add_detail_row("Code Snippet", code_snippet)
        add_detail_row("Analysis Date", analysis_date)
        add_detail_row("Status", status)

        # Status-Dropdown zur Aktualisierung
        status_options = ["New", "Triaged", "FalsePositive", "Fixed", "Ignored"]
        current_status_var = tk.StringVar(value=status)
        
        ttk.Label(detail_frame, text="Update Status:", font=("Consolas", 10, "bold"), foreground="#00FFCC", background="#222222").grid(row=row_idx, column=0, sticky="nw", pady=10, padx=5)
        status_combobox = ttk.Combobox(detail_frame, textvariable=current_status_var, values=status_options, state="readonly", font=("Consolas", 10))
        status_combobox.grid(row=row_idx, column=1, sticky="nw", pady=10, padx=5)
        row_idx += 1

        def save_status():
            new_status = current_status_var.get()
            if self.db_manager.update_report_status(report_id, new_status):
                messagebox.showinfo("Success", f"Status for Report ID {report_id} updated to '{new_status}'.")
                self.refresh_reports() # Tabelle im Hauptfenster aktualisieren
                detail_window.destroy()
            else:
                messagebox.showerror("Error", f"Failed to update status for Report ID {report_id}.")

        save_button = ttk.Button(detail_frame, text="Save Status", command=save_status)
        save_button.grid(row=row_idx, column=1, sticky="se", pady=10, padx=5)
        row_idx += 1

        # Fokus setzen und auf Schließen warten
        detail_window.update_idletasks()
        detail_window.geometry(f"+{self.gui_frame.winfo_x() + 50}+{self.gui_frame.winfo_y() + 50}") # Position relativ zum Hauptfenster
        detail_window.wait_window(detail_window) # Blockiert, bis das Detailfenster geschlossen wird

    def run(self, **kwargs):
        """
        Wird aufgerufen, wenn das Plugin gestartet oder aktiviert wird.
        Lädt initial die Berichte.
        """
        self.refresh_reports()

    def stop(self):
        """
        Wird aufgerufen, wenn das Plugin gestoppt oder deaktiviert wird.
        """
        pass # Keine spezifische Stopp-Logik für dieses einfache Plugin
