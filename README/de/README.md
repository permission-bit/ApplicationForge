# Bewerbungs-Tool

CLI-Tool zum automatisierten Erstellen, Prüfen und Versenden von Bewerbungen.

Das Tool kombiniert:

- Bewerberdaten
- Stelleninformationen
- automatisches Job-Matching
- Match Score und Confidence Score
- automatische Template-Erkennung
- sprachabhängige Templates
- individuelle Anschreiben
- Anschreiben als PDF
- vollständige Bewerbungsunterlagen als ZIP
- Bewerbungshistorie
- Duplicate Detection
- Einzelversand per E-Mail
- automatischen Massenvorsand
- Dry-Run
- Preview
- reproduzierbare Template-Auswahl über Seeds
- ausführliches Logging

---

# Inhaltsverzeichnis

- [Voraussetzungen](#voraussetzungen)
- [Projektstruktur](#projektstruktur)
- [CLI](#cli)
- [Unternehmen](#unternehmen)
- [Bewerbung erstellen](#bewerbung-erstellen)
- [Matching](#matching)
- [Templates](#templates)
- [Automatische Template-Erkennung](#automatische-template-erkennung)
- [Template erzwingen](#template-erzwingen)
- [Styles](#styles)
- [Sprache](#sprache)
- [Seed](#seed)
- [Dokumente](#dokumente)
- [E-Mail-Versand](#e-mail-versand)
- [Dry-Run](#dry-run)
- [Massenvorsand](#massenvorsand)
- [Bewerbungshistorie](#bewerbungshistorie)
- [Duplicate Detection](#duplicate-detection)
- [Force](#force)
- [Logging](#logging)
- [Typische Workflows](#typische-workflows)
- [CLI-Optionen](#cli-optionen)
- [Konflikte](#konflikte)
- [Exit Codes](#exit-codes)
- [Sicherheitsmechanismen](#sicherheitsmechanismen)

---

# Voraussetzungen

Das Tool benötigt eine funktionierende Python-Umgebung und die Projektstruktur mit den erforderlichen JSON-Dateien.

Wichtige Daten:

```text
data/
├── applicant.json
├── companies.json
├── history.json
├── de/
│   ├── cybersecurity.json
│   ├── it.json
│   └── ...
└── en/
    ├── cybersecurity.json
    ├── it.json
    └── ...
```

Die eigentlichen Template-Dateien befinden sich sprachabhängig in:

```text
data/de/
data/en/
```

Das bedeutet beispielsweise:

```text
data/de/cybersecurity.json
data/en/cybersecurity.json
```

Das Template wird anhand der gewählten Sprache geladen.

---

# Projektstruktur

Eine typische Projektstruktur sieht ungefähr so aus:

```text
project/
│
├── main.py
├── config.py
│
├── data/
│   ├── applicant.json
│   ├── companies.json
│   ├── history.json
│   │
│   ├── de/
│   │   ├── cybersecurity.json
│   │   ├── it.json
│   │   └── software.json
│   │
│   └── en/
│       ├── cybersecurity.json
│       ├── it.json
│       └── software.json
│
├── app/
│   ├── application/
│   │   └── generator.py
│   │
│   ├── documents/
│   │   ├── archive.py
│   │   └── converter.py
│   │
│   ├── matching/
│   │   └── matcher.py
│   │
│   └── mail/
│       └── sender.py
│
├── Documents/
├── generated/
└── logs/
```

Die konkrete Ordnerkonfiguration wird über `config.py` gesteuert.

---

# CLI

Das Tool wird grundsätzlich über `main.py` gestartet:

```bash
python main.py [OPTIONEN]
```

Eine Bewerbung benötigt entweder:

```text
--company
```

oder:

```text
--send-all
```

Ausnahmen sind:

```text
--list-companies
--history
```

Diese beiden Modi können unabhängig davon ausgeführt werden.

---

# Unternehmen

## Unternehmen auflisten

Alle Unternehmen aus `companies.json` anzeigen:

```bash
python main.py --list-companies
```

Beispiel:

```text
================================================================================
VERFÜGBARE UNTERNEHMEN
================================================================================

ID:          example-security
Name:        Example Security GmbH
Position:    Junior Security Engineer
E-Mail:      jobs@example.com
Typ:         Cybersecurity
Größe:       enterprise
Ort:         Berlin
Job-Typ:     Full-Time
Seniorität:  Junior
Arbeitsart:  Employment
Remote:      Remote
Keywords:    Python, Linux, Cybersecurity, Networking
--------------------------------------------------------------------------------
```

Die angezeigte `ID` kann anschließend mit `--company` verwendet werden.

---

# Bewerbung erstellen

Eine normale Bewerbung erstellen:

```bash
python main.py --company example-security
```

Der Ablauf ist:

```text
Bewerber laden
        ↓
Unternehmen laden
        ↓
Duplicate Detection
        ↓
Dokumente prüfen
        ↓
Job Matching
        ↓
Template automatisch bestimmen
        ↓
Style bestimmen
        ↓
Anschreiben generieren
        ↓
PDF erstellen
        ↓
ZIP erstellen
        ↓
History speichern
```

Ohne `--send` wird **keine E-Mail verschickt**.

Das Tool zeigt das generierte Anschreiben anschließend im Terminal an.

---

# Matching

## Nur Matching durchführen

Wenn ausschließlich geprüft werden soll, wie gut eine Stelle zum Bewerber passt:

```bash
python main.py \
    --company example-security \
    --match-only
```

Dabei werden unter anderem angezeigt:

- Match Score
- Confidence Score
- gematchte Kenntnisse
- fehlende Kenntnisse
- Job-Typ
- Seniorität
- Beschäftigungsart
- Arbeitsmodell

Beispiel:

```text
================================================================================
MATCHING
================================================================================

Match Score:       82.5%
Confidence Score:  91.0%

Gematchte Kenntnisse:

  ✓ Python
  ✓ Linux
  ✓ Cybersecurity
  ✓ Networking

Fehlende Kenntnisse:

  ✗ Kubernetes

Job-Typ: Full-Time
Seniorität: Junior
Beschäftigung: Employment
Arbeitsmodell: Remote

================================================================================
```

`--match-only` erstellt keine Bewerbungsunterlagen und versendet keine E-Mail.

---

# Templates

## Grundprinzip

Templates sind sprachabhängig organisiert.

Beispiel:

```text
data/
├── de/
│   ├── cybersecurity.json
│   ├── it.json
│   └── software.json
│
└── en/
    ├── cybersecurity.json
    ├── it.json
    └── software.json
```

Bei:

```bash
python main.py \
    --company example-security \
    --language en
```

werden Templates aus:

```text
data/en/
```

verwendet.

Bei:

```bash
python main.py \
    --company example-security \
    --language de
```

werden Templates aus:

```text
data/de/
```

verwendet.

---

# Automatische Template-Erkennung

Templates müssen nicht mehr fest im Python-Code eingetragen werden.

Der Generator durchsucht das jeweilige Sprachverzeichnis automatisch nach `.json`-Dateien.

Beispielsweise:

```text
data/en/
├── cybersecurity.json
├── it.json
├── software.json
└── system-administration.json
```

wird automatisch erkannt als:

```text
cybersecurity
it
software
system-administration
```

Dabei werden bestimmte Daten-Dateien ignoriert, beispielsweise:

```text
applicant.json
companies.json
history.json
templates.json
```

Nur gültige Template-Dateinamen werden berücksichtigt.

Das bedeutet:

> Eine neue Template-Datei kann einfach in das entsprechende Sprachverzeichnis gelegt werden.

Beispiel:

```text
data/en/cloud-security.json
```

Danach steht das Template grundsätzlich automatisch zur Verfügung.

Es muss dafür nicht zusätzlich in einer Python-Liste registriert werden.

Die Implementierung durchsucht das Sprachverzeichnis und verwendet den Dateinamen ohne `.json` als Template-Typ.

---

# Template-Auswahl

Wenn kein `--template` angegeben wird, entscheidet der Generator automatisch über den Template-Typ.

Der Generator:

1. lädt die Templates der gewählten Sprache
2. validiert die Templates
3. bestimmt den passenden Template-Typ
4. bestimmt anschließend den Style
5. generiert das Anschreiben

Diese Auswahl wird innerhalb von `generate_application()` durchgeführt.

---

# Template erzwingen

Ein bestimmtes Template kann explizit angegeben werden:

```bash
python main.py \
    --company example-security \
    --template cybersecurity
```

Dadurch wird die automatische Template-Auswahl für den Template-Typ überschrieben.

Der Generator dokumentiert ausdrücklich:

```text
An explicit template_type always overrides automatic
template selection.
```

Beispiele:

```text
cybersecurity
it
software
cloud-security
system-administration
```

Welche Templates tatsächlich verfügbar sind, hängt von den vorhandenen JSON-Dateien im jeweiligen Sprachverzeichnis ab.

---

# Styles

Ein Template kann mehrere Styles enthalten.

Beispielsweise:

```text
formal
technical
modern
```

Ein Style kann ebenfalls explizit vorgegeben werden:

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

Damit werden:

```text
Template:
cybersecurity

Style:
technical
```

verwendet.

Wenn kein Style angegeben wird, wird der Style automatisch ausgewählt.

Die Style-Auswahl erfolgt nach der Auswahl des Template-Typs.

---

# Template + Style kombinieren

Beispiel:

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

Damit werden sowohl Template-Typ als auch Style vorgegeben.

---

# Sprache

Unterstützte Sprachen:

```text
de
en
```

Standard:

```text
de
```

## Deutsches Anschreiben

```bash
python main.py \
    --company example-security \
    --language de
```

Verwendet:

```text
data/de/
```

## Englisches Anschreiben

```bash
python main.py \
    --company example-security \
    --language en
```

Verwendet:

```text
data/en/
```

Die Sprache wird ebenfalls beim PDF- und ZIP-Erstellungsprozess berücksichtigt.

---

# Seed

Mit `--seed` kann die Template-/Style-Auswahl reproduzierbar gemacht werden.

Beispiel:

```bash
python main.py \
    --company example-security \
    --seed 12345
```

Intern wird dafür ein eigener Random-Generator mit dem angegebenen Seed verwendet.

Dadurch kann derselbe Auswahlprozess reproduziert werden.

Beispiel:

```bash
python main.py \
    --company example-security \
    --language en \
    --seed 12345
```

Bei gleichen Eingaben und gleichem Seed kann die Auswahl reproduziert werden.

---

# Dokumente

Standardmäßig verwendet das Tool den in `config.py` definierten Dokumentenordner.

Ein eigener Ordner kann über `--documents` angegeben werden:

```bash
python main.py \
    --company example-security \
    --documents "/Users/max/Documents/Bewerbung"
```

Der Pfad wird aufgelöst und überprüft.

Das Tool erwartet mindestens ein verwendbares Bewerbungsdokument.

Die gefundenen Dokumente werden anschließend in die Bewerbungs-ZIP aufgenommen.

Beispielausgabe:

```text
DOKUMENTE
------------------------------------------------------------

  • Lebenslauf.pdf
  • Zeugnisse.pdf
  • Zertifikate.pdf

------------------------------------------------------------
Anzahl: 3
```

---

# E-Mail-Versand

## Einzelne Bewerbung senden

Eine Bewerbung erstellen und anschließend nach Bestätigung senden:

```bash
python main.py \
    --company example-security \
    --send
```

Vor dem Versand erscheint eine Sicherheitsabfrage:

```text
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

ACHTUNG: E-MAIL WIRD VERSENDET

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Bewerber:    Max Mustermann
Unternehmen: Example Security GmbH
Position:    Junior Security Engineer
Empfänger:   jobs@example.com
Anhang:      generated/...

Bewerbung wirklich versenden? [y/N]:
```

Bestätigungen:

```text
y
yes
j
ja
```

Alles andere bricht den Versand ab.

---

# Versand ohne Nachfrage

Für automatisierte Abläufe kann die Bestätigung übersprungen werden:

```bash
python main.py \
    --company example-security \
    --send \
    --yes
```

Kurzform:

```bash
python main.py \
    --company example-security \
    --send \
    -y
```

**Achtung:** In diesem Modus wird direkt versendet.

---

# Dry-Run

Der Dry-Run ist der sicherste Weg, den vollständigen Versand-Workflow zu testen.

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

Dabei werden:

- Bewerberdaten geladen
- Unternehmen geladen
- Dokumente geprüft
- Matching durchgeführt
- Template ausgewählt
- Anschreiben generiert
- PDF erstellt
- ZIP erstellt

aber:

**keine E-Mail wird tatsächlich versendet.**

Beispiel:

```text
================================================================================
DRY-RUN – KEINE E-MAIL WIRD VERSENDET
================================================================================

Empfänger: jobs@example.com
Betreff: Bewerbung als Junior Security Engineer
Anhang: generated/...

→ Keine JSON-Datei wird verändert.
→ Keine E-Mail wurde versendet.
```

---

# Massenvorsand

Mit `--send-all` können alle Unternehmen aus `companies.json` nacheinander verarbeitet werden:

```bash
python main.py --send-all
```

Der Ablauf pro Unternehmen ist:

```text
Company laden
      ↓
Duplicate Detection
      ↓
Bewerbung erstellen
      ↓
Matching
      ↓
Template auswählen
      ↓
Anschreiben generieren
      ↓
PDF erstellen
      ↓
ZIP erstellen
      ↓
E-Mail senden
      ↓
History speichern
      ↓
Company aus companies.json entfernen
```

Die Unternehmen werden nacheinander verarbeitet.

Beispiel:

```text
================================================================================
AUTOMATISCHER BEWERBUNGSVERSAND
================================================================================

5 Unternehmen gefunden.
Die Bewerbungen werden nacheinander verarbeitet.
Eine Company wird erst nach erfolgreichem Versand entfernt.

================================================================================
[1/5] Example Security GmbH
Position: Junior Security Engineer
E-Mail:   jobs@example.com
================================================================================
```

---

# Wichtig: Verhalten von `--send-all`

Eine Company wird **erst nach erfolgreichem E-Mail-Versand** aus `companies.json` entfernt.

Wenn die Erstellung fehlschlägt:

```text
✗ Erstellung fehlgeschlagen
→ Company bleibt erhalten.
```

Wenn der Versand fehlschlägt:

```text
✗ Versand fehlgeschlagen
→ Company bleibt erhalten.
```

Wenn die Entfernung aus `companies.json` fehlschlägt:

```text
⚠ E-Mail wurde versendet,
aber Company konnte nicht aus companies.json entfernt werden.
```

Dieses Verhalten verhindert, dass ein Unternehmen aufgrund eines vorherigen Fehlers einfach aus der Warteschlange verschwindet.

---

# `--send-all` und Templates

`--send-all` verwendet denselben Generator wie der normale Einzelversand.

Für jedes Unternehmen wird deshalb ebenfalls:

```text
Matching
    ↓
Template-Auswahl
    ↓
Style-Auswahl
    ↓
Anschreiben
```

durchgeführt.

Der Massenvorsand ruft für jedes Unternehmen `build_application()` auf und übergibt dabei Template, Style, Sprache und Seed.

Wenn kein `--template` angegeben wird, kann der Generator deshalb automatisch das passende Template bestimmen.

Beispiel:

```bash
python main.py --send-all
```

Jede Company wird individuell verarbeitet.

---

# Massenvorsand mit Sprache

Alle Bewerbungen auf Englisch:

```bash
python main.py \
    --send-all \
    --language en
```

Alle Bewerbungen auf Deutsch:

```bash
python main.py \
    --send-all \
    --language de
```

---

# Massenvorsand mit Template

Ein bestimmtes Template für alle Unternehmen erzwingen:

```bash
python main.py \
    --send-all \
    --template cybersecurity
```

Ein bestimmtes Template und einen bestimmten Style erzwingen:

```bash
python main.py \
    --send-all \
    --template cybersecurity \
    --style technical
```

Damit wird die automatische Template-Auswahl überschrieben.

---

# Massenvorsand simulieren

Der vollständige Massenvorsand kann ebenfalls als Dry-Run ausgeführt werden:

```bash
python main.py \
    --send-all \
    --dry-run
```

Dabei wird für jedes Unternehmen die Bewerbung aufgebaut.

Es wird jedoch:

- keine E-Mail versendet
- keine Company aus `companies.json` entfernt
- keine JSON-Datei verändert

Beispiel:

```text
================================================================================
[1/20] Example Security GmbH
================================================================================

DRY-RUN – KEINE E-MAIL WIRD VERSENDET

Empfänger: jobs@example.com
Betreff: Bewerbung als Junior Security Engineer
Anhang: generated/...

→ Company bleibt in companies.json.
```

Der Dry-Run ist besonders geeignet, um vor einem echten Massenvorsand den kompletten Ablauf zu überprüfen.

---

# Bewerbungshistorie

Die Bewerbungshistorie befindet sich in:

```text
data/history.json
```

Anzeigen:

```bash
python main.py --history
```

Gespeichert werden unter anderem:

- Unternehmen
- Company-ID
- Position
- E-Mail
- URL
- Job-ID
- Bewerber
- Status
- Erstellungszeit
- Versandzeit
- Match Score
- Confidence Score
- Template-Typ
- Template-Style
- ZIP-Datei

Beispiel:

```text
================================================================================
BEWERBUNGSHISTORIE
================================================================================

[1] Example Security GmbH
    Position: Junior Security Engineer
    E-Mail:   jobs@example.com
    Status:   sent
    Erstellt: 2026-09-09T02:30:00+00:00
    Gesendet: 2026-09-09T02:31:00+00:00
    Match:    82.5%
    Confidence: 91.0%

================================================================================
```

---

# History-Status

Je nach Workflow können unterschiedliche Status gespeichert werden.

Beispielsweise:

```text
generated
sent
failed
cancelled
```

Ein `sent`-Eintrag bedeutet, dass die Bewerbung tatsächlich versendet wurde.

---

# Duplicate Detection

Das Tool besitzt eine Duplicate Detection.

Für eine Bewerbung wird ein stabiler History-Key erzeugt.

Priorität:

```text
1. job_id
2. company id + position + email
3. company name + position + email
```

Dadurch kann eine Stelle auch dann wiedererkannt werden, wenn sich beispielsweise andere Felder verändert haben.

---

# Verhalten bei Duplikaten

Wenn bereits ein History-Eintrag existiert, erscheint eine Warnung.

Bei einem normalen Erstellen kann die Bewerbung weiterhin erstellt werden.

Beim Versand wird eine bereits versendete Bewerbung standardmäßig blockiert.

Beispiel:

```text
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

WARNUNG: MÖGLICHE DOPPELTE BEWERBUNG

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Unternehmen: Example Security GmbH
Position:    Junior Security Engineer
Status:      sent
Erstellt:    2026-09-09T02:30:00+00:00
Gesendet:    2026-09-09T02:31:00+00:00

Versand wird verhindert.

Nutze --force, wenn du diese Bewerbung bewusst erneut senden möchtest.
```

---

# Force

Wenn eine bereits vorhandene Bewerbung bewusst erneut versendet werden soll:

```bash
python main.py \
    --company example-security \
    --send \
    --force
```

Mit automatischer Bestätigung:

```bash
python main.py \
    --company example-security \
    --send \
    --force \
    --yes
```

`--force` deaktiviert die Duplicate-Sperre für diesen Lauf.

---

# Logging

Das Tool verwendet Logging für wichtige Verarbeitungsschritte.

Standardmäßig werden Logs sowohl im Terminal als auch in der konfigurierten Log-Datei ausgegeben.

Ausführlicheres Logging:

```bash
python main.py \
    --company example-security \
    --verbose
```

Kurzform:

```bash
python main.py \
    --company example-security \
    -v
```

Kann mit anderen Optionen kombiniert werden:

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run \
    --verbose
```

Im Verbose-Modus wird der Logger auf `DEBUG` gesetzt.

---

# Typische Workflows

## 1. Unternehmen anzeigen

```bash
python main.py --list-companies
```

---

## 2. Stelle prüfen

```bash
python main.py \
    --company example-security \
    --match-only
```

---

## 3. Bewerbung erstellen

```bash
python main.py \
    --company example-security
```

---

## 4. Bewerbung auf Englisch erstellen

```bash
python main.py \
    --company example-security \
    --language en
```

---

## 5. Anschreiben mit bestimmtem Template

```bash
python main.py \
    --company example-security \
    --template cybersecurity
```

---

## 6. Template und Style festlegen

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

---

## 7. Reproduzierbare Generierung

```bash
python main.py \
    --company example-security \
    --seed 12345
```

---

## 8. Anschreiben prüfen

```bash
python main.py \
    --company example-security \
    --preview
```

---

## 9. Versand simulieren

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

---

## 10. Bewerbung senden

```bash
python main.py \
    --company example-security \
    --send
```

---

## 11. Bewerbung automatisiert senden

```bash
python main.py \
    --company example-security \
    --send \
    --yes
```

---

## 12. Alle Bewerbungen simulieren

```bash
python main.py \
    --send-all \
    --dry-run
```

---

## 13. Alle Bewerbungen senden

```bash
python main.py \
    --send-all \
    --yes
```

---

## 14. Alle Bewerbungen auf Englisch senden

```bash
python main.py \
    --send-all \
    --language en \
    --yes
```

---

## 15. Bewerbung erneut senden

```bash
python main.py \
    --company example-security \
    --send \
    --force
```

---

## 16. Bewerbung erneut ohne Nachfrage senden

```bash
python main.py \
    --company example-security \
    --send \
    --force \
    --yes
```

---

## 17. History anzeigen

```bash
python main.py --history
```

---

# CLI-Optionen

| Option                | Beschreibung                                            |
| --------------------- | ------------------------------------------------------- |
| `--company COMPANY`   | ID des Unternehmens aus `companies.json`                |
| `--send-all`          | Alle Unternehmen nacheinander verarbeiten und versenden |
| `--documents PATH`    | Eigenen Dokumentenordner verwenden                      |
| `--template TEMPLATE` | Template-Typ erzwingen                                  |
| `--style STYLE`       | Template-Style erzwingen                                |
| `--language {de,en}`  | Sprache des Anschreibens                                |
| `--seed SEED`         | Seed für reproduzierbare Auswahl                        |
| `--match-only`        | Nur Matching durchführen                                |
| `--preview`           | Anschreiben anzeigen, niemals versenden                 |
| `--send`              | Bewerbung per E-Mail versenden                          |
| `--dry-run`           | Versand simulieren                                      |
| `--yes`, `-y`         | Versandbestätigung überspringen                         |
| `--list-companies`    | Unternehmen anzeigen                                    |
| `--history`           | Bewerbungshistorie anzeigen                             |
| `--force`             | Duplicate Detection beim Versand umgehen                |
| `--verbose`, `-v`     | Ausführlicheres Logging                                 |
| `--help`              | Hilfe anzeigen                                          |

---

# `--preview`

Zeigt das generierte Anschreiben direkt im Terminal.

```bash
python main.py \
    --company example-security \
    --preview
```

Es wird keine E-Mail versendet.

Die generierte Bewerbung wird trotzdem in der History gespeichert.

---

# `--match-only`

Führt ausschließlich das Matching durch:

```bash
python main.py \
    --company example-security \
    --match-only
```

Es werden keine Bewerbungsunterlagen erstellt.

---

# `--dry-run`

Simuliert einen Versand.

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

Es wird keine E-Mail versendet und keine JSON-Datei verändert.

---

# `--send-all`

Verarbeitet alle Unternehmen aus:

```text
data/companies.json
```

nacheinander.

Erfolgreich versendete Unternehmen werden anschließend aus der Warteschlange entfernt.

Fehlgeschlagene Unternehmen bleiben erhalten.

---

# `--force`

Ignoriert einen vorhandenen History-Eintrag und erlaubt einen erneuten Versand.

```bash
--force
```

Sollte nur verwendet werden, wenn ein erneuter Versand bewusst gewünscht ist.

---

# `--yes`

Überspringt die interaktive Versandbestätigung.

Nur sinnvoll in Kombination mit:

```bash
--send
```

oder einem automatisierten Massenvorsand.

Beispiel:

```bash
python main.py \
    --send-all \
    --yes
```

---

# `--documents`

Verwendet einen alternativen Bewerbungsordner:

```bash
python main.py \
    --company example-security \
    --documents "/Users/max/Documents/Bewerbung"
```

---

# `--template`

Erzwingt einen bestimmten Template-Typ:

```bash
python main.py \
    --company example-security \
    --template cybersecurity
```

Ohne diese Option wird der Template-Typ automatisch ausgewählt.

---

# `--style`

Erzwingt einen bestimmten Style:

```bash
python main.py \
    --company example-security \
    --style technical
```

Kann zusammen mit `--template` verwendet werden:

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

---

# `--language`

Verfügbare Sprachen:

```text
de
en
```

Beispiel:

```bash
python main.py \
    --company example-security \
    --language en
```

---

# `--seed`

Erlaubt eine reproduzierbare Auswahl:

```bash
python main.py \
    --company example-security \
    --seed 12345
```

---

# Konflikte

Einige Optionen können nicht miteinander kombiniert werden.

## `--send-all` + `--company`

Nicht erlaubt:

```bash
python main.py \
    --company example-security \
    --send-all
```

`--send-all` verarbeitet bereits alle Unternehmen und darf deshalb nicht zusammen mit einer einzelnen Company verwendet werden.

---

## `--send-all` + `--preview`

Nicht erlaubt:

```bash
python main.py \
    --send-all \
    --preview
```

---

## `--send-all` + `--match-only`

Nicht erlaubt:

```bash
python main.py \
    --send-all \
    --match-only
```

Für eine einzelne Stelle:

```bash
python main.py \
    --company example-security \
    --match-only
```

---

## `--preview` + `--send`

Nicht sinnvoll und nicht erlaubt.

`--preview` ist ausdrücklich ein Modus ohne Versand.

---

## `--match-only` + `--send`

Nicht erlaubt.

`--match-only` führt ausschließlich das Matching durch.

---

## `--match-only` + `--preview`

Nicht erlaubt.

---

## `--yes` ohne `--send`

Nicht erlaubt.

Falsch:

```bash
python main.py \
    --company example-security \
    --yes
```

Richtig:

```bash
python main.py \
    --company example-security \
    --send \
    --yes
```

Die CLI validiert diese grundlegenden Konflikte vor dem eigentlichen Workflow.

---

# Exit Codes

## `0`

Erfolgreich abgeschlossen.

---

## `1`

Fehler bei:

- Verarbeitung
- Matching
- Template-Laden
- Template-Validierung
- Dokumentenprüfung
- PDF-Erstellung
- ZIP-Erstellung
- E-Mail-Versand
- History
- anderen Verarbeitungsschritten

---

## `130`

Programm wurde beispielsweise mit:

```text
Ctrl+C
```

abgebrochen.

---

# Sicherheitsmechanismen

Das Tool enthält mehrere Schutzmechanismen gegen versehentliche oder doppelte Versendungen.

## Keine automatische E-Mail ohne `--send`

Ein normaler Aufruf:

```bash
python main.py \
    --company example-security
```

versendet keine E-Mail.

---

## Bestätigung vor Versand

Ohne:

```text
--yes
```

wird vor dem Versand nachgefragt.

---

## Dry-Run

Mit:

```text
--dry-run
```

kann der komplette Workflow ohne tatsächlichen Versand getestet werden.

---

## Duplicate Detection

Bereits versendete Bewerbungen werden erkannt und standardmäßig nicht erneut versendet.

---

## Atomic File Writes

History und Änderungen an `companies.json` werden über temporäre Dateien geschrieben und anschließend ersetzt.

Dadurch wird verhindert, dass eine Datei bei einem Schreibfehler unnötig beschädigt wird.

---

## Erfolgreicher Versand vor Entfernung

Bei `--send-all` wird eine Company erst nach erfolgreichem Versand aus der Warteschlange entfernt.

Dadurch bleibt eine fehlgeschlagene Bewerbung für einen späteren Lauf erhalten.

---

# Template-Sicherheit

Template-Dateien werden vor ihrer Verwendung geladen und validiert.

Der Generator:

1. bestimmt das Sprachverzeichnis
2. entdeckt verfügbare Templates
3. lädt die Template-Datei
4. validiert das JSON
5. validiert die Template-Struktur
6. bestimmt den Template-Typ
7. bestimmt den Style

Nicht existierende Templates erzeugen einen Fehler und geben die verfügbaren Templates für die gewählte Sprache aus.

---

# Neues Template hinzufügen

Ein neues Template benötigt grundsätzlich keine Änderung an `generator.py`.

Beispiel für Englisch:

```text
data/en/cloud-security.json
```

Danach kann es beispielsweise explizit verwendet werden:

```bash
python main.py \
    --company example-security \
    --language en \
    --template cloud-security
```

Für Deutsch:

```text
data/de/cloud-security.json
```

und:

```bash
python main.py \
    --company example-security \
    --language de \
    --template cloud-security
```

Die Erkennung erfolgt automatisch über die `.json`-Dateien im jeweiligen Sprachverzeichnis.

---

# Empfohlener Testablauf

Vor einem echten Versand sollte zunächst das Matching geprüft werden:

```bash
python main.py \
    --company example-security \
    --match-only
```

Danach die Bewerbung generieren:

```bash
python main.py \
    --company example-security
```

Anschließend den Versand simulieren:

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

Für mehrere Unternehmen:

```bash
python main.py \
    --send-all \
    --dry-run
```

Erst wenn der Dry-Run korrekt aussieht, sollte der echte Versand erfolgen:

```bash
python main.py \
    --send-all \
    --yes
```

---

# Vollständiger Beispiel-Workflow

```bash
# Unternehmen anzeigen
python main.py --list-companies

# Stelle prüfen
python main.py \
    --company example-security \
    --match-only

# Bewerbung auf Englisch erstellen
python main.py \
    --company example-security \
    --language en

# Bewerbung mit bestimmtem Template testen
python main.py \
    --company example-security \
    --language en \
    --template cybersecurity \
    --style technical \
    --preview

# Versand simulieren
python main.py \
    --company example-security \
    --language en \
    --send \
    --dry-run

# Einzelne Bewerbung senden
python main.py \
    --company example-security \
    --language en \
    --send

# History anzeigen
python main.py --history
```

---

# Vollständiger Massenvorsand

Vorbereitung:

```bash
python main.py \
    --send-all \
    --dry-run
```

Wenn alles korrekt aussieht:

```bash
python main.py \
    --send-all \
    --yes
```

Englischer Massenvorsand:

```bash
python main.py \
    --send-all \
    --language en \
    --yes
```

Mit einem festen Template:

```bash
python main.py \
    --send-all \
    --language en \
    --template cybersecurity \
    --yes
```

---

# Hilfe

Die vollständige CLI-Hilfe kann jederzeit angezeigt werden:

```bash
python main.py --help
```

---

# Kurzreferenz

```text
LISTE
python main.py --list-companies

MATCHING
python main.py --company ID --match-only

ERSTELLEN
python main.py --company ID

PREVIEW
python main.py --company ID --preview

ENGLISCH
python main.py --company ID --language en

TEMPLATE
python main.py --company ID --template cybersecurity

STYLE
python main.py --company ID --template cybersecurity --style technical

SEED
python main.py --company ID --seed 12345

DRY-RUN
python main.py --company ID --send --dry-run

SENDEN
python main.py --company ID --send

SENDEN OHNE NACHFRAGE
python main.py --company ID --send --yes

MASSENVORSAND
python main.py --send-all

MASSENVORSAND DRY-RUN
python main.py --send-all --dry-run

MASSENVORSAND AUTOMATISCH
python main.py --send-all --yes

HISTORY
python main.py --history

ERNEUT SENDEN
python main.py --company ID --send --force

VERBOSE
python main.py --company ID --verbose

HILFE
python main.py --help
```

---

# Architektur

Der zentrale Ablauf ist bewusst modular aufgebaut:

```text
main.py
   │
   ├── application.generator
   │       │
   │       ├── Template Discovery
   │       ├── Template Validation
   │       ├── Template Selection
   │       ├── Style Selection
   │       └── Cover Letter Generation
   │
   ├── matching.matcher
   │       └── Job Matching
   │
   ├── documents.converter
   │       └── PDF
   │
   ├── documents.archive
   │       └── ZIP
   │
   └── mail.sender
           └── E-Mail
```

Dadurch sind Matching, Generierung, Dokumentenerstellung, Archivierung und Versand voneinander getrennt.

---

# Designprinzip

Das System ist darauf ausgelegt, dass neue Templates über die Datenstruktur hinzugefügt werden können, ohne den Generator für jedes neue Template manuell erweitern zu müssen.

Beispiel:

```text
data/en/
├── cybersecurity.json
├── it.json
├── software.json
├── cloud-security.json
└── devops.json
```

Der Generator erkennt diese Dateien automatisch.

Die Template-Auswahl bleibt dabei dynamisch:

```text
Company
   ↓
Job Type / Keywords / Informationen
   ↓
Matching
   ↓
verfügbare Templates der Sprache
   ↓
automatische Template-Auswahl
   ↓
automatische Style-Auswahl
   ↓
individuelles Anschreiben
```

Ein explizites:

```text
--template
```

überschreibt die automatische Auswahl.

Ein explizites:

```text
--style
```

überschreibt die automatische Style-Auswahl.

---

# Fazit

Das Bewerbungs-Tool kann sowohl einzelne Bewerbungen als auch komplette Bewerbungswarteschlangen automatisiert verarbeiten.

Die wichtigsten Modi sind:

```bash
# Prüfen
python main.py --company ID --match-only

# Erstellen
python main.py --company ID

# Testen
python main.py --company ID --send --dry-run

# Senden
python main.py --company ID --send

# Alle testen
python main.py --send-all --dry-run

# Alle senden
python main.py --send-all --yes
```

Templates werden sprachabhängig automatisch aus den vorhandenen JSON-Dateien erkannt. Dadurch kann das System erweitert werden, indem neue Templates in `data/de/` oder `data/en/` hinzugefügt werden, ohne für jeden neuen Template-Typ die CLI oder den Generator anpassen zu müssen.
