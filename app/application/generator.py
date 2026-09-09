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

SUPPORTED_LANGUAGES = {"de", "en"}

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
    "company_name",
    "company_type",
    "company_size",
    "company_id",
    "position",
    "location",
    "job_id",
    "job_type",
    "seniority",
    "employment_type",
    "remote_type",
    "source_url",
    "first_name",
    "last_name",
    "full_name",
    "email",
    "phone",
    "address",
    "zip_code",
    "city",
    "github",
    "applicant_keywords",
    "job_keywords",
    "matched_keywords",
    "relevant_keywords",
    "missing_keywords",
    "match_score",
    "confidence_score",
    "experience",
}

DEFAULT_APPLICATION_SKILLS = {
    "de": {
        "cybersecurity": ["Python", "Linux", "IT-Sicherheit"],
        "software": ["Python", "Linux", "Softwareentwicklung"],
        "it": ["Python", "Linux", "IT-Systeme"],
        "devops": ["Python", "Linux", "DevOps"],
        "networking": ["Python", "Linux", "Netzwerkadministration"],
        "cloud": ["Python", "Linux", "Cloud Computing"],
        "default": ["Python", "Linux", "IT-Sicherheit"],
    },
    "en": {
        "cybersecurity": ["Python", "Linux", "Cyber Security"],
        "software": ["Python", "Linux", "Software Development"],
        "it": ["Python", "Linux", "IT Systems"],
        "devops": ["Python", "Linux", "DevOps"],
        "networking": ["Python", "Linux", "Network Administration"],
        "cloud": ["Python", "Linux", "Cloud Computing"],
        "default": ["Python", "Linux", "Cyber Security"],
    },
}

IGNORED_TEMPLATE_FILES = {
    "applicant.json",
    "companies.json",
    "history.json",
    "templates.json",
}

PLACEHOLDER_PATTERN = re.compile(
    r"{([a-zA-Z_][a-zA-Z0-9_]*)}"
)

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

TEMPLATE_NAME_PATTERN = re.compile(
    r"[a-zA-Z0-9_-]+"
)


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class JobContext:
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
    if value is None:
        return ""

    text = str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_single_line(value: Any) -> str:
    text = clean_text(value)
    text = text.replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def unique_strings(values: list[Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()

    for value in values:
        text = clean_text(value)
        if not text:
            continue

        key = text.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(text)

    return result


def ensure_string_list(
    value: Any,
    field_name: str,
) -> list[str]:
    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(
            f"'{field_name}' muss eine Liste sein."
        )

    return unique_strings(value)


def normalize_language(language: str) -> str:
    language = clean_single_line(language).casefold()

    if language not in SUPPORTED_LANGUAGES:
        available = ", ".join(sorted(SUPPORTED_LANGUAGES))
        raise ValueError(
            f"Nicht unterstützte Sprache: '{language}'. "
            f"Verfügbar: {available}"
        )

    return language


def format_list(
    values: list[str],
    language: str = DEFAULT_LANGUAGE,
) -> str:
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
    return format_list(keywords, language)


def format_score(value: Any) -> str:
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = 0.0

    score = max(0.0, min(100.0, score))
    return f"{score:.1f} %"


def _read_score(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(100.0, score))


# ============================================================
# JSON
# ============================================================

def load_json(filename: str) -> dict[str, Any]:
    filename = clean_single_line(filename)

    if not filename:
        raise ValueError("Kein JSON-Dateiname angegeben.")

    data_root = DATA_DIR.resolve()
    path = (DATA_DIR / filename).resolve()

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
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ungültiges JSON in {path}: "
            f"Zeile {exc.lineno}, Spalte {exc.colno}"
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
    company_id = clean_single_line(company_id)

    if not company_id:
        raise ValueError("Keine Company-ID angegeben.")

    data = load_json("companies.json")
    companies = data.get("companies", [])

    if not isinstance(companies, list):
        raise ValueError(
            "companies.json: 'companies' muss eine Liste sein."
        )

    for company in companies:
        if not isinstance(company, dict):
            continue

        if clean_single_line(company.get("id")) == company_id:
            return company

    raise ValueError(
        f"Unternehmen '{company_id}' nicht gefunden."
    )


# ============================================================
# APPLICANT
# ============================================================

def build_applicant_context(
    applicant: dict[str, Any],
) -> ApplicantContext:
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

    return ApplicantContext(
        first_name=first_name,
        last_name=last_name,
        email=clean_single_line(applicant.get("email")),
        phone=clean_single_line(applicant.get("phone")),
        address=clean_single_line(applicant.get("address")),
        zip_code=clean_single_line(applicant.get("zip_code")),
        city=clean_single_line(applicant.get("city")),
        github=clean_single_line(applicant.get("github")),
        skills=ensure_string_list(
            applicant.get("skills", []),
            "skills",
        ),
        experience=ensure_string_list(
            applicant.get("experience", []),
            "experience",
        ),
    )


# ============================================================
# JOB
# ============================================================

def build_job_context(
    company: dict[str, Any],
) -> JobContext:
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

    return JobContext(
        company_name=company_name,
        position=position,
        company_id=clean_single_line(company.get("id")),
        company_type=clean_single_line(company.get("type")),
        company_size=clean_single_line(company.get("size")),
        location=clean_single_line(company.get("location")),
        job_id=clean_single_line(company.get("job_id")),
        job_type=clean_single_line(company.get("job_type")),
        seniority=clean_single_line(company.get("seniority")),
        employment_type=clean_single_line(
            company.get("employment_type")
        ),
        remote_type=clean_single_line(
            company.get("remote_type")
        ),
        job_keywords=ensure_string_list(
            company.get("keywords", []),
            "keywords",
        ),
        matched_keywords=ensure_string_list(
            company.get("matched_keywords", []),
            "matched_keywords",
        ),
        relevant_keywords=ensure_string_list(
            company.get("relevant_keywords", []),
            "relevant_keywords",
        ),
        missing_keywords=ensure_string_list(
            company.get("missing_keywords", []),
            "missing_keywords",
        ),
        experience=ensure_string_list(
            company.get("experience", []),
            "experience",
        ),
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

def _get_default_skills(
    language: str,
    company_type: str,
) -> list[str]:
    language = normalize_language(language)
    company_type = clean_single_line(
        company_type
    ).casefold()

    defaults = DEFAULT_APPLICATION_SKILLS[language]

    return unique_strings(
        defaults.get(
            company_type,
            defaults["default"],
        )
    )


def build_variables(
    applicant: ApplicantContext,
    job: JobContext,
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, str]:
    language = normalize_language(language)

    full_name = f"{applicant.first_name} {applicant.last_name}"

    matched_keywords = unique_strings(
        job.matched_keywords
    )
    relevant_keywords = unique_strings(
        job.relevant_keywords
    )

    if relevant_keywords:
        application_relevant_keywords = relevant_keywords
    elif matched_keywords:
        application_relevant_keywords = matched_keywords
    elif applicant.skills:
        application_relevant_keywords = unique_strings(
            applicant.skills
        )
    else:
        application_relevant_keywords = _get_default_skills(
            language,
            job.company_type,
        )

    if matched_keywords:
        application_experience = matched_keywords
    elif applicant.experience:
        application_experience = unique_strings(
            applicant.experience
        )
    else:
        application_experience = _get_default_skills(
            language,
            job.company_type,
        )

    return {
        "company_name": job.company_name,
        "company_type": job.company_type,
        "company_size": job.company_size,
        "company_id": job.company_id,

        "position": job.position,
        "location": job.location,
        "job_id": job.job_id,
        "job_type": job.job_type,
        "seniority": job.seniority,
        "employment_type": job.employment_type,
        "remote_type": job.remote_type,
        "source_url": job.source_url,

        "first_name": applicant.first_name,
        "last_name": applicant.last_name,
        "full_name": full_name,
        "email": applicant.email,
        "phone": applicant.phone,
        "address": applicant.address,
        "zip_code": applicant.zip_code,
        "city": applicant.city,
        "github": applicant.github,

        "applicant_keywords": format_list(
            applicant.skills,
            language,
        ),
        "job_keywords": format_list(
            job.job_keywords,
            language,
        ),
        "matched_keywords": format_list(
            matched_keywords,
            language,
        ),
        "relevant_keywords": format_list(
            application_relevant_keywords,
            language,
        ),
        "missing_keywords": format_list(
            job.missing_keywords,
            language,
        ),
        "experience": format_list(
            application_experience,
            language,
        ),

        "match_score": format_score(
            job.match_score
        ),
        "confidence_score": format_score(
            job.confidence_score
        ),
    }


# ============================================================
# PLACEHOLDERS
# ============================================================

def find_placeholders(text: str) -> list[str]:
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
    for placeholder in find_placeholders(text):
        if placeholder not in SUPPORTED_PLACEHOLDERS:
            raise ValueError(
                "Unbekannter Template-Platzhalter: "
                f"{{{placeholder}}}"
            )

        if placeholder not in variables:
            raise ValueError(
                f"Keine Variable für "
                f"{{{placeholder}}} vorhanden."
            )


def render_text(
    text: str,
    variables: dict[str, str],
) -> str:
    text = clean_text(text)

    if not text:
        return ""

    validate_placeholders(text, variables)

    try:
        rendered = text.format(**variables)
    except (KeyError, ValueError, IndexError) as exc:
        raise ValueError(
            f"Template konnte nicht gerendert werden: {exc}"
        ) from exc

    return clean_text(rendered)


# ============================================================
# TEMPLATE DIRECTORY
# ============================================================

def get_template_directory(
    language: str = DEFAULT_LANGUAGE,
) -> Path:
    language = normalize_language(language)
    directory = DATA_DIR / language

    if not directory.exists():
        raise FileNotFoundError(
            f"Template-Verzeichnis nicht gefunden: {directory}"
        )

    if not directory.is_dir():
        raise ValueError(
            f"Template-Pfad ist kein Verzeichnis: {directory}"
        )

    return directory


# ============================================================
# TEMPLATE DISCOVERY
# ============================================================

def get_available_template_types(
    language: str = DEFAULT_LANGUAGE,
) -> list[str]:
    directory = get_template_directory(language)
    template_types: list[str] = []

    for path in directory.glob("*.json"):
        if not path.is_file():
            continue

        if path.name.casefold() in IGNORED_TEMPLATE_FILES:
            continue

        if not TEMPLATE_NAME_PATTERN.fullmatch(path.stem):
            continue

        template_types.append(path.stem.casefold())

    return sorted(set(template_types))


def get_template_path(
    template_type: str,
    language: str = DEFAULT_LANGUAGE,
) -> Path:
    template_type = clean_single_line(
        template_type
    ).casefold()

    if not template_type:
        raise ValueError(
            "Kein Template-Typ angegeben."
        )

    if not TEMPLATE_NAME_PATTERN.fullmatch(template_type):
        raise ValueError(
            f"Ungültiger Template-Typ: '{template_type}'"
        )

    directory = get_template_directory(language).resolve()
    path = (directory / f"{template_type}.json").resolve()

    try:
        path.relative_to(directory)
    except ValueError as exc:
        raise ValueError(
            f"Ungültiger Template-Pfad: {path}"
        ) from exc

    return path


# ============================================================
# TEMPLATE ROOT
# ============================================================

def _looks_like_direct_style_map(
    template: dict[str, Any],
) -> bool:
    if not template:
        return False

    found_style = False

    for key, value in template.items():
        if key == "order":
            continue

        if not isinstance(key, str):
            return False

        if not isinstance(value, dict):
            return False

        if (
            "order" not in value
            and not any(
                section in value
                for section in DEFAULT_SECTION_ORDER
            )
        ):
            return False

        found_style = True

    return found_style


def unwrap_template(
    template_type: str,
    template: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(template, dict):
        raise ValueError(
            f"Template '{template_type}' muss ein Objekt sein."
        )

    normalized_type = clean_single_line(
        template_type
    ).casefold()

    for key, value in template.items():
        if (
            isinstance(key, str)
            and key.casefold() == normalized_type
        ):
            if not isinstance(value, dict):
                raise ValueError(
                    f"Template '{template_type}': "
                    f"oberster Schlüssel '{key}' "
                    "muss ein Objekt sein."
                )

            return value

    if _looks_like_direct_style_map(template):
        return template

    raise ValueError(
        f"Template-Datei für Typ '{template_type}' "
        "besitzt keine passende oberste Ebene "
        f"'{template_type}' und keine gültige "
        "direkte Style-Struktur."
    )


# ============================================================
# TEMPLATE LOADING
# ============================================================

def load_template(
    template_type: str,
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:
    language = normalize_language(language)
    template_type = clean_single_line(
        template_type
    ).casefold()

    path = get_template_path(
        template_type,
        language,
    )

    if not path.exists():
        available = get_available_template_types(language)
        available_text = ", ".join(available) or "keine"

        raise FileNotFoundError(
            f"Template-Datei nicht gefunden: {path}\n"
            f"Verfügbare Templates für '{language}': "
            f"{available_text}"
        )

    if not path.is_file():
        raise ValueError(
            f"Template-Pfad ist keine Datei: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            template = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ungültiges Template-JSON in {path}: "
            f"Zeile {exc.lineno}, Spalte {exc.colno}"
        ) from exc

    if not isinstance(template, dict):
        raise ValueError(
            f"Template-Datei {path} "
            "muss ein JSON-Objekt enthalten."
        )

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
    language = normalize_language(language)

    template_types = get_available_template_types(language)

    if not template_types:
        raise ValueError(
            f"Keine Templates für Sprache '{language}' gefunden."
        )

    return {
        template_type: load_template(
            template_type,
            language,
        )
        for template_type in template_types
    }


# ============================================================
# TEMPLATE TYPE SELECTION
# ============================================================

def choose_template_type(
    company: dict[str, Any],
    templates: dict[str, Any],
    requested_type: str | None = None,
) -> str:
    if not templates:
        raise ValueError("Keine Templates verfügbar.")

    available = list(templates.keys())
    available_map = {
        clean_single_line(name).casefold(): name
        for name in available
    }

    if requested_type:
        requested = clean_single_line(
            requested_type
        ).casefold()

        if requested in available_map:
            return available_map[requested]

        raise ValueError(
            f"Template-Typ '{requested}' nicht vorhanden. "
            f"Verfügbar: {', '.join(available)}"
        )

    company_template = clean_single_line(
        company.get("template")
    ).casefold()

    if company_template in available_map:
        return available_map[company_template]

    company_type = clean_single_line(
        company.get("type")
    ).casefold()

    if company_type in available_map:
        return available_map[company_type]

    position = clean_text(
        company.get("position")
    ).casefold()

    keywords = company.get("keywords", [])

    if isinstance(keywords, list):
        keyword_text = " ".join(
            clean_single_line(keyword).casefold()
            for keyword in keywords
        )
    else:
        keyword_text = ""

    text = f"{position} {company_type} {keyword_text}"

    classifications = [
        (
            "cybersecurity",
            [
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
            ],
        ),
        (
            "devops",
            [
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
                "platform engineer",
                "site reliability",
                "sre",
            ],
        ),
        (
            "software",
            [
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
            ],
        ),
        (
            "it",
            [
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
            ],
        ),
    ]

    for template_type, words in classifications:
        if any(word in text for word in words):
            if template_type in available_map:
                return available_map[template_type]

    if "it" in available_map:
        return available_map["it"]

    return available[0]


# ============================================================
# STYLE SELECTION
# ============================================================

def get_available_styles(
    template: dict[str, Any],
) -> list[str]:
    if not isinstance(template, dict):
        return []

    return [
        name
        for name, value in template.items()
        if name != "order"
        and isinstance(name, str)
        and isinstance(value, dict)
    ]


def choose_style(
    template: dict[str, Any],
    company: dict[str, Any],
    requested_style: str | None = None,
) -> str:
    available = get_available_styles(template)

    if not available:
        raise ValueError(
            "Template enthält keine Styles."
        )

    available_map = {
        style.casefold(): style
        for style in available
    }

    if requested_style:
        requested = clean_single_line(
            requested_style
        ).casefold()

        if requested not in available_map:
            raise ValueError(
                f"Template-Stil '{requested}' "
                "nicht verfügbar. "
                f"Verfügbar: {', '.join(available)}"
            )

        return available_map[requested]

    company_style = clean_single_line(
        company.get("template_style")
    ).casefold()

    if company_style in available_map:
        return available_map[company_style]

    company_size = clean_single_line(
        company.get("size")
    ).casefold()

    size_mapping = {
        "startup": ["startup", "modern", "technical", "formal"],
        "small": ["modern", "formal", "technical"],
        "medium": ["formal", "technical", "modern"],
        "large": ["formal", "technical", "modern"],
        "enterprise": ["formal", "technical", "modern"],
    }

    for candidate in size_mapping.get(company_size, []):
        if candidate in available_map:
            return available_map[candidate]

    if DEFAULT_TEMPLATE_STYLE in available_map:
        return available_map[DEFAULT_TEMPLATE_STYLE]

    return available[0]


# ============================================================
# SECTION HANDLING
# ============================================================

def get_section_order(
    style: dict[str, Any],
) -> list[str]:
    if not isinstance(style, dict):
        raise ValueError(
            "Template-Style muss ein Objekt sein."
        )

    custom_order = style.get("order")

    if custom_order is not None:
        if not isinstance(custom_order, list):
            raise ValueError(
                "Template 'order' muss eine Liste sein."
            )

        result = []

        for section in custom_order:
            if not isinstance(section, str):
                raise ValueError(
                    "Alle Einträge in Template 'order' "
                    "müssen Strings sein."
                )

            section = clean_single_line(section)

            if section:
                result.append(section)

        if result:
            return result

    return DEFAULT_SECTION_ORDER.copy()


def get_section(
    style: dict[str, Any],
    section_name: str,
) -> Any:
    return style.get(section_name)


# ============================================================
# SENTENCE HANDLING
# ============================================================

def normalize_options(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        value = [value]

    if not isinstance(value, list):
        raise ValueError(
            "Template-Abschnitt muss String oder Liste sein."
        )

    result = []

    for item in value:
        if not isinstance(item, str):
            raise ValueError(
                "Template-Varianten müssen Strings sein."
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
    if not sentences:
        return ""

    return render_text(
        rng.choice(sentences),
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
    if section_definition is None:
        return ""

    if isinstance(section_definition, str):
        return render_text(
            section_definition,
            variables,
        )

    if isinstance(section_definition, list):
        return choose_sentence(
            normalize_options(section_definition),
            variables,
            rng,
        )

    if isinstance(section_definition, dict):
        variants = section_definition.get("variants")

        if variants is None:
            variants = section_definition.get("sentences")

        return choose_sentence(
            normalize_options(variants),
            variables,
            rng,
        )

    raise ValueError(
        f"Ungültige Definition für "
        f"Template-Abschnitt '{section_name}'."
    )


# ============================================================
# APPLICATION ASSEMBLY
# ============================================================

def assemble_application(
    sections: dict[str, str],
    section_order: list[str],
) -> str:
    paragraphs = []

    for section_name in section_order:
        text = clean_text(
            sections.get(section_name, "")
        )

        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs).strip()


# ============================================================
# TEMPLATE VALIDATION
# ============================================================

def _get_definition_options(
    definition: Any,
) -> list[str]:
    if isinstance(definition, str):
        return [definition]

    if isinstance(definition, list):
        return normalize_options(definition)

    if isinstance(definition, dict):
        variants = definition.get("variants")

        if variants is None:
            variants = definition.get("sentences", [])

        return normalize_options(variants)

    raise ValueError("Ungültige Template-Abschnittsdefinition.")


def validate_template(
    template_type: str,
    template: dict[str, Any],
) -> None:
    if not isinstance(template, dict):
        raise ValueError(
            f"Template '{template_type}' muss ein Objekt sein."
        )

    styles = get_available_styles(template)

    if not styles:
        raise ValueError(
            f"Template '{template_type}' enthält keine Styles."
        )

    for style_name in styles:
        style = template[style_name]

        if not isinstance(style, dict):
            raise ValueError(
                f"Template '{template_type}' "
                f"Style '{style_name}' muss ein Objekt sein."
            )

        order = get_section_order(style)

        if not order:
            raise ValueError(
                f"Template '{template_type}' "
                f"Style '{style_name}' besitzt keine Sections."
            )

        for section_name in order:
            definition = style.get(section_name)

            if definition is None:
                continue

            try:
                options = _get_definition_options(definition)
            except ValueError as exc:
                raise ValueError(
                    f"Ungültiger Abschnitt "
                    f"'{section_name}' in "
                    f"{template_type}.{style_name}"
                ) from exc

            for option in options:
                for placeholder in find_placeholders(option):
                    if placeholder not in SUPPORTED_PLACEHOLDERS:
                        raise ValueError(
                            "Unbekannter Placeholder "
                            f"'{{{placeholder}}}' in "
                            f"{template_type}."
                            f"{style_name}."
                            f"{section_name}"
                        )


def validate_all_templates(
    templates: dict[str, Any],
) -> None:
    if not isinstance(templates, dict):
        raise ValueError(
            "Templates müssen ein Objekt enthalten."
        )

    if not templates:
        raise ValueError(
            "Keine Templates vorhanden."
        )

    for template_type, template in templates.items():
        if not isinstance(template_type, str):
            raise ValueError(
                "Template-Typ muss ein String sein."
            )

        validate_template(
            template_type,
            template,
        )


# ============================================================
# COMPANY VALIDATION
# ============================================================

def validate_company(
    company: dict[str, Any],
) -> None:
    if not isinstance(company, dict):
        raise ValueError(
            "Company muss ein Objekt sein."
        )

    if not clean_text(company.get("name")):
        raise ValueError(
            "Company 'name' fehlt."
        )

    if not clean_text(company.get("position")):
        raise ValueError(
            "Company 'position' fehlt."
        )

    company_id = company.get("id")

    if company_id is not None and not isinstance(
        company_id,
        str,
    ):
        raise ValueError(
            "Company 'id' muss ein String sein."
        )

    email = clean_single_line(
        company.get("email")
    )

    if email and not EMAIL_PATTERN.fullmatch(email):
        raise ValueError(
            f"Ungültige E-Mail-Adresse: {email}"
        )


# ============================================================
# APPLICATION RESULT VALIDATION
# ============================================================

def validate_application_result(
    result: GeneratedApplication,
) -> None:
    if not isinstance(result.text, str):
        raise ValueError(
            "Generierter Bewerbungstext muss ein String sein."
        )

    if not result.text.strip():
        raise ValueError(
            "Generierter Bewerbungstext ist leer."
        )

    if not result.company_name.strip():
        raise ValueError(
            "Generierte Bewerbung besitzt keinen Firmennamen."
        )

    if not result.position.strip():
        raise ValueError(
            "Generierte Bewerbung besitzt keine Position."
        )

    if not 0.0 <= result.match_score <= 100.0:
        raise ValueError(
            "match_score liegt außerhalb von 0-100."
        )

    if not 0.0 <= result.confidence_score <= 100.0:
        raise ValueError(
            "confidence_score liegt außerhalb von 0-100."
        )


# ============================================================
# GITHUB FOOTER
# ============================================================

def build_github_footer(
    github: str,
    language: str = DEFAULT_LANGUAGE,
) -> str:
    language = normalize_language(language)
    github = clean_single_line(github)

    if not github:
        return ""

    if language == "en":
        return (
            "For more information about my technical "
            "projects and code, please visit my GitHub "
            f"profile: {github}"
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
    validate_company(company)

    language = normalize_language(language)

    applicant = build_applicant_context(
        load_json("applicant.json")
    )

    job = build_job_context(company)

    templates = load_templates(language)
    validate_all_templates(templates)

    selected_type = choose_template_type(
        company=company,
        templates=templates,
        requested_type=template_type,
    )

    selected_template = templates[selected_type]

    selected_style = choose_style(
        template=selected_template,
        company=company,
        requested_style=template_style,
    )

    style = selected_template[selected_style]

    variables = build_variables(
        applicant=applicant,
        job=job,
        language=language,
    )

    rng = random.Random(seed)

    section_order = get_section_order(style)
    sections: dict[str, str] = {}

    for section_name in section_order:
        definition = get_section(
            style,
            section_name,
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

    text = assemble_application(
        sections,
        section_order,
    )

    if not text:
        raise ValueError(
            "Das Template hat keinen Inhalt "
            "für die Bewerbung erzeugt."
        )

    github_footer = build_github_footer(
        applicant.github,
        language,
    )

    if github_footer:
        text = clean_text(
            f"{text}\n\n{github_footer}"
        )

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

    validate_application_result(result)

    return result


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def generate_application_text(
    company: dict[str, Any],
    *,
    template_type: str | None = None,
    template_style: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    seed: int | None = None,
) -> GeneratedApplication:
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
    return generate_application(
        company=company,
        template_type=template_type,
        template_style=template_style,
        language=language,
        seed=seed,
    ).text


# ============================================================
# PREVIEW
# ============================================================

def preview_application(
    company: dict[str, Any],
    *,
    template_type: str | None = None,
    template_style: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    seed: int | None = None,
) -> str:
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
            language,
        )
        or "Keine"
    )

    missing = (
        format_list(
            result.missing_keywords,
            language,
        )
        or "Keine"
    )

    template_path = get_template_path(
        result.template_type,
        result.language,
    )

    lines = [
        "",
        "Bewerbungsvorschau",
        "",
        "=" * 60,
        "",
        "Unternehmen:",
        result.company_name,
        "",
        "Position:",
        result.position,
        "",
        "Company-ID:",
        result.company_id or "Keine",
        "",
        "Job-ID:",
        result.job_id or "Keine",
        "",
        "Template:",
        result.template_type,
        "",
        "Template-Datei:",
        str(template_path),
        "",
        "Style:",
        result.template_style,
        "",
        "Sprache:",
        result.language,
        "",
        "Match Score:",
        format_score(result.match_score),
        "",
        "Confidence Score:",
        format_score(result.confidence_score),
        "",
        "Gematchte Kenntnisse:",
        matched,
        "",
        "Fehlende Kenntnisse:",
        missing,
        "",
        "-" * 60,
        "",
        "ANSCHREIBEN",
        "",
        "-" * 60,
        "",
        result.text,
        "",
        "=" * 60,
    ]

    return "\n".join(lines).strip()