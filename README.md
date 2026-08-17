# AB Bestellunterlagen Checker

Ein Python-Tool zum Vergleich von Bestellung (PO) und Auftragsbestätigung (AB).

## Funktionen

- Extrahiert Inhalte aus PDF-Dateien
- Vergleicht Bestellung und Auftragsbestätigung
- Erkennt Abweichungen bei Mengen, Preisen und Lieferterminen
- Exportiert Ergebnisse als CSV, JSON und HTML

## Projektstruktur

```text
AB.pdf
BESTELLUNG.pdf
ab_bestellunterlagen_checker.py
ab_bestellunterlagen_checker_v2.py
ab_bestellunterlagen_checker_v3.py
AB_Check_Report.csv
AB_Check_Report.html
AB_Check_Report.json
```

## Verwendung

```powershell
python ab_bestellunterlagen_checker_v3.py
```

Die Auswertung wird als Report-Datei ausgegeben.

## Git Ignore Empfehlung

Folgende Dateitypen sollten nicht ins Repository hochgeladen werden:

```gitignore
*.pdf
*.xls
*.xlsx
*.xlsm
*.xlsb
```

## Anforderungen

- Python 3.10+
- Abhängigkeiten gemäß Skript

## Autor

James Li
