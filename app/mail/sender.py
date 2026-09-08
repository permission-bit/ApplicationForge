from __future__ import annotations

import mimetypes
import smtplib

from html import escape
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
    Erstellt eine professionelle Bewerbungs-E-Mail
    mit Plain-Text- und HTML-Version.
    """

    language = validate_language(language)

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

    raw_recipient = company.get("email")

    if not isinstance(raw_recipient, str):
        raise ValueError(
            "Unternehmen enthält keine gültige "
            "Empfänger-E-Mail-Adresse."
        )

    recipient = raw_recipient.strip()

    # --------------------------------------------------------
    # Configuration validation
    # --------------------------------------------------------

    if not recipient or "@" not in recipient:
        raise ValueError(
            f"Ungültige Empfänger-E-Mail-Adresse: "
            f"{recipient!r}"
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
    # HTML-safe values
    # --------------------------------------------------------

    html_position = escape(
        position
    )

    html_company_name = escape(
        company_name
    )

    html_full_name = escape(
        full_name
    )

    html_applicant_email = escape(
        applicant_email
    )

    html_applicant_phone = escape(
        applicant_phone
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

    # ========================================================
    # PLAIN TEXT
    # ========================================================

    if language == "en":

        plain_text = f"""\
Dear Sir or Madam,

please find attached my application for the position of
{position} at {company_name}.

Attached you will find my complete application documents.

I would be pleased to have the opportunity to introduce
myself in a personal interview.

Kind regards,

{full_name}
{applicant_email}
{applicant_phone}
"""

    else:

        plain_text = f"""\
Sehr geehrte Damen und Herren,

anbei übersende ich Ihnen meine Bewerbung als
{position} bei {company_name}.

Im Anhang finden Sie meine vollständigen
Bewerbungsunterlagen.

Ich freue mich über die Möglichkeit eines
persönlichen Gesprächs.

Mit freundlichen Grüßen

{full_name}
{applicant_email}
{applicant_phone}
"""

    # ========================================================
    # HTML
    # ========================================================

    if language == "en":

        html_body = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">
    <title>Application</title>
</head>

<body style="
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
    font-family: Arial, Helvetica, sans-serif;
    color: #222222;
">

<table width="100%"
       cellpadding="0"
       cellspacing="0"
       border="0"
       style="background-color: #f5f5f5;">

    <tr>
        <td align="center"
            style="padding: 40px 20px;">

            <table width="600"
                   cellpadding="0"
                   cellspacing="0"
                   border="0"
                   style="
                       width: 100%;
                       max-width: 600px;
                       background-color: #ffffff;
                       border: 1px solid #e5e5e5;
                   ">

                <!-- Header -->

                <tr>
                    <td style="
                        padding: 32px 36px 24px 36px;
                        border-bottom: 1px solid #eeeeee;
                    ">

                        <div style="
                            font-size: 22px;
                            font-weight: bold;
                            color: #111111;
                        ">
                            {html_full_name}
                        </div>

                        <div style="
                            margin-top: 6px;
                            font-size: 14px;
                            color: #777777;
                        ">
                            Application for {html_position}
                        </div>

                    </td>
                </tr>

                <!-- Content -->

                <tr>
                    <td style="
                        padding: 32px 36px;
                        font-size: 15px;
                        line-height: 1.7;
                        color: #333333;
                    ">

                        <p style="margin: 0 0 22px 0;">
                            Dear Sir or Madam,
                        </p>

                        <p style="margin: 0 0 22px 0;">
                            please find attached my application
                            for the position of
                            <strong>{html_position}</strong>
                            at <strong>{html_company_name}</strong>.
                        </p>

                        <p style="margin: 0 0 22px 0;">
                            Attached you will find my complete
                            application documents.
                        </p>

                        <p style="margin: 0 0 28px 0;">
                            I would be pleased to have the
                            opportunity to introduce myself in
                            a personal interview.
                        </p>

                        <p style="
                            margin: 0;
                            line-height: 1.6;
                        ">
                            Kind regards,<br><br>

                            <strong>{html_full_name}</strong><br>

                            <span style="color: #777777;">
                                {html_applicant_email}
                            </span><br>

                            <span style="color: #777777;">
                                {html_applicant_phone}
                            </span>
                        </p>

                    </td>
                </tr>

                <!-- Footer -->

                <tr>
                    <td style="
                        padding: 18px 36px;
                        border-top: 1px solid #eeeeee;
                        font-size: 12px;
                        color: #999999;
                    ">
                        Application documents attached.
                    </td>
                </tr>

            </table>

        </td>
    </tr>

</table>

</body>
</html>
"""

    else:

        html_body = f"""\
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">
    <title>Bewerbung</title>
</head>

<body style="
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
    font-family: Arial, Helvetica, sans-serif;
    color: #222222;
">

<table width="100%"
       cellpadding="0"
       cellspacing="0"
       border="0"
       style="background-color: #f5f5f5;">

    <tr>
        <td align="center"
            style="padding: 40px 20px;">

            <table width="600"
                   cellpadding="0"
                   cellspacing="0"
                   border="0"
                   style="
                       width: 100%;
                       max-width: 600px;
                       background-color: #ffffff;
                       border: 1px solid #e5e5e5;
                   ">

                <!-- Header -->

                <tr>
                    <td style="
                        padding: 32px 36px 24px 36px;
                        border-bottom: 1px solid #eeeeee;
                    ">

                        <div style="
                            font-size: 22px;
                            font-weight: bold;
                            color: #111111;
                        ">
                            {html_full_name}
                        </div>

                        <div style="
                            margin-top: 6px;
                            font-size: 14px;
                            color: #777777;
                        ">
                            Bewerbung als {html_position}
                        </div>

                    </td>
                </tr>

                <!-- Content -->

                <tr>
                    <td style="
                        padding: 32px 36px;
                        font-size: 15px;
                        line-height: 1.7;
                        color: #333333;
                    ">

                        <p style="margin: 0 0 22px 0;">
                            Sehr geehrte Damen und Herren,
                        </p>

                        <p style="margin: 0 0 22px 0;">
                            anbei übersende ich Ihnen meine Bewerbung
                            als <strong>{html_position}</strong>
                            bei <strong>{html_company_name}</strong>.
                        </p>

                        <p style="margin: 0 0 22px 0;">
                            Im Anhang finden Sie meine vollständigen
                            Bewerbungsunterlagen.
                        </p>

                        <p style="margin: 0 0 28px 0;">
                            Ich freue mich über die Möglichkeit
                            eines persönlichen Gesprächs.
                        </p>

                        <p style="
                            margin: 0;
                            line-height: 1.6;
                        ">
                            Mit freundlichen Grüßen<br><br>

                            <strong>{html_full_name}</strong><br>

                            <span style="color: #777777;">
                                {html_applicant_email}
                            </span><br>

                            <span style="color: #777777;">
                                {html_applicant_phone}
                            </span>
                        </p>

                    </td>
                </tr>

                <!-- Footer -->

                <tr>
                    <td style="
                        padding: 18px 36px;
                        border-top: 1px solid #eeeeee;
                        font-size: 12px;
                        color: #999999;
                    ">
                        Bewerbungsunterlagen im Anhang.
                    </td>
                </tr>

            </table>

        </td>
    </tr>

</table>

</body>
</html>
"""

    # ========================================================
    # MULTIPART MESSAGE
    # ========================================================

    message.set_content(
        plain_text
    )

    message.add_alternative(
        html_body,
        subtype="html",
    )

    # ========================================================
    # ZIP PRÜFEN
    # ========================================================

    check_attachment_size(
        zip_file
    )

    # ========================================================
    # ZIP ANHÄNGEN
    # ========================================================

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