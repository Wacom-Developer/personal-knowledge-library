2026/09/01 - RELEASE 5.0.0
==========================
The 4.4.2 and 4.4.3 entries were never published; everything since 4.4.1 ships here.

A correctness and alignment release. Several defects were live crashes or silent data loss on
documented paths; the service's OpenAPI specification and source were used to find a class of
bug the SDK's own tests cannot catch, where a request is well-formed but the service ignores it.
The ontology API gains the surface added for PKA-531, and the Wikidata / Wikipedia ingestion path
had three failures that all shared one shape: a request or a cache silently returned less than it
should, and the caller could not tell the difference from "there is nothing there".

Wikidata and Wikipedia ingestion
--------------------------------
Three silent-degradation bugs. In each case the pipeline kept running and produced a smaller or
emptier result, so nothing distinguished a broken integration from a sparse source.

- **FIXED** — every Wikimedia request now sends an identifying `User-Agent`. Wikimedia answers
  HTTP 403 to the default `python-requests/x.y` agent, and `knowledge/utils/wikipedia.py` set no
  header, so `__extract_abstract__` and `__extract_thumb__` raised `ExtractionException` on every
  call. `get_wikipedia_summary` swallows that exception and returns `""`, which made the failure
  invisible: a refused request and an article with no abstract look identical to the caller.

  ```python
  get_wikipedia_summary("Vincent van Gogh", "en")   # before: ""   after: 3149 characters
  ```
  The agent is exported as `knowledge.utils.wikipedia.USER_AGENT` and built from
  `knowledge.__version__`, following Wikimedia's policy of tool name, version and contact URL.
  Both request sites now share one `__wikimedia_session__` helper, so a new call site cannot
  omit the header.
- **FIXED** — `wikidata_to_thing(pull_wikipedia=True)` no longer discards the Wikidata
  descriptions in favour of blank ones. It appended one `Description` per sitelink language and
  only fell back to the Wikidata descriptions when that list was *empty* — but an empty summary
  still counts as an entry, so with the 403 above every entity came back holding nothing but
  empty strings, strictly worse than `pull_wikipedia=False`. Blank and whitespace-only summaries
  are now treated as "nothing pulled".
- Covered by `tests/test_wikipedia_unit.py` (9 offline tests pinning the header and the
  fallback) and `tests/test_wikipedia.py` (3 live tests against Wikimedia).
- **FIXED** — `MappingConfiguration.add_class` indexed `WikidataClass` **objects** instead of QID
  strings when the subclass cache was warm, so Wikidata → PKS class mapping worked on the first
  run and silently degraded to the fallback once the cache had been populated or loaded from
  disk. Both paths now index the flattened hierarchy by QID.
- **FIXED** — `WikidataClass.create_from_dict` now restores the subclass tree. `as_dict`
  serialized both directions but the reader only read `superclasses` back, so every class
  loaded from `subclass_cache.ndjson` came back as a leaf. `MappingConfiguration` builds its
  Wikidata-class index from those hierarchies, so reusing a cache silently shrank the index
  from 4671 classes to 56 and re-typed entities — `Q43229` mapped to `wacom:core#Organization`
  instead of `wacom:business#Company`. Restoring the subclasses brings a reused cache back to
  3236 indexed classes. The entry above fixes the in-memory half of this bug; this is the
  on-disk half.

  **Existing caches are already damaged and must be deleted once.** A cache that was loaded by
  the old reader and saved again has the trees stripped on disk: all 5093 entries in the
  shipped `pkl-cache/subclass_cache.ndjson` carry empty `subclasses` *and* `superclasses`.
  Delete `subclass_cache.ndjson` and `superclass_cache.ndjson` to let them regenerate.

  **Known limitation:** a reused cache still does not reproduce a cold build exactly (3236 vs
  4671 indexed classes), because `build_configuration` flattens a single cached root tree
  where a cold fetch flattens every node the hierarchy query returns. Concept types therefore
  still depend on cache state. Closing that gap needs a change to what the subclass cache
  stores, not just how it is read.
- **FIXED** — a QID that Wikidata redirects is now cached under the id that was requested as
  well as the id it resolves to. `Q18220463` resolves to `Q1255283`, so
  `qid_in_cache("Q18220463")` was permanently `False` and every reference re-fetched it — three
  times in a few seconds on one observed crawl. `WikidataCache` gained `cache_redirect` / `resolve_redirect`
  and persists the aliases to `redirect_cache.ndjson`.
- Covered by `tests/test_wikidata_cache_unit.py` — 9 offline tests over both round-trips,
  cycles in the class graph, and redirect resolution across save and load.

Ontology API
------------
Aligns the SDK with the PKA-531 release of the ontology service (reset to base ontology, deletion safety checks, base-property extensions, tenant-vs-base diff, and an apply endpoint that now reports failures).

- **NEW** — `WacomKnowledgeService.ontology_update_status()` and `AsyncWacomKnowledgeService.ontology_update_status()` wrap `GET /v1/ontology-update/status`, returning a typed `OntologyUpdateStatus`. This closes a real gap: `ontology_update` only *accepts* an apply, the work continues in the background while the tenant is locked, and **every graph write is rejected with a 400 until it completes**. Without a way to observe that, callers had no correct way to know when to resume writing.

  ```python
  client.ontology_update()
  while not client.ontology_update_status().is_idle:
      time.sleep(2.0)
  # graph writes are safe again
  ```
  `OntologyUpdateStatus` exposes `state` (an `OntologyUpdateState` of `NoUpdateInProgress` / `Pending` / `Failed`, `None` for values the SDK does not know), the convenience flags `is_idle` / `is_pending` / `has_failed`, `ontology_name`, `previous_ontology_version`, `applied_ontology_version`, `date_added` and `date_modified`. A `Failed` status is resumed — not redone — with `ontology_update(fix=True)`, which the service permits even while the tenant is locked.
- **BREAKING** — `OntologyService.context_diff` returns a typed `OntologyDiff` instead of `Dict[str, Any]`; the service now documents the response schema. New models `OntologyDiff`, `AddedConcept`, `AddedProperty` and `ModifiedBaseProperty` in `knowledge.base.ontology`.

  ```python
  diff = client.context_diff("core")
  if not diff.is_empty:                      # everything reset_context would destroy
      for concept in diff.added_concepts:
          print(concept.reference, concept.subclass_of)
      for prop in diff.modified_base_properties:
          print(prop.reference, prop.added_domains, prop.added_ranges)
  ```
- **Corrected `reset_context` documentation.** The docstring claimed it discards *uncommitted changes*. It does not: it removes all tenant customizations (concepts, properties, base-property extensions, NEL settings, version history), restarts version numbering, and **auto-commits**. It then leaves the tenant locked at ontology version 0 — which blocks every graph write *and* blocks deleting the tenant — until `ontology_update` has been called and the background work has finished. The 409 blockers are now documented as well (another reset in progress, a pending or failed update, a running import job, vector-search settings referencing the ontology, or entities/relations/values still using the tenant's concepts or properties).
- Documented the apply contract change on `ontology_update` (sync and async): a 200 means *accepted*, not *applied*; a 400 means no committed version exists or a failed update must be fixed first; a 409 means the version is already applied, the committed version is older than the applied one, an import job is running, or the apply failed mid-flight and needs `fix=True`. Also documented what `commit(force=True)` bypasses — without it the service rejects "nothing to commit" and "already committed" with a 409.
- **NEW** — `ObjectProperty.incoming_uris` and `ObjectProperty.outgoing_uris` report the target URIs of a relation. `incoming_relations` / `outgoing_relations` are typed `List[Union[str, ThingObject]]` and hold whichever form the service sent: `GET /entity/{uri}/relation` answers with full entity objects, while the bulk-import format uses bare URI strings. Comparing those lists against a URI therefore silently fails, which is easy to get wrong:

  ```python
  relations = client.relations(entity_uri)
  # before: works for imported data, fails against the service's own response
  assert target_uri in relations[prop].outgoing_relations
  # after
  assert target_uri in relations[prop].outgoing_uris
  ```
  Entities that carry no URI are skipped. `outgoing_relations` / `incoming_relations` are unchanged.
- Documented that **inverse relations are materialized by the service** (`create_relation`, sync and async). When the ontology declares an `inverseOf` partner, a single `create_relation` yields all four views of the edge — the relation outgoing on the source and incoming on the target, plus its inverse outgoing on the target and incoming on the source. Creating the reciprocal explicitly is rejected with `409 The relation already exists`, which previously looked like an unexplained failure.
- New **Ontology API** section in `README.md` covering the ontology model, the edit → commit → apply cycle, the asynchronous apply and its two sequencing traps, inverse-relation materialization, the deletion guards, and the reset lifecycle.
- `samples/ontology_creation.py` rewritten around the real lifecycle, fixing three bugs in the process: it called `knowledge_client.use_session(session.id)` with a session id minted by a *different* client (each client owns its own token manager, so this raises `Unknown session id`); it applied the ontology before making any change (now `409 already applied`); and it dereferenced the Leonardo lookup without checking for `None`. It now also demonstrates an inverse property pair and waits for both the commit and the apply. The copy embedded in `README.md` is generated from the file, so the two cannot drift.
- `tests/test_ontology_lifecycle.py` now waits for each apply to finish before writing entities, and finishes the reset with an apply before deleting the tenant — two failures the previous version would have hit against the new service. Its teardown recovers a tenant left mid-reset instead of leaking it.

- **BREAKING** — `OntologyService.pending_version` returns a typed `PendingOntologyVersion` instead of `Dict[str, Any]`. The previous annotation was wrong: `GET /context/{name}/versions/pending` answers with a **list** of change log entries, so the method returned a `list` while claiming a dict, and every attribute access on the result failed.

  ```python
  # before (annotation lied; the value was a list of raw entries)
  pending = client.pending_version("core")
  # after
  pending = client.pending_version("core")
  if not pending.is_empty:
      print(f"version {pending.version}, {len(pending.changes)} change(s)")
      for change in pending.changes:
          print(change.operation, change.element_kind, change.element_uri)
  ```
- New models in `knowledge.base.ontology` for that change log:
  - `PendingOntologyVersion` — the uncommitted version, with `version`, `changes`, `is_empty` and the convenience groupings `concepts`, `data_properties` and `object_properties`.
  - `OntologyChangeRecord` — one entry. Splits the service's composite `kind` (e.g. `INSERT_CONCEPT`) into an `operation` (`OntologyChangeOperation`: `INSERT` / `CHANGE` / `DELETE`) and an `element_kind` (`OntologyElementKind`: `CONCEPT` / `LITERAL` / `RELATION`), and decodes the JSON-string body into a regular `OntologyClass` or `OntologyProperty` via `element` / `concept` / `ontology_property`. The raw `kind` string and the decoded `body` stay available, and an unrecognised `kind` yields `None` for both derived fields rather than raising.
- The change log serialises elements differently from the rest of the REST API; both quirks are normalized by the new models:
  - keys are PascalCase (`SubClassOf`, `Domains`, `Labels: [{Value, Lang}]`) rather than camelCase;
  - the property kind is numeric (`0` = object property, `1` = data property) rather than `"Relation"` / `"Literal"`.
- Timestamps from the ontology service are parsed with a new `parse_service_timestamp` helper, which tolerates a `Z` suffix and the up-to-seven fractional digits .NET emits — neither of which `datetime.fromisoformat` accepts on Python 3.10, the floor this package supports.
- New offline tests in `tests/test_ontology_pending_version.py`, built from a verbatim stage capture, plus updated contract tests in `tests/test_ontology_spec.py` (no PKS stage required).
- New end-to-end integration test `tests/test_ontology_lifecycle.py`: provisions its own tenant with `createAndApplyOnto=True`, walks the whole `OntologyService` surface (create / modify / commit / apply / reset), verifies the graph service honours the applied ontology, and removes the tenant again. Skipped unless `TENANT_MANAGEMENT_API_KEY` is set, since it creates and deletes a tenant.

Wire-format alignment against `graph.json` (GraphDataService API v1) and the service source
--------------------------------------------------------------------------------------------
- **FIXED / BREAKING** — the **locale filter was silently discarded** on `search_all`,
  `search_literal` and `search_relation` (sync and async). All five `/semantic-search/*`
  endpoints bind `locale`; these three sent `language`, which binds to `null`, so the caller's
  `language_code` argument was thrown away and the search ran unfiltered. The requests returned
  200, so nothing surfaced the problem. `search_labels` and `search_description` were already
  correct.

  ```python
  # before: the locale was ignored, results came back for every language
  results, _ = client.search_literal(literal=birth_year, search_term="1452", language_code=EN_US)
  ```
  The now-unused constant `knowledge.services.LANGUAGE_PARAMETER` has been **removed**: it named
  a query parameter no endpoint accepts. Use `LOCALE_TAG`.
- **NEW** — `descriptions(uri)` and `update_descriptions(uri, descriptions)` on both
  `WacomKnowledgeService` and `AsyncWacomKnowledgeService`, wrapping
  `GET`/`PATCH /v1/entity/{uri}/descriptions` (PKA-589). The update is partial and the argument
  carries three distinct meanings:

  ```python
  client.update_descriptions(uri, [Description("A digital pen.", EN_US)])  # replace the set
  client.update_descriptions(uri, [])                                      # delete all
  client.update_descriptions(uri, None)                                    # no-op (204)
  ```
  **The non-empty case replaces the whole set — it does not merge.** Confirmed against the
  service: an entity holding `en_US` and `de_DE`, patched with only `en_US`, is left with
  `en_US` alone. The PKA-589 ticket calls this an "upsert", which reads as if unmentioned
  locales survive; they do not, so patching one locale in isolation destroys the others.
  Always send the complete set the entity should end up with. `None` and `[]` are likewise not
  interchangeable. Covered by wire-format tests plus a live integration test
  (`tests/test_entity_descriptions.py`).
- `entity_payload` now always sends the `descriptions` key, including as an empty list, which is
  what allows an update to clear an entity's descriptions under the PKA-589 semantics above.
  The serialization moved to the shared `knowledge.services.helper.descriptions_payload`.

Correctness
-----------
- **FIXED** — `WikiDataAPIClient.retrieve_entities` raised `IndexError: list index out of range`
  whenever every requested QID was already cached or filtered out as malformed — the ordinary
  case on a second call.
- **FIXED** — `WikiDataAPIClient.search_term` returned only the **first** search result (the
  `return` sat inside the loop) and returned `None` when nothing matched, despite declaring
  `List[WikidataSearchResult]`.
- **FIXED** — a `.ndjson.gz` round-trip **silently dropped the first entity**.
  `load_import_format` skipped line 0 of a gzip file as a header, but the format has no header
  and neither the plain-`.ndjson` reader nor `iterate_large_import_format` skipped anything.
  All three readers and the writer now share one code path.
- **FIXED / BREAKING** — `save_import_format` silently wrote **nothing** for any suffix other
  than `.gz` or `.ndjson`, and matched `.ndjson` case-sensitively. Unsupported suffixes now raise
  `ValueError`.
- **FIXED** — `WacomKnowledgeService.create_entity_bulk` **lost the URIs of entities it had
  created** when an image upload failed: the URI was assigned after the upload, so an exception
  skipped it while the entity existed server-side, leaving the caller unable to reference it and
  prone to duplicating it on retry. The URI is now assigned first and image failures are logged,
  matching the async client.
- **FIXED** — `AsyncWacomKnowledgeService.create_entity_bulk` **silently skipped a rejected
  batch**, returning entities without URIs and no indication that nothing had been written. It
  now raises, as the sync client does.
- **FIXED** — `PendingOntologyVersion.from_list` raised `AttributeError` when the service
  reported a context with no pending changes as a JSON `null`.
- **FIXED** — every `ThingObject` shared **one** `TenantAccessRight` instance, so granting a
  single entity tenant access silently published every entity created afterwards. `tenant_rights`
  was a mutable default argument, evaluated once at import and stored by reference, and both
  parse paths only replaced it when the service actually reported rights (`from_dict` treats the
  empty list the service returns for an entity with none as "absent"). An entity read back
  without rights therefore handed out the shared default, and mutating it in place leaked into
  the constructor:

  ```python
  entity = client.entity(uri)              # no tenant rights -> the shared default
  entity.tenant_access_right.read = True   # intended for this entity only
  ThingObject().tenant_access_right        # before: [Read]   after: []
  ```
  Because `entity_payload` sends `tenantRights` on create, unrelated entities were then created
  tenant-readable — visible to every user in the tenant. The default is now `None` and each
  entity owns its rights; passing an explicit `TenantAccessRight` is unchanged. Covered by three
  offline tests in `tests/test_ontology_unit.py`.
- **FIXED** — `ThingObject.label_lang`, `description_lang` and `alias_lang` accept
  `Union[LocaleCode, LanguageCode]` but compared for exact equality, so a bare language code
  never matched: `label_lang(EN)` silently returned `None` for an entity with an `en_US` label.
  A language code now matches every locale of that language, via the new
  `knowledge.base.ontology.matches_locale`.
- Removed a dead duplicate definition of `WikiDataAPIClient.superclasses` — the first of the two
  was unreachable, and the surviving one is the LRU-cached implementation.

Reliability and performance
---------------------------
- **BREAKING** — the sync transport no longer retries `POST` and `PATCH` on 502/503/504. A
  gateway error can reach the client *after* the backend has committed, so replaying
  `create_entity` / `create_entity_bulk` / `import_entities` silently created duplicates. Retries
  now cover idempotent methods only (`knowledge.services.base.IDEMPOTENT_RETRY_METHODS`). To
  recover from a failed create, check for the source reference id and retry deliberately.
- **FIXED** — `handle_token` is now serialised per client in the sync client, as it already was
  in the async one. A client shared across threads had every thread notice the same
  nearly-expired token and post to `/user/refresh` at once; where the service rotates refresh
  tokens, all but one of those requests invalidated the token the others were about to use.
  Measured: 8 threads produced 8 concurrent refreshes, now 1.
- **FIXED** — `WikidataThing.__hash__` returned `0` for every instance, so every thing landed in
  one hash bucket and any `set` or `dict` of them degraded to a linear scan. Measured at n=2000:
  140.8 ms → 0.16 ms for the same inserts, an **855×** difference that grows with n.
- `WikiDataAPIClient.retrieve_entities` now uses a thread pool instead of `multiprocessing.Pool`.
  The work is HTTP-bound, so processes cost an interpreter re-import per worker (spawn on macOS)
  and a pickling round-trip, while capping parallelism at the core count.
- Failed SPARQL class-hierarchy lookups are no longer cached. `lru_cache` stored the empty
  result returned on error, so one transient Wikidata outage kept a QID's hierarchy empty for the
  lifetime of the process.
- The Wikidata retry budget is bounded (`backoff_max=20`). With `respect_retry_after_header` and
  an unbounded backoff, a single 429 could stall a bulk import for minutes with no progress
  signal.
- **BREAKING** — `WacomKnowledgeService.entities` now splits long URI lists across requests
  (`batch_size`, default `ENTITY_URI_BATCH_SIZE = 40`, shared with the async client's
  `MAX_NUMBER_URIS`). The URIs travel in the query string, so a few hundred of them overran the
  gateway's URL limit and came back as 414. The async client already chunked; it gains the same
  `batch_size` parameter.
- `create_entity_bulk` serialises one batch at a time instead of the whole input up front,
  removing a memory spike at the start of a large import (sync and async).
- `diff_entities` / `diff_entities_async` no longer rebuild the target URI list inside the
  per-target loop, and use a set for the membership test — O(n·m) to O(n+m) per relation type.
- `AsyncSession.close()` no longer clears the process-global DNS cache, which discarded
  resolutions every other live client was still using. The resolver's cache is now keyed by
  address family, so an IPv4 lookup is not answered from an IPv6 entry.
- The async transport converts `timeout` to `aiohttp.ClientTimeout` and `verify_ssl` to `ssl`
  centrally. Both bare-number timeouts and `verify_ssl` are deprecated in aiohttp and removed in
  4.x. `aiohttp` is now pinned `<4.0.0`.
- The async client uses `loguru` for the failed-image-upload message; it was the one stdlib
  `logging` call in the library.

Tooling
-------
- `pyproject.toml`: the mypy setting was spelled `disable_error_codes`, which mypy reported as an
  unrecognised option, so it never applied. Corrected to `disable_error_code`.
- `.pylintrc`: removed two options pylint rejects with `E0015` (`suggestion-mode`,
  `max-complexity`) and added a missing comma that left `not-an-iterable` un-disabled.
- CI now runs pylint with `--fail-on=E`. The score threshold alone let error-level messages
  through, because a handful of errors barely moves a 9.9 rating — that is how the duplicate
  `superclasses` definition survived.
- 104 new offline unit tests, covering the fixes above. They stub the transport and need no
  stage server, and `tests/` now holds 16 `*_unit.py` modules that run without PKS. The one
  deliberate exception is `tests/test_wikipedia.py`, which calls Wikimedia for real — an offline
  suite cannot catch a policy change on their side, which is how the 403 went unnoticed.

2026/08/13 - RELEASE 4.4.1
==========================
- Align `OntologyService` with the Wacom OntologyManager API v1 OpenAPI specification. Twelve operations that had no client method are now available.
- **BREAKING** — `OntologyService.update_concept` now issues `PATCH /context/{context}/concepts/{uri}` instead of `PUT` against the collection URL, which the service does not implement. The signature changed accordingly: the `name: str` and `subclass_of: Optional[str]` parameters are replaced by a single `reference: OntologyClassReference`, and the method returns `None` rather than a dict. The API accepts only labels, comments and the icon; a concept's superclass cannot be changed through it.

  ```python
  # before (did not work against the service)
  client.update_concept(context, "demo:creative#Artist", "wacom:core#Person", icon="i.png")
  # after
  client.update_concept(context, OntologyClassReference.parse("demo:creative#Artist"), icon="i.png")
  ```
- New concept operation: `set_concept_metadata` (`PUT .../concepts/{uri}/metadata`) sets the Named Entity Linking inflection level and case sensitivity of a concept class. Adds an `InflectionLevel` enum (`LOW`, `MID`, `HIGH`) to `knowledge.base.ontology`.
- New context operations: `update_context` (`PUT /context/{name}`), `reset_context` (`POST /context/{name}/reset`) and `context_diff` (`GET /context/{name}/diff`).
- New property operations: `update_property`, `rename_property`, `add_property_domains`, `remove_property_domains`, `add_property_ranges` and `remove_property_ranges`.
- New version operations: `versions`, `pending_version` and `rdf_import` (multipart RDF upload), the last returning a typed `ImportResponse`. Adds `ImportResponse`, `ImportValidation`, `ImportedResource` and `FailedImportResource` to `knowledge.base.ontology`.
- `context_metadata` accepts an optional `version` parameter to read the metadata of a specific context version. Existing calls are unaffected.
- `versions`, `pending_version` and `context_diff` return the parsed JSON payload (`Dict[str, Any]` / `List[Dict[str, Any]]`) because the OpenAPI specification defines no response schema for those three operations.
- New offline tests in `tests/test_ontology_spec.py` and `tests/test_ontology_models.py` (no PKS stage required).
- Fix `OntologyContext.from_dict` against the current service response. `GET /context` returns a **list** of envelopes shaped `{"version": <int>, "data": {...}}`, but the parser indexed the response with `["context"]`, so every call to `OntologyService.context()` raised `TypeError: list indices must be integers or slices, not str`. This broke the entry point of every ontology workflow and cascaded into the Wikidata flows. The parser now reads the `data` payload, still accepts the legacy `context` envelope key, and raises a descriptive `ValueError` naming the received keys when neither is present.
- New `OntologyService.contexts()` returns every context of the tenant; `context()` delegates to it and returns the first, keeping its previous `Optional` / `None`-on-error contract.
- **Note:** the context envelope no longer carries `concepts` or `properties`, so `OntologyContext.concepts` and `.properties` are empty. Use `OntologyService.concepts(context)` and `OntologyService.properties(context)` instead; `tests/test_ontology.py` was updated accordingly.

2026/07/27 - RELEASE 4.3.4
==========================
- Fix that description of an entity cannot be deleted. 
- Improve data-property comparison in both sync and async `diff_entities`

2026/07/10 - RELEASE 4.3.3
==========================
- Fix `AsyncContentClient.download_content` corrupting file bodies whose stored MIME type is `application/json`. The async transport (`AsyncSession._request_content`) deserialized any `application/json` response into a `dict`, so `download_content` returned a re-`str()`-ified dict (invalid JSON) instead of the exact uploaded bytes. The download path now requests raw bytes via a new `raw_content` transport flag; other endpoints are unchanged. Regression guard in `tests/test_content_download_raw.py` (no PKS stage required).

2026/07/01 - RELEASE 4.3.2
==========================
- **Deprecated** `knowledge.utils.wikidata` — the module has no internal callers and is scheduled for removal in v5.0. Importing it now emits a `DeprecationWarning`. Migrate to `knowledge.public.wikidata` or vendor the helpers you need.
- Fixing issue with ontology mapping 

2026/05/04 - RELEASE 4.3.1
==========================
- Token handling hardening in `knowledge/services/session.py`:
  - `TokenManager.add_session` no longer coerces a missing refresh token to an empty string. A `PermanentSession` constructed without a starter refresh token now correctly reports `refreshable == False` and avoids a doomed POST to `/refresh` on the first refresh cycle (the SDK falls back to `request_user_token` directly).
  - `PermanentSession` now raises `ValueError` if the constructor's `external_user_id` does not match the JWT's `ext-sub` claim, eliminating a class of silent identity divergence (BREAKING — previously accepted; the duplicate `__external_user_id` override has been removed and the value is sourced from the inherited `TimedSession` property).
  - `RefreshableSession.update_session` now rejects empty / non-string refresh tokens with `ValueError` instead of silently overwriting a working refresh token.
  - `TimedSession.extract_session_id` now raises `ValueError("Invalid authentication token.")` for JWTs missing any required claim (`tenant`, `roles`, `exp`, `iss`, `ext-sub`); previously a missing claim leaked a `KeyError`. JWT-claim validation is consolidated in a single `_decode_and_validate_token` helper used by `_auth_token_details_`, `extract_session_id`, and `update_session`.
- New unit tests in `tests/test_session_unit.py` covering the four behaviours above (no PKS stage required).
- Adding single activation function
- Add missing showDeleted parameter for listing entities

2026/04/13 - RELEASE 4.3.0
==========================
- Adding clients for the Content API of graph service
- Optimize code for wikidata handling with caching

2026/02/20 - RELEASE 4.2.2
==========================
- Add additional checks for unsupported locales in the description 
- Fix grammar in API documentation
- Re-generate API documentation

2026/02/20 - RELEASE 4.2.1
==========================
- Introduce a raise_on_error parameter to import parsing paths to control error handling.

2026/02/20 - RELEASE 4.2.0
==========================
- Refactoring, move the functions for queue management to dedicated QueueClient
- Adding QueueManagementClient for managing the queues, e.g., listing queues, getting queue details, etc.
- Adding IndexManagementClient for managing the indexes of the Vector Search service
- Adding InkServicseClient for using the conversion services or ink to text, ink to math, services
- Adding additional samples


2026/02/06 - RELEASE 4.1.0
==========================
- Added type annotations and return types - Added -> None, -> str, -> Dict[str, Any], etc. to functions missing return type annotations, and added proper type parameters to generic types like Dict, List, and Tuple
- Fixed response.content type casting - Wrapped all response.content assignments with cast(Dict[str, Any], ...) or appropriate type since the async response content is a union type (str | bytes | bool | dict | list)
- Fixed variable redefinitions in try/except blocks - Changed patterns like var: Type = value in both try and except branches to declare the type first (var: Type) then assign in each branch to avoid mypy "already defined" errors
- Added Optional types and logger guards - Changed function parameters from List[T] = None to Optional[List[T]] = None, and wrapped logger calls with if logger: guards since the logger can be None
- Fixed imports and type compatibility issues - Corrected import paths for symbols like DEFAULT_TIMEOUT, changed setter parameter types to accept Optional[str] where needed, and used cast() with Literal types for enum-like values
- Refactored response handling - Moved response handling code out of the client classes into a separate structure ResponseData

2026/01/21 - RELEASE 4.0.4
==========================
- Adding a new function to use filtering of documents endpoint

2025/12/03 - RELEASE 4.0.3
==========================
- Minor improvements in import format handling
- Adding exact match filter for semantic search sync client

2025/11/27 - RELEASE 4.0.1
==========================
- Major refactoring of the session management and reusing of the same requests and asyncio session for multiple requests
- Adding queue API support for async client
- Changing the constructor parameters of all clients and make it more consistent
- Minor fixes

2025/11//07 - RELEASE 3.5.0
==========================
- Adding support for the new include relations feature of listing entities
- Save import format export now supports export of group ids 
- Minor fixes and improvements

2025/10/24 - RELEASE 3.4.0
==========================
- Adding timeout parameter to an async client
- Support new version of GZIP new uri endpoint
- Update parameters for create tenant parameters
- Minor fixes

2025/09/18 - RELEASE 3.3.2
==========================
- Adding filter_mode to semantic search

2025/09/18 - RELEASE 3.3.1
==========================
- Fix issue with async client for named entity linking.

2025/09/17 - RELEASE 3.3.0
==========================
- Add tokens and tokens indexes to named entity linking results
- Adding support for import format endpoint
- Minor fixes

2025/07/03 - RELEASE 3.2.2
==========================
- Minor fixes
- Adding support for entity getter with multiple uris

2025/06/04 - RELEASE 3.2.1
==========================
- Minor fixes
- Adding force parameter for ontology commit

2025/05/07 - RELEASE 3.2.0
==========================
- Adding support for new API for indexing entities 
- Minor fixes and improvements
- Adding new role of ContentManager user

2025/04/04 - RELEASE 3.1.2
==========================
- Adding support for import format
- Fixing issue with reference id not properly added to import format export

2025/03/20 - RELEASE 3.1.1
==========================
- Improved wikidata cache handling

2025/03/19 - RELEASE 3.0.0
==========================
- Change to Poetry for package management
- Remove tools from the package
- Improvements for wikidata import
- Introduce black for formatting

2025/01/22 - RELEASE 2.5.0
==========================
- Refactoring of the clients, adding the timeout, max_retries, and backoff_factor parameters
- Minor fixes and improvements
- Changes in wikidata import

2024/12/17 - RELEASE 2.4.3
==========================
- FIX: Delete function in async client

2024/12/09 - RELEASE 2.4.2
==========================
- FIX: Issue with create group. Response was parsed after the request was closed
- User management service client uses session for requests
- Update of requirements and pinning of test dependencies

2024/11/26 - RELEASE 2.4.1
==========================
- Minor bug fix for SYSTEM_REFERENCE_ID handling
- Parsing of import format with backward compatibility

2024/10/24 - RELEASE 2.4.0
==========================
- Introduce graceful shutdown for async client

2024/10/10 - RELEASE 2.3.0
==========================
- Enable ontology to export different versions of the ontology

2024/09/26 - RELEASE 2.2.0
==========================
- Introduction of new API for indexing entities for vector search, now Full-text search index can be controlled as target
- Tenant management API is also extended to configure the vector search properties

2024/09/02 - RELEASE 2.1.6
==========================
- Adding support for indexing entities for vector search

2024/06/12 - RELEASE 2.1.5
==========================
- Adding a function to count vector documents and labels using a filter
- Fixing issue tool for wikidata import

2024/05/31 - RELEASE 2.1.4
==========================
- Minor fix use is owner flag in utility function

2024/04/08 - RELEASE 2.1.3
==========================
- Fix issues with import format, sendToNEL flag was not parsed correctly

2024/02/27 - RELEASE 2.1.2
==========================
- Fix some minor issues for timestamp parsing with older python versions (<3.10)
- Adding support for filter owner entities
- Adding vector search sample and tools
- Update helper functions for listing and counting entities

2024/02/15 - RELEASE 2.1.1
==========================
- Fix some minor issues for refresh token handling
- Cosmetics updates to improve pylint score
- Remove requirement for dateutil

2024/02/13 - RELEASE 2.1.0
==========================
- Fix some minor issues for auth token handling with image 
- Adding implementation for vector search 

2024/01/18 - RELEASE 2.0.3
==========================
- Fix issue with auth token handling in async client

2024/01/11 - RELEASE 2.0.2
==========================
- Adding new helper functions
- Fix issue with refresh in async client

2024/01/09 - RELEASE 2.0.1
==========================
- Adding missing dependency

2024/01/09 - RELEASE 2.0.0
==========================
- Major refactoring of the library
- Adding a script to set up a new tenant
- Support for async Client
- Introduction of token management and session handling (breaking change)
- Minor fixes and improvements
- Adding sample for async client
- Adding more unit tests

2023/7/13 - RELEASE 1.0.8
==========================
- Minor fix: No entities returned from Wikidata

2023/7/13 - RELEASE 1.0.7
==========================
- Minor fix: Unclosed file handle
- Ontology configuration update

2023/7/04 - RELEASE 1.0.6
==========================
- Improve handling of the ontology configuration file
- Handle aliases and labels in wikidata to thing mapping

2023/7/03 - RELEASE 1.0.5
==========================
- Ontology configuration file can be now defined as parameter
- Adding support for force parameter in delete group

2023/6/26 - RELEASE 1.0.4
==========================
- Minor fix: sendToNEL flag parse in entity pull
- Automatically fix issue with only alias for a language code defined in entity

2023/6/18 - RELEASE 1.0.3
==========================
- Minor fixe: State of thing object did not handle tenant access rights
- Adding support for fix ontology endpoint 
- Adding support for url data type in wikidata

2023/6/15 - RELEASE 1.0.2
==========================
- Minor fix: Update entity did ignore the sendToNEL flag

2023/6/15 - RELEASE 1.0.1
==========================
- Improve the wikidata scrapping 
- Refactoring typing
- pylint fixes
- Adding some helper functions for the entity management
- Fixing issues with unit tests
- Move Ontology classes to the ontology module

2023/5/23 - RELEASE 0.9.6
==========================
- Improve the session management
- Rename metaData tag to metadata
- Some fixes 

2023/4/24- RELEASE 0.9.5
==========================
- Adding some helper functions for the entity management 
- Fixing some issues with parameters, e.g., force in delete
- Introducing session with retry and backoff in case of private knowledge service is under load

2023/3/24- RELEASE 0.9.4
==========================
- Fixing named entity linking URL

2023/2/23- RELEASE 0.9.3
==========================
- REST API introduced versioning (v1), added the service endpoint constant in constructors
- Improvements in export entities script

2023/1/11- RELEASE 0.9.2
==========================
- Return datatime object rather than a str
- Adding several minor fixes

2022/11/30- RELEASE 0.9.1
==========================
- Adding helper functions for expiration date
- Fix of remove relation function

2022/11/23 - RELEASE 0.9.0
==========================
- Introduce refresh user flow

2022/11/19 - RELEASE 0.8.0
==========================
- Update all samples with the latest changes

2022/10/28 - RELEASE 0.7.1
==========================
- Minor fixes and updated samples

2022/10/26 - RELEASE 0.7.0
==========================
- Supporting the latest version of the service
- Remove the multiple contexts in ontology service
- Adding ownerID and group ids for entities

2022/09/20 - RELEASE 0.6.2
==========================
- Additional function to remove alias
- Fix group removal function

2022/08/26- RELEASE 0.6.1
==========================
- Fix parameters for object properties
- Adding push image functionality for local files

2022/08/09- RELEASE 0.6.0
==========================
- Improve consistency in parameter naming
- Adding visibility flag
- Adding delete concept and property functions
- Fix parameters for multiple domains

2022/07/03- RELEASE 0.5.0
==========================
- Update all samples and tools to pass the instance of the deployed service
- Check the supported languages

2022/03/31- RELEASE 0.4.0
==========================
- Properties can have now multiple domains and ranges.

2022/03/31- RELEASE 0.3.1
==========================
- Fix in ontology API.

2022/03/25- RELEASE 0.3.0
==========================
- Include API changes

2022/01/28- RELEASE 0.2.4
==========================
- Update library to work with the new deployment of Personal knowledge backend staging environment
- Adding User-Agent to request

2021/12/08- RELEASE 0.2.1
==========================
- Adding two functions to upload images for icons

2021/11/23- RELEASE 0.2.0
==========================
- Introducing data structures for user management
- Adding additional documentation
- Introducing group management

2021/11/19- RELEASE 0.1.5
==========================
- Refactoring the user management
- Adding wiki-data handling
- Integrating changes from Ontology services

2021/11/18- RELEASE 0.1.4
==========================
- Adding ontology class 
- Parse RDF export and create an ontology class
- Adding 

2021/11/10- RELEASE 0.1.2
==========================
- Adding support for ontology service. 
- Improving documentation
- Data structure refactoring

2021/11/05- RELEASE 0.1.1
==========================
First private release.