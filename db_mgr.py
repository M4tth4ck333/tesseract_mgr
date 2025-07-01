# db_manager_updated.py

import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import inspect

# Basis für die deklarative Definition von Tabellen
Base = declarative_base()

class Scan(Base):
    """
    Repräsentiert einen Scan-Eintrag in der Datenbank.
    Kann verschiedene Arten von Scans umfassen (Netzwerk, Host, etc.).
    """
    __tablename__ = 'scans'
    id = Column(Integer, primary_key=True)
    scan_type = Column(String)  # z.B. 'network', 'host', 'wifi', 'bluetooth'
    target = Column(String)     # Ziel des Scans (IP, Hostname, MAC-Adresse, SSID)
    start_time = Column(DateTime, default=datetime.datetime.now)
    end_time = Column(DateTime)
    status = Column(String)     # z.B. 'completed', 'running', 'failed'
    results = Column(Text)      # JSON-String für detaillierte Scan-Ergebnisse

    # Beziehung zu CodeAnalysisReport (ein Scan kann mehrere Berichte generieren)
    code_analysis_reports = relationship("CodeAnalysisReport", back_populates="scan")

    def __repr__(self):
        return f"<Scan(id={self.id}, type='{self.scan_type}', target='{self.target}', status='{self.status}')>"

class WordlistEntry(Base):
    """
    Repräsentiert einen Eintrag in einer Wortliste.
    Wird vom Sorter-Modul verwaltet.
    """
    __tablename__ = 'wordlist_entries'
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False, index=True)
    category = Column(String)  # z.B. 'common_passwords', 'usernames', 'technical_terms'
    source = Column(String)    # z.B. 'SET_dictionaries', 'OSINT_crawl', 'custom'
    added_date = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<WordlistEntry(id={self.id}, word='{self.word}', category='{self.category}')>"

class ExploitEntry(Base):
    """
    Repräsentiert einen Eintrag in der Exploit-Datenbank.
    """
    __tablename__ = 'exploit_entries'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    cve_id = Column(String, index=True) # Common Vulnerabilities and Exposures ID
    exploit_type = Column(String) # z.B. 'remote', 'local', 'web_app'
    platform = Column(String)   # z.B. 'Windows', 'Linux', 'Web'
    language = Column(String)   # z.B. 'Python', 'Ruby', 'C'
    path = Column(String)       # Pfad zur Exploit-Datei im Tesseract-System
    added_date = Column(DateTime, default=datetime.datetime.now)
    # Weitere Felder wie 'risk_score', 'references', 'payload_types' könnten hinzugefügt werden

    def __repr__(self):
        return f"<ExploitEntry(id={self.id}, name='{self.name}', cve_id='{self.cve_id}')>"

class CodeAnalysisReport(Base):
    """
    Repräsentiert einen Bericht der Code-Analyse durch "Jan's Eye".
    """
    __tablename__ = 'code_analysis_reports'
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey('scans.id')) # Verknüpfung zum auslösenden Scan
    file_path = Column(String, nullable=False)
    issue_type = Column(String, nullable=False) # z.B. 'Vulnerability', 'BadPractice', 'InformationLeak'
    severity = Column(String) # z.B. 'Critical', 'High', 'Medium', 'Low', 'Informational'
    description = Column(Text)
    line_number = Column(Integer)
    code_snippet = Column(Text)
    analysis_date = Column(DateTime, default=datetime.datetime.now)
    status = Column(String, default='New') # z.B. 'New', 'Triaged', 'FalsePositive', 'Fixed'

    scan = relationship("Scan", back_populates="code_analysis_reports")

    def __repr__(self):
        return f"<CodeAnalysisReport(id={self.id}, file='{self.file_path}', issue='{self.issue_type}', severity='{self.severity}')>"


class DBManager:
    """
    Verwaltet die Datenbankverbindung und CRUD-Operationen für Tesseract.
    """
    def __init__(self, db_path='teasesraect.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        self._create_tables_if_not_exists()

    def _create_tables_if_not_exists(self):
        """
        Erstellt alle in Base deklarierten Tabellen, falls sie noch nicht existieren.
        """
        # Überprüfen, ob die Tabellen bereits existieren
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()

        for table_name in Base.metadata.tables.keys():
            if table_name not in existing_tables:
                print(f"INFO: Tabelle '{table_name}' wird erstellt.")
                Base.metadata.tables[table_name].create(self.engine)
            else:
                print(f"INFO: Tabelle '{table_name}' existiert bereits.")

    def add_entry(self, entry_object):
        """Fügt einen neuen Eintrag in die Datenbank ein."""
        session = self.Session()
        try:
            session.add(entry_object)
            session.commit()
            print(f"INFO: Eintrag hinzugefügt: {entry_object}")
            return True
        except Exception as e:
            session.rollback()
            print(f"FEHLER beim Hinzufügen des Eintrags: {e}")
            return False
        finally:
            session.close()

    def get_all_code_analysis_reports(self):
        """Ruft alle CodeAnalysisReport-Einträge ab."""
        session = self.Session()
        try:
            reports = session.query(CodeAnalysisReport).all()
            return reports
        except Exception as e:
            print(f"FEHLER beim Abrufen der Code-Analyse-Berichte: {e}")
            return []
        finally:
            session.close()

    def get_all_scans(self):
        """Ruft alle Scan-Einträge ab."""
        session = self.Session()
        try:
            scans = session.query(Scan).all()
            return scans
        except Exception as e:
            print(f"FEHLER beim Abrufen der Scans: {e}")
            return []
        finally:
            session.close()

    # Beispiel für eine Update-Methode (kann bei Bedarf erweitert werden)
    def update_report_status(self, report_id, new_status):
        """Aktualisiert den Status eines CodeAnalysisReport."""
        session = self.Session()
        try:
            report = session.query(CodeAnalysisReport).filter_by(id=report_id).first()
            if report:
                report.status = new_status
                session.commit()
                print(f"INFO: Status für Bericht {report_id} auf '{new_status}' aktualisiert.")
                return True
            else:
                print(f"WARNUNG: Bericht mit ID {report_id} nicht gefunden.")
                return False
        except Exception as e:
            session.rollback()
            print(f"FEHLER beim Aktualisieren des Berichtsstatus: {e}")
            return False
        finally:
            session.close()

    # Beispiel für eine Delete-Methode (kann bei Bedarf erweitert werden)
    def delete_entry(self, entry_object):
        """Löscht einen Eintrag aus der Datenbank."""
        session = self.Session()
        try:
            session.delete(entry_object)
            session.commit()
            print(f"INFO: Eintrag gelöscht: {entry_object}")
            return True
        except Exception as e:
            session.rollback()
            print(f"FEHLER beim Löschen des Eintrags: {e}")
            return False
        finally:
            session.close()

# Beispielnutzung und Dummy-Daten für den Proto-Release
if __name__ == "__main__":
    db_manager = DBManager()

    # Dummy-Scan hinzufügen, falls noch nicht vorhanden
    session = db_manager.Session()
    existing_scan = session.query(Scan).filter_by(scan_type='initial_code_scan').first()
    session.close()

    if not existing_scan:
        print("Füge Dummy-Scan hinzu...")
        dummy_scan = Scan(
            scan_type='initial_code_scan',
            target='Tesseract_Core_Modules',
            start_time=datetime.datetime.now() - datetime.timedelta(days=7),
            end_time=datetime.datetime.now(),
            status='completed',
            results='{"files_scanned": 150, "total_issues": 10}'
        )
        db_manager.add_entry(dummy_scan)
        # Scan erneut abrufen, um die ID zu erhalten
        session = db_manager.Session()
        dummy_scan = session.query(Scan).filter_by(scan_type='initial_code_scan').first()
        session.close()
    else:
        print("Dummy-Scan existiert bereits.")
        dummy_scan = existing_scan

    # Dummy-CodeAnalysisReports hinzufügen, falls noch nicht vorhanden
    if dummy_scan:
        session = db_manager.Session()
        existing_reports_count = session.query(CodeAnalysisReport).filter_by(scan_id=dummy_scan.id).count()
        session.close()

        if existing_reports_count == 0:
            print("Füge Dummy-CodeAnalysisReports hinzu...")
            reports_to_add = [
                CodeAnalysisReport(
                    scan_id=dummy_scan.id,
                    file_path='/tesseract/core/james_donts/ai_logic.py',
                    issue_type='Vulnerability',
                    severity='Critical',
                    description='Hardcoded API key found in AI agent communication module.',
                    line_number=123,
                    code_snippet='api_key = "sk_hardcoded_secret_123"',
                    status='New'
                ),
                CodeAnalysisReport(
                    scan_id=dummy_scan.id,
                    file_path='/tesseract/plugins/network_scanner.py',
                    issue_type='BadPractice',
                    severity='Medium',
                    description='Use of os.system() instead of subprocess.run() for external commands.',
                    line_number=45,
                    code_snippet='os.system("nmap -sV " + target_ip)',
                    status='New'
                ),
                CodeAnalysisReport(
                    scan_id=dummy_scan.id,
                    file_path='/tesseract/db_manager_updated.py',
                    issue_type='Informational',
                    severity='Low',
                    description='Missing index on "description" column in ExploitEntry table (potential performance issue).',
                    line_number=None, # Für Tabellen-Schema-Probleme keine Zeilennummer
                    code_snippet='class ExploitEntry(Base): ... description = Column(Text)',
                    status='New'
                ),
                CodeAnalysisReport(
                    scan_id=dummy_scan.id,
                    file_path='/tesseract/core/krypto/hash_cracker.py',
                    issue_type='Vulnerability',
                    severity='High',
                    description='Weak hashing algorithm (MD5) used for internal password storage.',
                    line_number=78,
                    code_snippet='hashed_pass = hashlib.md5(password.encode()).hexdigest()',
                    status='New'
                ),
                CodeAnalysisReport(
                    scan_id=dummy_scan.id,
                    file_path='/tesseract/utils/log_parser.py',
                    issue_type='InformationLeak',
                    severity='Medium',
                    description='Sensitive data (IP addresses) logged without redaction.',
                    line_number=20,
                    code_snippet='logger.info(f"Connection from {client_ip}")',
                    status='New'
                )
            ]
            for report in reports_to_add:
                db_manager.add_entry(report)
        else:
            print(f"Es existieren bereits {existing_reports_count} CodeAnalysisReports für den Dummy-Scan.")

    print("\nAlle Code-Analyse-Berichte:")
    all_reports = db_manager.get_all_code_analysis_reports()
    for report in all_reports:
        print(report)

    print("\nAlle Scans:")
    all_scans = db_manager.get_all_scans()
    for scan in all_scans:
        print(scan)

    # Beispiel: Status eines Berichts aktualisieren
    if all_reports:
        first_report_id = all_reports[0].id
        db_manager.update_report_status(first_report_id, 'Triaged')

    print("\nAktualisierte Code-Analyse-Berichte:")
    all_reports_updated = db_manager.get_all_code_analysis_reports()
    for report in all_reports_updated:
        print(report)

    # Beispiel: Einen Eintrag löschen
    # if all_reports_updated:
    #     report_to_delete = all_reports_updated[0]
    #     db_manager.delete_entry(report_to_delete)
    #
    # print("\nBerichte nach dem Löschen:")
    # all_reports_after_delete = db_manager.get_all_code_analysis_reports()
    # for report in all_reports_after_delete:
    #     print(report)
