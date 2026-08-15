# The Athenaeum

The Athenaeum is a public collection of standalone notes, research, and historical project planning. Operational documentation needed to build or run software remains with the repository that owns that software.

## Topics

- [Book club](book-club/)
- [Interview preparation](interview-prep/)
- [Project notes](projects/)
  - [Career-page snapshots](projects/career-page-snapshots/)
  - [Fantasy football](projects/fantasy-football/)
- [Research](research/)
  - [Data engineering](research/data-engineering/)
  - [Local LLM experiments](research/local-llm/)

## Related code repositories

- [The Citadel](https://github.com/dangroshan-wnd/the-citadel) owns active dbt modeling.
- [The Wasteland](https://github.com/dangroshan-wnd/the-wasteland) owns ingestion, scraping, and raw-data handling.
- [Fantasy Football](https://github.com/dangroshan-wnd/fantasy-football) owns the application, agent, Android client, and retained analytical Python.

## Repository validation

Before publishing changes, run:

```powershell
python scripts/validate_repository.py
```

The validator checks tracked files for sensitive paths, likely credentials,
oversized files, and non-UTF-8 text. The same check runs in GitHub Actions.

## Local-only data

`dna-analysis/` remains physically inside this working directory as a temporary local-only exception. The entire directory is ignored because it contains sensitive personal data and must never be committed to this public repository.
