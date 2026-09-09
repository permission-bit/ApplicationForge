from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from config import DATA_DIR


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_LANGUAGE = "de"

SUPPORTED_LANGUAGES = {
    "de",
    "en",
}

DEFAULT_TEMPLATE_STYLE = "formal"

DEFAULT_SECTION_ORDER = [
    "subject",
    "salutation",
    "opening",
    "background",
    "technical_approach",
    "experience",
    "job_connection",
    "motivation",
    "closing",
]

SUPPORTED_PLACEHOLDERS = {
    # Company
    "company_name",
    "company_type",
    "company_size",
    "company_id",
    "relevant_keywords",

    # Job
    "position",
    "location",
    "job_id",
    "job_type",
    "seniority",
    "employment_type",
    "remote_type",
    "source_url",

    # Applicant
    "first_name",
    "last_name",
    "full_name",
    "email",
    "phone",
    "address",
    "zip_code",
    "city",
    "github",

    # Keywords
    "applicant_keywords",
    "job_keywords",
    "matched_keywords",
    "missing_keywords",

    # Matching
    "match_score",
    "confidence_score",

    # Experience
    "experience",
}


# Fallback values used when the job/company data does not
# provide enough relevant technical keywords.
DEFAULT_APPLICATION_SKILLS = {
    "de": [
        "Python",
        "Linux",
        "IT-Sicherheit",
    ],
    "en": [
        "Python",
        "Linux",
        "Cyber Security",
    ],
}


# These files live in data/ or may accidentally be placed
# inside a language directory, but they are not templates.
IGNORED_TEMPLATE_FILES = {
    "applicant.json",
    "companies.json",
    "history.json",
    "templates.json",
}


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class JobContext:
    """
    Contains all relevant information about the advertised job.
    """

    company_name: str
    position: str

    company_id: str = ""
    company_type: str = ""
    company_size: str = ""

    location: str = ""
    job_id: str = ""
    job_type: str = ""
    seniority: str = ""
    employment_type: str = ""
    remote_type: str = ""

    job_keywords: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    relevant_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)

    experience: list[str] = field(default_factory=list)

    source_url: str = ""

    match_score: float = 0.0
    confidence_score: float = 0.0


@dataclass
class ApplicantContext:
    """
    Contains applicant information.
    """

    first_name: str
    last_name: str

    email: str = ""
    phone: str = ""

    address: str = ""
    zip_code: str = ""
    city: str = ""

    github: str = ""

    skills: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)


@dataclass
class GeneratedApplication:
    """
    Result of a fully generated application.
    """

    text: str

    company_name: str
    position: str

    template_type: str
    template_style: str
    language: str

    matched_keywords: list[str]
    missing_keywords: list[str]

    variables: dict[str, str]

    sections: dict[str, str] = field(default_factory=dict)

    match_score: float = 0.0
    confidence_score: float = 0.0

    company_id: str = ""
    job_id: str = ""
    source_url: str = ""


# ============================================================
# TEXT HELPERS
# ============================================================

def clean_text(value: Any) -> str:
    """
    Normalize arbitrary values into clean text.
    """

    if value is None:
        return ""

    text = str(value)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Collapse spaces and tabs.
    text = re.sub(r"[ \t]+", " ", text)

    # Maximum two consecutive newlines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_single_line(value: Any) -> str:
    """
    Normalize a value and remove line breaks.
    """

    text = clean_text(value)

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def unique_strings(values: list[Any]) -> list[str]:
    """
    Remove duplicate strings while preserving order.
    """

    result: list[str] = []
    seen: set[str] = set()

    for value in values:
        text = clean_text(value)

        if not text:
            continue

        normalized = text.casefold()

        if normalized in seen:
            continue

        seen.add(normalized)
        result.append(text)

    return result


def ensure_string_list(
    value: Any,
    field_name: str,
) -> list[str]:
    """
    Validate and normalize a list of strings.
    """

    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(
            f"'{field_name}' muss eine Liste sein."
        )

    return unique_strings(value)


def format_list(
    values: list[str],
    language: str = DEFAULT_LANGUAGE,
) -> str:
    """
    Format a list naturally according to the language.
    """

    language = normalize_language(language)
    values = unique_strings(values)

    if not values:
        return ""

    if len(values) == 1:
        return values[0]

    conjunction = "and" if language == "en" else "und"

    if len(values) == 2:
        return f"{values[0]} {conjunction} {values[1]}"

    return ", ".join(values[:-1]) + f" {conjunction} " + values[-1]


def format_keywords(
    keywords: list[str],
    language: str = DEFAULT_LANGUAGE,
) -> str:
    """
    Format keywords.
    """

    return format_list(
        keywords,
        language=language,
    )


def format_score(value: Any) -> str:
    """
    Format a score as percentage.
    """

    try:
        score = float(value)
    except (TypeError, ValueError):
        score = 0.0

    score = max(0.0, min(100.0, score))

    return f"{score:.1f} %"


# ============================================================
# JSON
# ============================================================

def load_json(filename: str) -> dict[str, Any]:
    """
    Load a JSON file from data/.
    """

    filename = clean_single_line(filename)

    if not filename:
        raise ValueError("Kein JSON-Dateiname angegeben.")

    path = (DATA_DIR / filename).resolve()
    data_root = DATA_DIR.resolve()

    try:
        path.relative_to(data_root)
    except ValueError as exc:
        raise ValueError(
            f"Ungültiger JSON-Pfad: {filename}"
        ) from exc

    if not path.exists():
        raise FileNotFoundError(
            f"JSON-Datei nicht gefunden: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Pfad ist keine Datei: {path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ungültiges JSON in {path}: "
            f"Zeile {exc.lineno}, "
            f"Spalte {exc.colno}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"{path} muss ein JSON-Objekt enthalten."
        )

    return data


# ============================================================
# COMPANY
# ============================================================

def get_company(company_id: str) -> dict[str, Any]:
    """
    Find a company by ID.
    """

    company_id = clean_single_line(company_id)

    if not company_id:
        raise ValueError(
            "Keine Company-ID angegeben."
        )

    data = load_json("companies.json")

    companies = data.get("companies", [])

    if not isinstance(companies, list):
        raise ValueError(
            "companies.json: "
            "'companies' muss eine Liste sein."
        )

    for company in companies:
        if not isinstance(company, dict):
            continue

        current_id = clean_single_line(
            company.get("id")
        )

        if current_id == company_id:
            return company

    raise ValueError(
        f"Unternehmen '{company_id}' nicht gefunden."
    )


# ============================================================
# APPLICANT CONTEXT
# ============================================================

def build_applicant_context(
    applicant: dict[str, Any],
) -> ApplicantContext:
    """
    Build a validated ApplicantContext.
    """

    if not isinstance(applicant, dict):
        raise ValueError(
            "Applicant-Daten müssen ein Objekt sein."
        )

    first_name = clean_single_line(
        applicant.get("first_name")
    )

    last_name = clean_single_line(
        applicant.get("last_name")
    )

    if not first_name:
        raise ValueError(
            "applicant.json: 'first_name' fehlt."
        )

    if not last_name:
        raise ValueError(
            "applicant.json: 'last_name' fehlt."
        )

    skills = ensure_string_list(
        applicant.get("skills", []),
        "skills",
    )

    experience = ensure_string_list(
        applicant.get("experience", []),
        "experience",
    )

    return ApplicantContext(
        first_name=first_name,
        last_name=last_name,

        email=clean_single_line(
            applicant.get("email")
        ),

        phone=clean_single_line(
            applicant.get("phone")
        ),

        address=clean_single_line(
            applicant.get("address")
        ),

        zip_code=clean_single_line(
            applicant.get("zip_code")
        ),

        city=clean_single_line(
            applicant.get("city")
        ),

        github=clean_single_line(
            applicant.get("github")
        ),

        skills=skills,
        experience=experience,
    )


# ============================================================
# JOB CONTEXT
# ============================================================

def _read_score(value: Any) -> float:
    """
    Read and normalize a numeric score.
    """

    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    return max(
        0.0,
        min(100.0, score),
    )


def build_job_context(
    company: dict[str, Any],
) -> JobContext:
    """
    Build a validated JobContext from a company/job record.
    """

    if not isinstance(company, dict):
        raise ValueError(
            "Unternehmensdaten müssen ein Objekt sein."
        )

    company_name = clean_single_line(
        company.get("name")
    )

    position = clean_single_line(
        company.get("position")
    )

    if not company_name:
        raise ValueError(
            "Unternehmen besitzt keinen Namen."
        )

    if not position:
        raise ValueError(
            "Unternehmen besitzt keine Position."
        )

    job_keywords = ensure_string_list(
        company.get("keywords", []),
        "keywords",
    )

    matched_keywords = ensure_string_list(
        company.get("matched_keywords", []),
        "matched_keywords",
    )

    relevant_keywords = ensure_string_list(
        company.get("relevant_keywords", []),
        "relevant_keywords",
    )

    missing_keywords = ensure_string_list(
        company.get("missing_keywords", []),
        "missing_keywords",
    )

    experience = ensure_string_list(
        company.get("experience", []),
        "experience",
    )

    return JobContext(
        company_name=company_name,
        position=position,

        company_id=clean_single_line(
            company.get("id")
        ),

        company_type=clean_single_line(
            company.get("type")
        ),

        company_size=clean_single_line(
            company.get("size")
        ),

        location=clean_single_line(
            company.get("location")
        ),

        job_id=clean_single_line(
            company.get("job_id")
        ),

        job_type=clean_single_line(
            company.get("job_type")
        ),

        seniority=clean_single_line(
            company.get("seniority")
        ),

        employment_type=clean_single_line(
            company.get("employment_type")
        ),

        remote_type=clean_single_line(
            company.get("remote_type")
        ),

        job_keywords=job_keywords,
        matched_keywords=matched_keywords,
        relevant_keywords=relevant_keywords,
        missing_keywords=missing_keywords,
        experience=experience,

        source_url=clean_single_line(
            company.get("source_url")
        ),

        match_score=_read_score(
            company.get("match_score")
        ),

        confidence_score=_read_score(
            company.get("confidence_score")
        ),
    )


# ============================================================
# VARIABLES
# ============================================================

def build_variables(
    applicant: ApplicantContext,
    job: JobContext,
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, str]:
    """
    Build all available template variables.

    Keyword fallback hierarchy:

        1. relevant_keywords
        2. matched_keywords
        3. applicant skills
        4. Python + Linux + Cyber Security / IT-Sicherheit
    """

    language = normalize_language(language)

    full_name = (
        f"{applicant.first_name} "
        f"{applicant.last_name}"
    )

    # --------------------------------------------------------
    # Default technical skills
    # --------------------------------------------------------

    default_skills = DEFAULT_APPLICATION_SKILLS.get(
        language,
        DEFAULT_APPLICATION_SKILLS["de"],
    )

    # --------------------------------------------------------
    # Matched keywords
    # --------------------------------------------------------

    matched_keywords = unique_strings(
        job.matched_keywords
    )

    # --------------------------------------------------------
    # Relevant keywords
    #
    # IMPORTANT:
    # If relevant_keywords are missing, matched_keywords
    # become the fallback.
    # --------------------------------------------------------

    relevant_keywords = unique_strings(
        job.relevant_keywords
    )

    if relevant_keywords:
        application_relevant_keywords = (
            relevant_keywords
        )
    elif matched_keywords:
        application_relevant_keywords = (
            matched_keywords
        )
    elif applicant.skills:
        application_relevant_keywords = (
            unique_strings(applicant.skills)
        )
    else:
        application_relevant_keywords = (
            default_skills
        )

    # --------------------------------------------------------
    # Experience fallback
    #
    # Keep the old behavior compatible:
    # matched keywords -> fallback technical skills.
    # --------------------------------------------------------

    if matched_keywords:
        application_experience = matched_keywords
    elif applicant.experience:
        application_experience = (
            unique_strings(applicant.experience)
        )
    else:
        application_experience = default_skills

    return {
        # ----------------------------------------------------
        # Company
        # ----------------------------------------------------

        "company_name": job.company_name,
        "company_type": job.company_type,
        "company_size": job.company_size,
        "company_id": job.company_id,

        # ----------------------------------------------------
        # Job
        # ----------------------------------------------------

        "position": job.position,
        "location": job.location,
        "job_id": job.job_id,
        "job_type": job.job_type,
        "seniority": job.seniority,
        "employment_type": job.employment_type,
        "remote_type": job.remote_type,
        "source_url": job.source_url,

        # ----------------------------------------------------
        # Applicant
        # ----------------------------------------------------

        "first_name": applicant.first_name,
        "last_name": applicant.last_name,
        "full_name": full_name,

        "email": applicant.email,
        "phone": applicant.phone,

        "address": applicant.address,
        "zip_code": applicant.zip_code,
        "city": applicant.city,

        "github": applicant.github,

        # ----------------------------------------------------
        # Keywords
        # ----------------------------------------------------

        "applicant_keywords": format_list(
            applicant.skills,
            language=language,
        ),

        "job_keywords": format_list(
            job.job_keywords,
            language=language,
        ),

        "matched_keywords": format_list(
            matched_keywords,
            language=language,
        ),

        "relevant_keywords": format_list(
            application_relevant_keywords,
            language=language,
        ),

        "missing_keywords": format_list(
            job.missing_keywords,
            language=language,
        ),

        "experience": format_list(
            application_experience,
            language=language,
        ),

        # ----------------------------------------------------
        # Matching
        # ----------------------------------------------------

        "match_score": format_score(
            job.match_score
        ),

        "confidence_score": format_score(
            job.confidence_score
        ),
    }


# ============================================================
# PLACEHOLDER HANDLING
# ============================================================

PLACEHOLDER_PATTERN = re.compile(
    r"{([a-zA-Z_][a-zA-Z0-9_]*)}"
)


def find_placeholders(
    text: str,
) -> list[str]:
    """
    Find all placeholders in a template string.
    """

    if not text:
        return []

    return list(
        dict.fromkeys(
            PLACEHOLDER_PATTERN.findall(text)
        )
    )


def validate_placeholders(
    text: str,
    variables: dict[str, str],
) -> None:
    """
    Validate placeholders against the supported variables.
    """

    placeholders = find_placeholders(text)

    for placeholder in placeholders:

        if placeholder not in SUPPORTED_PLACEHOLDERS:
            raise ValueError(
                "Unbekannter "
                f"Template-Platzhalter: "
                f"{{{placeholder}}}"
            )

        if placeholder not in variables:
            raise ValueError(
                "Keine Variable für "
                f"{{{placeholder}}} vorhanden."
            )


def render_text(
    text: str,
    variables: dict[str, str],
) -> str:
    """
    Render one template text.
    """

    text = clean_text(text)

    if not text:
        return ""

    validate_placeholders(
        text,
        variables,
    )

    try:
        rendered = text.format(
            **variables
        )
    except (
        KeyError,
        ValueError,
        IndexError,
    ) as exc:
        raise ValueError(
            "Template konnte nicht "
            f"gerendert werden: {exc}"
        ) from exc

    return clean_text(rendered)


# ============================================================
# LANGUAGE
# ============================================================

def normalize_language(
    language: str,
) -> str:
    """
    Normalize and validate a language.
    """

    language = clean_single_line(
        language
    ).casefold()

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Nicht unterstützte Sprache: "
            f"'{language}'. "
            f"Verfügbar: "
            f"{', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )

    return language


# ============================================================
# TEMPLATE DIRECTORY
# ============================================================

def get_template_directory(
    language: str = DEFAULT_LANGUAGE,
) -> Path:
    """
    Return the language-specific template directory.

    Example:

        data/de/
        data/en/
    """

    language = normalize_language(language)

    directory = DATA_DIR / language

    if not directory.exists():
        raise FileNotFoundError(
            "Template-Verzeichnis nicht gefunden: "
            f"{directory}"
        )

    if not directory.is_dir():
        raise ValueError(
            "Template-Pfad ist kein Verzeichnis: "
            f"{directory}"
        )

    return directory


# ============================================================
# TEMPLATE FILE DISCOVERY
# ============================================================

def get_available_template_types(
    language: str = DEFAULT_LANGUAGE,
) -> list[str]:
    """
    Automatically discover all template types.

    Example:

        data/en/cybersecurity.json
        data/en/it.json
        data/en/software.json

    becomes:

        [
            "cybersecurity",
            "it",
            "software",
        ]
    """

    directory = get_template_directory(language)

    template_types: list[str] = []

    for path in directory.glob("*.json"):

        if not path.is_file():
            continue

        if path.name.casefold() in IGNORED_TEMPLATE_FILES:
            continue

        filename = path.stem

        if not re.fullmatch(
            r"[a-zA-Z0-9_-]+",
            filename,
        ):
            continue

        template_types.append(
            filename.casefold()
        )

    return sorted(
        set(template_types)
    )


def get_template_path(
    template_type: str,
    language: str = DEFAULT_LANGUAGE,
) -> Path:
    """
    Resolve a template file path safely.
    """

    template_type = clean_single_line(
        template_type
    ).casefold()

    if not template_type:
        raise ValueError(
            "Kein Template-Typ angegeben."
        )

    if not re.fullmatch(
        r"[a-zA-Z0-9_-]+",
        template_type,
    ):
        raise ValueError(
            f"Ungültiger Template-Typ: "
            f"'{template_type}'"
        )

    directory = get_template_directory(
        language
    )

    directory_resolved = directory.resolve()
    path = (
        directory_resolved
        / f"{template_type}.json"
    ).resolve()

    # Additional protection against path traversal.
    try:
        path.relative_to(
            directory_resolved
        )
    except ValueError as exc:
        raise ValueError(
            f"Ungültiger Template-Pfad: {path}"
        ) from exc

    return path


# ============================================================
# TEMPLATE ROOT HANDLING
# ============================================================

def _looks_like_direct_style_map(
    template: dict[str, Any],
) -> bool:
    """
    Determine whether a template is already in direct
    style-map form:

        {
            "formal": {...},
            "modern": {...}
        }

    This prevents accidentally interpreting:

        {
            "cybersecurity": {
                "formal": {...}
            }
        }

    as a style map.
    """

    if not template:
        return False

    values = list(template.values())

    if not values:
        return False

    for value in values:

        if not isinstance(value, dict):
            return False

        # A style normally contains "order" or at least one
        # known section.
        if (
            "order" not in value
            and not any(
                section in value
                for section in DEFAULT_SECTION_ORDER
            )
        ):
            return False

    return True


def unwrap_template(
    template_type: str,
    template: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize supported template structures.

    Supported:

        {
            "cybersecurity": {
                "formal": {...},
                "modern": {...}
            }
        }

    and:

        {
            "formal": {...},
            "modern": {...}
        }
    """

    if not isinstance(template, dict):
        raise ValueError(
            f"Template '{template_type}' "
            "muss ein Objekt sein."
        )

    normalized_type = clean_single_line(
        template_type
    ).casefold()

    # --------------------------------------------------------
    # 1. Wrapped structure
    # --------------------------------------------------------

    matching_root: str | None = None

    for key in template.keys():

        if not isinstance(key, str):
            continue

        if key.casefold() == normalized_type:
            matching_root = key
            break

    if matching_root is not None:

        root = template[matching_root]

        if not isinstance(root, dict):
            raise ValueError(
                f"Template '{template_type}': "
                f"oberster Schlüssel "
                f"'{matching_root}' "
                "muss ein Objekt sein."
            )

        return root

    # --------------------------------------------------------
    # 2. Direct style structure
    # --------------------------------------------------------

    if _looks_like_direct_style_map(template):
        return template

    raise ValueError(
        f"Template-Datei für Typ "
        f"'{template_type}' besitzt keine "
        f"passende oberste Ebene "
        f"'{template_type}' und keine "
        "gültige direkte Style-Struktur."
    )


# ============================================================
# TEMPLATE LOADING
# ============================================================

def load_template(
    template_type: str,
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    """
    Load exactly one template file.
    """

    language = normalize_language(language)

    template_type = clean_single_line(
        template_type
    ).casefold()

    path = get_template_path(
        template_type,
        language,
    )

    if not path.exists():

        available = get_available_template_types(
            language
        )

        available_text = (
            ", ".join(available)
            if available
            else "keine"
        )

        raise FileNotFoundError(
            f"Template-Datei nicht gefunden: "
            f"{path}\n"
            f"Verfügbare Templates für "
            f"'{language}': "
            f"{available_text}"
        )

    if not path.is_file():
        raise ValueError(
            f"Template-Pfad ist keine Datei: "
            f"{path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            template = json.load(file)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ungültiges Template-JSON in {path}: "
            f"Zeile {exc.lineno}, "
            f"Spalte {exc.colno}."
        ) from exc

    if not isinstance(template, dict):
        raise ValueError(
            f"Template-Datei {path} "
            "muss ein JSON-Objekt enthalten."
        )

    # IMPORTANT:
    # Unwrap first, then validate styles.
    template = unwrap_template(
        template_type,
        template,
    )

    validate_template(
        template_type,
        template,
    )

    return template


def load_templates(
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    """
    Load ALL automatically discovered templates.
    """

    language = normalize_language(language)

    template_types = get_available_template_types(
        language
    )

    if not template_types:
        raise ValueError(
            f"Keine Templates für Sprache "
            f"'{language}' gefunden."
        )

    templates: dict[str, Any] = {}

    for template_type in template_types:

        templates[template_type] = load_template(
            template_type=template_type,
            language=language,
        )

    return templates


# ============================================================
# TEMPLATE TYPE AUTOMATIC SELECTION
# ============================================================

def choose_template_type(
    company: dict[str, Any],
    templates: dict[str, Any],
    requested_type: str | None = None,
) -> str:
    """
    Determine the template type.

    Priority:

        1. Explicit template type
        2. company.template
        3. company.type
        4. Automatic classification
        5. Generic fallback
    """

    if not templates:
        raise ValueError(
            "Keine Templates verfügbar."
        )

    available = list(templates.keys())

    available_lower = {
        clean_single_line(name).casefold(): name
        for name in available
    }

    # --------------------------------------------------------
    # 1. Explicit template type
    # --------------------------------------------------------

    if requested_type:

        requested = clean_single_line(
            requested_type
        ).casefold()

        if requested in available_lower:
            return available_lower[requested]

        raise ValueError(
            f"Template-Typ "
            f"'{requested}' nicht vorhanden. "
            f"Verfügbar: "
            f"{', '.join(available)}"
        )

    # --------------------------------------------------------
    # 2. Company template override
    # --------------------------------------------------------

    company_template = clean_single_line(
        company.get("template")
    ).casefold()

    if company_template in available_lower:
        return available_lower[
            company_template
        ]

    # --------------------------------------------------------
    # 3. Company type
    #
    # This is especially important for --send-all.
    # --------------------------------------------------------

    company_type = clean_single_line(
        company.get("type")
    ).casefold()

    if company_type in available_lower:
        return available_lower[
            company_type
        ]

    # --------------------------------------------------------
    # 4. Automatic classification
    # --------------------------------------------------------

    position = clean_text(
        company.get("position")
    ).casefold()

    keywords = company.get(
        "keywords",
        [],
    )

    if isinstance(keywords, list):
        keyword_text = " ".join(
            clean_single_line(
                keyword
            ).casefold()
            for keyword in keywords
        )
    else:
        keyword_text = ""

    text = " ".join(
        [
            position,
            company_type,
            keyword_text,
        ]
    )

    # --------------------------------------------------------
    # Cybersecurity
    # --------------------------------------------------------

    cybersecurity_words = [
        "security",
        "cybersecurity",
        "cyber security",
        "cyber-security",
        "penetration testing",
        "penetration tester",
        "pentest",
        "pentester",
        "soc",
        "siem",
        "incident response",
        "ethical hacking",
        "vulnerability",
        "vulnerability management",
        "threat detection",
        "threat intelligence",
        "malware analysis",
        "reverse engineering",
        "digital forensics",
        "security analyst",
        "security engineer",
        "security specialist",
        "it security",
        "it-sicherheit",
        "information security",
        "infosec",
    ]

    if any(
        word in text
        for word in cybersecurity_words
    ):
        if "cybersecurity" in available_lower:
            return available_lower[
                "cybersecurity"
            ]

    # --------------------------------------------------------
    # Software
    # --------------------------------------------------------

    software_words = [
        "developer",
        "software developer",
        "software engineer",
        "software",
        "python developer",
        "django",
        "flask",
        "fastapi",
        "backend",
        "backend developer",
        "frontend",
        "frontend developer",
        "full stack",
        "fullstack",
        "programming",
        "software development",
        "softwareentwicklung",
        "application developer",
    ]

    if any(
        word in text
        for word in software_words
    ):
        if "software" in available_lower:
            return available_lower[
                "software"
            ]

    # --------------------------------------------------------
    # DevOps
    # --------------------------------------------------------

    devops_words = [
        "devops",
        "dev ops",
        "ci/cd",
        "cicd",
        "continuous integration",
        "continuous deployment",
        "docker",
        "kubernetes",
        "terraform",
        "ansible",
        "jenkins",
        "gitlab ci",
        "github actions",
        "cloud engineer",
        "platform engineer",
        "site reliability",
        "sre",
    ]

    if any(
        word in text
        for word in devops_words
    ):
        if "devops" in available_lower:
            return available_lower[
                "devops"
            ]

    # --------------------------------------------------------
    # IT
    # --------------------------------------------------------

    it_words = [
        "systemadministrator",
        "system administrator",
        "system administration",
        "administrator",
        "network administrator",
        "it administrator",
        "it systemadministrator",
        "it administration",
        "windows server",
        "active directory",
        "infrastructure",
        "system engineer",
        "it support",
        "helpdesk",
        "service desk",
        "technical support",
        "it technician",
        "network engineer",
        "netzwerkadministrator",
        "fachinformatiker",
    ]

    if any(
        word in text
        for word in it_words
    ):
        if "it" in available_lower:
            return available_lower["it"]

    # --------------------------------------------------------
    # Generic fallback
    # --------------------------------------------------------

    if "it" in available_lower:
        return available_lower["it"]

    return available[0]


# ============================================================
# TEMPLATE STYLE SELECTION
# ============================================================

def get_available_styles(
    template: dict[str, Any],
) -> list[str]:
    """
    Return all available styles.
    """

    if not isinstance(template, dict):
        return []

    styles: list[str] = []

    for name, value in template.items():

        if name == "order":
            continue

        if isinstance(value, dict):
            styles.append(name)

    return styles


def choose_style(
    template: dict[str, Any],
    company: dict[str, Any],
    requested_style: str | None = None,
) -> str:
    """
    Select the template style.
    """

    available = get_available_styles(
        template
    )

    if not available:
        raise ValueError(
            "Template enthält keine Styles."
        )

    available_map = {
        style.casefold(): style
        for style in available
    }

    # --------------------------------------------------------
    # 1. Explicit style
    # --------------------------------------------------------

    if requested_style:

        requested_style = clean_single_line(
            requested_style
        ).casefold()

        if requested_style not in available_map:
            raise ValueError(
                f"Template-Stil "
                f"'{requested_style}' "
                "nicht verfügbar. "
                f"Verfügbar: "
                f"{', '.join(available)}"
            )

        return available_map[
            requested_style
        ]

    # --------------------------------------------------------
    # 2. Company override
    # --------------------------------------------------------

    company_style = clean_single_line(
        company.get("template_style")
    ).casefold()

    if company_style in available_map:
        return available_map[
            company_style
        ]

    # --------------------------------------------------------
    # 3. Automatic selection by company size
    # --------------------------------------------------------

    company_size = clean_single_line(
        company.get("size")
    ).casefold()

    size_mapping = {
        "startup": [
            "startup",
            "modern",
            "technical",
            "formal",
        ],
        "small": [
            "modern",
            "formal",
            "technical",
        ],
        "medium": [
            "formal",
            "technical",
            "modern",
        ],
        "large": [
            "formal",
            "technical",
            "modern",
        ],
        "enterprise": [
            "formal",
            "technical",
            "modern",
        ],
    }

    for candidate in size_mapping.get(
        company_size,
        [],
    ):
        if candidate in available_map:
            return available_map[candidate]

    # --------------------------------------------------------
    # 4. Formal preferred
    # --------------------------------------------------------

    if DEFAULT_TEMPLATE_STYLE in available_map:
        return available_map[
            DEFAULT_TEMPLATE_STYLE
        ]

    # --------------------------------------------------------
    # 5. Fallback
    # --------------------------------------------------------

    return available[0]


# ============================================================
# SECTION HANDLING
# ============================================================

def get_section_order(
    style: dict[str, Any],
) -> list[str]:
    """
    Determine section order.
    """

    if not isinstance(style, dict):
        raise ValueError(
            "Template-Style muss "
            "ein Objekt sein."
        )

    custom_order = style.get("order")

    if custom_order is not None:

        if not isinstance(
            custom_order,
            list,
        ):
            raise ValueError(
                "Template 'order' "
                "muss eine Liste sein."
            )

        result: list[str] = []

        for section in custom_order:

            if not isinstance(section, str):
                raise ValueError(
                    "Alle Einträge in "
                    "Template 'order' "
                    "müssen Strings sein."
                )

            section = clean_single_line(
                section
            )

            if section:
                result.append(section)

        if result:
            return result

    return DEFAULT_SECTION_ORDER.copy()


def get_section(
    style: dict[str, Any],
    section_name: str,
) -> Any:
    """
    Get one section from a template style.
    """

    return style.get(section_name)


# ============================================================
# SENTENCE SELECTION
# ============================================================

def normalize_options(
    value: Any,
) -> list[str]:
    """
    Normalize supported template formats into a list.
    """

    if value is None:
        return []

    if isinstance(value, str):
        value = [value]

    if not isinstance(value, list):
        raise ValueError(
            "Template-Abschnitt "
            "muss String oder Liste sein."
        )

    result: list[str] = []

    for item in value:

        if not isinstance(item, str):
            raise ValueError(
                "Template-Varianten "
                "müssen Strings sein."
            )

        item = clean_text(item)

        if item:
            result.append(item)

    return result


def choose_sentence(
    sentences: list[str],
    variables: dict[str, str],
    rng: random.Random,
) -> str:
    """
    Choose one sentence variant and render it.
    """

    if not sentences:
        return ""

    sentence = rng.choice(sentences)

    return render_text(
        sentence,
        variables,
    )


# ============================================================
# SECTION GENERATION
# ============================================================

def generate_section(
    section_name: str,
    section_definition: Any,
    variables: dict[str, str],
    rng: random.Random,
) -> str:
    """
    Generate one template section.
    """

    if section_definition is None:
        return ""

    # --------------------------------------------------------
    # String
    # --------------------------------------------------------

    if isinstance(
        section_definition,
        str,
    ):
        return render_text(
            section_definition,
            variables,
        )

    # --------------------------------------------------------
    # List
    # --------------------------------------------------------

    if isinstance(
        section_definition,
        list,
    ):
        options = normalize_options(
            section_definition
        )

        return choose_sentence(
            options,
            variables,
            rng,
        )

    # --------------------------------------------------------
    # Object
    # --------------------------------------------------------

    if isinstance(
        section_definition,
        dict,
    ):
        variants = section_definition.get(
            "variants"
        )

        if variants is None:
            variants = section_definition.get(
                "sentences"
            )

        options = normalize_options(
            variants
        )

        if not options:
            return ""

        return choose_sentence(
            options,
            variables,
            rng,
        )

    raise ValueError(
        "Ungültige Definition für "
        f"Template-Abschnitt "
        f"'{section_name}'."
    )


# ============================================================
# APPLICATION TEXT
# ============================================================

def assemble_application(
    sections: dict[str, str],
    section_order: list[str],
) -> str:
    """
    Assemble generated sections into the final application.
    """

    paragraphs: list[str] = []

    for section_name in section_order:

        text = clean_text(
            sections.get(
                section_name,
                "",
            )
        )

        if not text:
            continue

        paragraphs.append(text)

    return "\n\n".join(
        paragraphs
    ).strip()


# ============================================================
# TEMPLATE VALIDATION
# ============================================================

def validate_template(
    template_type: str,
    template: dict[str, Any],
) -> None:
    """
    Validate a complete template type.
    """

    if not isinstance(
        template,
        dict,
    ):
        raise ValueError(
            f"Template '{template_type}' "
            "muss ein Objekt sein."
        )

    styles = get_available_styles(
        template
    )

    if not styles:
        raise ValueError(
            f"Template '{template_type}' "
            "enthält keine Styles."
        )

    for style_name in styles:

        style = template[style_name]

        if not isinstance(
            style,
            dict,
        ):
            raise ValueError(
                f"Template "
                f"'{template_type}' "
                f"Style '{style_name}' "
                "muss ein Objekt sein."
            )

        order = get_section_order(
            style
        )

        if not order:
            raise ValueError(
                f"Template "
                f"'{template_type}' "
                f"Style '{style_name}' "
                "besitzt keine Sections."
            )

        for section_name in order:

            definition = style.get(
                section_name
            )

            if definition is None:
                continue

            options: list[str] = []

            # ------------------------------------------------
            # String
            # ------------------------------------------------

            if isinstance(
                definition,
                str,
            ):
                options = [definition]

            # ------------------------------------------------
            # List
            # ------------------------------------------------

            elif isinstance(
                definition,
                list,
            ):
                options = normalize_options(
                    definition
                )

            # ------------------------------------------------
            # Object
            # ------------------------------------------------

            elif isinstance(
                definition,
                dict,
            ):
                variants = definition.get(
                    "variants"
                )

                if variants is None:
                    variants = definition.get(
                        "sentences",
                        [],
                    )

                options = normalize_options(
                    variants
                )

            else:
                raise ValueError(
                    "Ungültiger Abschnitt "
                    f"'{section_name}' in "
                    f"{template_type}."
                    f"{style_name}"
                )

            if not options:
                continue

            # ------------------------------------------------
            # Placeholder validation
            # ------------------------------------------------

            for option in options:

                placeholders = find_placeholders(
                    option
                )

                for placeholder in placeholders:

                    if placeholder not in (
                        SUPPORTED_PLACEHOLDERS
                    ):
                        raise ValueError(
                            "Unbekannter "
                            "Placeholder "
                            f"'{{{placeholder}}}' "
                            "in "
                            f"{template_type}."
                            f"{style_name}."
                            f"{section_name}"
                        )


def validate_all_templates(
    templates: dict[str, Any],
) -> None:
    """
    Validate all loaded templates.
    """

    if not isinstance(
        templates,
        dict,
    ):
        raise ValueError(
            "Templates müssen "
            "ein Objekt enthalten."
        )

    if not templates:
        raise ValueError(
            "Keine Templates vorhanden."
        )

    for template_type, template in templates.items():

        if not isinstance(
            template_type,
            str,
        ):
            raise ValueError(
                "Template-Typ muss "
                "ein String sein."
            )

        validate_template(
            template_type,
            template,
        )


# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_company(
    company: dict[str, Any],
) -> None:
    """
    Perform basic validation of a company record.
    """

    if not isinstance(
        company,
        dict,
    ):
        raise ValueError(
            "Company muss ein Objekt sein."
        )

    if not clean_text(
        company.get("name")
    ):
        raise ValueError(
            "Company 'name' fehlt."
        )

    if not clean_text(
        company.get("position")
    ):
        raise ValueError(
            "Company 'position' fehlt."
        )

    company_id = company.get("id")

    if company_id is not None:
        if not isinstance(
            company_id,
            str,
        ):
            raise ValueError(
                "Company 'id' muss "
                "ein String sein."
            )


def validate_application_result(
    result: GeneratedApplication,
) -> None:
    """
    Validate the generated application result.
    """

    if not isinstance(
        result.text,
        str,
    ):
        raise ValueError(
            "Generierter Bewerbungstext "
            "muss ein String sein."
        )

    if not result.text.strip():
        raise ValueError(
            "Generierter Bewerbungstext "
            "ist leer."
        )

    if not result.company_name.strip():
        raise ValueError(
            "Generierte Bewerbung besitzt "
            "keinen Firmennamen."
        )

    if not result.position.strip():
        raise ValueError(
            "Generierte Bewerbung besitzt "
            "keine Position."
        )

    if not (
        0.0
        <= result.match_score
        <= 100.0
    ):
        raise ValueError(
            "match_score liegt "
            "außerhalb von 0-100."
        )

    if not (
        0.0
        <= result.confidence_score
        <= 100.0
    ):
        raise ValueError(
            "confidence_score liegt "
            "außerhalb von 0-100."
        )


# ============================================================
# GITHUB FOOTER
# ============================================================

def build_github_footer(
    github: str,
    language: str = DEFAULT_LANGUAGE,
) -> str:
    """
    Build an optional GitHub footer.
    """

    language = normalize_language(language)

    github = clean_single_line(github)

    if not github:
        return ""

    if language == "en":
        return (
            "For more information about my technical "
            "projects and code, please visit my "
            f"GitHub profile: {github}"
        )

    return (
        "Weitere Informationen zu meinen technischen "
        "Projekten und meinem Code finden Sie auf meinem "
        f"GitHub-Profil: {github}"
    )


# ============================================================
# GENERATE APPLICATION
# ============================================================

def generate_application(
    company: dict[str, Any],
    *,
    template_type: str | None = None,
    template_style: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    seed: int | None = None,
) -> GeneratedApplication:
    """
    Main application generator.

    Automatic example:

        company["type"] = "cybersecurity"
        language = "en"

    results in:

        data/en/cybersecurity.json

    An explicit template_type always overrides automatic
    template selection.
    """

    # --------------------------------------------------------
    # Validate company
    # --------------------------------------------------------

    validate_company(company)

    # --------------------------------------------------------
    # Language
    # --------------------------------------------------------

    language = normalize_language(language)

    # --------------------------------------------------------
    # Applicant
    # --------------------------------------------------------

    applicant_data = load_json(
        "applicant.json"
    )

    applicant = build_applicant_context(
        applicant_data
    )

    # --------------------------------------------------------
    # Job
    # --------------------------------------------------------

    job = build_job_context(
        company
    )

    # --------------------------------------------------------
    # Load templates
    # --------------------------------------------------------

    templates = load_templates(
        language
    )

    # --------------------------------------------------------
    # Validate templates
    # --------------------------------------------------------

    validate_all_templates(
        templates
    )

    # --------------------------------------------------------
    # Template type
    # --------------------------------------------------------

    selected_type = choose_template_type(
        company=company,
        templates=templates,
        requested_type=template_type,
    )

    selected_template = templates[
        selected_type
    ]

    # --------------------------------------------------------
    # Template style
    # --------------------------------------------------------

    selected_style = choose_style(
        template=selected_template,
        company=company,
        requested_style=template_style,
    )

    style = selected_template[
        selected_style
    ]

    # --------------------------------------------------------
    # Variables
    # --------------------------------------------------------

    variables = build_variables(
        applicant=applicant,
        job=job,
        language=language,
    )

    # --------------------------------------------------------
    # RNG
    # --------------------------------------------------------

    rng = random.Random(seed)

    # --------------------------------------------------------
    # Sections
    # --------------------------------------------------------

    section_order = get_section_order(
        style
    )

    sections: dict[str, str] = {}

    for section_name in section_order:

        definition = get_section(
            style=style,
            section_name=section_name,
        )

        if definition is None:
            continue

        generated = generate_section(
            section_name=section_name,
            section_definition=definition,
            variables=variables,
            rng=rng,
        )

        if generated:
            sections[section_name] = generated

    # --------------------------------------------------------
    # Final text
    # --------------------------------------------------------

    text = assemble_application(
        sections=sections,
        section_order=section_order,
    )

    if not text:
        raise ValueError(
            "Das Template hat keinen "
            "Inhalt für die Bewerbung erzeugt."
        )

    # --------------------------------------------------------
    # GitHub footer
    # --------------------------------------------------------

    github_footer = build_github_footer(
        applicant.github,
        language=language,
    )

    if github_footer:
        text = (
            f"{text}\n\n"
            f"{github_footer}"
        )

        text = clean_text(text)

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    result = GeneratedApplication(
        text=text,

        company_name=job.company_name,
        position=job.position,

        template_type=selected_type,
        template_style=selected_style,
        language=language,

        matched_keywords=job.matched_keywords,
        missing_keywords=job.missing_keywords,

        variables=variables,
        sections=sections,

        match_score=job.match_score,
        confidence_score=job.confidence_score,

        company_id=job.company_id,
        job_id=job.job_id,
        source_url=job.source_url,
    )

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    validate_application_result(
        result
    )

    return result


# ============================================================
# BACKWARD / API COMPATIBILITY
# ============================================================

def generate_application_text(
    company: dict[str, Any],
    *,
    template_type: str | None = None,
    template_style: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    seed: int | None = None,
) -> GeneratedApplication:
    """
    Compatibility wrapper for callers expecting
    generate_application_text().

    Returns the complete GeneratedApplication object.
    """

    return generate_application(
        company=company,
        template_type=template_type,
        template_style=template_style,
        language=language,
        seed=seed,
    )


def generate_letter(
    company: dict[str, Any],
    *,
    template_type: str | None = None,
    template_style: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    seed: int | None = None,
) -> str:
    """
    Backward-compatible function returning only the text.
    """

    result = generate_application(
        company=company,
        template_type=template_type,
        template_style=template_style,
        language=language,
        seed=seed,
    )

    return result.text


# ============================================================
# PREVIEW / DEBUG
# ============================================================

def preview_application(
    company: dict[str, Any],
    *,
    template_type: str | None = None,
    template_style: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    seed: int | None = None,
) -> str:
    """
    Create a human-readable application preview including
    template and matching information.
    """

    result = generate_application(
        company=company,
        template_type=template_type,
        template_style=template_style,
        language=language,
        seed=seed,
    )

    matched = (
        format_list(
            result.matched_keywords,
            language=language,
        )
        or "Keine"
    )

    missing = (
        format_list(
            result.missing_keywords,
            language=language,
        )
        or "Keine"
    )

    return (
        "\n"
        "Bewerbungsvorschau\n"
        "\n"
        + "=" * 60
        + "\n"
        "\n"
        "Unternehmen:\n"
        f"{result.company_name}\n"
        "\n"
        "Position:\n"
        f"{result.position}\n"
        "\n"
        "Company-ID:\n"
        f"{result.company_id or 'Keine'}\n"
        "\n"
        "Job-ID:\n"
        f"{result.job_id or 'Keine'}\n"
        "\n"
        "Template:\n"
        f"{result.template_type}\n"
        "\n"
        "Template-Datei:\n"
        f"{get_template_path(result.template_type, result.language)}\n"
        "\n"
        "Style:\n"
        f"{result.template_style}\n"
        "\n"
        "Sprache:\n"
        f"{result.language}\n"
        "\n"
        "Match Score:\n"
        f"{format_score(result.match_score)}\n"
        "\n"
        "Confidence Score:\n"
        f"{format_score(result.confidence_score)}\n"
        "\n"
        "Gematchte Kenntnisse:\n"
        f"{matched}\n"
        "\n"
        "Fehlende Kenntnisse:\n"
        f"{missing}\n"
        "\n"
        + "-" * 60
        + "\n"
        "\n"
        "ANSCHREIBEN\n"
        "\n"
        + "-" * 60
        + "\n"
        "\n"
        f"{result.text}\n"
        "\n"
        + "=" * 60
    ).strip()