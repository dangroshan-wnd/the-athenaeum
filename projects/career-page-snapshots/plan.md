# Career Page Snapshots implementation plan

Each numbered step is a logical, reviewable unit, not a mandatory one-commit boundary. Follow the sequence generally, but combine small adjacent steps or split a step when that makes the change easier to review. Do not separate implementation from the tests or documentation needed to leave the repository usable.

## Agreed V1 decisions

- Keep the current repository directory name, use `career-page-snapshots` for project and flow naming, and use `career_page_snapshots` for the Python package.
- Use separate dev and prod databases selected through `DATABASE_URL`, with the same fixed `landing` schema in both environments. Application code must not branch on the environment to choose database behavior.
- Treat each configured company `name` as its canonical, stable V1 identity. Also reject duplicate normalized `(scraper, slug)` pairs.
- Store a versioned JSONB envelope containing normalized jobs and source/debug metadata. A successful empty board is a valid snapshot with `job_count = 0`; malformed required job data fails the complete company collection rather than producing a partial snapshot.
- Derive `collection_key` from the Prefect flow-run ID, establish an aware UTC `captured_at` before company task execution, and preserve both across retries. An idempotency conflict returns the existing snapshot without updating it.
- Treat configuration/bootstrap failures as flow-level failures. Treat collection, parsing, and persistence failures after company dispatch as company-level failures summarized by a final `Completed` flow state, including when every company fails.
- Treat Netflix, Kalshi, Google, and Palantir as the definitive V1 company set. V1 must not silently substitute demo companies when a source becomes difficult.
- Implement four V1 source adapters: Eightfold for Netflix, Greenhouse for Kalshi, Google Careers for Google, and Lever for Palantir. A successful run captures each company's complete global public inventory; descriptions remain optional.
- Note Meta, NVIDIA, and Microsoft as V2 candidates only. Do not implement or prototype Meta-specific GraphQL, Workday, Microsoft source handling, or Playwright/browser automation in V1.
- V1 may register a deliberately non-runnable Prefect deployment record. It has no work pool, code-storage contract, runtime database-secret injection, or schedule. Those remain explicit production follow-up work.
- The pinned Prefect 3.8.2 feasibility check confirmed that `PrefectClient.create_deployment` accepts omitted work-pool, schedule, storage, and infrastructure fields. Use that narrow SDK path for V1 metadata registration; keep offline validation to YAML structure and flow-entrypoint import so validation itself does not require a Prefect API.
- The numbered steps are suggested review units. Commits may combine or split them when useful; tests stay with the behavior they cover.

1. **Initialize the Git repository and establish repository hygiene**
   - Initialize this directory as a Git repository with `main` as the initial branch.
   - Add a Python-focused `.gitignore` covering virtual environments, caches, build output, local Prefect state, `.env` files, coverage output, dbt build artifacts, and editor/OS files.
   - Add `.env.example`, an initial `README.md`, and the agreed `src`, `tests`, `alembic`, `dbt`, and `.github/workflows` directories with placeholder files only where Git requires them.
   - Preserve `intent.md` and this plan as project documentation.
   - Verify that no credentials, local databases, generated artifacts, or machine-specific settings are tracked.
   - Suggested commit: `chore: initialize career page snapshots repository`

2. **Select and document the definitive V1 companies**
   - Configure Netflix, Kalshi, Google, and Palantir; do not use substitute demo companies.
   - Manually verify each canonical public source, required source identifiers, expected pagination, and the minimum fields needed for inventory tracking without building a general discovery system.
   - Record all four choices in `companies.yml`: Netflix via Eightfold, Kalshi via Greenhouse, Google via Google Careers, and Palantir via Lever.
   - Require complete global public inventory for a successful collection and keep descriptions optional. Live endpoint availability is a setup concern, not a unit-test dependency.
   - Note Meta, NVIDIA, and Microsoft in documentation as V2 candidates only. Exclude their integrations, Workday, browser automation, and anti-bot work from V1.
   - Suggested commit: `docs: lock definitive V1 company sources`

3. **Create the installable Python project and lock its toolchain**
   - Create the `src/career_page_snapshots` package and its `flows`, `scrapers`, and `database` subpackages.
   - Configure `pyproject.toml` for Python `>=3.12,<3.13`, Prefect 3.x, runtime dependencies, and development dependencies.
   - Configure Ruff linting/formatting and pytest, including registration of the `integration` marker and default exclusion of integration tests.
   - Use `uv` to resolve dependencies and commit `uv.lock` so local development, CI, and Docker use the same versions.
   - With the pinned Prefect version, perform a small local feasibility check for offline `prefect.yaml` validation and metadata-only deployment registration with no work pool or schedule. Record whether the supported implementation uses the CLI or a narrow Prefect SDK/client call so this is not discovered late in V1.
   - Add a minimal import/version smoke test and run `uv run ruff check .`, `uv run ruff format --check .`, and the default `uv run pytest`.
   - Add baseline `.github/workflows/ci.yml` coverage for these same locked-environment checks on pull requests and appropriate pushes. Keep it credential-free and extend it later when dbt exists.
   - Suggested commit: `build: scaffold Python package and locked toolchain`

4. **Implement environment and company configuration**
   - Add validated settings for the application environment, `DATABASE_URL`, companies-file path, HTTP timeout, and other genuinely shared runtime settings.
   - Add typed validation for `companies.yml`, including supported scraper names, nonempty company names/slugs, case-normalized duplicate company-name and `(scraper, slug)` detection, and the fewer-than-10-company limit.
   - Use the company name as the canonical V1 identity and document that changing it starts a new history. Support an optional validated Lever `region` (`global` or `eu`) that defaults to `global`; require a validated HTTPS `careers_host` and nonempty `domain` for Eightfold; keep the Google Careers source URL adapter-owned rather than configurable.
   - Resolve configuration paths predictably for both an installed package and local execution; do not embed dev/prod branches in application logic.
   - Add deterministic unit tests for valid configuration and representative invalid configurations.
   - Update `.env.example` with safe placeholders only.
   - Suggested commit: `feat: add validated environment and company configuration`

5. **Define the normalized job and scraper contracts**
   - Define `external_job_id`, `title`, and `url` as required strings; define `description` as optional text; and explicitly choose collection-valued normalized fields for location and department so multi-location/source records are not flattened or discarded. Require `raw_payload` to remain JSON-serializable.
   - Define the small common scraper interface and the result metadata needed to construct a debuggable full-company snapshot.
   - Define a versioned payload envelope such as `{schema_version, source, jobs}`. Include the adapter, source identifier, canonical API URL, retrieval/page metadata, and other bounded debugging fields; require `job_count == len(jobs)`.
   - Specify all-or-nothing parsing: missing documented optional fields are allowed, but one malformed required job fails the company collection. A valid empty API response produces an empty successful result.
   - Define one shared HTTP failure policy: retry transport errors plus HTTP 408, 429, and 5xx responses with bounded attempts/backoff; do not retry ordinary 4xx responses, configuration errors, or deterministic parsing failures.
   - Keep retrieval separate from pure payload parsing and use only the small concrete dispatch needed for the four V1 adapters; do not build a plugin framework.
   - Add contract-level unit tests for serialization and optional-field behavior.
   - Suggested commit: `feat: define scraper and normalized job contracts`

6. **Implement and test the Greenhouse adapter**
   - Save a representative Greenhouse response under `tests/fixtures`; remove or replace unnecessary personal or volatile data.
   - Implement a pure Greenhouse parser that maps the fixture into normalized jobs while retaining each source record in `raw_payload`.
   - Implement the Greenhouse HTTP retrieval function using its structured public endpoint with full content enabled, a bounded timeout, status checking, and the shared retry classification. Do not invent pagination for the public board-list endpoint if the pinned API contract does not expose it.
   - Include useful source metadata and the resolved source URL in the collection result.
   - Unit-test parsing, missing optional fields, empty boards, and malformed payloads without making live network calls.
   - Suggested commit: `feat: add Greenhouse job board adapter`

7. **Implement and test the Lever adapter**
   - Save a representative Lever response under `tests/fixtures`; remove or replace unnecessary personal or volatile data.
   - Implement a pure Lever parser with the same normalized contract and retained `raw_payload`.
   - Implement Lever HTTP retrieval with the validated global/EU base URL, a bounded timeout, status checking, the shared retry classification, and complete `skip`/`limit` pagination with a finite safety bound.
   - Include useful source metadata and the resolved source URL in the collection result.
   - Unit-test parsing, missing optional fields, empty boards, and malformed payloads without making live network calls.
   - Suggested commit: `feat: add Lever job board adapter`

8. **Implement and test the Eightfold adapter for Netflix**
   - Save representative Eightfold list and detail responses under `tests/fixtures`; remove or replace unnecessary personal or volatile data.
   - Implement a pure Eightfold parser using stable posting IDs, titles, locations, departments, canonical URLs, and retained `raw_payload`.
   - Implement complete `start`/`num` list pagination against the validated HTTPS careers host and domain, with bounded timeouts, status checking, the shared retry classification, and a finite safety bound.
   - Do not make per-job detail retrieval a completeness requirement. Descriptions may be populated when already available through a bounded retrieval strategy, but the complete inventory takes priority.
   - Unit-test parsing, missing optional descriptions, pagination, empty results, count mismatches, repeated pages, and malformed payloads without live network calls.
   - Suggested commit: `feat: add Netflix Eightfold adapter`

9. **Implement and test the Google Careers adapter**
   - Save representative first, middle, final, and empty Google Careers HTML pages under `tests/fixtures`; remove volatile presentation content that is not needed by the parser.
   - Implement a pure server-rendered HTML parser for stable job IDs/URLs, titles, locations, and other available normalized fields while retaining bounded source data for debugging.
   - Implement complete `page` pagination against the adapter-owned official Google Careers results URL with bounded timeouts, status checking, the shared retry classification, duplicate-page detection, and a finite safety bound.
   - Validate completeness using the reported result count and unique collected IDs. A layout change, count mismatch, repeated page, or missing required job data fails the collection rather than writing a partial snapshot.
   - Unit-test parsing, pagination termination, empty results, duplicate detection, count mismatches, and malformed HTML without live network calls.
   - Suggested commit: `feat: add Google Careers adapter`

10. **Provide a local Postgres development environment**
   - Add a minimal `compose.yaml` for a pinned Postgres image with a named development volume and a health check.
   - Expose credentials only through environment variables with non-production defaults documented in `.env.example`; do not commit actual secrets.
   - Document commands to start, inspect, stop, and reconnect to the development database without deleting its volume.
   - Confirm that the application and migration tooling can consume the same `DATABASE_URL`.
   - Suggested commit: `chore: add local Postgres development service`

11. **Initialize Alembic and create the landing snapshot schema**
   - Configure Alembic to read `DATABASE_URL` from the environment rather than from committed configuration.
   - Create an initial migration that creates the `landing` schema and `landing.career_page_snapshots`.
   - Define a UUID primary key, required text identifiers, `captured_at timestamptz`, a nonnegative `job_count`, required `jsonb payload`, and required `collection_key`.
   - Add uniqueness on `(company_name, collection_key)` plus useful company/capture-time indexes, and provide a correct downgrade.
   - Test upgrade/downgrade only against a dedicated disposable database selected through `TEST_DATABASE_URL`; never run destructive migration verification against the normal dev or prod database. Verify the resulting constraints and column types.
   - Make downgrade behavior safe when the `landing` schema pre-existed or contains unrelated objects; do not use a cascading schema drop.
   - Suggested commit: `feat: add career snapshot database migration`

12. **Implement idempotent snapshot persistence**
    - Add the database writer using parameterized SQL or a lightweight database library; do not add an ORM unless it solves a concrete need.
    - Construct payloads containing normalized jobs and source/debug metadata, calculate `job_count`, and accept a capture timestamp established by the caller.
    - Make repeated writes for the same `(company_name, collection_key)` idempotent so task retries cannot create duplicate snapshots. On conflict, preserve and return the existing row rather than updating the first successful observation.
    - Add unit tests for payload construction and schema-level expectations.
    - Add separately marked Postgres integration tests for a successful insert, retry/idempotency behavior, JSONB round-tripping, and constraint enforcement.
    - Suggested commit: `feat: persist idempotent company snapshots`

13. **Build the Prefect ingestion flow**
    - Create the `career-page-snapshots` flow and focused tasks for network collection and persistence.
    - Load companies from configuration, dispatch to the selected adapter, and process each company independently.
    - Establish one aware UTC `captured_at` per logical company collection and derive its `collection_key` from the Prefect flow-run ID before company task execution; retain both across retries.
    - Retry transient network failures with bounded attempts/backoff; do not retry deterministic parsing or configuration failures indiscriminately.
    - Do not write a snapshot when collection of that company's full board fails.
    - Return a structured summary of successful and failed companies. If any dispatched company fails, including persistence failure or an all-company failure, finish the Prefect run in a manually constructed `Completed` state with a message and summary status of `completed_with_errors`. Invalid application/company configuration remains a failed flow run.
    - Add unit tests with mocked adapters and writer calls for total success, partial failure, retry, empty-board, and idempotency-key behavior.
    - Suggested commit: `feat: orchestrate snapshot ingestion with Prefect`

14. **Validate the complete manual development workflow**
    - Add a clear local entry point for running the unscheduled flow with the dev configuration.
   - Start Postgres, apply Alembic migrations, run the flow against all four configured public sources, and query one stored snapshot per company.
    - Confirm logs show job counts/source URLs without leaking secrets or dumping full descriptions unnecessarily.
    - Add a small smoke-test checklist or script that performs non-destructive readiness checks; keep live-board execution outside the deterministic pytest suite.
    - Fix integration issues discovered by this first end-to-end run.
    - Suggested commit: `test: validate the local ingestion workflow`

15. **Add the lightweight dbt project scaffold**
    - Create a dbt Postgres project under `dbt/` with profiles driven by environment variables and no committed credentials.
    - Declare `landing.career_page_snapshots` as a source and add enough structure for `dbt parse` to validate the project and source declaration; do not claim that future model lineage exists yet.
    - Document the future `staging.stg_job_postings` and `marts.job_postings_history` models and derived fields (`first_seen_at`, `last_seen_at`, `is_active`, and `days_open`) without building speculative staging logic or marts.
    - Add lightweight source/schema tests where they do not require a live warehouse during normal CI.
    - Verify `dbt parse` locally.
    - Suggested commit: `feat: scaffold dbt project and snapshot source`

16. **Containerize the application reproducibly**
    - Add a minimal Dockerfile based on a pinned Python 3.12 image.
    - Install dependencies from the committed `uv.lock`, install the project, run as a non-root user where practical, and keep build context small with `.dockerignore`.
    - Supply a default command suitable for invoking the flow/worker code while allowing deployment-time override.
    - Do not bake configuration, credentials, or a local `.env` into the image.
    - Build the image and run a non-destructive import/help smoke test; document how the container connects to the Compose Postgres service.
    - Suggested commit: `build: add reproducible application container`

17. **Define intentionally non-runnable Prefect deployment metadata**
    - Add `prefect.yaml` for the production-named deployment using the implemented flow entry point.
    - Keep V1 register-only and deliberately non-runnable: no work pool, code-storage/image pull contract, or schedule. Clearly label this state in deployment metadata and documentation.
    - Validate YAML structure and flow-entrypoint import without requiring a Prefect API. Use the metadata-only CLI or narrow Prefect SDK/client mechanism proven during toolchain setup; do not invent infrastructure merely to satisfy the standard runnable-deployment path.
    - Do not read, template, or pass `PROD_DATABASE_URL` during V1 registration. Document it as a future runtime-injected secret after the execution model is chosen.
    - Record the future daily schedule and the unresolved execution decision: persistent worker versus managed container platform/work pool.
    - Validate the file with the pinned Prefect version.
    - Suggested commit: `chore: add register-only Prefect deployment definition`

18. **Extend pull-request and push CI for the complete scaffold**
    - Extend the baseline `.github/workflows/ci.yml` created with the toolchain.
    - Continue using Python 3.12 and `uv` from the lockfile; run Ruff check/format validation, run default pytest with integration tests excluded, and add `dbt parse` without requiring a live warehouse.
    - Cache only safe dependency artifacts and grant the workflow minimum permissions.
    - Ensure CI requires no Prefect, Postgres, or production credentials.
    - Run the same commands locally and fix all failures before committing.
    - Suggested commit: `ci: extend checks with dbt validation`

19. **Add the main-branch Prefect registration workflow**
    - Add `.github/workflows/deploy.yml` triggered only after changes reach `main`, with an optional manual trigger if useful for controlled registration.
    - Install the exact locked environment and always run the offline YAML/entrypoint validation. Authenticate with `PREFECT_API_KEY` and `PREFECT_API_URL` and register/update the non-runnable production deployment metadata only when both are available.
    - Do not expose or consume `PROD_DATABASE_URL`; runtime secret injection is outside V1 registration.
    - On an automatic main push without Prefect credentials, succeed after validation and clearly report that registration was skipped. Fail clearly when a manual registration is explicitly requested without required Prefect credentials. Keep ordinary PR CI independent of them.
    - Clearly label the workflow/register job as a scaffold: it does not publish an image, operate a worker, or activate the daily schedule.
    - Suggested commit: `ci: scaffold Prefect deployment registration`

20. **Complete the operating documentation**
    - Expand `README.md` with the project purpose, package/database architecture, and a compact Mermaid diagram.
    - Document prerequisites, `uv` setup, environment variables, company selection/configuration, local Postgres startup, Alembic migrations, manual flow execution, tests, integration tests, dbt validation, and Docker usage.
    - Explain dev versus prod, CI versus deployment registration, the `completed_with_errors` behavior, snapshot idempotency, and how to add another supported company.
    - List intentional V1 boundaries: Meta, NVIDIA, and Microsoft are V2-only; no Workday, Meta-specific GraphQL, Microsoft-specific integration, or Playwright; no active production schedule, production worker/runtime, image registry, or analytical marts.
    - Include troubleshooting for unavailable public boards and database connection failures.
    - Suggested commit: `docs: add project setup and operations guide`

21. **Run the V1 release-quality pass**
    - Run Ruff checks, formatting validation, the deterministic unit suite, marked Postgres integration tests, Alembic upgrade/downgrade checks against the dedicated disposable test database, `dbt parse`, a Docker build/smoke test, and one manual dev flow run.
    - Review all tracked files for secrets, generated artifacts, stale placeholders, accidental live-network unit tests, and environment-specific paths.
    - Confirm all four V1 companies can produce complete inventory snapshots, a single-company failure produces `completed_with_errors`, successful companies still persist, and retrying a write does not duplicate a snapshot.
    - Update documentation with any final corrections and summarize intentionally deferred production work.
    - Record the next three small PRs: choose and provision the production execution model, activate/observe the daily Prefect schedule, and build the first staging job-posting model.
    - Suggested commit: `chore: finalize and verify working V1`
