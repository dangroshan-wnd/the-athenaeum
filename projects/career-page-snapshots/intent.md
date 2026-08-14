Build the initial scaffold for a small production-style data engineering project called **Career Page Snapshots**.

## Goal

Create a Python project that:

* Collects job postings from a configurable set of fewer than 10 company career sites
* Saves each company's full observed job-listing snapshot as JSONB into Postgres
* Uses Prefect for orchestration
* Supports separate dev and prod environments
* Uses GitHub Actions for PR CI and main-branch deployment
* Is structured so dbt modeling can be added immediately after ingestion
* Is intentionally production-ish, but should stay simple and understandable

Do not overengineer this. Avoid Kubernetes, Terraform, Kafka, microservices, or unnecessary abstractions.

## Initial architecture

Use this rough structure:

```text
career-page-snapshots/
├── src/
│   └── career_page_snapshots/
│       ├── __init__.py
│       ├── flows/
│       │   └── career_snapshots.py
│       ├── scrapers/
│       │   ├── base.py
│       │   ├── greenhouse.py
│       │   ├── lever.py
│       │   ├── eightfold.py
│       │   └── google.py
│       ├── database/
│       │   └── writer.py
│       └── config.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── dbt/
├── alembic/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── companies.yml
├── prefect.yaml
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

Adjust the structure if there is a strong reason, but keep responsibilities clearly separated.

## Functional requirements

### 1. Company configuration

Create a `companies.yml` that allows companies to be added without modifying orchestration code.

Example shape:

```yaml
companies:
  - name: ExampleCo
    scraper: greenhouse
    slug: exampleco

  - name: AnotherCo
    scraper: lever
    slug: anotherco
```

The config should be loaded and validated in Python.

### 2. Scraper interface

Create a small common scraper interface.

Each scraper should return normalized job dictionaries containing fields such as:

```text
external_job_id
title
location
department
url
description
raw_payload
```

Do not force every source to populate every field.

Implement V1 adapters for:

* Greenhouse
* Lever
* Eightfold
* Google Careers

Prefer structured/public JSON endpoints over HTML scraping.

Keep HTTP retrieval separate from payload parsing. Parsing functions should be pure and directly testable with saved fixture payloads. HTTP clients must use bounded timeouts, check response status, and handle pagination when the source API uses it.

The definitive V1 companies are Netflix, Kalshi, Google, and Palantir. A successful collection must capture the complete global public job inventory exposed by the configured source. Full descriptions are best-effort and may be omitted when the inventory response does not provide them or retrieving them would require disproportionate per-job traffic.

Meta, NVIDIA, and Microsoft are V2 candidates only. Do not implement, prototype, configure, or test their integrations in V1. Do not implement Workday, Meta-specific GraphQL retrieval, Microsoft-specific source handling, or Playwright/browser automation yet.

### 3. Snapshot storage

Use Postgres.

Create an Alembic migration for:

```sql
landing.career_page_snapshots
```

with approximately these fields:

```text
snapshot_id
company_name
captured_at
source_url
job_count
payload jsonb
collection_key
```

Each row should represent one full company snapshot at one point in time.

Use a UUID primary key for `snapshot_id`, `text not null` for company/source identifiers, `timestamptz not null` for `captured_at`, a nonnegative integer check for `job_count`, and `jsonb not null` for `payload`. The Alembic migration should create the `landing` schema if it does not already exist and add useful indexes for company and capture-time queries.

`collection_key` should be `text not null` and identify one logical company collection within a flow run. Enforce uniqueness on `(company_name, collection_key)` and make writes idempotent so a Prefect retry cannot create a second snapshot. Establish `captured_at` once for the logical collection rather than once per database-write attempt.

The `payload` should contain the normalized jobs plus enough source metadata to debug ingestion later.

Database connectivity must come from environment variables, preferably a single `DATABASE_URL`.

### 4. Prefect orchestration

Create a Prefect flow named something like:

```text
career-page-snapshots
```

The flow should:

1. Load configured companies
2. Run collection independently for each company
3. Save one snapshot per company
4. Log job counts and failures clearly

Use Prefect tasks where they provide real value.

A failure for one company must not prevent other companies from being collected. Catch and report company-level failures, do not write a snapshot unless the full company collection succeeds, and return a structured run summary containing successes and failures. When one or more companies fail, the Prefect flow run should finish in a `Completed` state whose message and returned summary identify the outcome as `completed_with_errors`; it should not fail the entire flow run.

Add sensible retry behavior for network-related failures.

Develop and validate the unscheduled dev environment first. Do not activate a production schedule in V1. The later production deployment must include a Prefect-managed daily schedule; dev remains manually executed and unscheduled.

### 5. Dev vs prod

Support environment-driven configuration.

Assume:

```text
dev:
- manually executed
- dev Postgres database/schema
- no automatic schedule

prod:
- deployed through CI/CD
- prod Postgres
- scheduled daily through Prefect once the production execution environment is implemented
```

Do not duplicate application code between environments.

### 6. Testing

Use `pytest`.

Add deterministic unit tests for scraper parsing using saved fixtures.

Tests must not depend on live company career sites.

Include at least:

* Greenhouse parser test
* Lever parser test
* Eightfold parser and pagination test
* Google Careers parser and pagination test
* config-loading test
* database payload/schema-level test where practical

If an integration test requires Postgres, clearly isolate and mark it.

Register such tests with a `pytest` `integration` marker. The default local and CI `pytest` command must exclude that marker; document a separate command for running integration tests explicitly.

### 7. Linting / quality

Use modern lightweight Python tooling.

Prefer:

* Ruff for linting/formatting
* pytest for tests

Configure these through `pyproject.toml`.

Use Python 3.12 and Prefect 3.x. Declare `requires-python = ">=3.12,<3.13"`, use `uv` for dependency management, and commit `uv.lock`. Direct dependencies should have sensible compatible bounds, while the lockfile supplies exact reproducible versions for local development, CI, and Docker builds.

### 8. GitHub Actions CI

Create `.github/workflows/ci.yml`.

It should run on pull requests and pushes as appropriate.

At minimum:

```text
checkout
install Python
install dependencies
ruff check
pytest
```

If dbt is scaffolded sufficiently, include `dbt parse` or an equivalent lightweight validation, but do not make CI depend on a real warehouse yet.

### 9. GitHub Actions deployment scaffold

Create `.github/workflows/deploy.yml`.

It should run only after changes reach `main`.

V1 uses a register-only deployment scaffold because the production execution host has not yet been selected. The workflow should validate the deployment configuration and, when the required Prefect secrets are available, register or update deployment metadata. It must not claim that production execution is operational and must not activate the production schedule yet.

Scaffold this path:

```text
checkout
install dependencies
authenticate to Prefect using secrets
validate `prefect.yaml`
register/update the production Prefect deployment metadata
```

Use GitHub Secrets for credentials such as:

```text
PREFECT_API_KEY
PREFECT_API_URL
PROD_DATABASE_URL
```

Do not hardcode secrets.

The later production implementation must choose one of these execution models:

* a persistent Prefect worker on a VM or similar host
* a Docker image executed by a managed container platform and Prefect work pool

That choice must also define code storage or an image registry, runtime secret injection, and the worker/work-pool configuration. Leave these portions and schedule activation clearly documented as next implementation steps rather than inventing infrastructure. The deployment workflow should fail clearly when explicitly invoked for registration without its required Prefect secrets; ordinary PR CI must not require those secrets.

### 10. Docker

Create a simple Dockerfile capable of running the Prefect flow/worker code reproducibly.

Keep it minimal.

### 11. dbt

Create a lightweight dbt directory scaffold, but do not spend substantial time building marts yet.

The eventual intended lineage is:

```text
landing.career_page_snapshots
        ↓
staging.stg_job_postings
        ↓
marts.job_postings_history
```

Future derived fields will include:

```text
first_seen_at
last_seen_at
is_active
days_open
```

For this kickoff, prioritize ingestion/orchestration/CI over analytics modeling.

## README

Write a useful README covering:

* Project purpose
* Architecture
* Local setup
* Environment variables
* Running a flow locally
* Running tests
* Applying Alembic migrations
* How dev vs prod is intended to work
* How to add another company
* CI/CD overview
* Known next steps

Include a simple architecture diagram in Mermaid if appropriate.

## Implementation philosophy

Optimize for:

* readability
* testability
* easy PRs
* easy incremental development
* realistic engineering practices
* minimal infrastructure

Do not create generic abstraction layers unless they already solve a concrete problem.

Do not build speculative features.

## First companies

The definitive V1 set is **Netflix, Kalshi, Google, and Palantir**. Do not silently substitute demo companies. If one of these sources becomes inaccessible or cannot be collected completely without expanding into the deferred V2 techniques, surface that as an explicit implementation blocker or company-level runtime failure rather than weakening snapshot completeness.

Record **Meta, NVIDIA, and Microsoft** as V2 candidates, but do no implementation work for them in V1.

## Deliverable

Implement the project scaffold and working V1.

When finished:

1. Run lint/tests locally
2. Fix any failures
3. Summarize what was created
4. Call out anything intentionally left as a stub
5. Recommend the next 3 small PRs I should make after the initial scaffold
