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
    "salutation",
    "opening",
    "experience",
    "job_connection",
    "motivation",
    "closing",
]

SUPPORTED_PLACEHOLDERS = {
    # --------------------------------------------------------
    # Company
    # --------------------------------------------------------
    "company_name",
    "company_type",
    "company_size",
    "company_id",
    "relevant_keywords",

    # --------------------------------------------------------
    # Job
    # --------------------------------------------------------
    "position",
    "location",
    "job_id",
    "job_type",
    "seniority",
    "employment_type",
    "remote_type",
    "source_url",

    # --------------------------------------------------------
    # Applicant
    # --------------------------------------------------------
    "first_name",
    "last_name",
    "full_name",
    "email",
    "phone",
    "address",
    "zip_code",
    "city",
    "github",

    # --------------------------------------------------------
    # Keywords
    # --------------------------------------------------------
    "applicant_keywords",
    "job_keywords",
    "matched_keywords",
    "missing_keywords",

    # --------------------------------------------------------
    # Matching
    # --------------------------------------------------------
    "match_score",
    "confidence_score",

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------
    "experience",
}

DEFAULT_APPLICATION_SKILLS = [
    "Python",
    "Linux",
    "IT-Sicherheit",
]


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class JobContext:
    """
    Enthält alle Informationen zur ausgeschriebenen Stelle.

    Die Daten kommen ausschließlich aus dem manuell gepflegten
    companies.json bzw. aus vorgelagerten Modulen wie matcher.py.
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

    job_keywords: list[str] = field(
        default_factory=list
    )

    matched_keywords: list[str] = field(
        default_factory=list
    )

    relevant_keywords: list[str] = field(
        default_factory=list
    )

    missing_keywords: list[str] = field(
        default_factory=list
    )

    experience: list[str] = field(
        default_factory=list
    )

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
    skills: list[str] = field(
        default_factory=list
    )
    experience: list[str] = field(
        default_factory=list
    )


@dataclass
class GeneratedApplication:
    """
    Ergebnis einer vollständig generierten Bewerbung.
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
    sections: dict[str, str] = field(
        default_factory=dict
    )
    match_score: float = 0.0
    confidence_score: float = 0.0
    company_id: str = ""
    job_id: str = ""
    source_url: str = ""

# ============================================================
# JSON
# ============================================================

def load_json(
    filename: str,
) -> dict[str, Any]:
    """
    Lädt eine JSON-Datei aus data/.

    Beispiel:

        data = load_json("applicant.json")
    """

    path = DATA_DIR / filename

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

def get_company(
    company_id: str,
) -> dict[str, Any]:
    """
    Sucht ein Unternehmen anhand seiner ID.

    Wird vom CLI verwendet:

        python main.py --company example-security
    """

    company_id = clean_text(company_id)

    if not company_id:
        raise ValueError(
            "Keine Company-ID angegeben."
        )

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

    for company in companies:

        if not isinstance(
            company,
            dict,
        ):
            continue

        current_id = clean_text(
            company.get("id")
        )

        if current_id == company_id:
            return company

    raise ValueError(
        f"Unternehmen '{company_id}' nicht gefunden."
    )


# ============================================================
# TEXT HELPERS
# ============================================================

def clean_text(
    value: Any,
) -> str:
    """
    Normalisiert einen Wert zu sauberem Text.

    Eigenschaften:

    - None -> ""
    - CRLF -> LF
    - CR -> LF
    - mehrere Spaces -> ein Space
    - maximal zwei aufeinanderfolgende Leerzeilen
    """

    if value is None:
        return ""

    text = str(value)

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    # Mehrere Spaces/Tabs reduzieren.
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Mehr als zwei Leerzeilen verhindern.
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def clean_single_line(
    value: Any,
) -> str:
    """
    Bereinigt einen Wert und entfernt Zeilenumbrüche.

    Geeignet für:

    - Company Name
    - Position
    - Ort
    - IDs
    """

    text = clean_text(value)

    text = text.replace(
        "\n",
        " ",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def unique_strings(
    values: list[Any],
) -> list[str]:
    """
    Entfernt Duplikate und behält die Reihenfolge.
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
    Validiert und normalisiert eine String-Liste.
    """

    if value is None:
        return []

    if not isinstance(
        value,
        list,
    ):
        raise ValueError(
            f"'{field_name}' muss eine Liste sein."
        )

    return unique_strings(
        value
    )


def format_list(
    values: list[str],
    language: str = DEFAULT_LANGUAGE,
) -> str:

    language = clean_single_line(language).casefold()

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Nicht unterstützte Sprache: '{language}'."
        )

    values = unique_strings(values)

    if not values:
        return ""

    if len(values) == 1:
        return values[0]

    conjunction = (
        "and"
        if language == "en"
        else "und"
    )

    if len(values) == 2:
        return (
            f"{values[0]} {conjunction} {values[1]}"
        )

    return (
        ", ".join(values[:-1])
        + f" {conjunction} {values[-1]}"
    )


def format_keywords(
    keywords: list[str],
    language: str = DEFAULT_LANGUAGE,
) -> str:
    return format_list(
        keywords,
        language=language,
    )


def format_score(
    value: Any,
) -> str:
    """
    Formatiert einen Score für Templates.

    Beispiel:

        82.456
        -> 82.5 %

        90
        -> 90.0 %
    """

    try:
        score = float(value)
    except (
        TypeError,
        ValueError,
    ):
        score = 0.0

    score = max(
        0.0,
        min(
            100.0,
            score,
        ),
    )

    return f"{score:.1f} %"


# ============================================================
# APPLICANT CONTEXT
# ============================================================

def build_applicant_context(
    applicant: dict[str, Any],
) -> ApplicantContext:
    """
    Erstellt einen validierten ApplicantContext.
    """

    if not isinstance(
        applicant,
        dict,
    ):
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
            "applicant.json: "
            "'first_name' fehlt."
        )

    if not last_name:
        raise ValueError(
            "applicant.json: "
            "'last_name' fehlt."
        )

    skills = ensure_string_list(
        applicant.get(
            "skills",
            [],
        ),
        "skills",
    )

    experience = ensure_string_list(
        applicant.get(
            "experience",
            [],
        ),
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

def _read_score(
    value: Any,
) -> float:
    """
    Liest einen numerischen Score.

    Werte außerhalb von 0-100 werden begrenzt.
    """

    try:
        score = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    return max(
        0.0,
        min(
            100.0,
            score,
        ),
    )


def build_job_context(
    company: dict[str, Any],
) -> JobContext:
    """
    Erstellt einen validierten JobContext.

    Wichtig:

    Das Matching selbst findet NICHT hier statt.

    matched_keywords,
    missing_keywords,
    match_score und
    confidence_score

    können vorher von matcher.py berechnet
    und anschließend an company angehängt werden.
    """

    if not isinstance(
        company,
        dict,
    ):
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
        company.get(
            "keywords",
            [],
        ),
        "keywords",
    )

    matched_keywords = ensure_string_list(
        company.get(
            "matched_keywords",
            [],
        ),
        "matched_keywords",
    )


    relevant_keywords = ensure_string_list(
        company.get(
            "relevant_keywords",
            [],
        ),
        "relevant_keywords",
    )

    missing_keywords = ensure_string_list(
        company.get(
            "missing_keywords",
            [],
        ),
        "missing_keywords",
    )

    experience = ensure_string_list(
        company.get(
            "experience",
            [],
        ),
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

    full_name = (
        f"{applicant.first_name} "
        f"{applicant.last_name}"
    )

    # ----------------------------------------------------
    # Matching
    # ----------------------------------------------------

    matched_keywords = unique_strings(
        job.matched_keywords
    )

    # ----------------------------------------------------
    # Application Experience
    # ----------------------------------------------------

    application_experience = (
        matched_keywords
        if matched_keywords
        else DEFAULT_APPLICATION_SKILLS
    )

    # ----------------------------------------------------
    # Relevant Keywords
    # ----------------------------------------------------

    relevant_keywords = unique_strings(
        job.relevant_keywords
    )

    application_relevant_keywords = (
        relevant_keywords
        if relevant_keywords
        else application_experience
    )

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

        # Echte Matchergebnisse
        "matched_keywords": format_list(
            matched_keywords,
            language=language,
        ),

        # Für den Bewerbungstext:
        # echte relevante Keywords oder kontrollierter Fallback
        "relevant_keywords": format_list(
            application_relevant_keywords,
            language=language,
        ),

        "missing_keywords": format_list(
            job.missing_keywords,
            language=language,
        ),

        # Für {experience}:
        # echte Matches oder kontrollierter Fallback
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
    Findet alle Placeholder in einem Template.

    Beispiel:

        "Hallo {first_name}"

    -> ["first_name"]
    """

    if not text:
        return []

    return list(
        dict.fromkeys(
            PLACEHOLDER_PATTERN.findall(
                text
            )
        )
    )


def validate_placeholders(
    text: str,
    variables: dict[str, str],
) -> None:
    """
    Prüft:

    1. ob Placeholder offiziell unterstützt werden
    2. ob für jeden Placeholder eine Variable existiert
    """

    placeholders = find_placeholders(
        text
    )

    for placeholder in placeholders:

        if (
            placeholder
            not in SUPPORTED_PLACEHOLDERS
        ):
            raise ValueError(
                "Unbekannter "
                f"Template-Platzhalter: "
                f"{{{placeholder}}}"
            )

        if (
            placeholder
            not in variables
        ):
            raise ValueError(
                "Keine Variable für "
                f"{{{placeholder}}} vorhanden."
            )


def render_text(
    text: str,
    variables: dict[str, str],
) -> str:
    """
    Rendert einen einzelnen Template-Text.
    """

    text = clean_text(
        text
    )

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

    return clean_text(
        rendered
    )


# ============================================================
# TEMPLATE SELECTION
# ============================================================

def get_available_styles(
    template: dict[str, Any],
) -> list[str]:
    """
    Gibt alle verfügbaren Styles eines Template-Typs zurück.

    Der Schlüssel 'order' wird ignoriert.
    """

    if not isinstance(
        template,
        dict,
    ):
        return []

    styles: list[str] = []

    for name, value in template.items():

        if name == "order":
            continue

        if isinstance(
            value,
            dict,
        ):
            styles.append(
                name
            )

    return styles


def choose_style(
    template: dict[str, Any],
    company: dict[str, Any],
    requested_style: str | None = None,
) -> str:
    """
    Entscheidet, welcher Template-Stil verwendet wird.

    Priorität:

    1. explizit angegebener Style
    2. company.template_style
    3. company.size
    4. formal
    5. erster verfügbarer Style
    """

    available = get_available_styles(
        template
    )

    if not available:
        raise ValueError(
            "Template enthält keine Styles."
        )

    # --------------------------------------------------------
    # 1. Manuell angefordert
    # --------------------------------------------------------

    if requested_style:

        requested_style = clean_text(
            requested_style
        )

        if requested_style not in available:

            raise ValueError(
                f"Template-Stil "
                f"'{requested_style}' "
                "nicht verfügbar. "
                f"Verfügbar: "
                f"{', '.join(available)}"
            )

        return requested_style

    # --------------------------------------------------------
    # 2. Company override
    # --------------------------------------------------------

    company_style = clean_text(
        company.get(
            "template_style"
        )
    )

    if company_style in available:
        return company_style

    # --------------------------------------------------------
    # 3. Automatische Auswahl nach Größe
    # --------------------------------------------------------

    company_size = clean_text(
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
        ],

        "medium": [
            "formal",
            "technical",
            "modern",
        ],

        "large": [
            "formal",
            "technical",
        ],

        "enterprise": [
            "formal",
            "technical",
        ],
    }

    for candidate in size_mapping.get(
        company_size,
        [],
    ):

        if candidate in available:
            return candidate

    # --------------------------------------------------------
    # 4. Formal bevorzugen
    # --------------------------------------------------------

    if (
        DEFAULT_TEMPLATE_STYLE
        in available
    ):
        return DEFAULT_TEMPLATE_STYLE

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
    Ermittelt die Reihenfolge der Abschnitte.

    Wenn das Template 'order' definiert,
    wird diese verwendet.

    Sonst DEFAULT_SECTION_ORDER.
    """

    if not isinstance(
        style,
        dict,
    ):
        raise ValueError(
            "Template-Style muss "
            "ein Objekt sein."
        )

    custom_order = style.get(
        "order"
    )

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

            section = clean_single_line(
                section
            )

            if section:
                result.append(
                    section
                )

        if result:
            return result

    return DEFAULT_SECTION_ORDER.copy()


def get_section(
    style: dict[str, Any],
    section_name: str,
) -> Any:
    """
    Holt einen Abschnitt aus dem Template.

    Fehlende Abschnitte sind erlaubt.
    """

    return style.get(
        section_name
    )


# ============================================================
# SENTENCE SELECTION
# ============================================================

def normalize_options(
    value: Any,
) -> list[str]:
    """
    Macht aus unterschiedlichen Template-Formaten
    immer eine Liste.

    Erlaubt:

        "Text"

    oder:

        [
            "Text 1",
            "Text 2"
        ]
    """

    if value is None:
        return []

    if isinstance(
        value,
        str,
    ):
        value = [
            value
        ]

    if not isinstance(
        value,
        list,
    ):
        raise ValueError(
            "Template-Abschnitt "
            "muss String oder Liste sein."
        )

    result: list[str] = []

    for item in value:

        if not isinstance(
            item,
            str,
        ):
            raise ValueError(
                "Template-Varianten "
                "müssen Strings sein."
            )

        item = clean_text(
            item
        )

        if item:
            result.append(
                item
            )

    return result


def choose_sentence(
    sentences: list[str],
    variables: dict[str, str],
    rng: random.Random,
) -> str:
    """
    Wählt zufällig eine Variante und rendert sie.
    """

    if not sentences:
        return ""

    sentence = rng.choice(
        sentences
    )

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
    Generiert einen einzelnen Abschnitt.

    Unterstützte Formen:

        "opening": "Text"

    oder:

        "opening": [
            "Text 1",
            "Text 2"
        ]

    oder:

        "opening": {
            "variants": [
                "Text 1",
                "Text 2"
            ]
        }

    oder:

        "opening": {
            "required": true,
            "variants": [
                "Text 1"
            ]
        }
    """

    if section_definition is None:
        return ""

    # --------------------------------------------------------
    # Einfacher String
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
    # Liste
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
    # Objekt
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
    Baut die einzelnen Abschnitte
    zu einem Bewerbungstext zusammen.
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

        paragraphs.append(
            text
        )

    return (
        "\n\n".join(
            paragraphs
        ).strip()
    )


# ============================================================
# TEMPLATE VALIDATION
# ============================================================

def validate_template(
    template_type: str,
    template: dict[str, Any],
) -> None:
    """
    Prüft einen kompletten Template-Typ.
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

        style = template[
            style_name
        ]

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
                options = [
                    definition
                ]

            # ------------------------------------------------
            # Liste
            # ------------------------------------------------

            elif isinstance(
                definition,
                list,
            ):
                options = normalize_options(
                    definition
                )

            # ------------------------------------------------
            # Objekt
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

            # ------------------------------------------------
            # Placeholder prüfen
            # ------------------------------------------------

            for option in options:

                placeholders = find_placeholders(
                    option
                )

                for placeholder in placeholders:

                    if (
                        placeholder
                        not in SUPPORTED_PLACEHOLDERS
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
    Validiert alle Templates.
    """

    if not isinstance(
        templates,
        dict,
    ):
        raise ValueError(
            "templates.json muss "
            "ein Objekt enthalten."
        )

    if not templates:
        raise ValueError(
            "templates.json enthält "
            "keine Templates."
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
# TEMPLATE LOADING
# ============================================================

def load_templates(
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, Any]:

    language = clean_single_line(language).casefold()

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Nicht unterstützte Sprache: '{language}'. "
            f"Verfügbar: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )

    if language == "en":
        filename = "templates_en.json"
    else:
        filename = "templates.json"

    templates = load_json(filename)
    validate_all_templates(templates)

    return templates


# ============================================================
# TEMPLATE TYPE SELECTION
# ============================================================

def choose_template_type(
    company: dict[str, Any],
    templates: dict[str, Any],
    requested_type: str | None = None,
) -> str:
    """
    Bestimmt den Template-Typ.

    Priorität:

    1. expliziter Typ
    2. company.template
    3. company.type
    4. einfache Klassifizierung
    5. generischer Fallback
    """

    available = list(
        templates.keys()
    )

    if not available:
        raise ValueError(
            "templates.json enthält "
            "keine Templates."
        )

    # --------------------------------------------------------
    # 1. Explizit
    # --------------------------------------------------------

    if requested_type:

        requested_type = clean_text(
            requested_type
        )

        if requested_type not in templates:

            raise ValueError(
                f"Template-Typ "
                f"'{requested_type}' "
                "nicht vorhanden. "
                f"Verfügbar: "
                f"{', '.join(available)}"
            )

        return requested_type

    # --------------------------------------------------------
    # 2. Company Template
    # --------------------------------------------------------

    company_template = clean_text(
        company.get(
            "template"
        )
    )

    if company_template in templates:
        return company_template

    # --------------------------------------------------------
    # 3. Company Type
    # --------------------------------------------------------

    company_type = clean_text(
        company.get(
            "type"
        )
    ).casefold()

    if company_type in templates:
        return company_type

    # --------------------------------------------------------
    # 4. Automatische einfache Klassifizierung
    # --------------------------------------------------------

    position = clean_text(
        company.get(
            "position"
        )
    ).casefold()

    keywords = company.get(
        "keywords",
        [],
    )

    if isinstance(
        keywords,
        list,
    ):
        keyword_text = format_list(
            keywords
        ).casefold()
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
    ]

    if any(
        word in text
        for word in cybersecurity_words
    ):
        if "cybersecurity" in templates:
            return "cybersecurity"

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
        "softwareentwicklung",
        "softwareentwicklung",
    ]

    if any(
        word in text
        for word in software_words
    ):
        if "software" in templates:
            return "software"

    # --------------------------------------------------------
    # IT
    # --------------------------------------------------------

    it_words = [
        "systemadministrator",
        "system administration",
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
    ]

    if any(
        word in text
        for word in it_words
    ):
        if "it" in templates:
            return "it"

    # --------------------------------------------------------
    # Generischer Fallback
    # --------------------------------------------------------

    if "it" in templates:
        return "it"

    return available[0]


# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_company(
    company: dict[str, Any],
) -> None:
    """
    Führt grundlegende Validierungen für
    einen Company-Datensatz durch.

    Dies ersetzt NICHT die JSON-Schema-Validierung,
    sondern verhindert offensichtliche Fehler
    zur Laufzeit.
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

    company_id = company.get(
        "id"
    )

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
    Prüft das fertige Generator-Ergebnis.
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

    if (
        not 0.0
        <= result.match_score
        <= 100.0
    ):
        raise ValueError(
            "match_score liegt "
            "außerhalb von 0-100."
        )

    if (
        not 0.0
        <= result.confidence_score
        <= 100.0
    ):
        raise ValueError(
            "confidence_score liegt "
            "außerhalb von 0-100."
        )



def build_github_footer(
    github: str,
    language: str = DEFAULT_LANGUAGE,
) -> str:

    language = clean_single_line(language).casefold()

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
    Hauptfunktion des Generators.

    Beispiel:

        result = generate_application(
            company,
            template_type="cybersecurity",
            template_style="technical",
        )

        print(result.text)

    Wichtig:

    Das Matching erfolgt außerhalb dieses Moduls.

    Beispiel:

        from app.matching.matcher import (
            apply_match_result,
            match_job,
        )

        result = match_job(
            applicant,
            company,
        )

        company = apply_match_result(
            company,
            result,
        )

        application = generate_application(
            company
        )
    """

    # --------------------------------------------------------
    # Validate company
    # --------------------------------------------------------

    validate_company(
        company
    )

    # --------------------------------------------------------
    # Load applicant
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
    # Templates
    # --------------------------------------------------------

    templates = load_templates(language)

    # --------------------------------------------------------
    # Template Type
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
    # Template Style
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

    rng = random.Random(
        seed
    )

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
            sections[
                section_name
            ] = generated

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
    # GitHub Footer
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
# BACKWARD COMPATIBILITY
# ============================================================

def generate_letter(
    company: dict[str, Any],
    *,
    template_type: str | None = None,
    template_style: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    seed: int | None = None,
) -> str:
    """
    Kompatibilität mit dem bisherigen Generator.

    Der alte Aufruf:

        generate_letter(company)

    funktioniert weiterhin.

    Intern wird jetzt der Production-Generator verwendet.
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
    Erstellt eine menschenlesbare Vorschau
    inklusive Template- und Matching-Informationen.
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
            result.matched_keywords
        )
        or "Keine"
    )

    missing = (
        format_list(
            result.missing_keywords
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
        "Style:\n"
        f"{result.template_style}\n"
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