# Application Tool

CLI tool for automatically creating, validating, and sending job applications.

The tool combines:

- Applicant data
- Job information
- Automatic job matching
- Match Score and Confidence Score
- Automatic template discovery
- Language-dependent templates
- Individual cover letters
- Cover letters as PDF
- Complete application documents as ZIP
- Application history
- Duplicate detection
- Individual email delivery
- Automated bulk sending
- Dry-run mode
- Preview mode
- Reproducible template selection using seeds
- Extensive logging

---

# Table of Contents

- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [CLI](#cli)
- [Companies](#companies)
- [Creating an Application](#creating-an-application)
- [Matching](#matching)
- [Templates](#templates)
- [Automatic Template Discovery](#automatic-template-discovery)
- [Forcing a Template](#forcing-a-template)
- [Styles](#styles)
- [Language](#language)
- [Seed](#seed)
- [Documents](#documents)
- [Email Delivery](#email-delivery)
- [Dry-Run](#dry-run)
- [Bulk Sending](#bulk-sending)
- [Application History](#application-history)
- [Duplicate Detection](#duplicate-detection)
- [Force](#force)
- [Logging](#logging)
- [Typical Workflows](#typical-workflows)
- [CLI Options](#cli-options)
- [Conflicts](#conflicts)
- [Exit Codes](#exit-codes)
- [Security Mechanisms](#security-mechanisms)
- [Template Safety](#template-safety)
- [Adding a New Template](#adding-a-new-template)
- [Recommended Test Workflow](#recommended-test-workflow)
- [Complete Example Workflow](#complete-example-workflow)
- [Complete Bulk Sending](#complete-bulk-sending)
- [Help](#help)
- [Quick Reference](#quick-reference)
- [Architecture](#architecture)
- [Design Principle](#design-principle)
- [Conclusion](#conclusion)

---

# Requirements

The tool requires a working Python environment and the required JSON files.

Important data:

```text
data/

├── applicant.json
├── companies.json
├── history.json
├── de/
│   ├── cybersecurity.json
│   ├── it.json
│   └── ...
└── en/
    ├── cybersecurity.json
    ├── it.json
    └── ...
```

The actual template files are organized by language in:

```text
data/de/

data/en/
```

For example:

```text
data/de/cybersecurity.json

data/en/cybersecurity.json
```

The template is loaded based on the selected language.

---

# Project Structure

A typical project structure looks like this:

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
│   │   └── software.json
│   │
│   └── en/
│       ├── cybersecurity.json
│       ├── it.json
│       └── software.json
│
├── app/
│   ├── application/
│   │   └── generator.py
│   │
│   ├── documents/
│   │   ├── archive.py
│   │   └── converter.py
│   │
│   ├── matching/
│   │   └── matcher.py
│   │
│   └── mail/
│       └── sender.py
│
├── Documents/
├── generated/
└── logs/
```

The actual directory configuration is controlled through `config.py`.

---

# CLI

The tool is generally started through `main.py`:

```bash
python main.py [OPTIONS]
```

An application requires either:

```text
--company
```

or:

```text
--send-all
```

Exceptions are:

```text
--list-companies

--history
```

These two modes can be executed independently.

---

# Companies

## List Companies

Display all companies from `companies.json`:

```bash
python main.py --list-companies
```

Example:

```text
================================================================================

AVAILABLE COMPANIES

================================================================================

ID:          example-security
Name:        Example Security GmbH
Position:    Junior Security Engineer
Email:       jobs@example.com
Type:        Cybersecurity
Size:        enterprise
Location:    Berlin
Job Type:    Full-Time
Seniority:   Junior
Employment:  Employment
Remote:      Remote

Keywords:    Python, Linux, Cybersecurity, Networking

--------------------------------------------------------------------------------
```

The displayed `ID` can then be used with `--company`.

---

# Creating an Application

Create a normal application:

```bash
python main.py --company example-security
```

The workflow is:

```text
Load applicant

        ↓

Load company

        ↓

Duplicate Detection

        ↓

Validate documents

        ↓

Job Matching

        ↓

Automatically determine template

        ↓

Determine style

        ↓

Generate cover letter

        ↓

Create PDF

        ↓

Create ZIP

        ↓

Save history
```

Without `--send`, **no email is sent**.

The generated cover letter is displayed in the terminal.

---

# Matching

## Run Matching Only

If you only want to check how well a position matches the applicant:

```bash
python main.py \
    --company example-security \
    --match-only
```

The tool displays information such as:

- Match Score
- Confidence Score
- Matched skills
- Missing skills
- Job type
- Seniority
- Employment type
- Work model

Example:

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

`--match-only` does not create application documents and does not send an email.

---

# Templates

## Basic Principle

Templates are organized by language.

Example:

```text
data/

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

When running:

```bash
python main.py \
    --company example-security \
    --language en
```

templates are loaded from:

```text
data/en/
```

When running:

```bash
python main.py \
    --company example-security \
    --language de
```

templates are loaded from:

```text
data/de/
```

---

# Automatic Template Discovery

Templates no longer need to be hard-coded into Python.

The generator automatically scans the selected language directory for `.json` files.

For example:

```text
data/en/

├── cybersecurity.json
├── it.json
├── software.json
└── system-administration.json
```

is automatically discovered as:

```text
cybersecurity

it

software

system-administration
```

Certain data files are ignored, for example:

```text
applicant.json
companies.json
history.json
templates.json
```

Only valid template filenames are considered.

This means that a new template can simply be placed into the appropriate language directory.

For example:

```text
data/en/cloud-security.json
```

After adding the file, the template is automatically available.

No additional Python list or registration step is required.

The implementation scans the language directory and uses the filename without `.json` as the template type.

---

# Template Selection

If `--template` is not specified, the generator automatically determines the template type.

The generator:

1. Loads the templates for the selected language
2. Validates the templates
3. Determines the appropriate template type
4. Determines the style
5. Generates the cover letter

The selection is performed inside `generate_application()`.

---

# Forcing a Template

A specific template can be explicitly selected:

```bash
python main.py \
    --company example-security \
    --template cybersecurity
```

This overrides automatic template-type selection.

The generator explicitly follows the rule:

```text
An explicit template_type always overrides automatic
template selection.
```

Examples:

```text
cybersecurity
it
software
cloud-security
system-administration
```

The templates actually available depend on the JSON files present in the selected language directory.

---

# Styles

A template can contain multiple styles.

For example:

```text
formal
technical
modern
```

A style can also be explicitly selected:

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

This results in:

```text
Template:

cybersecurity

Style:

technical
```

If no style is specified, the style is selected automatically.

Style selection takes place after the template type has been selected.

---

# Combining Template and Style

Example:

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

Both the template type and style are explicitly specified.

---

# Language

Supported languages:

```text
de
en
```

Default:

```text
de
```

## German Cover Letter

```bash
python main.py \
    --company example-security \
    --language de
```

Uses:

```text
data/de/
```

## English Cover Letter

```bash
python main.py \
    --company example-security \
    --language en
```

Uses:

```text
data/en/
```

The selected language is also taken into account when generating the PDF and ZIP archive.

---

# Seed

`--seed` can be used to make template and style selection reproducible.

Example:

```bash
python main.py \
    --company example-security \
    --seed 12345
```

Internally, the tool uses a dedicated random generator initialized with the specified seed.

This allows the same selection process to be reproduced.

Example:

```bash
python main.py \
    --company example-security \
    --language en \
    --seed 12345
```

With the same inputs and the same seed, the selection can be reproduced.

---

# Documents

By default, the tool uses the documents directory configured in `config.py`.

A custom directory can be specified using `--documents`:

```bash
python main.py \
    --company example-security \
    --documents "/Users/max/Documents/Application"
```

The path is resolved and validated.

The tool expects at least one usable application document.

The discovered documents are then included in the application ZIP archive.

Example output:

```text
DOCUMENTS

------------------------------------------------------------

  • Resume.pdf

  • Certificates.pdf

  • References.pdf

------------------------------------------------------------

Count: 3
```

---

# Email Delivery

## Send an Individual Application

Create an application and then send it after confirmation:

```bash
python main.py \
    --company example-security \
    --send
```

Before sending, a security confirmation is displayed:

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

Accepted confirmations:

```text
y
yes
j
ja
```

Any other input cancels the send operation.

---

# Sending Without Confirmation

For automated workflows, the confirmation can be skipped:

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

**Warning:** In this mode, the email is sent immediately.

---

# Dry-Run

Dry-run mode is the safest way to test the complete sending workflow.

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

The following steps are executed:

- Applicant data is loaded
- Company data is loaded
- Documents are validated
- Matching is performed
- Template is selected
- Cover letter is generated
- PDF is created
- ZIP archive is created

However:

**No email is actually sent.**

Example:

```text
================================================================================

DRY-RUN – NO EMAIL WILL BE SENT

================================================================================

Recipient: jobs@example.com
Subject: Application for Junior Security Engineer
Attachment: generated/...

→ No JSON file is modified.

→ No email was sent.
```

---

# Bulk Sending

`--send-all` processes all companies from `companies.json` sequentially:

```bash
python main.py --send-all
```

The workflow for each company is:

```text
Load company

      ↓

Duplicate Detection

      ↓

Create application

      ↓

Matching

      ↓

Select template

      ↓

Generate cover letter

      ↓

Create PDF

      ↓

Create ZIP

      ↓

Send email

      ↓

Save history

      ↓

Remove company from companies.json
```

Companies are processed one at a time.

Example:

```text
================================================================================

AUTOMATED APPLICATION SENDING

================================================================================

5 companies found.

Applications will be processed sequentially.

A company is only removed after a successful email delivery.

================================================================================

[1/5] Example Security GmbH

Position: Junior Security Engineer

Email:    jobs@example.com

================================================================================
```

---

# Important: `--send-all` Behavior

A company is **only removed from `companies.json` after successful email delivery**.

If application generation fails:

```text
✗ Application generation failed

→ Company remains in companies.json.
```

If email delivery fails:

```text
✗ Email delivery failed

→ Company remains in companies.json.
```

If email delivery succeeds but removing the company from `companies.json` fails:

```text
⚠ Email was sent,

but the company could not be removed from companies.json.
```

This prevents a company from accidentally disappearing from the queue after a previous failure.

---

# `--send-all` and Templates

`--send-all` uses the same generator as the normal individual sending workflow.

Therefore, each company also goes through:

```text
Matching

    ↓

Template Selection

    ↓

Style Selection

    ↓

Cover Letter Generation
```

The bulk sender calls `build_application()` for every company and passes the selected template, style, language, and seed.

If no `--template` is specified, the generator can automatically determine the appropriate template.

Example:

```bash
python main.py --send-all
```

Each company is therefore processed individually.

---

# Bulk Sending with Language

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

# Bulk Sending with Template

Force one template for all companies:

```bash
python main.py \
    --send-all \
    --template cybersecurity
```

Force both a template and a style:

```bash
python main.py \
    --send-all \
    --template cybersecurity \
    --style technical
```

This overrides automatic template selection.

---

# Simulating Bulk Sending

The complete bulk sending process can also be executed as a dry-run:

```bash
python main.py \
    --send-all \
    --dry-run
```

For every company, the application is built.

However:

- No email is sent
- No company is removed from `companies.json`
- No JSON file is modified

Example:

```text
================================================================================

[1/20] Example Security GmbH

================================================================================

DRY-RUN – NO EMAIL WILL BE SENT

Recipient: jobs@example.com
Subject: Application for Junior Security Engineer
Attachment: generated/...

→ Company remains in companies.json.
```

Dry-run mode is particularly useful for verifying the complete workflow before performing a real bulk send.

---

# Application History

Application history is stored in:

```text
data/history.json
```

Display the history:

```bash
python main.py --history
```

The history contains information such as:

- Company
- Company ID
- Position
- Email
- URL
- Job ID
- Applicant
- Status
- Creation timestamp
- Send timestamp
- Match Score
- Confidence Score
- Template type
- Template style
- ZIP file

Example:

```text
================================================================================

APPLICATION HISTORY

================================================================================

[1] Example Security GmbH

    Position: Junior Security Engineer

    Email:    jobs@example.com

    Status:   sent

    Created:  2026-09-09T02:30:00+00:00

    Sent:     2026-09-09T02:31:00+00:00

    Match:    82.5%

    Confidence: 91.0%

================================================================================
```

---

# History Status

Depending on the workflow, different statuses can be stored.

For example:

```text
generated
sent
failed
cancelled
```

A `sent` entry means that the application was actually sent.

---

# Duplicate Detection

The tool includes duplicate detection.

A stable history key is generated for each application.

Priority:

```text
1. job_id

2. company id + position + email

3. company name + position + email
```

This allows a job to be recognized even if other fields have changed.

---

# Duplicate Behavior

If an existing history entry is found, a warning is displayed.

During normal application creation, the application can still be generated.

During sending, an already-sent application is blocked by default.

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

# Force

If an existing application should intentionally be sent again:

```bash
python main.py \
    --company example-security \
    --send \
    --force
```

With automatic confirmation:

```bash
python main.py \
    --company example-security \
    --send \
    --force \
    --yes
```

`--force` disables duplicate protection for the current run.

---

# Logging

The tool uses logging for important processing steps.

By default, logs are written both to the terminal and to the configured log file.

Enable more detailed logging:

```bash
python main.py \
    --company example-security \
    --verbose
```

Short form:

```bash
python main.py \
    --company example-security \
    -v
```

It can be combined with other options:

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run \
    --verbose
```

In verbose mode, the logger is set to `DEBUG`.

---

# Typical Workflows

## 1. List Companies

```bash
python main.py --list-companies
```

---

## 2. Check a Position

```bash
python main.py \
    --company example-security \
    --match-only
```

---

## 3. Create an Application

```bash
python main.py \
    --company example-security
```

---

## 4. Create an English Application

```bash
python main.py \
    --company example-security \
    --language en
```

---

## 5. Use a Specific Template

```bash
python main.py \
    --company example-security \
    --template cybersecurity
```

---

## 6. Set Template and Style

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

---

## 7. Reproducible Generation

```bash
python main.py \
    --company example-security \
    --seed 12345
```

---

## 8. Preview the Cover Letter

```bash
python main.py \
    --company example-security \
    --preview
```

---

## 9. Simulate Sending

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

---

## 10. Send an Application

```bash
python main.py \
    --company example-security \
    --send
```

---

## 11. Send Automatically

```bash
python main.py \
    --company example-security \
    --send \
    --yes
```

---

## 12. Simulate All Applications

```bash
python main.py \
    --send-all \
    --dry-run
```

---

## 13. Send All Applications

```bash
python main.py \
    --send-all \
    --yes
```

---

## 14. Send All Applications in English

```bash
python main.py \
    --send-all \
    --language en \
    --yes
```

---

## 15. Send an Application Again

```bash
python main.py \
    --company example-security \
    --send \
    --force
```

---

## 16. Resend Without Confirmation

```bash
python main.py \
    --company example-security \
    --send \
    --force \
    --yes
```

---

## 17. Display History

```bash
python main.py --history
```

---

# CLI Options

| Option                | Description                                 |
| --------------------- | ------------------------------------------- |
| `--company COMPANY`   | Company ID from `companies.json`            |
| `--send-all`          | Process and send all companies sequentially |
| `--documents PATH`    | Use a custom application document directory |
| `--template TEMPLATE` | Force a specific template type              |
| `--style STYLE`       | Force a specific template style             |
| `--language {de,en}`  | Language of the cover letter                |
| `--seed SEED`         | Seed for reproducible selection             |
| `--match-only`        | Run matching only                           |
| `--preview`           | Display the cover letter without sending    |
| `--send`              | Send the application via email              |
| `--dry-run`           | Simulate sending                            |
| `--yes`, `-y`         | Skip the sending confirmation               |
| `--list-companies`    | Display available companies                 |
| `--history`           | Display application history                 |
| `--force`             | Bypass duplicate detection during sending   |
| `--verbose`, `-v`     | Enable verbose logging                      |
| `--help`              | Display help                                |

---

# `--preview`

Displays the generated cover letter directly in the terminal:

```bash
python main.py \
    --company example-security \
    --preview
```

No email is sent.

The generated application is still stored in the history.

---

# `--match-only`

Runs only the matching process:

```bash
python main.py \
    --company example-security \
    --match-only
```

No application documents are created.

---

# `--dry-run`

Simulates an email sending workflow:

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

No email is sent and no JSON files are modified.

---

# `--send-all`

Processes all companies from:

```text
data/companies.json
```

sequentially.

Successfully sent companies are subsequently removed from the queue.

Failed companies remain in the queue.

---

# `--force`

Ignores an existing history entry and allows an application to be sent again:

```text
--force
```

This should only be used when a resend is intentionally required.

---

# `--yes`

Skips the interactive sending confirmation.

It is only useful in combination with:

```text
--send
```

or an automated bulk sending workflow.

Example:

```bash
python main.py \
    --send-all \
    --yes
```

---

# `--documents`

Uses an alternative application document directory:

```bash
python main.py \
    --company example-security \
    --documents "/Users/max/Documents/Application"
```

---

# `--template`

Forces a specific template type:

```bash
python main.py \
    --company example-security \
    --template cybersecurity
```

Without this option, the template type is selected automatically.

---

# `--style`

Forces a specific template style:

```bash
python main.py \
    --company example-security \
    --style technical
```

It can be combined with `--template`:

```bash
python main.py \
    --company example-security \
    --template cybersecurity \
    --style technical
```

---

# `--language`

Available languages:

```text
de
en
```

Example:

```bash
python main.py \
    --company example-security \
    --language en
```

---

# `--seed`

Allows reproducible template and style selection:

```bash
python main.py \
    --company example-security \
    --seed 12345
```

---

# Conflicts

Some options cannot be combined.

## `--send-all` + `--company`

Not allowed:

```bash
python main.py \
    --company example-security \
    --send-all
```

`--send-all` already processes all companies and therefore cannot be combined with a single company selection.

---

## `--send-all` + `--preview`

Not allowed:

```bash
python main.py \
    --send-all \
    --preview
```

---

## `--send-all` + `--match-only`

Not allowed:

```bash
python main.py \
    --send-all \
    --match-only
```

For a single position:

```bash
python main.py \
    --company example-security \
    --match-only
```

---

## `--preview` + `--send`

Not allowed.

`--preview` is explicitly a no-send mode.

---

## `--match-only` + `--send`

Not allowed.

`--match-only` exclusively performs matching.

---

## `--match-only` + `--preview`

Not allowed.

---

## `--yes` Without `--send`

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

The CLI validates these basic conflicts before starting the actual workflow.

---

# Exit Codes

## `0`

Successfully completed.

---

## `1`

Processing error, including:

- Matching
- Template loading
- Template validation
- Document validation
- PDF generation
- ZIP creation
- Email delivery
- History handling
- Other processing errors

---

## `130`

The program was interrupted, for example using:

```text
Ctrl+C
```

---

# Security Mechanisms

The tool contains several protection mechanisms against accidental or duplicate application sending.

## No Automatic Email Without `--send`

A normal invocation:

```bash
python main.py \
    --company example-security
```

does not send an email.

---

## Confirmation Before Sending

Without:

```text
--yes
```

the user must confirm the email before it is sent.

---

## Dry-Run

Using:

```text
--dry-run
```

allows the complete workflow to be tested without actually sending an email.

---

## Duplicate Detection

Previously sent applications are detected and are not sent again by default.

---

## Atomic File Writes

History and changes to `companies.json` are written using temporary files and then replaced atomically.

This helps prevent files from being unnecessarily corrupted if a write operation fails.

---

## Successful Delivery Before Removal

With `--send-all`, a company is only removed from the queue after successful email delivery.

This ensures that failed applications remain available for a later run.

---

# Template Safety

Template files are loaded and validated before they are used.

The generator:

1. Determines the language directory
2. Discovers available templates
3. Loads the template file
4. Validates the JSON
5. Validates the template structure
6. Determines the template type
7. Determines the style

Non-existent templates result in an error and the available templates for the selected language are displayed.

---

# Adding a New Template

A new template generally requires no changes to `generator.py`.

Example for English:

```text
data/en/cloud-security.json
```

It can then be explicitly selected with:

```bash
python main.py \
    --company example-security \
    --language en \
    --template cloud-security
```

For German:

```text
data/de/cloud-security.json
```

and:

```bash
python main.py \
    --company example-security \
    --language de \
    --template cloud-security
```

Discovery is automatic through the `.json` files in the selected language directory.

---

# Recommended Test Workflow

Before sending an application, matching should first be checked:

```bash
python main.py \
    --company example-security \
    --match-only
```

Then generate the application:

```bash
python main.py \
    --company example-security
```

After that, simulate the sending process:

```bash
python main.py \
    --company example-security \
    --send \
    --dry-run
```

For multiple companies:

```bash
python main.py \
    --send-all \
    --dry-run
```

Only after the dry-run has been verified should the real sending process be executed:

```bash
python main.py \
    --send-all \
    --yes
```

---

# Complete Example Workflow

```bash
# List companies

python main.py --list-companies

# Check position

python main.py \
    --company example-security \
    --match-only

# Create application in English

python main.py \
    --company example-security \
    --language en

# Test application with a specific template

python main.py \
    --company example-security \
    --language en \
    --template cybersecurity \
    --style technical \
    --preview

# Simulate sending

python main.py \
    --company example-security \
    --language en \
    --send \
    --dry-run

# Send individual application

python main.py \
    --company example-security \
    --language en \
    --send

# Display history

python main.py --history
```

---

# Complete Bulk Sending

Preparation:

```bash
python main.py \
    --send-all \
    --dry-run
```

If everything looks correct:

```bash
python main.py \
    --send-all \
    --yes
```

English bulk sending:

```bash
python main.py \
    --send-all \
    --language en \
    --yes
```

Using a fixed template:

```bash
python main.py \
    --send-all \
    --language en \
    --template cybersecurity \
    --yes
```

---

# Help

The complete CLI help can be displayed at any time:

```bash
python main.py --help
```

---

# Quick Reference

```text
LIST

python main.py --list-companies


MATCHING

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


SEND WITHOUT CONFIRMATION

python main.py --company ID --send --yes


BULK SEND

python main.py --send-all


BULK SEND DRY-RUN

python main.py --send-all --dry-run


AUTOMATED BULK SEND

python main.py --send-all --yes


HISTORY

python main.py --history


RESEND

python main.py --company ID --send --force


VERBOSE

python main.py --company ID --verbose


HELP

python main.py --help
```

---

# Architecture

The central workflow is deliberately modular:

```text
main.py

   │

   ├── application.generator
   │       │
   │       ├── Template Discovery
   │       ├── Template Validation
   │       ├── Template Selection
   │       ├── Style Selection
   │       └── Cover Letter Generation
   │
   ├── matching.matcher
   │       └── Job Matching
   │
   ├── documents.converter
   │       └── PDF
   │
   ├── documents.archive
   │       └── ZIP
   │
   └── mail.sender
           └── Email
```

This keeps matching, generation, document creation, archiving, and email delivery separated from each other.

---

# Design Principle

The system is designed so that new templates can be added through the data structure without manually extending the generator for every new template type.

Example:

```text
data/en/

├── cybersecurity.json
├── it.json
├── software.json
├── cloud-security.json
└── devops.json
```

The generator automatically discovers these files.

Template selection remains dynamic:

```text
Company

   ↓

Job Type / Keywords / Information

   ↓

Matching

   ↓

Available templates for selected language

   ↓

Automatic template selection

   ↓

Automatic style selection

   ↓

Individual cover letter
```

An explicit:

```text
--template
```

overrides automatic template selection.

An explicit:

```text
--style
```

overrides automatic style selection.

---

# Conclusion

The Application Tool can process both individual applications and complete application queues automatically.

The most important modes are:

```bash
# Check

python main.py --company ID --match-only


# Create

python main.py --company ID


# Test

python main.py --company ID --send --dry-run


# Send

python main.py --company ID --send


# Test all

python main.py --send-all --dry-run


# Send all

python main.py --send-all --yes
```

Templates are automatically discovered from the existing language-specific JSON files in `data/de/` and `data/en/`.

This makes the system easily extensible: new template types can be added simply by placing a new JSON template into the appropriate language directory.

No changes to the CLI or generator are required for every new template type.
