# ApplicationForge

# AI generierte Inhalte

## (free-version-ChatGPT)

> A production-ready Python CLI for creating, matching, packaging, and managing job applications.

**ApplicationForge** is a modular command-line application that automates repetitive parts of the job application process.

It combines applicant data, company/job data, document management, job matching, cover-letter generation, PDF creation, ZIP packaging, email delivery, and application history into one workflow.

The project is designed with a strong focus on **modularity, reproducibility, safe email delivery, structured data, and extensibility**.

---

## Features

- 📄 Applicant profile management
- 🏢 Company and job management using JSON
- 🎯 Applicant-to-job matching
- 📊 Match and confidence scores
- ✍️ Individual cover-letter generation
- 🌍 German and English application generation
- 🎨 Multiple template types and writing styles
- 📑 Automatic cover-letter PDF generation
- 📦 Automatic application ZIP creation
- 📧 Optional SMTP email delivery
- 🧪 Dry-run mode
- 👀 Cover-letter preview mode
- 📚 Application history
- 🔁 Duplicate application detection
- ⚡ Batch processing with `--send-all`
- 🌱 Reproducible generation using seeds
- 📝 Structured logging
- 🔒 Environment-based SMTP configuration
- 🧩 Modular Python architecture
- 💻 Fully CLI-based workflow

---

## How It Works

ApplicationForge follows a simple application pipeline:

```text
                  ┌─────────────────┐
                  │ applicant.json  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ companies.json  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    Matching     │
                  │                 │
                  │ Match Score     │
                  │ Confidence      │
                  │ Keywords        │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Cover Letter    │
                  │ Generator       │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   PDF Creator   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  ZIP Archive    │
                  └────────┬────────┘
                           │
                    ┌──────┴───────┐
                    │              │
                    ▼              ▼
                 Preview         Email
                    │              │
                    └──────┬───────┘
                           ▼
                  ┌─────────────────┐
                  │    History      │
                  └─────────────────┘
```

---

# Project Structure

A typical ApplicationForge installation looks like this:

```text
ApplicationForge/
│
├── app/
│   ├── application/
│   │   ├── generator.py
│   │   └── ...
│   │
│   ├── documents/
│   │   ├── archive.py
│   │   ├── converter.py
│   │   └── ...
│   │
│   ├── mail/
│   │   ├── sender.py
│   │   └── ...
│   │
│   └── matching/
│       ├── matcher.py
│       └── ...
│
├── data/
│   ├── applicant.json
│   ├── companies.json
│   └── history.json
│
├── Documents/
│   ├── cv.pdf
│   ├── certificates.pdf
│   ├── references.pdf
│   └── ...
│
├── generated/
│   ├── cover letters
│   └── application archives
│
├── config.py
├── main.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

The project is intentionally split into separate modules so that individual components can be developed, tested, and replaced independently.

---

# Requirements

- Python 3.10+
- pip
- SMTP account for email delivery
- A valid PDF/document directory

Optional:

- Virtual environment
- Git

---

# Installation

Clone the repository:

```bash
git clone https://github.com/your-username/ApplicationForge.git
cd ApplicationForge
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Configuration

ApplicationForge uses environment variables for sensitive configuration such as SMTP credentials.

Create your local environment file:

```bash
cp .env.example .env
```

Example:

```env
# ============================================================
# SMTP
# ============================================================

SMTP_HOST=smtp.example.com
SMTP_PORT=587

SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-smtp-password

SMTP_USE_TLS=true

MAIL_FROM=your-email@example.com
```

**Never commit `.env` to Git.**

The repository should only contain `.env.example`.

---

# Applicant Configuration

Applicant information is stored locally in:

```text
data/applicant.json
```

Example:

```json
{
  "first_name": "Max",
  "last_name": "Mustermann",

  "email": "max.mustermann@example.com",
  "phone": "+49 170 12345678",

  "address": "Musterstraße 1",
  "zip_code": "10115",
  "city": "Berlin",

  "github": "https://github.com/example-user",

  "skills": [
    "Python",
    "Linux",
    "Cyber Security",
    "Networking",
    "Git",
    "Web Development"
  ],

  "experience": [
    "Python development",
    "Linux administration",
    "REST API development",
    "Web development",
    "Security testing"
  ],

  "security_tools": ["Nmap", "Wireshark", "Ghidra"],

  "python_technologies": [
    "Python",
    "Django",
    "Flask",
    "REST APIs",
    "SQLite",
    "Argparse",
    "Logging"
  ]
}
```

A public repository should only contain an example file:

```text
data/applicant.json.example
```

Personal applicant data should remain local.

---

# Company Configuration

Companies and job postings are stored in:

```text
data/companies.json
```

Example:

```json
{
  "companies": [
    {
      "id": "example-security",
      "name": "Example Security GmbH",
      "email": "jobs@example.com",
      "type": "cybersecurity",
      "size": "enterprise",
      "location": "Berlin",

      "position": "Junior Security Analyst",

      "keywords": [
        "Cyber Security",
        "Penetration Testing",
        "Linux",
        "Python",
        "Networking",
        "Web Security"
      ],

      "requirements": [
        "Grundkenntnisse in Cyber Security",
        "Kenntnisse in Linux",
        "Python-Kenntnisse",
        "Netzwerkkenntnisse",
        "Analytisches Denken"
      ],

      "description": "Unterstützung bei Security Assessments, Schwachstellenanalysen und technischen Sicherheitsprüfungen."
    }
  ]
}
```

For public repositories, use:

```text
data/companies.json.example
```

with fictional data.

---

# Documents

ApplicationForge can collect documents from a configurable directory.

For example:

```text
Documents/
├── cv.pdf
├── zeugnis.pdf
├── arbeitszeugnis.pdf
├── ausbildungszeugnis.pdf
├── zertifikate.pdf
└── weiterbildungen.pdf
```

The default document directory is:

```text
Documents/
```

You can specify another directory using:

```bash
python main.py \
    --company example-security \
    --documents "/path/to/Documents"
```

---

# CLI

ApplicationForge is primarily controlled through the command line.

Basic syntax:

```bash
python main.py [OPTIONS]
```

---

## Show Help

```bash
python main.py --help
```

---

## List Companies

Display all configured companies:

```bash
python main.py --list-companies
```

This shows information such as:

- Company ID
- Company name
- Position
- Email
- Location
- Job type
- Seniority
- Employment type
- Remote model
- Keywords

---

# Generate an Application

Generate an application for a specific company:

```bash
python main.py --company example-security
```

The application pipeline will:

1. Load the applicant profile
2. Load the company
3. Check the document directory
4. Calculate the job match
5. Generate the cover letter
6. Create a PDF
7. Create the application ZIP
8. Store the application in history

No email is sent unless `--send` is explicitly specified.

---

# Preview a Cover Letter

To generate and display the cover letter:

```bash
python main.py \
    --company example-security \
    --preview
```

This is useful for checking the generated application before sending it.

---

# Matching

ApplicationForge includes a job matching system.

Run matching without generating documents:

```bash
python main.py \
    --company example-security \
    --match-only
```

Example output:

```text
================================================================================
MATCHING
================================================================================

Match Score:       87.5%
Confidence Score:  91.0%

Gematchte Kenntnisse:
  ✓ Python
  ✓ Linux
  ✓ Networking
  ✓ Cyber Security
  ✓ Web Security

Fehlende Kenntnisse:
  ✗ Vulnerability Assessment
```

The matching result can contain:

- Match score
- Confidence score
- Matched keywords
- Missing keywords
- Job type
- Seniority
- Employment type
- Remote model

---

# Templates

You can explicitly select a template:

```bash
python main.py \
    --company example-security \
    --template cybersecurity
```

You can also select a writing style:

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

Possible template/style names depend on the installed generator configuration.

Examples:

```text
cybersecurity
it
software
formal
technical
modern
```

---

# Languages

ApplicationForge supports multiple application languages.

German:

```bash
python main.py \
    --company example-security \
    --language de
```

English:

```bash
python main.py \
    --company example-security \
    --language en
```

The default language is:

```text
de
```

---

# Reproducible Generation

ApplicationForge supports deterministic generation through a seed.

Example:

```bash
python main.py \
    --company example-security \
    --seed 12345
```

Using the same seed and input data allows template selection and other randomized behavior to be reproduced.

This is useful for:

- Debugging
- Testing
- Development
- Reproducing application output

---

# Email Sending

To send an application:

```bash
python main.py \
    --company example-security \
    --send
```

By default, ApplicationForge asks for confirmation before sending.

Example:

```text
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ACHTUNG: E-MAIL WIRD VERSENDET
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Bewerber:    Max Mustermann
Unternehmen: Example Security GmbH
Position:    Junior Security Analyst
Empfänger:   jobs@example.com
Anhang:      generated/Application_Example_Security.zip

Bewerbung wirklich versenden? [y/N]:
```

This confirmation step is intentional.

It prevents accidental email delivery.

---

# Automatic Sending

To skip the confirmation:

```bash
python main.py \
    --company example-security \
    --send \
    --yes
```

Use this option carefully.

`--yes` should primarily be used when the sending process is already verified and trusted.

---

# Dry Run

ApplicationForge provides a dry-run mode.

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

A dry run:

- Creates the application
- Runs matching
- Generates the cover letter
- Creates the PDF
- Creates the ZIP
- Does **not** send an email
- Does **not** modify JSON data

Example:

```text
================================================================================
DRY-RUN – KEINE E-MAIL WIRD VERSENDET
================================================================================

Empfänger: jobs@example.com
Betreff: Bewerbung als Junior Security Analyst
Anhang: generated/Application_Example_Security.zip

→ Keine JSON-Datei wird verändert.
→ Keine E-Mail wurde versendet.
```

Dry-run mode is strongly recommended before using automated sending.

---

# Batch Processing

ApplicationForge can process all companies automatically:

```bash
python main.py --send-all
```

The companies are processed sequentially.

For every company:

```text
Load company
     ↓
Check history
     ↓
Match job
     ↓
Generate application
     ↓
Create PDF
     ↓
Create ZIP
     ↓
Send email
     ↓
Save history
     ↓
Remove company
```

A company is only removed from `companies.json` after the email delivery succeeds.

---

# Batch Dry Run

Before using the batch sender, it is recommended to test the entire process:

```bash
python main.py \
    --send-all \
    --dry-run
```

This allows the complete application-generation pipeline to be tested without sending email.

Companies remain in `companies.json`.

---

# Batch Output

Example:

```text
================================================================================
AUTOMATISCHER BEWERBUNGSVERSAND
================================================================================

3 Unternehmen gefunden.
Die Bewerbungen werden nacheinander verarbeitet.
Eine Company wird erst nach erfolgreichem Versand entfernt.

================================================================================

[1/3] Example Security GmbH
Position: Junior Security Analyst
E-Mail:   jobs@example.com

✓ Bewerbung erfolgreich versendet.
✓ Company aus companies.json entfernt.

================================================================================

[2/3] Example Software AG
Position: Junior Python Developer
E-Mail:   careers@example.com

✓ Bewerbung erfolgreich versendet.
✓ Company aus companies.json entfernt.

================================================================================

[3/3] Example IT Services GmbH
Position: Junior System Administrator
E-Mail:   jobs@example.com

✗ Versand fehlgeschlagen.
→ Company bleibt erhalten.
```

At the end, a summary is displayed:

```text
================================================================================
AUTOMATISCHER VERSAND ABGESCHLOSSEN
================================================================================

Gesamt:      3
Erfolgreich: 2
Übersprungen:0
Fehlgeschl.: 1
```

---

# Application History

ApplicationForge stores application history in:

```text
data/history.json
```

View the history:

```bash
python main.py --history
```

The history can contain information such as:

- Company
- Company ID
- Position
- Recipient
- Job ID
- Applicant
- Status
- Creation timestamp
- Sending timestamp
- Match score
- Confidence score
- Template
- Style
- Generated ZIP

Example:

```json
{
  "applications": [
    {
      "history_key": "company:example-security:junior security analyst:jobs@example.com",
      "company": "Example Security GmbH",
      "company_id": "example-security",
      "position": "Junior Security Analyst",
      "email": "jobs@example.com",
      "status": "sent",
      "match_score": 87.5,
      "confidence_score": 91.0,
      "template_type": "cybersecurity",
      "template_style": "technical"
    }
  ]
}
```

---

# Duplicate Protection

ApplicationForge checks the application history before sending.

This helps prevent accidentally sending the same application multiple times.

A history key is generated using identifiers such as:

```text
job_id
```

or:

```text
company_id + position + email
```

If a previously sent application is detected, the normal sending process is stopped.

---

# Force Resend

If an application intentionally needs to be sent again:

```bash
python main.py \
    --company example-security \
    --send \
    --force
```

`--force` bypasses the duplicate protection.

Use it intentionally.

---

# Logging

ApplicationForge uses Python's logging framework.

Logs contain information about:

- Application startup
- Configuration loading
- Document discovery
- Matching
- Generation
- PDF creation
- ZIP creation
- Email delivery
- History updates
- Errors

Verbose logging can be enabled with:

```bash
python main.py \
    --company example-security \
    --verbose
```

---

# Exit Codes

ApplicationForge uses standard CLI exit codes.

|  Code | Meaning                                           |
| ----: | ------------------------------------------------- |
|   `0` | Successful execution                              |
|   `1` | Processing/configuration/generation/sending error |
| `130` | Interrupted with `Ctrl+C`                         |

This makes ApplicationForge suitable for shell scripts and automation.

---

# Security

ApplicationForge handles potentially sensitive information.

This includes:

- Personal contact information
- Email addresses
- Application documents
- SMTP credentials
- Application history

### Never commit:

```text
.env
data/applicant.json
data/history.json
Documents/
generated/
```

The public repository should contain only example configuration and fictional data.

Recommended:

```text
.env.example
data/applicant.json.example
data/companies.json.example
```

---

# `.gitignore`

A recommended `.gitignore`:

```gitignore
# ============================================================
# ENVIRONMENT
# ============================================================

.env
.env.*

# ============================================================
# PERSONAL DATA
# ============================================================

data/applicant.json
data/history.json

Documents/

# ============================================================
# GENERATED DATA
# ============================================================

generated/

# ============================================================
# PYTHON
# ============================================================

__pycache__/
*.py[cod]
*.so

.venv/
venv/
env/

# ============================================================
# IDE
# ============================================================

.vscode/
.idea/

# ============================================================
# MACOS / WINDOWS
# ============================================================

.DS_Store
Thumbs.db

# ============================================================
# LOGS
# ============================================================

*.log
```

---

# Recommended Public Repository Layout

For a public GitHub repository, the recommended structure is:

```text
ApplicationForge/
│
├── app/
│   ├── application/
│   ├── documents/
│   ├── mail/
│   └── matching/
│
├── data/
│   ├── applicant.json.example
│   ├── companies.json.example
│   └── history.json.example
│
├── Documents/
│   └── .gitkeep
│
├── generated/
│   └── .gitkeep
│
├── tests/
│   └── ...
│
├── config.py
├── main.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

Personal data should never be required for cloning or understanding the project.

---

# Architecture

ApplicationForge is designed around separated responsibilities.

```text
main.py
   │
   ├── CLI
   │
   ├── Application Generator
   │
   ├── Matching
   │
   ├── Documents
   │
   ├── Mail
   │
   └── History
```

### Application

Responsible for generating individualized application text.

```text
app/application/
```

### Matching

Responsible for comparing applicant capabilities with job requirements.

```text
app/matching/
```

### Documents

Responsible for:

- Collecting documents
- Creating PDFs
- Creating ZIP archives

```text
app/documents/
```

### Mail

Responsible for SMTP email delivery.

```text
app/mail/
```

### CLI

The `main.py` module coordinates the complete workflow.

---

# Design Principles

ApplicationForge follows several design principles.

### Explicit over implicit

Sending email is never performed simply by generating an application.

The user must explicitly use:

```bash
--send
```

---

### Safe by default

The default workflow generates an application but does not send it.

Preview and dry-run modes provide additional safety.

---

### Modular architecture

Different components should be replaceable without rewriting the entire application.

For example, the SMTP implementation can be changed independently of the matching engine.

---

### Structured data

Applicant and company information is stored in JSON.

This keeps the data human-readable and easy to modify.

---

### Reproducibility

Generation can be controlled through a seed:

```bash
--seed 12345
```

This makes debugging and testing easier.

---

### Automation without losing control

Batch processing is supported:

```bash
--send-all
```

while individual sending remains explicitly controllable.

---

# Development

Create a development environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the CLI:

```bash
python main.py --help
```

Run a basic application generation:

```bash
python main.py \
    --company example-security
```

Test matching:

```bash
python main.py \
    --company example-security \
    --match-only
```

Test batch processing without sending:

```bash
python main.py \
    --send-all \
    --dry-run
```

---

# Testing

Tests should be added under:

```text
tests/
```

Recommended test areas:

```text
tests/
├── test_matching.py
├── test_generator.py
├── test_archive.py
├── test_history.py
├── test_cli.py
└── test_mail.py
```

Particular attention should be given to:

- Duplicate detection
- History handling
- JSON validation
- PDF generation
- ZIP generation
- Failed email delivery
- Batch processing
- Dry-run behavior
- Atomic JSON updates

---

# Roadmap

Potential future improvements include:

- [ ] Comprehensive automated test suite
- [ ] Better JSON schema validation
- [ ] Configuration file support
- [ ] More application templates
- [ ] More languages
- [ ] Richer matching algorithms
- [ ] Job URL/source tracking
- [ ] Application status management
- [ ] Statistics dashboard
- [ ] CSV import/export
- [ ] Interactive CLI mode
- [ ] `--version` support
- [ ] Package installation via PyPI
- [ ] Global `applicationforge` command
- [ ] Improved PDF templates
- [ ] Unit and integration test coverage
- [ ] CI/CD with GitHub Actions

---

# Example Workflow

A typical workflow looks like this.

### 1. Configure applicant

```text
data/applicant.json
```

### 2. Add companies

```text
data/companies.json
```

### 3. Add application documents

```text
Documents/
```

### 4. Check available jobs

```bash
python main.py --list-companies
```

### 5. Test matching

```bash
python main.py \
    --company example-security \
    --match-only
```

### 6. Generate application

```bash
python main.py \
    --company example-security
```

### 7. Preview

```bash
python main.py \
    --company example-security \
    --preview
```

### 8. Test sending

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

### 9. Send

```bash
python main.py \
    --company example-security \
    --send
```

### 10. Check history

```bash
python main.py --history
```

---

# Batch Workflow

For multiple companies:

```bash
python main.py --list-companies
```

Then test the complete batch:

```bash
python main.py \
    --send-all \
    --dry-run
```

If everything looks correct:

```bash
python main.py \
    --send-all
```

After processing:

```bash
python main.py --history
```

---

# Why ApplicationForge?

Traditional application workflows often require manually repeating the same steps:

```text
Find job
   ↓
Read requirements
   ↓
Adapt application
   ↓
Write cover letter
   ↓
Collect documents
   ↓
Create PDF
   ↓
Create archive
   ↓
Write email
   ↓
Send
   ↓
Track application
```

ApplicationForge turns this into a structured pipeline:

```text
Job Data
   ↓
Matching
   ↓
Generation
   ↓
PDF
   ↓
ZIP
   ↓
Email
   ↓
History
```

The goal is not to replace the applicant.

The goal is to **remove repetitive administrative work** so more time can be spent on the actual job search and preparation.

---

# Disclaimer

ApplicationForge is an automation tool for managing job applications.

The user is responsible for:

- Reviewing generated applications
- Verifying recipient addresses
- Checking attached documents
- Confirming application content
- Ensuring that applications are appropriate
- Complying with applicable laws and company/job-platform terms
- Configuring SMTP credentials securely

Automated email delivery should always be tested with `--dry-run` before real use.

---

# License

This project is licensed under the **MIT License**.

See:

```text
LICENSE
```

for the complete license text.

---

# Contributing

Contributions are welcome.

Typical contribution workflow:

```bash
git clone https://github.com/your-username/ApplicationForge.git
cd ApplicationForge

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Create a feature branch:

```bash
git checkout -b feature/my-feature
```

Make your changes, test them, and create a pull request.

When contributing, please avoid committing:

- Personal applicant data
- Real company contact information
- SMTP credentials
- Private documents
- Generated application archives
- Application history

---

# Project Status

ApplicationForge is an actively developed project.

The current version focuses on the core application pipeline:

```text
JSON
 ↓
Matching
 ↓
Cover Letter
 ↓
PDF
 ↓
ZIP
 ↓
Email
 ↓
History
```

The architecture is intentionally designed so additional functionality can be added without replacing the existing core workflow.

---

## ApplicationForge

**Build applications. Match opportunities. Automate the repetitive work.**
