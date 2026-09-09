# Application Tool

> A modular CLI application for generating, validating, matching, and sending job applications automatically.

The **Application Tool** is a Python-based command-line application designed to automate repetitive parts of the job application process while keeping the workflow structured, reproducible, and safe.

It combines applicant data, job information, automated matching, dynamic template discovery, document generation, email delivery, duplicate detection, application history, and bulk processing into one modular workflow.

---

## ✨ Features

- 🧑‍💼 **Applicant data management**
- 🏢 **Company and job management**
- 🎯 **Automatic job matching**
- 📊 **Match Score**
- 🔎 **Confidence Score**
- 📝 **Individual cover letter generation**
- 🌍 **Language-specific templates**
- 🧩 **Automatic template discovery**
- 🎨 **Automatic style selection**
- 🎲 **Reproducible generation with seeds**
- 📄 **PDF generation**
- 📦 **Complete application ZIP archives**
- 📧 **SMTP email delivery**
- 🚀 **Automated bulk sending**
- 🛡️ **Duplicate application detection**
- 🧪 **Dry-run mode**
- 👀 **Preview mode**
- 📚 **Application history**
- 📝 **Detailed logging**
- ⚛️ **Atomic JSON file updates**
- 🔐 **Multiple sending safety mechanisms**
- 🧱 **Modular architecture**

---

# Overview

The tool turns a company entry into a complete application workflow.

```text
                    ┌─────────────────────┐
                    │   Applicant Data    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Company / Job     │
                    │     Information     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Duplicate Check    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Job Matching      │
                    │                     │
                    │ Match + Confidence  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Template Discovery  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Template Selection  │
                    │    + Style          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Cover Letter        │
                    │ Generation          │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
             ┌──────────────┐      ┌──────────────┐
             │ PDF Document │      │ ZIP Archive  │
             └──────┬───────┘      └──────┬───────┘
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │    Email Delivery   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Application History │
                    └─────────────────────┘
```

---

# Why This Tool?

Applying for jobs repeatedly involves many manual steps:

- Finding the correct company entry
- Checking whether the job was already processed
- Evaluating the position
- Selecting the appropriate cover letter template
- Writing an individual application
- Creating documents
- Creating an archive
- Sending the email
- Recording the result

The Application Tool automates these steps while keeping the individual components separated.

The goal is not simply to send large numbers of applications, but to create a **consistent, reproducible, and traceable application workflow**.

---

# Requirements

The project requires:

- Python 3
- A working SMTP configuration for email delivery
- The required project data files
- At least one application document

A typical data structure:

```text
data/

├── applicant.json
├── companies.json
├── history.json
│
├── de/
│   ├── cybersecurity.json
│   ├── it.json
│   └── software.json
│
└── en/
    ├── cybersecurity.json
    ├── it.json
    └── software.json
```

---

# Project Structure

The application is organized into independent modules:

```text
project/
│
├── main.py
├── config.py
│
├── data/
│   ├── applicant.json
│   ├── companies.json
│   ├── history.json
│   │
│   ├── de/
│   │   ├── cybersecurity.json
│   │   ├── it.json
│   │   └── ...
│   │
│   └── en/
│       ├── cybersecurity.json
│       ├── it.json
│       └── ...
│
├── app/
│   │
│   ├── application/
│   │   └── generator.py
│   │
│   ├── matching/
│   │   └── matcher.py
│   │
│   ├── documents/
│   │   ├── converter.py
│   │   └── archive.py
│   │
│   └── mail/
│       └── sender.py
│
├── Documents/
├── generated/
└── logs/
```

The actual directories are configurable through `config.py`.

---

# Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd <project-directory>
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Then configure the project according to your environment.

---

# Quick Start

## 1. List available companies

```bash
python main.py --list-companies
```

---

## 2. Check job compatibility

```bash
python main.py \
    --company example-security \
    --match-only
```

This performs the matching process without creating or sending an application.

---

## 3. Generate an application

```bash
python main.py \
    --company example-security
```

No email is sent unless `--send` is explicitly specified.

---

## 4. Preview the application

```bash
python main.py \
    --company example-security \
    --preview
```

---

## 5. Test the complete sending workflow

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

---

## 6. Send the application

```bash
python main.py \
    --company example-security \
    --send
```

The tool asks for confirmation before sending.

---

## 7. Send automatically

```bash
python main.py \
    --company example-security \
    --send \
    --yes
```

---

# Matching Engine

The matching system evaluates the compatibility between the applicant and the job.

Example output:

```text
================================================================================

MATCHING

================================================================================

Match Score:       82.5%
Confidence Score:  91.0%

Matched Skills:

  ✓ Python
  ✓ Linux
  ✓ Cybersecurity
  ✓ Networking

Missing Skills:

  ✗ Kubernetes

Job Type:          Full-Time
Seniority:         Junior
Employment:        Employment
Work Model:        Remote

================================================================================
```

The system separates:

### Match Score

Represents how closely the applicant's profile matches the position.

### Confidence Score

Represents how confident the matching system is in the resulting evaluation.

---

# Template System

One of the core design principles is **data-driven template discovery**.

Templates are organized by language:

```text
data/
│
├── de/
│   ├── cybersecurity.json
│   ├── it.json
│   └── software.json
│
└── en/
    ├── cybersecurity.json
    ├── it.json
    └── software.json
```

The generator automatically scans the selected language directory for template files.

There is no need to maintain a hard-coded list inside `generator.py`.

---

# Automatic Template Discovery

For example:

```text
data/en/

├── cybersecurity.json
├── it.json
├── software.json
├── cloud-security.json
└── system-administration.json
```

The generator automatically discovers:

```text
cybersecurity
it
software
cloud-security
system-administration
```

Certain non-template data files are ignored, including:

```text
applicant.json
companies.json
history.json
templates.json
```

The filename becomes the template type.

Therefore, adding:

```text
data/en/cloud-security.json
```

automatically makes:

```text
cloud-security
```

available as a template.

No Python code needs to be modified.

---

# Template Selection

If no template is explicitly specified, the generator determines the template automatically.

The process is:

```text
Language
    │
    ▼
Discover Templates
    │
    ▼
Validate Templates
    │
    ▼
Analyze Job
    │
    ▼
Select Template
    │
    ▼
Select Style
    │
    ▼
Generate Cover Letter
```

The automatic selection happens inside `generate_application()`.

---

# Explicit Template Selection

A template can be forced using:

```bash
python main.py \
    --company example-security \
    --template cybersecurity
```

An explicit template always overrides automatic template selection.

For example:

```text
--template cybersecurity
--template it
--template software
--template cloud-security
```

The available templates depend on the JSON files present in the selected language directory.

---

# Styles

Templates can contain multiple styles.

For example:

```text
formal
technical
modern
```

A specific style can be selected:

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

The selection process is:

```text
Template
    │
    ▼
Available Styles
    │
    ▼
Explicit Style?
   / \
 Yes  No
  │    │
  ▼    ▼
Use   Automatic
      Selection
```

If `--style` is not provided, the generator selects a style automatically.

---

# Languages

Currently supported:

```text
de
en
```

Default language:

```text
de
```

### German

```bash
python main.py \
    --company example-security \
    --language de
```

Loads templates from:

```text
data/de/
```

### English

```bash
python main.py \
    --company example-security \
    --language en
```

Loads templates from:

```text
data/en/
```

The selected language is also used during document generation.

---

# Reproducible Generation

The `--seed` option allows deterministic template and style selection.

Example:

```bash
python main.py \
    --company example-security \
    --language en \
    --seed 12345
```

Using the same inputs and seed allows the selection process to be reproduced.

This is useful for:

- Testing
- Debugging
- Re-generating an application
- Comparing output
- Reproducing previous runs

---

# Documents

The tool supports a dedicated application document directory.

For example:

```text
Documents/

├── Resume.pdf
├── Certificates.pdf
└── References.pdf
```

A custom directory can be supplied:

```bash
python main.py \
    --company example-security \
    --documents "/Users/max/Documents/Application"
```

The tool validates the directory and collects usable application documents.

These files are included in the generated ZIP archive.

---

# Generated Output

A completed application produces the required documents and archive.

A typical output may look like:

```text
generated/

└── example-security/

    ├── cover-letter.pdf
    └── application.zip
```

The ZIP archive contains the generated cover letter together with the selected application documents.

---

# Email Delivery

Email delivery is performed through the configured SMTP server.

A normal application generation does **not** send an email.

Email sending requires:

```text
--send
```

Example:

```bash
python main.py \
    --company example-security \
    --send
```

Before sending, the user receives a confirmation:

```text
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

WARNING: EMAIL WILL BE SENT

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Applicant:   Max Mustermann
Company:     Example Security GmbH
Position:    Junior Security Engineer
Recipient:   jobs@example.com
Attachment:  generated/...

Send application? [y/N]:
```

Accepted confirmations include:

```text
y
yes
j
ja
```

Anything else cancels the operation.

---

# Automated Sending

The confirmation can be skipped using:

```bash
python main.py \
    --company example-security \
    --send \
    --yes
```

Short form:

```bash
python main.py \
    --company example-security \
    --send \
    -y
```

> ⚠️ `--yes` should only be used when the complete workflow has already been verified.

---

# Dry-Run Mode

Dry-run mode allows the complete workflow to be tested without sending an email.

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

The tool still performs:

```text
Applicant loading
       ↓
Company loading
       ↓
Document validation
       ↓
Matching
       ↓
Template discovery
       ↓
Template selection
       ↓
Style selection
       ↓
Cover letter generation
       ↓
PDF generation
       ↓
ZIP generation
```

But:

```text
                 ✕
          EMAIL DELIVERY
                 ✕
```

No email is sent.

No company is removed from the sending queue.

---

# Bulk Sending

The entire application queue can be processed using:

```bash
python main.py --send-all
```

Each company is processed independently.

```text
Company
   │
   ▼
Duplicate Detection
   │
   ▼
Matching
   │
   ▼
Template Selection
   │
   ▼
Cover Letter
   │
   ▼
PDF + ZIP
   │
   ▼
Email
   │
   ▼
History
   │
   ▼
Remove from Queue
```

A company is only removed after successful email delivery.

---

# Bulk Sending Safety

If application generation fails:

```text
✗ Application generation failed

→ Company remains in companies.json
```

If email delivery fails:

```text
✗ Email delivery failed

→ Company remains in companies.json
```

If sending succeeds but queue removal fails:

```text
⚠ Email was sent,

but the company could not be removed from companies.json.
```

This prevents failed applications from silently disappearing from the queue.

---

# Bulk Template Selection

`--send-all` uses the same application generator as an individual application.

Therefore, each company is evaluated independently.

For example:

```bash
python main.py --send-all
```

can perform:

```text
Company A
   → Cybersecurity template

Company B
   → Software template

Company C
   → IT template
```

depending on the available templates and job information.

A fixed template can still be forced:

```bash
python main.py \
    --send-all \
    --template cybersecurity
```

---

# Bulk Language Selection

Send all applications in English:

```bash
python main.py \
    --send-all \
    --language en
```

Send all applications in German:

```bash
python main.py \
    --send-all \
    --language de
```

---

# Bulk Dry-Run

Before a real bulk send, the recommended approach is:

```bash
python main.py \
    --send-all \
    --dry-run
```

This executes the application pipeline without sending emails or removing companies from the queue.

Once the result has been verified:

```bash
python main.py \
    --send-all \
    --yes
```

---

# Application History

The application history is stored in:

```text
data/history.json
```

View it with:

```bash
python main.py --history
```

The history can contain:

- Company
- Company ID
- Position
- Email
- URL
- Job ID
- Applicant
- Status
- Creation timestamp
- Sending timestamp
- Match Score
- Confidence Score
- Template type
- Template style
- Generated ZIP file

Example:

```text
================================================================================

APPLICATION HISTORY

================================================================================

[1] Example Security GmbH

    Position:   Junior Security Engineer
    Email:      jobs@example.com
    Status:     sent

    Created:    2026-09-09T02:30:00+00:00
    Sent:       2026-09-09T02:31:00+00:00

    Match:      82.5%
    Confidence: 91.0%

================================================================================
```

---

# History Statuses

Possible application states include:

```text
generated
sent
failed
cancelled
```

A `sent` entry represents an application that was actually sent.

---

# Duplicate Detection

The tool uses a stable identifier to detect previously processed jobs.

The priority is:

```text
1. job_id

2. company_id + position + email

3. company_name + position + email
```

This allows the system to recognize the same application even if other job information changes.

---

# Duplicate Protection

If an existing history entry is detected, the tool displays a warning.

During normal generation, the application can still be generated.

During sending, previously sent applications are blocked by default.

Example:

```text
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

WARNING: POSSIBLE DUPLICATE APPLICATION

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Company:     Example Security GmbH
Position:    Junior Security Engineer
Status:      sent

Created:     2026-09-09T02:30:00+00:00
Sent:        2026-09-09T02:31:00+00:00

Sending has been prevented.

Use --force if you intentionally want to send this application again.
```

---

# Force Resending

A previously sent application can intentionally be sent again:

```bash
python main.py \
    --company example-security \
    --send \
    --force
```

Combine it with `--yes` for automated sending:

```bash
python main.py \
    --company example-security \
    --send \
    --force \
    --yes
```

`--force` disables duplicate protection for the current execution.

---

# Logging

The application provides structured logging for important processing steps.

Normal logging is written to:

- Terminal
- Configured log file

Enable verbose logging:

```bash
python main.py \
    --company example-security \
    --verbose
```

or:

```bash
python main.py \
    --company example-security \
    -v
```

Verbose mode enables `DEBUG` logging.

It can also be combined with dry-run:

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run \
    --verbose
```

---

# Atomic Data Updates

Important JSON files are updated using an atomic write strategy.

Instead of directly overwriting a file:

```text
JSON
 │
 └── overwrite
```

the tool uses:

```text
JSON
 │
 ▼
Temporary File
 │
 ▼
Successful Write
 │
 ▼
Atomic Replacement
```

This reduces the risk of leaving important application data partially written after a failure.

---

# CLI Reference

| Option                | Description                                 |
| --------------------- | ------------------------------------------- |
| `--company COMPANY`   | Company ID from `companies.json`            |
| `--send-all`          | Process all companies sequentially          |
| `--documents PATH`    | Use a custom application document directory |
| `--template TEMPLATE` | Force a template type                       |
| `--style STYLE`       | Force a template style                      |
| `--language {de,en}`  | Select application language                 |
| `--seed SEED`         | Use a deterministic selection seed          |
| `--match-only`        | Run matching only                           |
| `--preview`           | Display the generated cover letter          |
| `--send`              | Send the application by email               |
| `--dry-run`           | Simulate the sending workflow               |
| `--yes`, `-y`         | Skip sending confirmation                   |
| `--list-companies`    | List available companies                    |
| `--history`           | Display application history                 |
| `--force`             | Override duplicate protection               |
| `--verbose`, `-v`     | Enable debug logging                        |
| `--help`              | Display CLI help                            |

---

# Command Examples

### List companies

```bash
python main.py --list-companies
```

### Match a position

```bash
python main.py --company example-security --match-only
```

### Generate an application

```bash
python main.py --company example-security
```

### Generate in English

```bash
python main.py \
    --company example-security \
    --language en
```

### Preview

```bash
python main.py \
    --company example-security \
    --preview
```

### Specific template

```bash
python main.py \
    --company example-security \
    --template cybersecurity
```

### Specific template and style

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

### Reproducible generation

```bash
python main.py \
    --company example-security \
    --seed 12345
```

### Dry-run

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

### Send

```bash
python main.py \
    --company example-security \
    --send
```

### Automated send

```bash
python main.py \
    --company example-security \
    --send \
    --yes
```

### Bulk dry-run

```bash
python main.py \
    --send-all \
    --dry-run
```

### Bulk send

```bash
python main.py \
    --send-all \
    --yes
```

### English bulk send

```bash
python main.py \
    --send-all \
    --language en \
    --yes
```

### Resend

```bash
python main.py \
    --company example-security \
    --send \
    --force
```

### History

```bash
python main.py --history
```

---

# CLI Conflicts

The CLI validates incompatible options before starting the application workflow.

### `--company` + `--send-all`

Not allowed:

```bash
python main.py \
    --company example-security \
    --send-all
```

Use either a specific company:

```bash
python main.py --company example-security
```

or the complete queue:

```bash
python main.py --send-all
```

---

### `--preview` + `--send`

Not allowed.

Preview is explicitly a non-sending mode.

---

### `--match-only` + `--send`

Not allowed.

Matching-only mode does not generate or send applications.

---

### `--match-only` + `--preview`

Not allowed.

---

### `--send-all` + `--preview`

Not allowed.

---

### `--send-all` + `--match-only`

Not allowed.

---

### `--yes` without `--send`

Not allowed.

Incorrect:

```bash
python main.py \
    --company example-security \
    --yes
```

Correct:

```bash
python main.py \
    --company example-security \
    --send \
    --yes
```

---

# Exit Codes

|  Code | Meaning                            |
| ----: | ---------------------------------- |
|   `0` | Successful execution               |
|   `1` | Processing or application error    |
| `130` | Program interrupted, e.g. `Ctrl+C` |

Exit code `1` can represent errors involving:

- Matching
- Template loading
- Template validation
- Document validation
- PDF generation
- ZIP generation
- Email delivery
- History
- Other processing operations

---

# Adding a New Template

Adding a new template does not require modifying the generator.

For English:

```text
data/en/cloud-security.json
```

For German:

```text
data/de/cloud-security.json
```

The template can then be explicitly selected:

```bash
python main.py \
    --company example-security \
    --language en \
    --template cloud-security
```

The important part is simply the filename:

```text
cloud-security.json
       │
       ▼
cloud-security
```

The generator discovers it automatically.

This makes the template system **data-driven and extensible**.

---

# Template Validation

Before a template is used, the generator performs validation.

The process is:

```text
Language Directory
       │
       ▼
Template Discovery
       │
       ▼
JSON Loading
       │
       ▼
JSON Validation
       │
       ▼
Template Structure Validation
       │
       ▼
Template Selection
       │
       ▼
Style Selection
       │
       ▼
Generation
```

Invalid or missing templates result in an error.

The available templates for the selected language can then be displayed to help identify the problem.

---

# Recommended Workflow

For an individual application:

```text
1. Match
   ↓
2. Generate
   ↓
3. Preview
   ↓
4. Dry-Run
   ↓
5. Send
```

Example:

```bash
# 1. Match

python main.py \
    --company example-security \
    --match-only

# 2. Generate

python main.py \
    --company example-security

# 3. Preview

python main.py \
    --company example-security \
    --preview

# 4. Dry-run

python main.py \
    --company example-security \
    --send \
    --dry-run

# 5. Send

python main.py \
    --company example-security \
    --send
```

For a bulk workflow:

```bash
# Test the complete queue

python main.py \
    --send-all \
    --dry-run

# Send after verification

python main.py \
    --send-all \
    --yes
```

---

# Architecture

The application follows a modular architecture:

```text
                         main.py
                            │
            ┌───────────────┼────────────────┐
            │               │                │
            ▼               ▼                ▼
     Application         Matching         Documents
      Generator           Engine           System
            │               │                │
            │               │         ┌──────┴──────┐
            │               │         │             │
            ▼               ▼         ▼             ▼
      Templates        Match Score    PDF           ZIP
      + Styles         + Confidence
            │
            ▼
       Cover Letter
            │
            └──────────────────────┐
                                   ▼
                              Mail Sender
                                   │
                                   ▼
                              Email Delivery
                                   │
                                   ▼
                               History
```

Core modules:

```text
app/application/generator.py
```

Responsible for application generation, template discovery, selection, styles, and cover letters.

```text
app/matching/matcher.py
```

Responsible for job matching and scoring.

```text
app/documents/converter.py
```

Responsible for PDF generation.

```text
app/documents/archive.py
```

Responsible for creating application ZIP archives.

```text
app/mail/sender.py
```

Responsible for email construction and SMTP delivery.

---

# Design Principles

The project follows several important principles.

### Modular

Each major responsibility is separated into its own module.

### Data-driven

Templates are discovered from the filesystem instead of being hard-coded.

### Reproducible

Seeds allow deterministic template and style selection.

### Safe by default

Generating an application does not automatically send an email.

### Traceable

Important operations are recorded in application history and logs.

### Failure-resistant

Failed applications remain in the queue during bulk processing.

### Extensible

New template types can be added without changing the generator.

---

# Complete Workflow

The complete system can be summarized as:

```text
                    APPLICATION TOOL

                           │
                           ▼

                    Applicant Data
                           +
                    Job Information
                           │
                           ▼
                    Duplicate Check
                           │
                           ▼
                     Job Matching
                           │
                    ┌──────┴──────┐
                    ▼             ▼
               Match Score   Confidence
                    │             │
                    └──────┬──────┘
                           ▼
                  Template Discovery
                           │
                           ▼
                  Template Selection
                           │
                           ▼
                    Style Selection
                           │
                           ▼
                 Cover Letter Generation
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                   PDF           ZIP
                    │             │
                    └──────┬──────┘
                           ▼
                    Email Delivery
                           │
                           ▼
                  Application History
```

---

# Safety Model

The tool deliberately separates **generation** from **sending**.

```text
python main.py --company ID
```

means:

```text
GENERATE
```

while:

```text
python main.py --company ID --send
```

means:

```text
GENERATE + SEND
```

And:

```text
python main.py --company ID --send --dry-run
```

means:

```text
GENERATE + SIMULATE SEND
```

This distinction prevents a normal application-generation command from accidentally sending an email.

---

# Bulk Processing Model

The bulk processor follows the same safety principle.

```text
companies.json
      │
      ▼
   Company 1
      │
      ├── Generate
      ├── Match
      ├── Template
      ├── PDF
      ├── ZIP
      ├── Send
      ├── History
      └── Remove from queue
      │
      ▼
   Company 2
      │
      └── ...
```

A company is removed only after successful sending.

Therefore:

```text
Generation failed  → Keep company
Email failed       → Keep company
Email succeeded    → Remove company
```

---

# Quick Reference

```text
LIST
python main.py --list-companies

MATCH
python main.py --company ID --match-only

CREATE
python main.py --company ID

PREVIEW
python main.py --company ID --preview

ENGLISH
python main.py --company ID --language en

TEMPLATE
python main.py --company ID --template cybersecurity

STYLE
python main.py --company ID --template cybersecurity --style technical

SEED
python main.py --company ID --seed 12345

DRY-RUN
python main.py --company ID --send --dry-run

SEND
python main.py --company ID --send

AUTOMATED SEND
python main.py --company ID --send --yes

BULK DRY-RUN
python main.py --send-all --dry-run

BULK SEND
python main.py --send-all --yes

HISTORY
python main.py --history

FORCE RESEND
python main.py --company ID --send --force

VERBOSE
python main.py --company ID --verbose

HELP
python main.py --help
```

---

# Extending the System

The architecture is designed to allow additional functionality without restructuring the entire application.

Potential extensions include:

- Additional languages
- Additional template categories
- Additional document formats
- More advanced matching algorithms
- Additional email providers
- Application analytics
- Additional scoring systems
- Job board integrations
- More granular history tracking
- Additional output formats

The template architecture in particular is intentionally designed around filesystem discovery, allowing new templates to be introduced through data rather than Python code.

---

# License

Add your project license here.

For example:

```text
MIT License
```

or:

```text
Proprietary
```

---

# Status

This project is actively developed.

The architecture is designed around modularity, automation, reproducibility, and safe application delivery.
