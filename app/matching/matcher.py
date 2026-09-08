from __future__ import annotations

import json
import re

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from config import DATA_DIR


# ============================================================
# CONSTANTS
# ============================================================

KEYWORDS_FILE = "keywords.json"

DEFAULT_MATCH_THRESHOLD = 0.0
DEFAULT_WEIGHT = 5.0

# Verhindert beispielsweise, dass "C" in jedem Wort gefunden wird.
MIN_SHORT_ALIAS_LENGTH = 2

# Sehr kurze Aliases, die ohne Boundary-Prüfung problematisch wären.
SHORT_ALIAS_PATTERN = re.compile(r"^[a-zA-Z0-9+#.-]+$")


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass(frozen=True)
class KeywordDefinition:
    """
    Eine kanonische Skill-/Technologie-Definition.

    Beispiel:

        name = "Python"
        category = "programming"
        weight = 10
        level = "core"
        aliases = ("python", "python 3", "python3")
    """

    name: str
    category: str
    weight: float
    level: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class KeywordMatch:
    """
    Ergebnis eines einzelnen Keyword-Matches.
    """

    keyword: str
    category: str
    weight: float
    level: str
    matched_alias: str
    source: str


@dataclass
class MatchResult:
    """
    Vollständiges Ergebnis des Bewerber-/Job-Matchings.
    """

    score: float

    matched_keywords: list[str] = field(default_factory=list)
    relevant_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)

    matched_details: list[KeywordMatch] = field(default_factory=list)

    job_keywords: list[str] = field(default_factory=list)
    applicant_keywords: list[str] = field(default_factory=list)

    job_type: str = ""
    job_type_score: float = 0.0

    seniority: str = ""
    seniority_score: float = 0.0

    employment_type: str = ""
    employment_score: float = 0.0

    remote_type: str = ""
    remote_score: float = 0.0

    confidence: float = 0.0


# ============================================================
# JSON LOADING
# ============================================================

def load_json(filename: str) -> dict[str, Any]:
    """
    Lädt eine JSON-Datei aus data/.
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


def load_keyword_data() -> dict[str, Any]:
    """
    Lädt keywords.json.
    """

    return load_json(KEYWORDS_FILE)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value: Any) -> str:
    """
    Normalisiert Text für Vergleiche.

    Beispiel:

        "  Cyber   Security "
        -> "cyber security"
    """

    if value is None:
        return ""

    text = str(value)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = text.casefold()

    # Unicode-artige Bindestriche vereinheitlichen.
    text = (
        text
        .replace("–", "-")
        .replace("—", "-")
        .replace("-", "-")
    )

    # Mehrfache Whitespaces.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def normalize_alias(value: Any) -> str:
    """
    Normalisiert ein Alias.

    Bindestriche und Leerzeichen werden für den Vergleich
    vereinheitlicht.

    Beispiel:

        "IT-Security"
        "IT Security"

    werden vergleichbarer.
    """

    text = normalize_text(value)

    text = re.sub(
        r"[-_/]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def unique_strings(
    values: Iterable[Any],
) -> list[str]:
    """
    Entfernt Duplikate und behält die ursprüngliche Reihenfolge.
    """

    result: list[str] = []
    seen: set[str] = set()

    for value in values:
        text = str(value).strip()

        if not text:
            continue

        key = normalize_alias(text)

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)
        result.append(text)

    return result


def build_text(
    values: Iterable[Any],
) -> str:
    """
    Verbindet mehrere Textfelder zu einem Suchtext.
    """

    parts = []

    for value in values:
        text = normalize_text(value)

        if text:
            parts.append(text)

    return " ".join(parts)


# ============================================================
# KEYWORD DEFINITIONS
# ============================================================

def load_keyword_definitions(
    data: dict[str, Any] | None = None,
) -> list[KeywordDefinition]:
    """
    Lädt sämtliche Keyword-Definitionen aus keywords.json.
    """

    if data is None:
        data = load_keyword_data()

    categories = data.get(
        "categories",
        {},
    )

    if not isinstance(categories, dict):
        raise ValueError(
            "keywords.json: 'categories' muss ein Objekt sein."
        )

    definitions: list[KeywordDefinition] = []

    for category_name, category_data in categories.items():

        if not isinstance(category_data, dict):
            continue

        keywords = category_data.get(
            "keywords",
            {},
        )

        if not isinstance(keywords, dict):
            continue

        for keyword_name, definition in keywords.items():

            if not isinstance(definition, dict):
                continue

            aliases = definition.get(
                "aliases",
                [],
            )

            if not isinstance(aliases, list):
                aliases = []

            aliases = unique_strings(
                [
                    keyword_name,
                    *aliases,
                ]
            )

            if not aliases:
                continue

            try:
                weight = float(
                    definition.get(
                        "weight",
                        DEFAULT_WEIGHT,
                    )
                )
            except (TypeError, ValueError):
                weight = DEFAULT_WEIGHT

            level = str(
                definition.get(
                    "level",
                    "basic",
                )
            ).strip().lower()

            definitions.append(
                KeywordDefinition(
                    name=str(keyword_name).strip(),
                    category=str(category_name).strip(),
                    weight=max(weight, 0.0),
                    level=level,
                    aliases=tuple(aliases),
                )
            )

    return definitions


# ============================================================
# ALIAS INDEX
# ============================================================

def build_alias_index(
    definitions: list[KeywordDefinition],
) -> dict[str, KeywordDefinition]:
    """
    Erstellt einen schnellen Alias-Index.

    Beispiel:

        "python" -> KeywordDefinition("Python")
        "python3" -> KeywordDefinition("Python")
    """

    index: dict[str, KeywordDefinition] = {}

    for definition in definitions:

        for alias in definition.aliases:

            normalized = normalize_alias(alias)

            if not normalized:
                continue

            # Bei Konflikten gewinnt die Definition mit höherem Gewicht.
            existing = index.get(normalized)

            if existing is None:
                index[normalized] = definition
                continue

            if definition.weight > existing.weight:
                index[normalized] = definition

    return index


# ============================================================
# MATCHING HELPERS
# ============================================================

def alias_matches_text(
    text: str,
    alias: str,
) -> bool:
    """
    Prüft, ob ein Alias sicher im Text vorkommt.

    Es werden Wortgrenzen verwendet, um False Positives
    zu reduzieren.

    Beispiel:

        "python" findet "Python 3"

        "c" findet NICHT automatisch "security"
    """

    normalized_text = normalize_alias(text)
    normalized_alias = normalize_alias(alias)

    if not normalized_text or not normalized_alias:
        return False

    escaped = re.escape(
        normalized_alias
    )

    # Für sehr kurze Aliases besonders strikt.
    if len(normalized_alias) < MIN_SHORT_ALIAS_LENGTH:
        pattern = rf"(?<![\w+#]){escaped}(?![\w+#])"
    else:
        pattern = rf"(?<![\w]){escaped}(?![\w])"

    return re.search(
        pattern,
        normalized_text,
        flags=re.IGNORECASE,
    ) is not None


def find_keyword_match(
    text: str,
    definition: KeywordDefinition,
) -> str | None:
    """
    Gibt den tatsächlich gefundenen Alias zurück.
    """

    # Längere Aliases zuerst.
    aliases = sorted(
        definition.aliases,
        key=lambda value: len(
            normalize_alias(value)
        ),
        reverse=True,
    )

    for alias in aliases:

        if alias_matches_text(
            text,
            alias,
        ):
            return alias

    return None


# ============================================================
# APPLICANT KEYWORDS
# ============================================================

def detect_keywords(
    text: str,
    definitions: list[KeywordDefinition],
    *,
    source: str,
) -> list[KeywordMatch]:
    """
    Erkennt kanonische Keywords in einem Text.

    Wichtig:

        Die Funktion behauptet NICHT, dass der Bewerber
        einen Skill besitzt.

    Sie erkennt lediglich, dass ein Keyword im übergebenen
    Text vorhanden ist.
    """

    matches: list[KeywordMatch] = []

    for definition in definitions:

        matched_alias = find_keyword_match(
            text,
            definition,
        )

        if matched_alias is None:
            continue

        matches.append(
            KeywordMatch(
                keyword=definition.name,
                category=definition.category,
                weight=definition.weight,
                level=definition.level,
                matched_alias=matched_alias,
                source=source,
            )
        )

    return matches


# ============================================================
# APPLICANT MATCHING
# ============================================================

def detect_applicant_keywords(
    applicant: dict[str, Any],
    definitions: list[KeywordDefinition],
) -> list[KeywordMatch]:
    """
    Erkennt Skills des Bewerbers.

    Es werden ausschließlich explizit in applicant.json
    angegebene Skills und Erfahrungen verwendet.
    """

    skills = applicant.get(
        "skills",
        [],
    )

    experience = applicant.get(
        "experience",
        [],
    )

    if not isinstance(skills, list):
        skills = []

    if not isinstance(experience, list):
        experience = []

    text = build_text(
        [
            *skills,
            *experience,
        ]
    )

    return detect_keywords(
        text=text,
        definitions=definitions,
        source="applicant",
    )


# ============================================================
# JOB MATCHING
# ============================================================

def detect_job_keywords(
    company: dict[str, Any],
    definitions: list[KeywordDefinition],
) -> list[KeywordMatch]:
    """
    Erkennt Keywords aus den manuell eingetragenen
    Jobinformationen.

    Wir verwenden dafür insbesondere:

        position
        keywords
        requirements
        description
        responsibilities
    """

    fields: list[Any] = [
        company.get("position", ""),
        company.get("keywords", []),
        company.get("requirements", []),
        company.get("description", ""),
        company.get("responsibilities", []),
    ]

    flattened: list[Any] = []

    for field in fields:

        if isinstance(field, list):
            flattened.extend(field)
        else:
            flattened.append(field)

    text = build_text(
        flattened
    )

    return detect_keywords(
        text=text,
        definitions=definitions,
        source="job",
    )


# ============================================================
# CANONICAL KEYWORD SETS
# ============================================================

def keyword_names(
    matches: Iterable[KeywordMatch],
) -> list[str]:
    """
    Extrahiert eindeutige kanonische Keyword-Namen.
    """

    return unique_strings(
        match.keyword
        for match in matches
    )


# ============================================================
# MATCH SCORE
# ============================================================

def calculate_match_score(
    job_matches: list[KeywordMatch],
    applicant_matches: list[KeywordMatch],
) -> float:
    """
    Berechnet einen gewichteten Match-Score.

    Formel:

        Summe der Gewichte gematchter Job-Keywords
        /
        Summe der Gewichte aller Job-Keywords
        * 100

    Damit zählt ein wichtiges Keyword stärker als ein
    nebensächliches Keyword.

    Beispiel:

        Python = 10
        HTML = 5

        Bewerber hat Python.

        Score = 10 / 15 * 100
              = 66.67
    """

    if not job_matches:
        return 0.0

    applicant_names = {
        normalize_alias(match.keyword)
        for match in applicant_matches
    }

    total_weight = sum(
        match.weight
        for match in job_matches
    )

    if total_weight <= 0:
        return 0.0

    matched_weight = sum(
        match.weight
        for match in job_matches
        if normalize_alias(match.keyword)
        in applicant_names
    )

    score = (
        matched_weight
        / total_weight
        * 100
    )

    return round(
        min(max(score, 0.0), 100.0),
        2,
    )


# ============================================================
# MATCHED / MISSING
# ============================================================

def calculate_matched_keywords(
    job_matches: list[KeywordMatch],
    applicant_matches: list[KeywordMatch],
) -> tuple[list[str], list[str]]:
    """
    Ermittelt:

        matched_keywords
        missing_keywords
    """

    applicant_names = {
        normalize_alias(match.keyword)
        for match in applicant_matches
    }

    matched: list[str] = []
    missing: list[str] = []

    for match in job_matches:

        key = normalize_alias(
            match.keyword
        )

        if key in applicant_names:
            matched.append(
                match.keyword
            )
        else:
            missing.append(
                match.keyword
            )

    return (
        unique_strings(matched),
        unique_strings(missing),
    )




def get_relevant_keywords(
    job_matches: list[KeywordMatch],
    applicant_matches: list[KeywordMatch],
    limit: int = 4,
) -> list[str]:
    """
    Gibt die wichtigsten gematchten Keywords zurück.

    Die Auswahl erfolgt anhand des Gewichts des Job-Keywords.
    Höher gewichtete Keywords werden bevorzugt.
    """

    applicant_names = {
        normalize_alias(match.keyword)
        for match in applicant_matches
    }

    matched = [
        match
        for match in job_matches
        if normalize_alias(match.keyword)
        in applicant_names
    ]

    matched.sort(
        key=lambda match: match.weight,
        reverse=True,
    )

    return unique_strings(
        match.keyword
        for match in matched[:limit]
    )
# ============================================================
# JOB TYPE
# ============================================================

def classify_job_type(
    company: dict[str, Any],
    data: dict[str, Any],
    definitions: list[KeywordDefinition],
) -> tuple[str, float]:
    """
    Bestimmt den Jobtyp anhand von:

        1. explizitem company.type
        2. position_patterns
        3. Keyword-Überschneidungen

    Rückgabe:

        ("cybersecurity", 92.0)
    """

    job_types = data.get(
        "job_types",
        {},
    )

    if not isinstance(job_types, dict):
        return "", 0.0

    explicit_type = normalize_text(
        company.get("type")
    )

    if explicit_type in job_types:
        return (
            explicit_type,
            100.0,
        )

    position = normalize_text(
        company.get("position")
    )

    company_keywords = company.get(
        "keywords",
        [],
    )

    if not isinstance(company_keywords, list):
        company_keywords = []

    job_text = build_text(
        [
            position,
            *company_keywords,
            company.get("description", ""),
            company.get("requirements", []),
        ]
    )

    scores: dict[str, float] = {}

    definition_map = {
        normalize_alias(definition.name): definition
        for definition in definitions
    }

    for job_type, config in job_types.items():

        if not isinstance(config, dict):
            continue

        score = 0.0

        # ----------------------------------------------------
        # Position patterns
        # ----------------------------------------------------

        patterns = config.get(
            "position_patterns",
            [],
        )

        if isinstance(patterns, list):

            for pattern in patterns:

                pattern_text = normalize_text(
                    pattern
                )

                if not pattern_text:
                    continue

                if alias_matches_text(
                    position,
                    pattern_text,
                ):
                    score += 100.0
                    break

        # ----------------------------------------------------
        # Keyword matches
        # ----------------------------------------------------

        type_keywords = config.get(
            "keywords",
            [],
        )

        if isinstance(type_keywords, list):

            for keyword in type_keywords:

                definition = definition_map.get(
                    normalize_alias(keyword)
                )

                if definition is None:
                    continue

                if find_keyword_match(
                    job_text,
                    definition,
                ):
                    score += max(
                        definition.weight,
                        1.0,
                    )

        scores[job_type] = score

    if not scores:
        return "", 0.0

    ordered = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    best_type, best_score = ordered[0]

    if best_score <= 0:
        return "", 0.0

    second_score = (
        ordered[1][1]
        if len(ordered) > 1
        else 0.0
    )

    # Confidence steigt, wenn der beste Typ deutlich
    # vor dem zweiten liegt.
    if best_score >= 100:
        confidence = 100.0
    else:
        total = best_score + second_score

        if total <= 0:
            confidence = 0.0
        else:
            confidence = (
                best_score
                / total
                * 100
            )

    return (
        best_type,
        round(
            min(confidence, 100.0),
            2,
        ),
    )


# ============================================================
# GENERIC PATTERN CLASSIFICATION
# ============================================================

def classify_pattern_group(
    text: str,
    group: dict[str, Any],
) -> tuple[str, float]:
    """
    Klassifiziert eine Gruppe mit:

        {
            "junior": {
                "patterns": [...]
            }
        }

    """

    if not isinstance(group, dict):
        return "", 0.0

    scores: dict[str, float] = {}

    for name, config in group.items():

        if not isinstance(config, dict):
            continue

        patterns = config.get(
            "patterns",
            [],
        )

        if not isinstance(patterns, list):
            continue

        score = 0.0

        for pattern in patterns:

            pattern_text = normalize_text(
                pattern
            )

            if not pattern_text:
                continue

            if alias_matches_text(
                text,
                pattern_text,
            ):
                score += 1.0

        scores[name] = score

    if not scores:
        return "", 0.0

    ordered = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    best_name, best_score = ordered[0]

    if best_score <= 0:
        return "", 0.0

    second_score = (
        ordered[1][1]
        if len(ordered) > 1
        else 0.0
    )

    if best_score == second_score:
        confidence = 50.0
    else:
        confidence = (
            best_score
            / max(
                best_score + second_score,
                1.0,
            )
            * 100
        )

    return (
        best_name,
        round(
            confidence,
            2,
        ),
    )


# ============================================================
# SENIORITY
# ============================================================

def classify_seniority(
    company: dict[str, Any],
    data: dict[str, Any],
) -> tuple[str, float]:
    """
    Erkennt Junior/Mid/Senior anhand der Stellenbezeichnung
    und optionaler Beschreibung.
    """

    text = build_text(
        [
            company.get("position", ""),
            company.get("description", ""),
            company.get("requirements", []),
        ]
    )

    return classify_pattern_group(
        text,
        data.get(
            "seniority",
            {},
        ),
    )


# ============================================================
# EMPLOYMENT
# ============================================================

def classify_employment(
    company: dict[str, Any],
    data: dict[str, Any],
) -> tuple[str, float]:
    """
    Erkennt Vollzeit/Teilzeit.
    """

    text = build_text(
        [
            company.get("position", ""),
            company.get("description", ""),
            company.get("employment_type", ""),
            company.get("requirements", []),
        ]
    )

    group = {
        "full_time": data.get(
            "employment",
            {},
        ).get(
            "full_time",
            {},
        ),
        "part_time": data.get(
            "employment",
            {},
        ).get(
            "part_time",
            {},
        ),
    }

    return classify_pattern_group(
        text,
        group,
    )


# ============================================================
# REMOTE / WORK LOCATION
# ============================================================

def classify_remote_type(
    company: dict[str, Any],
    data: dict[str, Any],
) -> tuple[str, float]:
    """
    Erkennt:

        remote
        hybrid
        onsite
    """

    text = build_text(
        [
            company.get("location", ""),
            company.get("description", ""),
            company.get("remote_type", ""),
            company.get("employment_type", ""),
        ]
    )

    group = {
        "remote": data.get(
            "employment",
            {},
        ).get(
            "remote",
            {},
        ),
        "hybrid": data.get(
            "employment",
            {},
        ).get(
            "hybrid",
            {},
        ),
        "onsite": data.get(
            "employment",
            {},
        ).get(
            "onsite",
            {},
        ),
    }

    return classify_pattern_group(
        text,
        group,
    )


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_confidence(
    *,
    match_score: float,
    job_type_score: float,
    seniority_score: float,
    employment_score: float,
    remote_score: float,
) -> float:
    """
    Ermittelt eine Gesamt-Confidence.

    Der Skill-Match wird am stärksten gewichtet.
    """

    confidence = (
        match_score * 0.60
        + job_type_score * 0.20
        + seniority_score * 0.08
        + employment_score * 0.06
        + remote_score * 0.06
    )

    return round(
        min(
            max(
                confidence,
                0.0,
            ),
            100.0,
        ),
        2,
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_company(
    company: dict[str, Any],
) -> None:
    """
    Validiert die minimal notwendigen Jobdaten.

    Jeder Job muss zwingend eine gültige
    Empfänger-E-Mail-Adresse enthalten.
    """

    if not isinstance(company, dict):
        raise ValueError(
            "company muss ein Dictionary sein."
        )

    required_fields = (
        "name",
        "position",
        "email",
    )

    for field_name in required_fields:

        value = company.get(
            field_name
        )

        if not value:
            raise ValueError(
                f"company['{field_name}'] fehlt."
            )

    # --------------------------------------------------------
    # E-Mail validieren
    # --------------------------------------------------------

    email = company.get("email")

    if not isinstance(email, str):
        raise ValueError(
            "company['email'] muss ein String sein."
        )

    email = email.strip()

    if not email:
        raise ValueError(
            "company['email'] darf nicht leer sein."
        )

    # Bewusst einfache Validierung.
    # Die eigentliche SMTP-Prüfung erfolgt später.
    email_pattern = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    if not email_pattern.fullmatch(email):
        raise ValueError(
            f"Ungültige E-Mail-Adresse: {email!r}"
        )

    keywords = company.get(
        "keywords",
        [],
    )

    if keywords is not None and not isinstance(
        keywords,
        list,
    ):
        raise ValueError(
            "company['keywords'] muss eine Liste sein."
        )


def validate_applicant(
    applicant: dict[str, Any],
) -> None:
    """
    Validiert die Bewerberdaten.
    """

    if not isinstance(applicant, dict):
        raise ValueError(
            "applicant muss ein Dictionary sein."
        )

    for field_name in (
        "first_name",
        "last_name",
    ):
        if not applicant.get(field_name):
            raise ValueError(
                f"applicant['{field_name}'] fehlt."
            )

    for field_name in (
        "skills",
        "experience",
    ):
        value = applicant.get(
            field_name,
            [],
        )

        if not isinstance(
            value,
            list,
        ):
            raise ValueError(
                f"applicant['{field_name}'] "
                f"muss eine Liste sein."
            )


# ============================================================
# MAIN MATCH FUNCTION
# ============================================================

def match_job(
    *,
    applicant: dict[str, Any],
    company: dict[str, Any],
) -> MatchResult:
    """
    Führt das komplette Matching aus.

    Beispiel:

        result = match_job(
            applicant=applicant,
            company=company,
        )

    Ergebnis:

        result.score
        result.matched_keywords
        result.missing_keywords
        result.job_type
        result.seniority
        result.employment_type
        result.remote_type
        result.confidence
    """

    validate_applicant(
        applicant
    )

    validate_company(
        company
    )

    # --------------------------------------------------------
    # Load keyword database
    # --------------------------------------------------------

    data = load_keyword_data()

    definitions = load_keyword_definitions(
        data
    )

    if not definitions:
        raise ValueError(
            "keywords.json enthält keine Keyword-Definitionen."
        )

    # --------------------------------------------------------
    # Detect applicant skills
    # --------------------------------------------------------

    applicant_matches = detect_applicant_keywords(
        applicant=applicant,
        definitions=definitions,
    )

    # --------------------------------------------------------
    # Detect job requirements
    # --------------------------------------------------------

    job_matches = detect_job_keywords(
        company=company,
        definitions=definitions,
    )

    # --------------------------------------------------------
    # Matched / missing
    # --------------------------------------------------------

    matched_keywords, missing_keywords = (
        calculate_matched_keywords(
            job_matches=job_matches,
            applicant_matches=applicant_matches,
        )
    )


    relevant_keywords = get_relevant_keywords(
        job_matches=job_matches,
        applicant_matches=applicant_matches,
        limit=4,
    )

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    score = calculate_match_score(
        job_matches=job_matches,
        applicant_matches=applicant_matches,
    )

    # --------------------------------------------------------
    # Job type
    # --------------------------------------------------------

    job_type, job_type_score = classify_job_type(
        company=company,
        data=data,
        definitions=definitions,
    )

    # --------------------------------------------------------
    # Seniority
    # --------------------------------------------------------

    seniority, seniority_score = classify_seniority(
        company=company,
        data=data,
    )

    # --------------------------------------------------------
    # Employment
    # --------------------------------------------------------

    employment_type, employment_score = (
        classify_employment(
            company=company,
            data=data,
        )
    )

    # --------------------------------------------------------
    # Remote
    # --------------------------------------------------------

    remote_type, remote_score = (
        classify_remote_type(
            company=company,
            data=data,
        )
    )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = calculate_confidence(
        match_score=score,
        job_type_score=job_type_score,
        seniority_score=seniority_score,
        employment_score=employment_score,
        remote_score=remote_score,
    )

    # --------------------------------------------------------
    # Applicant / Job canonical keywords
    # --------------------------------------------------------

    applicant_keywords = keyword_names(
        applicant_matches
    )

    job_keywords = keyword_names(
        job_matches
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return MatchResult(
        score=score,

        matched_keywords=matched_keywords,
        relevant_keywords=relevant_keywords,
        missing_keywords=missing_keywords,

        matched_details=[
            match
            for match in job_matches
            if normalize_alias(
                match.keyword
            )
            in {
                normalize_alias(
                    keyword
                )
                for keyword in matched_keywords
            }
        ],

        job_keywords=job_keywords,
        applicant_keywords=applicant_keywords,

        job_type=job_type,
        job_type_score=job_type_score,

        seniority=seniority,
        seniority_score=seniority_score,

        employment_type=employment_type,
        employment_score=employment_score,

        remote_type=remote_type,
        remote_score=remote_score,

        confidence=confidence,
    )


# ============================================================
# COMPANY UPDATE HELPER
# ============================================================

def apply_match_result(
    company: dict[str, Any],
    result: MatchResult,
) -> dict[str, Any]:
    """
    Erstellt eine Kopie der Company-Daten und ergänzt
    die berechneten Matching-Daten.

    Original-Dictionary wird NICHT verändert.

    """

    updated = dict(
        company
    )

    updated[
        "job_keywords"
    ] = result.job_keywords

    updated[
        "matched_keywords"
    ] = result.matched_keywords

    updated[
        "relevant_keywords"
    ] = result.relevant_keywords

    updated[
        "missing_keywords"
    ] = result.missing_keywords

    updated[
        "match_score"
    ] = result.score

    updated[
        "job_type"
    ] = result.job_type

    updated[
        "job_type_score"
    ] = result.job_type_score

    updated[
        "seniority"
    ] = result.seniority

    updated[
        "seniority_score"
    ] = result.seniority_score

    updated[
        "employment_type"
    ] = result.employment_type

    updated[
        "employment_score"
    ] = result.employment_score

    updated[
        "remote_type"
    ] = result.remote_type

    updated[
        "remote_score"
    ] = result.remote_score

    updated[
        "match_confidence"
    ] = result.confidence

    return updated


# ============================================================
# JSON-SERIALIZABLE RESULT
# ============================================================

def result_to_dict(
    result: MatchResult,
) -> dict[str, Any]:
    """
    Wandelt MatchResult in ein JSON-kompatibles Dictionary um.

    Sehr praktisch für CLI, Logs und History.
    """

    return {
        "score": result.score,

        "matched_keywords": result.matched_keywords,
        "missing_keywords": result.missing_keywords,

        "job_keywords": result.job_keywords,
        "applicant_keywords": result.applicant_keywords,

        "job_type": result.job_type,
        "job_type_score": result.job_type_score,

        "seniority": result.seniority,
        "seniority_score": result.seniority_score,

        "employment_type": result.employment_type,
        "employment_score": result.employment_score,

        "remote_type": result.remote_type,
        "remote_score": result.remote_score,

        "confidence": result.confidence,

        "matched_details": [
            {
                "keyword": match.keyword,
                "category": match.category,
                "weight": match.weight,
                "level": match.level,
                "matched_alias": match.matched_alias,
                "source": match.source,
            }
            for match in result.matched_details
        ],
    }


# ============================================================
# PRETTY SUMMARY
# ============================================================

def format_match_summary(
    result: MatchResult,
) -> str:
    """
    Erstellt eine CLI-freundliche Zusammenfassung.
    """

    matched = (
        ", ".join(
            result.matched_keywords
        )
        if result.matched_keywords
        else "Keine"
    )

    missing = (
        ", ".join(
            result.missing_keywords
        )
        if result.missing_keywords
        else "Keine"
    )

    return (
        "\n"
        "============================================================\n"
        "JOB MATCHING\n"
        "============================================================\n"
        f"Match Score:       {result.score:.2f}%\n"
        f"Confidence:        {result.confidence:.2f}%\n"
        f"Job Type:          {result.job_type or 'Unbekannt'}\n"
        f"Seniority:         {result.seniority or 'Unbekannt'}\n"
        f"Employment:        {result.employment_type or 'Unbekannt'}\n"
        f"Remote:            {result.remote_type or 'Unbekannt'}\n"
        "\n"
        f"Matched:           {matched}\n"
        f"Missing:           {missing}\n"
        "============================================================"
    )