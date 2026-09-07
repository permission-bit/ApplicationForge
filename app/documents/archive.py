from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil

from config import (
    GENERATED_DIR,
    DOCUMENTS_DIR,
    ZIP_PREFIX,
)

from app.documents.converter import convert_docx_to_pdf


# ============================================================
# IGNORED FILES
# ============================================================

IGNORED_NAMES = {
    ".DS_Store",
    "Thumbs.db",
}


# ============================================================
# DOCUMENTS
# ============================================================

def collect_documents(
    documents_dir: Path,
) -> list[Path]:

    documents = []

    for file in documents_dir.rglob("*"):

        if not file.is_file():
            continue

        if file.name in IGNORED_NAMES:
            continue

        if file.name.startswith("~$"):
            continue

        documents.append(file)

    return sorted(documents)


def copy_documents(
    source_dir: Path,
    destination_dir: Path,
) -> None:

    for source in source_dir.rglob("*"):

        if not source.is_file():
            continue

        if source.name in IGNORED_NAMES:
            continue

        if source.name.startswith("~$"):
            continue

        relative = source.relative_to(
            source_dir
        )

        # DOCX-Lebenslauf nicht direkt übernehmen.
        if source.name.lower() in {
            "lebenslauf.docx",
            "cv.docx",
        }:
            continue

        destination = (
            destination_dir / relative
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            source,
            destination,
        )


# ============================================================
# CV
# ============================================================

def find_cv(
    documents_dir: Path,
) -> Path | None:

    possible_names = {
        "lebenslauf.docx",
        "cv.docx",
    }

    for file in documents_dir.rglob("*"):

        if not file.is_file():
            continue

        if file.name.lower() in possible_names:
            return file

    return None


# ============================================================
# ZIP
# ============================================================

def create_zip(
    cover_letter: Path,
    applicant: dict,
    company: dict,
    documents_dir: Path | None = None,
) -> Path:

    if documents_dir is None:
        documents_dir = DOCUMENTS_DIR

    if not documents_dir.exists():
        raise FileNotFoundError(
            f"Documents-Ordner nicht gefunden: "
            f"{documents_dir}"
        )

    # --------------------------------------------------------
    # Bewerbungsname
    # --------------------------------------------------------

    applicant_name = sanitize_filename(
        f"{applicant['first_name']}_"
        f"{applicant['last_name']}"
    )

    company_name = sanitize_filename(
        company["name"]
    )

    application_name = (
        f"{ZIP_PREFIX}_"
        f"{applicant_name}_"
        f"{company_name}"
    )

    # --------------------------------------------------------
    # Build directory
    # --------------------------------------------------------

    build_dir = (
        GENERATED_DIR
        / "build"
        / application_name
    )

    if build_dir.exists():
        shutil.rmtree(build_dir)

    build_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Anschreiben
    # --------------------------------------------------------

    shutil.copy2(
        cover_letter,
        build_dir / "Anschreiben.pdf",
    )

    # --------------------------------------------------------
    # Alle Dokumente kopieren
    # --------------------------------------------------------

    copy_documents(
        source_dir=documents_dir,
        destination_dir=build_dir,
    )

    # --------------------------------------------------------
    # Lebenslauf DOCX -> PDF
    # --------------------------------------------------------

    cv = find_cv(
        documents_dir
    )

    if cv:

        cv_pdf = convert_docx_to_pdf(
            source=cv,
            output_dir=build_dir,
        )

        final_cv = (
            build_dir
            / "Lebenslauf.pdf"
        )

        if cv_pdf != final_cv:
            cv_pdf.rename(final_cv)

    # --------------------------------------------------------
    # ZIP erstellen
    # --------------------------------------------------------

    zip_path = (
        GENERATED_DIR
        / f"{application_name}.zip"
    )

    if zip_path.exists():
        zip_path.unlink()

    with ZipFile(
        zip_path,
        "w",
        ZIP_DEFLATED,
    ) as archive:

        for file in build_dir.rglob("*"):

            if not file.is_file():
                continue

            relative = file.relative_to(
                build_dir
            )

            archive.write(
                file,
                arcname=str(relative),
            )

    return zip_path


# ============================================================
# FILENAME
# ============================================================

def sanitize_filename(
    value: str,
) -> str:

    forbidden = '<>:"/\\|?*'

    for char in forbidden:
        value = value.replace(
            char,
            "_",
        )

    return value.strip()