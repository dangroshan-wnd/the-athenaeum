# The Athenaeum

The Athenaeum is a public library of standalone notes: book-club reading,
interview preparation, historical project planning, and small research
experiments.

It is not a software monorepo. Anything needed to build, run, or operate a
system stays in the repository that owns that system.

## Contents

### Book club

- [Designing Data-Intensive Applications](book-club/designing_data_intensive_applications.md) — chapter notes
- [Favorite articles](book-club/favorite_articles.md) — short write-ups of articles worth keeping

### Interview preparation

- [Underdog](interview-prep/underdog/) — talking points and interview notes

### Project notes

Historical planning and design. Active implementation lives in the related
code repositories below.

- [Scratch checklist](projects/project-notes.md)
- [Career-page snapshots](projects/career-page-snapshots/) — [intent](projects/career-page-snapshots/intent.md) and [V1 plan](projects/career-page-snapshots/plan.md) for a Prefect/Postgres job-board collector
- [Fantasy football](projects/fantasy-football/) — historical [schema charter](projects/fantasy-football/schema-design.md) and [data-model ideas](projects/fantasy-football/data-model-ideas.md)

### Research

- [Data engineering](research/data-engineering/) — Airflow and Docker operator notes
- [Local LLM experiments](research/local-llm/) — early Ollama prompt profile (`gwen-beta`)

## Related code repositories

| Repository | Owns |
| --- | --- |
| [The Citadel](https://github.com/dangroshan-wnd/the-citadel) | Active dbt modeling |
| [The Wasteland](https://github.com/dangroshan-wnd/the-wasteland) | Ingestion, scraping, and raw-data handling |
| [Fantasy Football](https://github.com/dangroshan-wnd/fantasy-football) | Application, agent, Android client, and retained analytical Python |

## What stays out of this repository

- Secrets, credentials, private keys, and `.env` files
- Operational runbooks and setup that belong with the owning code
- Generated artifacts, local databases, and machine-specific paths
- Sensitive personal data (see [Local-only data](#local-only-data))

## Repository validation

This repository is public. Before publishing changes, run:

```powershell
python scripts/validate_repository.py
```

The validator inspects **tracked** files for:

- Sensitive paths (`dna-analysis/` must never be tracked)
- Private-looking filenames and key material (`.env`, `.pem`, SSH keys)
- Likely credentials in text (private keys, GitHub tokens, AWS keys, secret assignments)
- Files larger than 10 MiB
- Non-UTF-8 text in expected text suffixes
- Tracked symbolic links

The same check runs on pull requests and on pushes to `main` via
[`.github/workflows/quality.yml`](.github/workflows/quality.yml). No extra
Python packages are required; Git must be available so the script can list
tracked files.

## Local-only data

`dna-analysis/` remains physically inside this working directory as a
temporary local-only exception. The entire directory is gitignored because it
contains sensitive personal data and must never be committed to this public
repository. The validator fails the build if any path under `dna-analysis/`
is tracked.
