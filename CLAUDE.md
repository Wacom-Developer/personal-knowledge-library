# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Python SDK (`personal_knowledge_library`, currently v4.3.0) for Wacom's **Private Knowledge System (PKS)** — a multi-tenant cloud knowledge-graph service. Wraps PKS REST APIs for ontology management, entity CRUD, semantic search, Named Entity Linking, group/user/access management, ink processing, and content APIs. Also ships a Wikidata connector for importing public-graph entities.

Library only — no application code, no server. Consumers are partner companies with a Wacom-issued tenant API key.

## Build, test, lint

uv-managed; Python ≥3.10 (CI matrix: 3.10, 3.11, 3.12, 3.13). `mypy` runs against 3.11.

```bash
uv sync --extra dev --extra cache    # full dev environment (creates .venv)
uv run pytest                        # full test suite (uses pytest.ini env; --cov + HTML report already on)
uv run pytest tests/test_async_client.py::test_name -v   # single test
uv run black .                       # format (line length 120)
uv run mypy knowledge                # strict type-check (3.11)
uv run pylint --rcfile=.pylintrc $(git ls-files '*.py') --fail-under=9.5
uv run flake8                        # max-line-length=120, ignore E203
uv build                             # build wheel + sdist into dist/
uv run --python 3.10 pytest          # run the suite against another supported interpreter
```

`uv run` re-syncs before it runs, which drops extras it was not asked for; pass the same
`--extra` flags, or `--no-sync` to use the environment exactly as `uv sync` left it.
`uv.lock` is committed — regenerate it with `uv lock` whenever a dependency range changes.

**Tests hit the live PKS stage server.** `pytest.ini` hard-codes `TENANT_API_KEY`, `INSTANCE=https://stage-private-knowledge.wacom.com`, and `EXTERNAL_USER_ID` as `pytest-env` vars. Failing tests can mean stage is down, not a code bug — check connectivity before debugging logic. There is no `conftest.py`; some tests provision and tear down users/entities directly.

## Architecture

```
knowledge/
├── base/              # Pure data models — no network, no I/O
│   ├── ontology.py    # ThingObject, OntologyClassReference, DataProperty, ObjectProperty, PropertyType
│   ├── entity.py      # Label, Description, Entity
│   ├── language.py    # LocaleCode constants (EN_US, DE_DE, JA_JP, …) — format "en-US"
│   ├── search.py / access.py / response.py / queue.py / index.py / ink.py / content.py / tenant.py
├── services/          # Sync REST clients (requests-based)
│   ├── base.py        # WacomServiceAPIClient, RESTAPIClient — base for all clients
│   ├── session.py     # TimedSession / RefreshableSession / PermanentSession + TokenManager
│   ├── graph.py       # WacomKnowledgeService — main entity/relation API
│   ├── ontology.py group.py users.py search.py ink.py content.py
│   ├── index_management.py queue_management.py helper.py
│   └── asyncio/       # Async mirrors of every sync client (aiohttp-based)
│       ├── base.py    # adds DNS TTLCache
│       └── graph.py group.py users.py … (NO ontology — sync-only)
├── public/            # Wikidata connector
│   ├── client.py wikidata.py cache.py helper.py relations.py
├── nel/               # Named Entity Linking abstractions + engine
├── ontomapping/       # Wikidata ↔ PKS ontology mapping
└── utils/             # graph iterators (things_iter, async_things_iter), diff, import_format (NDJSON), wikidata, wikipedia
```

**Sync/async parity:** every user-facing service client in `services/` has an `services/asyncio/` counterpart, *except* `OntologyService` (sync-only). Auth/infra modules `session.py`, `tenant.py`, and `helper.py` are also sync-only by design — they're not service clients. New service methods should be added to both forms unless there's a reason not to.

**Sessions own auth state, not clients.** `client.login(tenant_api_key, external_user_id)` returns a session object; clients can be re-bound to existing sessions via `client.use_session(session.id)` so multiple service clients share one token. Three session classes differ only in refresh behavior — `PermanentSession` re-logs in with the tenant key; `RefreshableSession` uses the refresh token but expires after a day idle; `TimedSession` is bare token, ~1h.

**Method-level `auth_key` override:** most service methods accept an optional `auth_key=` kwarg that bypasses the bound session — used in tests and admin-on-behalf-of flows. Don't strip it.

**Retry asymmetry is deliberate.** Sync clients install a `urllib3.Retry(total=3, backoff_factor=0.1, status_forcelist=[502,503,504])` via `RequestsSession` (sync CLI/script callers want transparent recovery). Async clients have **no transport-level retry** — backend callers own retry policy alongside their circuit breakers, idempotency keys, and back-pressure. Don't add a retry layer to `AsyncServiceAPIClient` without a design discussion; "fixing" the asymmetry is a regression.

## Domain glossary

- **PKS** — Wacom Private Knowledge System (the cloud service this SDK targets).
- **WPK** — Wacom Private Knowledge backend (the storage tier; same thing, different layer).
- **Tenant** — top-level isolation boundary. Tenant API key creates users; only Wacom creates tenants.
- **Shadow user** — a user known to PKS only by an `external_user_id`; the consuming app owns real auth.
- **Ontology** — formal domain spec (concepts, relations, data types). Editable via `OntologyService`; changes need `commit()` then `knowledge_client.ontology_update()` on the graph side.
- **ThingObject** — instance of an ontology class in the knowledge graph (a node).
- **DataProperty** vs **ObjectProperty** — literal-valued attribute vs relation to another ThingObject.
- **NEL** — Named Entity Linking; maps text spans to graph entities.
- **Locale codes** — always `<lang>-<COUNTRY>` (e.g. `"en-US"`, ISO-639 + ISO-3166). Use the constants in `knowledge/base/language.py` rather than literals.
- **Visibility / access** — entities are private by default; share via `Group` membership or by setting `tenant_access_right.read = True`.

## Conventions

- Line length 120 across `black`, `flake8`, `pylint`.
- `mypy` is **strict** (`strict = true`, `ignore_missing_imports = true`, `disable_error_codes = ["no-untyped-def"]`). New code must type-check.
- Pylint floor is 9.5/10 — CI fails below.
- Logging via `loguru` (not stdlib `logging`).
- JSON serialization via `orjson` where it appears in service code; keep it.
- Bump `version` in `pyproject.toml` and add a `CHANGELOG.md` entry for any release.

## Where to look first

- New API method → add to both `knowledge/services/<x>.py` and `knowledge/services/asyncio/<x>.py`; share request building via the base classes in `services/base.py`.
- New domain model → `knowledge/base/<x>.py`, no service imports.
- Wikidata import behavior → `knowledge/public/wikidata.py` + `knowledge/ontomapping/`.
- Auth/token bug → `knowledge/services/session.py` + `knowledge/services/base.py`.
- Test patterns → `tests/test_async_client.py` is the broadest example (sync mirrors live next to their async counterparts).
- End-to-end usage of a service → `samples/` has runnable scripts per API (`entity_handling.py`, `async_sample.py`, `nel_text.py`, `content_handling.py`, `ink_services.py`, `tenant_management.py`, …). Fastest way to see how a client is wired up.
- Runtime config → `config/` (`appsettings.json`, `content.json`, `performance.json`) — consumed by samples and tests, not part of the published library.
- Supplemental docs outside README → `docs/` (`mcp-tools-read-operations.md`, `knowledge/`, `tickets/`). `README.md` is still the primary reference.
