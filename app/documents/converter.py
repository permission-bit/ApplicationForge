from pathlib import Path
import shutil
import subprocess


def find_libreoffice() -> Path | None:
    """
    Sucht LibreOffice auf macOS, Linux und Windows.
    """

    # PATH
    executable = shutil.which("soffice")
    if executable:
        return Path(executable)

    executable = shutil.which("libreoffice")
    if executable:
        return Path(executable)

    # macOS
    mac_path = Path(
        "/Applications/LibreOffice.app/"
        "Contents/MacOS/soffice"
    )

    if mac_path.exists():
        return mac_path

    # Windows
    windows_paths = [
        Path(
            r"C:\Program Files\LibreOffice\program\soffice.exe"
        ),
        Path(
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
        ),
    ]

    for path in windows_paths:
        if path.exists():
            return path

    return None


def convert_docx_to_pdf(
    source: Path,
    output_dir: Path,
) -> Path:

    if not source.exists():
        raise FileNotFoundError(
            f"DOCX nicht gefunden: {source}"
        )

    if source.suffix.lower() != ".docx":
        raise ValueError(
            f"Keine DOCX-Datei: {source}"
        )

    soffice = find_libreoffice()

    if soffice is None:
        raise RuntimeError(
            "LibreOffice wurde nicht gefunden. "
            "Bitte LibreOffice installieren."
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        str(soffice),
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(source),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "DOCX konnte nicht in PDF "
            f"konvertiert werden:\n"
            f"{result.stderr}"
        )

    pdf_path = (
        output_dir /
        f"{source.stem}.pdf"
    )

    if not pdf_path.exists():
        raise RuntimeError(
            "LibreOffice meldete Erfolg, "
            "aber die PDF-Datei wurde nicht gefunden."
        )

    return pdf_path


def create_cover_letter_pdf(
    text: str,
    output_path: Path,
) -> Path:

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pdf = canvas.Canvas(
        str(output_path),
        pagesize=A4,
    )

    width, height = A4

    x = 70
    y = height - 70

    font = "Helvetica"
    font_size = 11
    line_height = 16

    pdf.setFont(
        font,
        font_size,
    )

    for paragraph in text.split("\n"):

        if not paragraph.strip():
            y -= line_height
            continue

        words = paragraph.split()
        line = ""

        for word in words:

            test = (
                f"{line} {word}"
                if line
                else word
            )

            if pdf.stringWidth(
                test,
                font,
                font_size,
            ) > width - 140:

                pdf.drawString(
                    x,
                    y,
                    line,
                )

                y -= line_height
                line = word

            else:
                line = test

        if line:
            pdf.drawString(
                x,
                y,
                line,
            )

            y -= line_height

        if y < 70:
            pdf.showPage()
            pdf.setFont(
                font,
                font_size,
            )
            y = height - 70

    pdf.save()

    return output_path