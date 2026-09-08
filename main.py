from __future__ import annotations

import argparse
import json
import logging
import sys

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import (
    DOCUMENTS_DIR,
    GENERATED_DIR,
    LOG_FILE,
)

from app.application.generator import (
    generate_application as generate_application_text,
    get_company,
    load_json,
)

from app.documents.archive import (
    collect_documents,
    create_zip,
)

from app.documents.converter import (
    create_cover_letter_pdf,
)

from app.mail.sender import (
    send_email,
)

from app.matching.matcher import (
    apply_match_result,
    match_job,
)


# ============================================================
# CONSTANTS
# ============================================================

HISTORY_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "history.json"
)

DEFAULT_SEED = None


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(
    "bewerbung"
)


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class ApplicationBuild:
    """
    Enthält alle erzeugten Artefakte einer Bewerbung.
    """

    company: dict[str, Any]

    applicant: dict[str, Any]

    documents_dir: Path

    documents: list[Path]

    letter: str

    cover_letter: Path

    zip_file: Path

    match_score: float = 0.0

    confidence_score: float = 0.0

    template_type: str = ""

    template_style: str = ""

    language: str = "de"
# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    """
    Erstellt den CLI-Parser.
    """

    parser = argparse.ArgumentParser(
        prog="bewerbung",
        description=(
            "Production-Ready Bewerbungs-Tool "
            "für Matching, Anschreiben, PDF, "
            "ZIP und E-Mail-Versand."
        ),
        formatter_class=(
            argparse.RawDescriptionHelpFormatter
        ),
        epilog="""
BEISPIELE
========

UNTERNEHMEN
-----------

Alle verfügbaren Unternehmen anzeigen:

    python main.py --list-companies


Eine bestimmte Stelle auswählen:

    python main.py --company example-security


BEWERBUNG ERSTELLEN
-------------------

Bewerbung erstellen:

    python main.py --company example-security


Anschreiben anzeigen:

    python main.py \\
        --company example-security \\
        --preview


MATCHING
--------

Nur das Stellen-Matching durchführen:

    python main.py \\
        --company example-security \\
        --match-only


TEMPLATES
---------

Bestimmtes Template verwenden:

    python main.py \\
        --company example-security \\
        --template cybersecurity


Template und Style festlegen:

    python main.py \\
        --company example-security \\
        --template cybersecurity \\
        --style technical


SPRACHE
-------

Englisches Anschreiben erzeugen:

    python main.py \\
        --company example-security \\
        --language en


REPRODUZIERBARE GENERIERUNG
---------------------------

Seed für reproduzierbare Template-Auswahl verwenden:

    python main.py \\
        --company example-security \\
        --seed 12345


DOKUMENTE
---------

Eigenen Dokumentenordner verwenden:

    python main.py \\
        --company example-security \\
        --documents "/Users/max/Documents/Bewerbung"


VERSAND
-------

Bewerbung erstellen und nach Bestätigung versenden:

    python main.py \\
        --company example-security \\
        --send


Bewerbung ohne Nachfrage versenden:

    python main.py \\
        --company example-security \\
        --send \\
        --yes


DRY-RUN
-------

Versand simulieren:

    python main.py \\
        --company example-security \\
        --send \\
        --dry-run


Der Dry-Run erstellt die Bewerbung und die Dateien,
versendet aber keine E-Mail und verändert keine JSON-Dateien.


MASSENVERSAND
-------------

Alle Unternehmen automatisch nacheinander verarbeiten:

    python main.py --send-all


Massenvorbereitung simulieren:

    python main.py \\
        --send-all \\
        --dry-run


Beim normalen Massenvorsand wird eine Company erst
nach erfolgreichem E-Mail-Versand aus companies.json entfernt.


HISTORIE
--------

Bewerbungshistorie anzeigen:

    python main.py --history


ERNEUTER VERSAND
----------------

Eine bereits versendete Bewerbung erneut erlauben:

    python main.py \\
        --company example-security \\
        --send \\
        --force


LOGGING
-------

Ausführlicheres Logging aktivieren:

    python main.py \\
        --company example-security \\
        --verbose


HINWEISE
========

--preview
    Zeigt das generierte Anschreiben an.
    Es wird keine E-Mail versendet.

--match-only
    Führt ausschließlich das Matching durch.
    Es werden keine Bewerbungsunterlagen erstellt.

--dry-run
    Simuliert den Ablauf ohne E-Mail-Versand.
    Keine JSON-Datei wird verändert.

--send-all
    Verarbeitet alle Unternehmen aus companies.json
    nacheinander.

--force
    Ignoriert einen vorhandenen History-Eintrag
    und erlaubt eine erneute Bewerbung.

--yes
    Überspringt die manuelle Versandbestätigung.

EXIT CODES
==========

0
    Erfolgreich abgeschlossen.

1
    Fehler bei Verarbeitung, Matching, Generierung
    oder Versand.

130
    Programm wurde mit Ctrl+C beendet.
        """,
    )

    # ========================================================
    # COMPANY
    # ========================================================

    parser.add_argument(
        "--language",
        choices=["de", "en"],
        default="de",
        help=(
            "Sprache des Anschreibens. "
            "Verfügbar: de, en. "
            "Standard: de."
        ),
    )

    parser.add_argument(
        "--company",
        help=(
            "ID des Unternehmens aus "
            "companies.json."
        ),
    )

    # ========================================================
    # DOCUMENTS
    # ========================================================

    parser.add_argument(
        "--documents",
        type=Path,
        default=DOCUMENTS_DIR,
        help=(
            "Ordner mit Bewerbungsunterlagen. "
            "Standard: Documents/"
        ),
    )

    # ========================================================
    # TEMPLATE
    # ========================================================

    parser.add_argument(
        "--template",
        help=(
            "Template-Typ erzwingen, "
            "z. B. cybersecurity, it oder software."
        ),
    )

    parser.add_argument(
        "--style",
        help=(
            "Template-Style erzwingen, "
            "z. B. formal, technical oder modern."
        ),
    )

    # ========================================================
    # SEED
    # ========================================================

    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=(
            "Seed für reproduzierbare "
            "Template-Auswahl."
        ),
    )

    # ========================================================
    # MATCH
    # ========================================================

    parser.add_argument(
        "--match-only",
        action="store_true",
        help=(
            "Nur die Stelle gegen die "
            "Bewerberdaten matchen."
        ),
    )

    # ========================================================
    # PREVIEW
    # ========================================================

    parser.add_argument(
        "--preview",
        action="store_true",
        help=(
            "Anschreiben anzeigen, "
            "aber niemals versenden."
        ),
    )

    # ========================================================
    # SEND
    # ========================================================

    parser.add_argument(
        "--send",
        action="store_true",
        help=(
            "Bewerbung nach der Erstellung "
            "per E-Mail versenden."
        ),
    )

    # ========================================================
    # DRY RUN
    # ========================================================

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Dry-Run: Bewerbung erzeugen, "
            "aber keine E-Mail senden und "
            "keine JSON-Dateien verändern."
        ),
    )

    # ========================================================
    # YES
    # ========================================================

    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help=(
            "Versandbestätigung automatisch bestätigen."
        ),
    )

    # ========================================================
    # LIST COMPANIES
    # ========================================================

    parser.add_argument(
        "--list-companies",
        action="store_true",
        help=(
            "Alle Unternehmen aus "
            "companies.json anzeigen."
        ),
    )

    # ========================================================
    # HISTORY
    # ========================================================

    parser.add_argument(
        "--history",
        action="store_true",
        help=(
            "Bewerbungshistorie anzeigen."
        ),
    )

    # ========================================================
    # FORCE
    # ========================================================

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Doppelte Bewerbung trotzdem zulassen."
        ),
    )

    # ========================================================
    # VERBOSE
    # ========================================================

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help=(
            "Ausführlicheres Logging aktivieren."
        ),
    )


    parser.add_argument(
        "--send-all",
        action="store_true",
        help=(
            "Alle Unternehmen aus companies.json "
            "nacheinander verarbeiten und versenden. "
            "Erfolgreich versendete Unternehmen werden entfernt."
        ),
    )

    return parser





# ============================================================
# HISTORY
# ============================================================

def load_history() -> dict[str, Any]:
    """
    Lädt data/history.json.

    Existiert die Datei noch nicht,
    wird eine leere Historie zurückgegeben.
    """

    if not HISTORY_FILE.exists():
        return {
            "applications": []
        }

    try:
        with HISTORY_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "history.json enthält ungültiges JSON: "
            f"Zeile {exc.lineno}, Spalte {exc.colno}"
        ) from exc

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "history.json muss ein Objekt sein."
        )

    applications = data.get(
        "applications",
        [],
    )

    if not isinstance(
        applications,
        list,
    ):
        raise ValueError(
            "history.json: "
            "'applications' muss eine Liste sein."
        )

    return data


def run_send_all(
    applicant: dict[str, Any],
    documents_dir: Path,
    *,
    template_type: str | None = None,
    template_style: str | None = None,
    language: str = "de",
    seed: int | None = None,
    dry_run: bool = False,
) -> int:
    """
    Verarbeitet alle Companies aus companies.json
    nacheinander.

    Nach erfolgreichem Versand wird die jeweilige
    Company aus companies.json entfernt.

    Bei einem Fehler bleibt die Company erhalten.
    """

    logger.info(
        "=" * 80
    )

    logger.info(
        "AUTOMATISCHER MASSENVERSAND START"
    )

    logger.info(
        "=" * 80
    )

    companies = load_companies()

    if not companies:

        print()
        print(
            "Keine Unternehmen in companies.json vorhanden."
        )
        print()

        return 0

    total = len(
        companies
    )

    print()

    print("=" * 80)
    print("AUTOMATISCHER BEWERBUNGSVERSAND")
    print("=" * 80)

    print()

    print(
        f"{total} Unternehmen gefunden."
    )

    print(
        "Die Bewerbungen werden nacheinander verarbeitet."
    )

    print(
        "Eine Company wird erst nach erfolgreichem "
        "Versand entfernt."
    )

    print()

    print("=" * 80)

    successful = 0
    failed = 0
    skipped = 0

    for index, company in enumerate(
        companies,
        start=1,
    ):

        company_name = str(
            company.get(
                "name",
                "-",
            )
        )

        position = str(
            company.get(
                "position",
                "-",
            )
        )

        email = str(
            company.get(
                "email",
                "-",
            )
        )

        print()

        print("=" * 80)

        print(
            f"[{index}/{total}] "
            f"{company_name}"
        )

        print(
            f"Position: {position}"
        )

        print(
            f"E-Mail:   {email}"
        )

        print("=" * 80)

        logger.info(
            "[%d/%d] Verarbeite %s",
            index,
            total,
            company_name,
        )

        # ====================================================
        # DUPLICATE CHECK
        # ====================================================

        try:

            previous_application = find_history_entry(
                company
            )

        except Exception as exc:

            logger.exception(
                "History konnte nicht geprüft werden: %s",
                exc,
            )

            failed += 1
            continue


        if previous_application:

            status = previous_application.get(
                "status",
                "",
            )

            # Nur tatsächlich versendete Bewerbungen
            # blockieren einen erneuten Versand.
            if status == "sent":

                logger.warning(
                    "Bewerbung für %s wurde bereits versendet.",
                    company_name,
                )

                print(
                    "⚠ Bereits erfolgreich versendet."
                )

                print(
                    "→ Company bleibt in companies.json."
                )

                skipped += 1
                continue

            logger.info(
                "Vorhandener History-Eintrag mit Status "
                "'%s' kann erneut verarbeitet werden.",
                status,
            )

        # ====================================================
        # BUILD
        # ====================================================

        try:

            build = build_application(
                company=company,
                applicant=applicant,
                documents_dir=documents_dir,
                template_type=template_type,
                template_style=template_style,
                language=language,
                seed=seed,
            )

        except Exception as exc:

            logger.exception(
                "Bewerbung für %s konnte "
                "nicht erstellt werden: %s",
                company_name,
                exc,
            )

            print(
                f"✗ Erstellung fehlgeschlagen: "
                f"{exc}"
            )

            print(
                "→ Company bleibt erhalten."
            )

            failed += 1
            continue

        # ====================================================
        # DRY RUN
        # ====================================================

        if dry_run:

            logger.info(
                "DRY-RUN: Keine E-Mail wird an %s versendet.",
                email,
            )

            print()
            print(
                "DRY-RUN – KEINE E-MAIL WIRD VERSENDET"
            )

            print(
                f"Empfänger: {email}"
            )

            print(
                f"Betreff: Bewerbung als {position}"
            )

            print(
                f"Anhang:   {build.zip_file}"
            )

            print(
                "→ Keine JSON-Datei wird verändert."
            )

            print(
                "→ Company bleibt in companies.json."
            )

            print()

            successful += 1

            continue


        # ====================================================
        # SEND
        # ====================================================

        try:

            logger.info(
                "Sende Bewerbung an %s...",
                email,
            )

            send_email(
                company=build.company,
                applicant=applicant,
                cover_letter=build.cover_letter,
                zip_file=build.zip_file,
                language=build.language,
            )

        except Exception as exc:

            logger.exception(
                "Versand an %s fehlgeschlagen: %s",
                email,
                exc,
            )

            print(
                f"✗ Versand fehlgeschlagen: "
                f"{exc}"
            )

            print(
                "→ Company bleibt erhalten."
            )

            add_history_entry(
                company=build.company,
                applicant=applicant,
                build=build,
                status="failed",
            )

            failed += 1
            continue

        # ====================================================
        # HISTORY
        # ====================================================

        try:

            add_history_entry(
                company=build.company,
                applicant=applicant,
                build=build,
                status="sent",
            )

        except Exception as exc:

            logger.exception(
                "History konnte nach erfolgreichem "
                "Versand nicht gespeichert werden: %s",
                exc,
            )

            print(
                "⚠ E-Mail wurde versendet, "
                "aber History konnte nicht "
                "gespeichert werden."
            )

        # ====================================================
        # REMOVE COMPANY
        # ====================================================

        try:

            remove_company_from_json(
                company
            )

        except Exception as exc:

            logger.exception(
                "Company konnte nach erfolgreichem "
                "Versand nicht entfernt werden: %s",
                exc,
            )

            print(
                "⚠ E-Mail wurde versendet, "
                "aber Company konnte nicht "
                "aus companies.json entfernt werden."
            )

            failed += 1
            continue

        # ====================================================
        # SUCCESS
        # ====================================================

        print()

        print(
            "✓ Bewerbung erfolgreich versendet."
        )

        print(
            "✓ Company aus companies.json entfernt."
        )

        successful += 1

    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 80)
    print("AUTOMATISCHER VERSAND ABGESCHLOSSEN")
    print("=" * 80)

    print()

    print(
        f"Gesamt:      {total}"
    )

    print(
        f"Erfolgreich: {successful}"
    )

    print(
        f"Übersprungen:{skipped}"
    )

    print(
        f"Fehlgeschl.: {failed}"
    )

    print()

    print("=" * 80)

    logger.info(
        "Massensendung beendet. "
        "Erfolgreich=%d, Übersprungen=%d, Fehler=%d",
        successful,
        skipped,
        failed,
    )

    return 0 if failed == 0 else 1

def load_companies() -> list[dict[str, Any]]:
    """
    Lädt alle Unternehmen aus companies.json.
    """

    data = load_json(
        "companies.json"
    )

    companies = data.get(
        "companies",
        [],
    )

    if not isinstance(
        companies,
        list,
    ):
        raise ValueError(
            "companies.json: "
            "'companies' muss eine Liste sein."
        )

    return [
        company
        for company in companies
        if isinstance(company, dict)
    ]


def remove_company_from_json(
    company: dict[str, Any],
) -> None:
    """
    Entfernt eine erfolgreich bearbeitete Company
    aus companies.json.

    Die Entfernung erfolgt anhand der Company-ID.
    """

    from config import DATA_DIR

    companies_file = (
        DATA_DIR
        / "companies.json"
    )

    if not companies_file.exists():
        raise FileNotFoundError(
            f"companies.json nicht gefunden: "
            f"{companies_file}"
        )

    with companies_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    companies = data.get(
        "companies",
        [],
    )

    if not isinstance(
        companies,
        list,
    ):
        raise ValueError(
            "companies.json: "
            "'companies' muss eine Liste sein."
        )

    target_id = str(
        company.get(
            "id",
            "",
        )
    ).strip()

    target_job_id = str(
        company.get(
            "job_id",
            "",
        )
    ).strip()

    target_email = str(
        company.get(
            "email",
            "",
        )
    ).strip()

    target_position = str(
        company.get(
            "position",
            "",
        )
    ).strip()

    def is_target(
        item: dict[str, Any],
    ) -> bool:

        item_id = str(
            item.get(
                "id",
                "",
            )
        ).strip()

        if target_id and item_id:
            return item_id == target_id

        item_job_id = str(
            item.get(
                "job_id",
                "",
            )
        ).strip()

        if target_job_id and item_job_id:
            return item_job_id == target_job_id

        item_email = str(
            item.get(
                "email",
                "",
            )
        ).strip()

        item_position = str(
            item.get(
                "position",
                "",
            )
        ).strip()

        return (
            item_email.casefold()
            == target_email.casefold()
            and
            item_position.casefold()
            == target_position.casefold()
        )

    original_count = len(
        companies
    )

    data["companies"] = [
        item
        for item in companies
        if not (
            isinstance(item, dict)
            and is_target(item)
        )
    ]

    if len(data["companies"]) == original_count:
        logger.warning(
            "Company konnte nicht aus "
            "companies.json entfernt werden: %s",
            company.get(
                "name",
                "-",
            ),
        )
        return

    temporary = companies_file.with_suffix(
        ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

        file.write("\n")

    temporary.replace(
        companies_file
    )

    logger.info(
        "Company aus companies.json entfernt: %s",
        company.get(
            "name",
            "-",
        ),
    )


def save_history(
    history: dict[str, Any],
) -> None:
    """
    Speichert die Bewerbungshistorie atomar.
    """

    HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = HISTORY_FILE.with_suffix(
        ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=2,
        )

        file.write("\n")

    temporary.replace(
        HISTORY_FILE
    )


def build_history_key(
    company: dict[str, Any],
) -> str:
    """
    Erstellt einen stabilen Schlüssel für
    Duplicate Detection.

    Priorität:

    job_id
    company id + position + email
    company name + position + email
    """

    job_id = str(
        company.get(
            "job_id",
            ""
        )
    ).strip()

    if job_id:
        return f"job:{job_id.casefold()}"

    company_id = str(
        company.get(
            "id",
            ""
        )
    ).strip()

    position = str(
        company.get(
            "position",
            ""
        )
    ).strip()

    email = str(
        company.get(
            "email",
            ""
        )
    ).strip()

    company_name = str(
        company.get(
            "name",
            ""
        )
    ).strip()

    if company_id:
        return (
            "company:"
            f"{company_id.casefold()}:"
            f"{position.casefold()}:"
            f"{email.casefold()}"
        )

    return (
        "company:"
        f"{company_name.casefold()}:"
        f"{position.casefold()}:"
        f"{email.casefold()}"
    )


def find_history_entry(
    company: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Sucht einen bestehenden History-Eintrag.
    """

    history = load_history()

    key = build_history_key(
        company
    )

    for entry in history.get(
        "applications",
        [],
    ):

        if not isinstance(
            entry,
            dict,
        ):
            continue

        if entry.get(
            "history_key"
        ) == key:

            return entry

    return None


def add_history_entry(
    company: dict[str, Any],
    applicant: dict[str, Any],
    build: ApplicationBuild,
    status: str,
) -> None:
    """
    Fügt einen Bewerbungseintrag zur Historie hinzu.
    """

    history = load_history()

    applications = history.setdefault(
        "applications",
        [],
    )

    now = datetime.now(
        timezone.utc
    ).isoformat()

    entry = {
        "history_key": build_history_key(
            company
        ),

        "company": company.get(
            "name",
            "",
        ),

        "company_id": company.get(
            "id",
            "",
        ),

        "position": company.get(
            "position",
            "",
        ),

        "email": company.get(
            "email",
            "",
        ),

        "url": company.get(
            "source_url",
            "",
        ),

        "job_id": company.get(
            "job_id",
            "",
        ),

        "applicant": (
            f"{applicant.get('first_name', '')} "
            f"{applicant.get('last_name', '')}"
        ),

        "status": status,

        "sent_at": (
            now
            if status == "sent"
            else None
        ),

        "created_at": now,

        "match_score": build.match_score,

        "confidence_score": (
            build.confidence_score
        ),

        "template_type": (
            build.template_type
        ),

        "template_style": (
            build.template_style
        ),

        "zip_file": str(
            build.zip_file
        ),
    }

    # Bestehenden Eintrag ersetzen,
    # falls vorhanden.
    history_key = build_history_key(company)

    applications[:] = [
        existing
        for existing in applications
        if not (
            isinstance(
                existing,
                dict,
            )
            and existing.get(
                "history_key"
            ) == history_key
        )
    ]

    applications.append(
        entry
    )

    save_history(
        history
    )


def print_history() -> None:
    """
    Gibt die Bewerbungshistorie aus.
    """

    history = load_history()

    applications = history.get(
        "applications",
        [],
    )

    print()

    print("=" * 80)
    print("BEWERBUNGSHISTORIE")
    print("=" * 80)

    if not applications:
        print()
        print(
            "Noch keine Bewerbungen vorhanden."
        )
        print()
        return

    for index, entry in enumerate(
        applications,
        start=1,
    ):

        print()

        print(
            f"[{index}] "
            f"{entry.get('company', '-')}"
        )

        print(
            f"    Position: "
            f"{entry.get('position', '-')}"
        )

        print(
            f"    E-Mail:   "
            f"{entry.get('email', '-')}"
        )

        print(
            f"    Status:   "
            f"{entry.get('status', '-')}"
        )

        print(
            f"    Erstellt: "
            f"{entry.get('created_at', '-')}"
        )

        if entry.get(
            "sent_at"
        ):
            print(
                f"    Gesendet: "
                f"{entry.get('sent_at')}"
            )

        print(
            f"    Match:    "
            f"{entry.get('match_score', 0):.1f}%"
        )

        print(
            f"    Confidence:"
            f" {entry.get('confidence_score', 0):.1f}%"
        )

    print()
    print("=" * 80)
    print()


# ============================================================
# COMPANY LIST
# ============================================================

def list_companies() -> None:
    """
    Zeigt alle Unternehmen aus companies.json.
    """

    data = load_json(
        "companies.json"
    )

    companies = data.get(
        "companies",
        [],
    )

    if not isinstance(
        companies,
        list,
    ):
        raise ValueError(
            "companies.json: "
            "'companies' muss eine Liste sein."
        )

    print()

    if not companies:
        print(
            "Keine Unternehmen gefunden."
        )
        return

    print("=" * 80)
    print("VERFÜGBARE UNTERNEHMEN")
    print("=" * 80)

    for company in companies:

        if not isinstance(
            company,
            dict,
        ):
            continue

        print()

        print(
            f"ID:          "
            f"{company.get('id', '-')}"
        )

        print(
            f"Name:        "
            f"{company.get('name', '-')}"
        )

        print(
            f"Position:    "
            f"{company.get('position', '-')}"
        )

        print(
            f"E-Mail:      "
            f"{company.get('email', '-')}"
        )

        print(
            f"Typ:         "
            f"{company.get('type', '-')}"
        )

        print(
            f"Größe:       "
            f"{company.get('size', '-')}"
        )

        print(
            f"Ort:         "
            f"{company.get('location', '-')}"
        )

        print(
            f"Job-Typ:     "
            f"{company.get('job_type', '-')}"
        )

        print(
            f"Seniorität:  "
            f"{company.get('seniority', '-')}"
        )

        print(
            f"Arbeitsart:  "
            f"{company.get('employment_type', '-')}"
        )

        print(
            f"Remote:      "
            f"{company.get('remote_type', '-')}"
        )

        keywords = company.get(
            "keywords",
            [],
        )

        if isinstance(
            keywords,
            list,
        ):
            print(
                "Keywords:    "
                + ", ".join(
                    str(item)
                    for item in keywords
                )
            )

        print(
            "-" * 80
        )

    print()


# ============================================================
# DOCUMENT CHECK
# ============================================================

def check_documents_directory(
    documents_dir: Path,
) -> list[Path]:
    """
    Prüft den Bewerbungsordner.
    """

    if not documents_dir.exists():
        raise FileNotFoundError(
            "Dokumentenordner wurde nicht gefunden:\n"
            f"{documents_dir}"
        )

    if not documents_dir.is_dir():
        raise NotADirectoryError(
            "Der angegebene Dokumentenpfad "
            "ist kein Ordner:\n"
            f"{documents_dir}"
        )

    documents = collect_documents(
        documents_dir
    )

    if not documents:
        raise RuntimeError(
            "Der Dokumentenordner enthält "
            "keine Bewerbungsunterlagen:\n"
            f"{documents_dir}"
        )

    return documents


# ============================================================
# DOCUMENT LIST
# ============================================================

def print_documents(
    documents: list[Path],
    documents_dir: Path,
) -> None:
    """
    Gibt die gefundenen Dokumente aus.
    """

    print()

    print("DOKUMENTE")
    print("-" * 60)

    for document in documents:

        try:
            relative = document.relative_to(
                documents_dir
            )

        except ValueError:
            relative = document.name

        print(
            f"  • {relative}"
        )

    print("-" * 60)

    print(
        f"Anzahl: {len(documents)}"
    )

    print()


# ============================================================
# MATCH OUTPUT
# ============================================================

def print_match_result(
    company: dict[str, Any],
) -> None:
    """
    Zeigt das Matchergebnis an.
    """

    print()

    print("=" * 80)
    print("MATCHING")
    print("=" * 80)

    match_score = float(
        company.get(
            "match_score",
            0.0,
        )
    )

    confidence_score = float(
        company.get(
            "confidence_score",
            0.0,
        )
    )

    print(
        f"Match Score:       "
        f"{match_score:.1f}%"
    )

    print(
        f"Confidence Score:  "
        f"{confidence_score:.1f}%"
    )

    matched = company.get(
        "matched_keywords",
        [],
    )

    missing = company.get(
        "missing_keywords",
        [],
    )

    print()

    print(
        "Gematchte Kenntnisse:"
    )

    if matched:
        for keyword in matched:
            print(
                f"  ✓ {keyword}"
            )
    else:
        print(
            "  Keine"
        )

    print()

    print(
        "Fehlende Kenntnisse:"
    )

    if missing:
        for keyword in missing:
            print(
                f"  ✗ {keyword}"
            )
    else:
        print(
            "  Keine"
        )

    print()

    for field_name, label in [
        ("job_type", "Job-Typ"),
        ("seniority", "Seniorität"),
        ("employment_type", "Beschäftigung"),
        ("remote_type", "Arbeitsmodell"),
    ]:

        value = company.get(
            field_name
        )

        if value:
            print(
                f"{label}: "
                f"{value}"
            )

    print(
        "=" * 80
    )

    print()


# ============================================================
# COVER LETTER PREVIEW
# ============================================================

def print_letter_preview(
    letter: str,
) -> None:
    """
    Zeigt das generierte Anschreiben.
    """

    print()

    print("=" * 80)
    print("ANSCHREIBEN – VORSCHAU")
    print("=" * 80)

    print()

    print(letter)

    print()

    print("=" * 80)
    print()


# ============================================================
# APPLICATION SUMMARY
# ============================================================

def print_summary(
    build: ApplicationBuild,
) -> None:
    """
    Zeigt eine Zusammenfassung der erzeugten Bewerbung.
    """

    company = build.company
    applicant = build.applicant

    full_name = (
        f"{applicant.get('first_name', '')} "
        f"{applicant.get('last_name', '')}"
    ).strip()

    print()

    print("=" * 80)
    print("BEWERBUNG ERSTELLT")
    print("=" * 80)

    print(
        f"Bewerber:         {full_name}"
    )

    print(
        f"Unternehmen:      "
        f"{company.get('name', '-')}"
    )

    print(
        f"Position:         "
        f"{company.get('position', '-')}"
    )

    print(
        f"Empfänger:        "
        f"{company.get('email', '-')}"
    )

    print(
        f"Ort:              "
        f"{company.get('location', '-')}"
    )

    print(
        f"Template:         "
        f"{build.template_type}"
    )

    print(
        f"Style:             "
        f"{build.template_style}"
    )

    print(
        f"Sprache:          "
        f"{build.language}"
    )

    print(
        f"Match Score:      "
        f"{build.match_score:.1f}%"
    )

    print(
        f"Confidence:       "
        f"{build.confidence_score:.1f}%"
    )

    print()

    print(
        f"Dokumentenordner:"
    )

    print(
        f"  {build.documents_dir}"
    )

    print()

    print(
        f"Anschreiben:"
    )

    print(
        f"  {build.cover_letter}"
    )

    print()

    print(
        f"ZIP:"
    )

    print(
        f"  {build.zip_file}"
    )

    print()

    print(
        f"Dokumente:        "
        f"{len(build.documents)}"
    )

    print("=" * 80)

    print()


# ============================================================
# SEND CONFIRMATION
# ============================================================

def confirm_send(
    company: dict[str, Any],
    applicant: dict[str, Any],
    zip_file: Path,
) -> bool:
    """
    Fragt vor dem tatsächlichen Versand nach.
    """

    full_name = (
        f"{applicant.get('first_name', '')} "
        f"{applicant.get('last_name', '')}"
    ).strip()

    print()

    print("!" * 80)
    print("ACHTUNG: E-MAIL WIRD VERSENDET")
    print("!" * 80)

    print()

    print(
        f"Bewerber:    {full_name}"
    )

    print(
        f"Unternehmen: "
        f"{company.get('name', '-')}"
    )

    print(
        f"Position:    "
        f"{company.get('position', '-')}"
    )

    print(
        f"Empfänger:   "
        f"{company.get('email', '-')}"
    )

    print(
        f"Anhang:      "
        f"{zip_file}"
    )

    print()

    answer = input(
        "Bewerbung wirklich versenden? "
        "[y/N]: "
    )

    return answer.strip().casefold() in {
        "y",
        "yes",
        "j",
        "ja",
    }


# ============================================================
# BUILD APPLICATION
# ============================================================

def build_application(
    company: dict[str, Any],
    applicant: dict[str, Any],
    documents_dir: Path,
    *,
    template_type: str | None = None,
    template_style: str | None = None,
    language: str = "de",
    seed: int | None = None,
) -> ApplicationBuild:
    """
    Baut eine komplette Bewerbung.

    Workflow:

        documents
            ↓
        matching
            ↓
        generator
            ↓
        PDF
            ↓
        ZIP
    """

    # ========================================================
    # DOCUMENTS
    # ========================================================

    logger.info(
        "Prüfe Dokumentenordner..."
    )

    documents = check_documents_directory(
        documents_dir
    )

    logger.info(
        "%d Dokument(e) gefunden.",
        len(documents),
    )

    # ========================================================
    # MATCHING
    # ========================================================

    logger.info(
        "Analysiere Bewerber-/Stellen-Match..."
    )

    match_result = match_job(
        applicant=applicant,
        company=company,
    )

    company = apply_match_result(
        company,
        match_result,
    )

    # ========================================================
    # PRESERVE / VALIDATE EMAIL
    # ========================================================

    recipient = company.get("email")

    if not isinstance(recipient, str) or not recipient.strip():
        raise ValueError(
            "Nach dem Matching enthält die Company "
            "keine gültige Empfänger-E-Mail-Adresse."
        )

    company["email"] = recipient.strip()

    logger.info(
        "Match Score: %.1f%%",
        company.get(
            "match_score",
            0.0,
        ),
    )

    logger.info(
        "Confidence Score: %.1f%%",
        company.get(
            "confidence_score",
            0.0,
        ),
    )

    # ========================================================
    # GENERATOR
    # ========================================================

    logger.info(
        "Erstelle individuelles Anschreiben..."
    )

    generated = generate_application_text(
        company=company,
        template_type=template_type,
        template_style=template_style,
        language=language,
        seed=seed,
    )

    # ========================================================
    # COVER LETTER PDF
    # ========================================================

    company_name = (
        str(
            company.get(
                "name",
                "unternehmen",
            )
        )
        .strip()
        .replace(
            " ",
            "_",
        )
        .replace(
            "/",
            "_",
        )
    )

    cover_letter_path = (
        GENERATED_DIR
        / f"Anschreiben_{company_name}.pdf"
    )

    logger.info(
        "Erstelle Anschreiben-PDF..."
    )

    create_cover_letter_pdf(
        text=generated.text,
        output_path=cover_letter_path,
    )

    if not cover_letter_path.exists():
        raise RuntimeError(
            "Anschreiben-PDF wurde nicht erstellt:\n"
            f"{cover_letter_path}"
        )

    logger.info(
        "Anschreiben erstellt: %s",
        cover_letter_path,
    )

    # ========================================================
    # ZIP
    # ========================================================

    logger.info(
        "Erstelle Bewerbungs-ZIP..."
    )

    zip_file = create_zip(
        cover_letter=cover_letter_path,
        applicant=applicant,
        company=company,
        documents_dir=documents_dir,
    )

    if not zip_file.exists():
        raise RuntimeError(
            "Bewerbungs-ZIP wurde nicht erstellt:\n"
            f"{zip_file}"
        )

    logger.info(
        "ZIP erstellt: %s",
        zip_file,
    )

    # ========================================================
    # RESULT
    # ========================================================

    return ApplicationBuild(
        company=company,

        applicant=applicant,

        documents_dir=documents_dir,

        documents=documents,

        letter=generated.text,

        cover_letter=cover_letter_path,

        zip_file=zip_file,

        match_score=(
            generated.match_score
        ),

        confidence_score=(
            generated.confidence_score
        ),

        template_type=(
            generated.template_type
        ),

        template_style=(
            generated.template_style
        ),

        language=language,
    )


# ============================================================
# MATCH ONLY
# ============================================================

def run_match_only(
    company: dict[str, Any],
    applicant: dict[str, Any],
) -> int:
    """
    Führt ausschließlich das Matching durch.
    """

    logger.info(
        "Starte Matching-only-Modus..."
    )

    result = match_job(
        applicant=applicant,
        company=company,
    )

    enriched = apply_match_result(
        company,
        result,
    )

    print_match_result(
        enriched
    )

    return 0


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """
    Hauptprogramm.
    """

    parser = build_parser()

    args = parser.parse_args()

    # ========================================================
    # VERBOSE
    # ========================================================

    if args.verbose:

        logger.setLevel(
            logging.DEBUG
        )

        logger.debug(
            "Verbose-Modus aktiviert."
        )

    # ========================================================
    # HISTORY
    # ========================================================

    if args.history:

        try:
            print_history()
            return 0

        except Exception as exc:

            logger.exception(
                "Historie konnte "
                "nicht geladen werden: %s",
                exc,
            )

            return 1

    # ========================================================
    # LIST COMPANIES
    # ========================================================

    if args.list_companies:

        try:

            list_companies()

            return 0

        except Exception as exc:

            logger.exception(
                "Unternehmen konnten "
                "nicht geladen werden: %s",
                exc,
            )

            return 1

    # ========================================================
    # COMPANY / SEND-ALL REQUIRED
    # ========================================================

    if not args.company and not args.send_all:

        parser.error(
            "--company oder --send-all ist erforderlich, "
            "außer --list-companies oder "
            "--history wird verwendet."
        )

    # ========================================================
    # CONFLICT CHECKS
    # ========================================================

    if args.send_all and args.company:

        parser.error(
            "--send-all kann nicht zusammen "
            "mit --company verwendet werden."
        )

    if args.send_all and args.preview:

        parser.error(
            "--send-all kann nicht zusammen "
            "mit --preview verwendet werden."
        )

    if args.send_all and args.match_only:

        parser.error(
            "--send-all kann nicht zusammen "
            "mit --match-only verwendet werden."
        )


    # ========================================================
    # SEND-ALL
    # ========================================================

    if args.send_all:

        logger.info(
            "=" * 80
        )

        logger.info(
            "BEWERBUNGS-TOOL START"
        )

        logger.info(
            "=" * 80
        )

        try:

            # ====================================================
            # APPLICANT
            # ====================================================

            logger.info(
                "Lade Bewerberdaten..."
            )

            applicant = load_json(
                "applicant.json"
            )

            logger.info(
                "Bewerber: %s %s",
                applicant.get(
                    "first_name",
                    "",
                ),
                applicant.get(
                    "last_name",
                    "",
                ),
            )

            # ====================================================
            # DOCUMENTS
            # ====================================================

            documents_dir = (
                args.documents
                .expanduser()
                .resolve()
            )

            logger.info(
                "Dokumentenordner: %s",
                documents_dir,
            )

            # ====================================================
            # SEND ALL
            # ====================================================

            return run_send_all(
                applicant=applicant,
                documents_dir=documents_dir,
                template_type=args.template,
                template_style=args.style,
                language=args.language,
                seed=args.seed,
                dry_run=args.dry_run,
            )

        except FileNotFoundError as exc:

            logger.error(
                "Datei nicht gefunden: %s",
                exc,
            )

            return 1

        except NotADirectoryError as exc:

            logger.error(
                "Ungültiger Ordner: %s",
                exc,
            )

            return 1

        except PermissionError as exc:

            logger.error(
                "Keine Berechtigung: %s",
                exc,
            )

            return 1

        except ValueError as exc:

            logger.error(
                "Ungültige Konfiguration: %s",
                exc,
            )

            return 1

        except RuntimeError as exc:

            logger.error(
                "Fehler: %s",
                exc,
            )

            return 1

        except KeyboardInterrupt:

            logger.warning(
                "Programm vom Benutzer beendet."
            )

            return 130

        except Exception as exc:

            logger.exception(
                "Unerwarteter Fehler: %s",
                exc,
            )

            return 1



    # ========================================================
    # CONFLICT CHECKS
    # ========================================================

    if args.preview and args.send:

        parser.error(
            "--preview und --send "
            "können nicht gleichzeitig "
            "verwendet werden."
        )

    if args.match_only and args.send:

        parser.error(
            "--match-only und --send "
            "können nicht gleichzeitig "
            "verwendet werden."
        )

    if args.match_only and args.preview:

        parser.error(
            "--match-only und --preview "
            "können nicht gleichzeitig "
            "verwendet werden."
        )

    if args.yes and not args.send:

        parser.error(
            "--yes kann nur zusammen "
            "mit --send verwendet werden."
        )

    # ========================================================
    # START
    # ========================================================

    logger.info(
        "=" * 80
    )

    logger.info(
        "BEWERBUNGS-TOOL START"
    )

    logger.info(
        "=" * 80
    )

    try:

        # ====================================================
        # APPLICANT
        # ====================================================

        logger.info(
            "Lade Bewerberdaten..."
        )

        applicant = load_json(
            "applicant.json"
        )

        first_name = applicant.get(
            "first_name",
            "",
        )

        last_name = applicant.get(
            "last_name",
            "",
        )

        logger.info(
            "Bewerber: %s %s",
            first_name,
            last_name,
        )

        # ====================================================
        # COMPANY
        # ====================================================

        logger.info(
            "Lade Unternehmen: %s",
            args.company,
        )

        company = get_company(
            args.company
        )

        logger.info(
            "Unternehmen: %s",
            company.get(
                "name",
                "-",
            ),
        )

        logger.info(
            "Position: %s",
            company.get(
                "position",
                "-",
            ),
        )

        logger.info(
            "Empfänger: %s",
            company.get(
                "email",
                "-",
            ),
        )

        # ====================================================
        # MATCH ONLY
        # ====================================================

        if args.match_only:

            return run_match_only(
                company=company,
                applicant=applicant,
            )

        # ====================================================
        # DUPLICATE CHECK
        # ====================================================

        previous_application = (
            find_history_entry(
                company
            )
        )

        if previous_application:

            logger.warning(
                "Für diese Stelle existiert "
                "bereits ein History-Eintrag."
            )

            print()

            print("!" * 80)
            print(
                "WARNUNG: MÖGLICHE DOPPELTE BEWERBUNG"
            )
            print("!" * 80)

            print()

            print(
                f"Unternehmen: "
                f"{previous_application.get('company', '-')}"
            )

            print(
                f"Position:    "
                f"{previous_application.get('position', '-')}"
            )

            print(
                f"Status:      "
                f"{previous_application.get('status', '-')}"
            )

            print(
                f"Erstellt:    "
                f"{previous_application.get('created_at', '-')}"
            )

            if previous_application.get(
                "sent_at"
            ):
                print(
                    f"Gesendet:    "
                    f"{previous_application.get('sent_at')}"
                )

            print()

            if not args.force:

                if args.send:

                    print(
                        "Versand wird verhindert."
                    )

                    print(
                        "Nutze --force, "
                        "wenn du diese Bewerbung "
                        "bewusst erneut senden möchtest."
                    )

                    print()

                    return 1

                logger.info(
                    "Bestehender Eintrag gefunden. "
                    "Erstellung wird fortgesetzt."
                )

        # ====================================================
        # DOCUMENTS DIR
        # ====================================================

        documents_dir = (
            args.documents
            .expanduser()
            .resolve()
        )

        logger.info(
            "Dokumentenordner: %s",
            documents_dir,
        )

        # ====================================================
        # BUILD
        # ====================================================

        build = build_application(
            company=company,
            applicant=applicant,
            documents_dir=documents_dir,
            template_type=args.template,
            template_style=args.style,
            language=args.language,
            seed=args.seed,
        )

        # ====================================================
        # MATCH OUTPUT
        # ====================================================

        print_match_result(
            build.company
        )

        # ====================================================
        # SUMMARY
        # ========================================================

        print_summary(
            build
        )

        # ====================================================
        # DOCUMENTS
        # ========================================================

        print_documents(
            documents=build.documents,
            documents_dir=build.documents_dir,
        )

        # ====================================================
        # PREVIEW
        # ========================================================

        if args.preview:

            print_letter_preview(
                build.letter
            )

            add_history_entry(
                company=build.company,
                applicant=applicant,
                build=build,
                status="generated",
            )

            logger.info(
                "Preview beendet."
            )

            logger.info(
                "Keine E-Mail wurde versendet."
            )

            return 0

        # ====================================================
        # NO SEND
        # ========================================================

        if not args.send:

            print_letter_preview(
                build.letter
            )

            add_history_entry(
                company=build.company,
                applicant=applicant,
                build=build,
                status="generated",
            )

            logger.info(
                "Bewerbung erfolgreich erstellt."
            )

            logger.info(
                "Keine E-Mail wurde versendet."
            )

            logger.info(
                "Für Versand: --send"
            )

            return 0

        # ====================================================
        # DRY RUN
        # ====================================================

        if args.dry_run:

            logger.info(
                "DRY-RUN aktiviert."
            )

            print()

            print("=" * 80)
            print(
                "DRY-RUN – KEINE E-MAIL WIRD VERSENDET"
            )
            print("=" * 80)

            print()

            print(
                f"Empfänger: "
                f"{build.company.get('email', '-')}"
            )

            print(
                f"Betreff: "
                f"Bewerbung als "
                f"{build.company.get('position', '-')}"
            )

            print(
                f"Anhang: "
                f"{build.zip_file}"
            )

            print()

            print(
                "→ Keine JSON-Datei wird verändert."
            )

            print(
                "→ Keine E-Mail wurde versendet."
            )

            logger.info(
                "Dry-Run erfolgreich beendet."
            )

            return 0

        # ====================================================
        # CONFIRMATION
        # ====================================================

        if not args.yes:

            confirmed = confirm_send(
                company=build.company,
                applicant=applicant,
                zip_file=build.zip_file,
            )

            if not confirmed:

                logger.info(
                    "Versand vom Benutzer abgebrochen."
                )

                add_history_entry(
                    company=build.company,
                    applicant=applicant,
                    build=build,
                    status="cancelled",
                )

                return 0

        # ====================================================
        # SEND
        # ========================================================

        logger.info(
            "Versende Bewerbung..."
        )

        print(
            f"DEBUG recipient: "
            f"{build.company.get('email')!r}"
        )

        logger.info(
            "DEBUG recipient=%r",
            build.company.get("email"),
        )

        send_email(
            company=build.company,
            applicant=applicant,
            cover_letter=build.cover_letter,
            zip_file=build.zip_file,
            language=build.language,
        )

        # ====================================================
        # HISTORY
        # ====================================================

        add_history_entry(
            company=build.company,
            applicant=applicant,
            build=build,
            status="sent",
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        print()

        print("=" * 80)
        print(
            "BEWERBUNG ERFOLGREICH VERSENDET"
        )
        print("=" * 80)

        print()

        print(
            f"Unternehmen: "
            f"{build.company.get('name', '-')}"
        )

        print(
            f"Position:    "
            f"{build.company.get('position', '-')}"
        )

        print(
            f"Empfänger:   "
            f"{build.company.get('email', '-')}"
        )

        print(
            f"ZIP:         "
            f"{build.zip_file}"
        )

        print()

        logger.info(
            "Bewerbung erfolgreich versendet."
        )

        return 0

    # ========================================================
    # EXPECTED ERRORS
    # ========================================================

    except FileNotFoundError as exc:

        logger.error(
            "Datei nicht gefunden: %s",
            exc,
        )

        return 1

    except NotADirectoryError as exc:

        logger.error(
            "Ungültiger Ordner: %s",
            exc,
        )

        return 1

    except PermissionError as exc:

        logger.error(
            "Keine Berechtigung: %s",
            exc,
        )

        return 1

    except ValueError as exc:

        logger.error(
            "Ungültige Konfiguration: %s",
            exc,
        )

        return 1

    except RuntimeError as exc:

        logger.error(
            "Fehler: %s",
            exc,
        )

        return 1

    except KeyboardInterrupt:

        logger.warning(
            "Programm vom Benutzer beendet."
        )

        return 130

    # ========================================================
    # UNKNOWN ERROR
    # ========================================================

    except Exception as exc:

        logger.exception(
            "Unerwarteter Fehler: %s",
            exc,
        )

        return 1

    finally:

        logger.info(
            "Bewerbungs-Tool beendet."
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(
        main()
    )