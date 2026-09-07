from __future__ import annotations

import mimetypes
import smtplib

from email.message import EmailMessage
from pathlib import Path

from config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_USE_TLS,
    MAIL_FROM,
    MAX_ATTACHMENT_SIZE_MB,
)


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_LANGUAGE = "de"

SUPPORTED_LANGUAGES = {
    "de",
    "en",
}


# ============================================================
# LANGUAGE
# ============================================================

def validate_language(
    language: str,
) -> str:
    """
    Validiert und normalisiert die Sprache.
    """

    language = str(
        language
    ).strip().casefold()

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Nicht unterstützte Sprache: "
            f"'{language}'. "
            f"Verfügbar: "
            f"{', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )

    return language


# ============================================================
# ATTACHMENT
# ============================================================

def attach_file(
    message: EmailMessage,
    file_path: Path,
) -> None:
    """
    Hängt eine Datei an eine E-Mail an.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Datei nicht gefunden: {file_path}"
        )

    content_type, _ = mimetypes.guess_type(
        file_path.name
    )

    if content_type is None:
        content_type = (
            "application/octet-stream"
        )

    maintype, subtype = (
        content_type.split(
            "/",
            1,
        )
    )

    with file_path.open(
        "rb"
    ) as file:

        message.add_attachment(
            file.read(),
            maintype=maintype,
            subtype=subtype,
            filename=file_path.name,
        )


# ============================================================
# ATTACHMENT SIZE
# ============================================================

def check_attachment_size(
    file_path: Path,
) -> None:
    """
    Prüft die maximale Größe des ZIP-Anhangs.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Datei nicht gefunden: {file_path}"
        )

    size_mb = (
        file_path.stat().st_size
        / 1024
        / 1024
    )

    if size_mb > MAX_ATTACHMENT_SIZE_MB:
        raise ValueError(
            f"ZIP ist {size_mb:.2f} MB groß. "
            f"Maximum: "
            f"{MAX_ATTACHMENT_SIZE_MB} MB."
        )


# ============================================================
# BUILD EMAIL
# ============================================================

def build_email(
    company: dict,
    applicant: dict,
    zip_file: Path,
    *,
    language: str = DEFAULT_LANGUAGE,
) -> EmailMessage:
    """
    Erstellt die Bewerbungs-E-Mail.

    Unterstützte Sprachen:

        de
        en
    """

    language = validate_language(
        language
    )

    message = EmailMessage()

    position = str(
        company.get(
            "position",
            "",
        )
    ).strip()

    company_name = str(
        company.get(
            "name",
            "",
        )
    ).strip()

    full_name = (
        f"{applicant.get('first_name', '')} "
        f"{applicant.get('last_name', '')}"
    ).strip()

    applicant_email = str(
        applicant.get(
            "email",
            "",
        )
    ).strip()

    applicant_phone = str(
        applicant.get(
            "phone",
            "",
        )
    ).strip()

    recipient = str(
        company.get(
            "email",
            "",
        )
    ).strip()

    # --------------------------------------------------------
    # Configuration validation
    # --------------------------------------------------------

    if not recipient:
        raise ValueError(
            "Unternehmen enthält keine "
            "Empfänger-E-Mail-Adresse."
        )

    if not position:
        raise ValueError(
            "Unternehmen enthält keine "
            "Positionsbezeichnung."
        )

    if not full_name:
        raise ValueError(
            "Bewerber enthält keinen Namen."
        )

    # --------------------------------------------------------
    # Headers
    # --------------------------------------------------------

    message["From"] = MAIL_FROM

    message["To"] = recipient

    if language == "en":

        message["Subject"] = (
            f"Application for {position} – "
            f"{full_name}"
        )

    else:

        message["Subject"] = (
            f"Bewerbung als {position} – "
            f"{full_name}"
        )

    # --------------------------------------------------------
    # Mail body
    # --------------------------------------------------------

    if language == "en":

        message_body = f"""\
Dear Sir or Madam,

please find attached my application
for the position of {position} at {company_name}.

Attached you will find my complete
application documents.

I would be pleased to have the opportunity
to introduce myself in a personal interview.

Kind regards,

{full_name}
{applicant_email}
{applicant_phone}
"""

    else:

        message_body = f"""\
Sehr geehrte Damen und Herren,

anbei übersende ich Ihnen meine Bewerbung
als {position} bei {company_name}.

Im Anhang finden Sie meine vollständigen
Bewerbungsunterlagen.

Ich freue mich über die Möglichkeit eines
persönlichen Gesprächs.

Mit freundlichen Grüßen

{full_name}
{applicant_email}
{applicant_phone}
"""

    message.set_content(
        message_body
    )

    # --------------------------------------------------------
    # ZIP prüfen
    # --------------------------------------------------------

    check_attachment_size(
        zip_file
    )

    # --------------------------------------------------------
    # ZIP anhängen
    # --------------------------------------------------------

    attach_file(
        message,
        zip_file,
    )

    return message


# ============================================================
# SEND EMAIL
# ============================================================

def send_email(
    company: dict,
    applicant: dict,
    cover_letter: Path,
    zip_file: Path,
    *,
    language: str = DEFAULT_LANGUAGE,
) -> None:
    """
    Versendet die Bewerbungs-E-Mail.

    language:
        de = Deutsch
        en = Englisch

    cover_letter wird als Parameter weiterhin
    akzeptiert, damit die bestehende API
    kompatibel bleibt.
    """

    language = validate_language(
        language
    )

    # --------------------------------------------------------
    # Configuration checks
    # --------------------------------------------------------

    if not SMTP_HOST:
        raise RuntimeError(
            "SMTP_HOST ist nicht konfiguriert."
        )

    if not SMTP_USERNAME:
        raise RuntimeError(
            "SMTP_USERNAME ist nicht konfiguriert."
        )

    if not SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP_PASSWORD ist nicht gesetzt."
        )

    if not MAIL_FROM:
        raise RuntimeError(
            "MAIL_FROM ist nicht konfiguriert."
        )

    # --------------------------------------------------------
    # Build message
    # --------------------------------------------------------

    message = build_email(
        company=company,
        applicant=applicant,
        zip_file=zip_file,
        language=language,
    )

    # --------------------------------------------------------
    # SMTP connection
    # --------------------------------------------------------

    if SMTP_PORT == 465:

        # ----------------------------------------------------
        # SMTP over SSL
        # ----------------------------------------------------

        with smtplib.SMTP_SSL(
            SMTP_HOST,
            SMTP_PORT,
            timeout=30,
        ) as server:

            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD,
            )

            server.send_message(
                message
            )

    else:

        # ----------------------------------------------------
        # STARTTLS
        # ----------------------------------------------------

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=30,
        ) as server:

            server.ehlo()

            if SMTP_USE_TLS:

                server.starttls()

                server.ehlo()

            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD,
            )

            server.send_message(
                message
            )