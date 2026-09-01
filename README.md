# Wacom Private Knowledge Library

[![Python package](https://github.com/Wacom-Developer/personal-knowledge-library/actions/workflows/python-package.yml/badge.svg)](https://github.com/Wacom-Developer/personal-knowledge-library/actions/workflows/python-package.yml)
[![Pylint](https://github.com/Wacom-Developer/personal-knowledge-library/actions/workflows/pylint.yml/badge.svg)](https://github.com/Wacom-Developer/personal-knowledge-library/actions/workflows/pylint.yml)

![License: Apache 2](https://img.shields.io/badge/License-Apache2-green.svg)
[![PyPI](https://img.shields.io/pypi/v/personal-knowledge-library.svg)](https://pypi.python.org/pypi/personal-knowledge-library)
[![PyPI](https://img.shields.io/pypi/pyversions/personal-knowledge-library.svg)](https://pypi.python.org/pypi/personal-knowledge-library)
[![Documentation](https://img.shields.io/badge/api-reference-blue.svg)](https://developer-docs.wacom.com/docs/private-knowledge-service) 

![Contributors](https://img.shields.io/github/contributors/Wacom-Developer/personal-knowledge-library.svg)
![GitHub forks](https://img.shields.io/github/forks/Wacom-Developer/personal-knowledge-library.svg)
![GitHub stars](https://img.shields.io/github/stars/Wacom-Developer/personal-knowledge-library.svg)

The required tenant API key is only available for selected partner companies.
Please contact your Wacom representative for more information.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Introduction](#introduction)
- [Technology Stack](#technology-stack)
  - [Domain Knowledge](#domain-knowledge)
  - [Knowledge Graph](#knowledge-graph)
  - [Semantic Technology](#semantic-technology)
- [Functionality](#functionality)
  - [Import Format](#import-format)
  - [Access API](#access-api)
  - [Ontology API](#ontology-api)
    - [The model](#the-model)
    - [The edit → commit → apply cycle](#the-edit--commit--apply-cycle)
    - [Inverse relations are materialized by the service](#inverse-relations-are-materialized-by-the-service)
    - [Deletion is guarded](#deletion-is-guarded)
    - [Resetting a context](#resetting-a-context)
  - [Entity API](#entity-api)
- [Choosing Between Sync and Async Clients](#choosing-between-sync-and-async-clients)
- [Samples](#samples)
  - [Entity Handling](#entity-handling)
  - [Named Entity Linking](#named-entity-linking)
  - [Access Management](#access-management)
  - [Ontology Creation](#ontology-creation)
  - [Asynchronous Client](#asynchronous-client)
  - [Semantic Search](#semantic-search)
  - [Ink Services](#ink-services)
  - [Content API](#content-api)
    - [Business Logic Recommendations](#content-api--business-logic-recommendations)
  - [Index Management](#index-management)
  - [Queue Management](#queue-management)
  - [Wikidata Scrapping](#wikidata-scrapping)
- [Development](#development)
  - [Requirements](#requirements)
  - [Setting Up Development Environment](#setting-up-development-environment)
  - [Running Tests](#running-tests)
  - [Code Quality](#code-quality)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

Install the library using pip:

```bash
pip install personal-knowledge-library
```

### Python Version

This library requires **Python 3.10 or higher** (supports Python 3.10, 3.11, 3.12, and 3.13).

### Optional Development Dependencies

To install development dependencies for testing and code quality tools:

```bash
pip install personal-knowledge-library[dev]
```

---

## Quick Start

Here's a minimal example to get you started with the Wacom Knowledge Service:

```python
from knowledge.services.graph import WacomKnowledgeService
from knowledge.base.ontology import OntologyClassReference, ThingObject
from knowledge.base.entity import Label
from knowledge.base.language import EN_US

# Initialize the client
client = WacomKnowledgeService(
    service_url="https://private-knowledge.wacom.com",
    application_name="My Application"
)

# Login with your credentials
client.login(tenant_api_key="<your-tenant-key>", external_user_id="<your-user-id>")

# Search for entities
results, _ = client.search_labels(search_term="Leonardo da Vinci", language_code=EN_US)

for entity in results:
    print(f"{entity.uri}: {[l.content for l in entity.label]}")
```

> **Note:** You need a valid tenant API key from Wacom to use this library.

---

## Introduction

In knowledge management there is a distinction between data, information, and knowledge.
In the domain of digital ink this means:

- **Data—** The equivalent would be the ink strokes
- **Information—** After using handwriting-, shape-, math-, or other recognition processes, ink strokes are converted into machine-readable content, such as text, shapes, math representations, other digital content
- **Knowledge / Semantics** - Beyond recognition content needs to be semantically analyzed to become semantically understood based on shared common knowledge.

The following illustration shows the different layers of knowledge:
![Levels of ink knowledge layers](https://github.com/Wacom-Developer/personal-knowledge-library/blob/main/assets/knowledge-levels.png)

For handling semantics, Wacom introduced the Wacom Private Knowledge System (PKS) cloud service to manage personal ontologies and its associated personal knowledge graph.

This library provides simplified access to Wacom's personal knowledge cloud service.
It contains:

- Basic datastructures for an Ontology object and entities from the knowledge graph
- Clients for the REST APIs
- Connector for Wikidata public knowledge graph

**Ontology service:**

- List all Ontology structures
- Modify Ontology structures
- Delete Ontology structures

**Entity service:**

- List all entities
- Add entities to the knowledge graph
- Access object properties

**Search service:**

- Search for entities for labels and descriptions with a given language
- Search for literals (data properties) 
- Search for relations (object properties)

**Group service:**

- List all groups
- Add groups, modify groups, delete groups
- Add users and entities to groups

**Named Entity Linking service:**

- Linking words to knowledge entities from the graph in a given text (Ontology-based Named Entity Linking)

**Wikidata connector:**

- Import entities from Wikidata
- Mapping Wikidata entities to WPK entities

---

# Technology Stack

## Domain Knowledge

The tasks of the ontology within Wacom's private knowledge system are to formalize the domain the technology is used in, such as education-, smart home-, or creative domain.
The domain model will be the foundation for the entities collected within the knowledge graph, describing real world concepts in a formal language understood by an artificial intelligence system:

- Foundation for structured data, knowledge representation as concepts and relations among concepts
- Being explicit definitions of shared vocabularies for interoperability
- Being actionable fragments of explicit knowledge that engines can use for inferencing (Reasoning)
- Can be used for problem-solving

An ontology defines (specifies) the concepts, relationships, and other distinctions that are relevant for modeling a domain.

## Knowledge Graph

- Knowledge graph is generated from unstructured and structured knowledge sources
- Contains all structured knowledge gathered from all sources
- Foundation for all semantic algorithms

## Semantic Technology

- Extract knowledge from various sources (Connectors)
- Linking words to knowledge entities from the graph in a given text (Ontology-based Named Entity Linking)
- Enables a smart search functionality which understands the context and finds related documents (Semantic Search)


---

# Functionality

## Import Format

For importing entities into the knowledge graph, the samples/import_entities.py script can be used.

The ThingObject supports a NDJSON-based import format, where the individual JSON files can contain the following structure.

| Field name             | Subfield name | Data Structure | Description                                                                                    |
|------------------------|---------------|----------------|------------------------------------------------------------------------------------------------|
| source_reference_id    |               | str            | A unique identifier for the entity used in the source system                                  |
| source_system          |               | str            | The source system describes the original source of the entity, such as wikidata, youtube, ... |
| image                  |               | str            | A string representing the URL of the entity's icon.                                           |
| labels                 |               | array          | An array of label objects, where each object has the following fields:                       |
|                        | value         | str            | A string representing the label text in the specified locale.                                |
|                        | locale        | str            | A string combining the ISO-3166 country code and the ISO-639 language code (e.g., "en-US").  |
|                        | isMain        | bool           | A boolean flag indicating if this label is the main label for the entity (true) or an alias (false). |
| descriptions           |               | array          | An array of description objects, where each object has the following fields:                 |
|                        | description   | str            | A string representing the description text in the specified locale.                          |
|                        | locale        | str            | A string combining the ISO-3166 country code and the ISO-639 language code (e.g., "en-US").  |
| type                   |               | str            | A string representing the IRI of the ontology class for this entity.                         |
| literals               |               | array[map]     | An array of data property objects, where each object has the following fields:               |


## Access API

The personal knowledge graph backend is implemented as a multi-tenancy system.
Thus, several tenants can be logically separated from each other and different organizations can build their one knowledge graph.

![Tenant concept](https://github.com/Wacom-Developer/personal-knowledge-library/blob/main/assets/tenant-concept.png)

In general, a tenant with their users, groups, and entities are logically separated.
Physically, the entities are stored in the same instance of the Wacom Private Knowledge (WPK) backend database system.

The user management is rather limited, each organization must provide their own authentication service and user management.
The backend only has a reference of the user (*“shadow user”*) by an **external user id**.

The management of tenants is limited to the system owner —Wacom —, as it requires a **tenant management API** key.
While users for each tenant can be created by the owner of the **Tenant API Key**.
You will receive this token from the system owner after the creation of the tenant.


> :warning: Stores the **Tenant API Key** in a secure key store, as attackers can use the key to harm your system.


The **Tenant API Key** should be only used by your authentication service to create shadow users and to log in your user into the WPK backend.
After a successful user login, you will receive a token which can be used by the user to create, update, or delete entities and relations.

The following illustration summarizes the flows for creation of tenant and users:

![Tenant and user creation](https://github.com/Wacom-Developer/personal-knowledge-library/blob/main/assets/tenant-user-creation.png)

The organization itself needs to implement their own authentication service which:

- handles the users and their passwords,
- controls the personal data of the users,
- connects the users with the WPK backend and share with them the user token.

The WPK backend only manages the access levels of the entities and the group management for users.
The illustration shows how the access token is received from the WPK endpoint:

![Access token request.](https://github.com/Wacom-Developer/personal-knowledge-library/blob/main/assets/access-token.png)

## Ontology API

The ontology defines what may exist in the graph: the concept classes entities can have, and the properties that describe and connect them.
`OntologyService` reads and edits it; the graph service enforces it.

> :pushpin: `OntologyService` is **sync-only** — there is no async counterpart. Reading the ontology works for any user; every change requires the **TenantAdmin** role.

### The model

| Term | Meaning |
|---|---|
| **Context** | A named ontology owned by the tenant, with a base URI (e.g. `core` / `wacom:core#`). New types must live under that base URI. |
| **Concept** | A class an entity can instantiate, e.g. `wacom:core#Person`. Every concept is a subclass of another, rooted at `wacom:core#Thing`. |
| **Data property** ("literal") | An attribute with an XSD range, e.g. a `xsd:string` stage name. Exactly one range, and no inverse. |
| **Object property** ("relation") | A link between entities, with a class domain and range. May declare an `inverseOf` partner. |
| **Base ontology** | The Wacom-supplied concepts and properties. Read-only — changing or deleting one answers **403**. |

The tenant's own additions sit on top of the base ontology. `context_diff()` reports exactly those:

```python
diff = ontology_client.context_diff("core")
diff.added_concepts            # [AddedConcept(reference, subclass_of), ...]
diff.added_properties          # [AddedProperty(reference, kind, domains, ranges), ...]
diff.modified_base_properties  # base properties the tenant extended
diff.is_empty                  # True when the tenant matches the base ontology
```

### The edit → commit → apply cycle

An ontology change is not live when the create call returns. It goes through three stages, and skipping any of them is the most common source of confusion:

```python
# 1. Edit — accumulates into an uncommitted "pending version"
ontology_client.create_concept(context, reference=ARTIST, subclass_of=PERSON)
ontology_client.create_data_property(context, reference=STAGE_NAME,
                                     domains_cls=[ARTIST], ranges_cls=[DataPropertyType.STRING])

# 2. Commit — persists the change on the ontology side
ontology_client.commit(context)

# 3. Apply — makes the graph service honour the new version
knowledge_client.ontology_update()
while not knowledge_client.ontology_update_status().is_idle:
    time.sleep(2.0)
```

Before committing, `pending_version()` shows the change log a commit would turn into the next version:

```python
pending = ontology_client.pending_version(context)
for change in pending.changes:
    print(change.operation, change.element_kind, change.element_uri)
    # INSERT CONCEPT  wacom:core#Artist
    # INSERT LITERAL  wacom:core#stageName
```

> :warning: **The apply is asynchronous.** `ontology_update()` returns as soon as the apply is *accepted*; the work continues in the background with the tenant locked, and every graph write (entities, groups, content) is rejected with `400 The tenant … is currently being updated.` until it finishes. Poll `ontology_update_status()` until `is_idle` before writing.

`OntologyUpdateStatus` reports `is_idle`, `is_pending` and `has_failed`. A failed apply is **resumed, not redone**, with `ontology_update(fix=True)` — which is permitted even while the tenant is locked.

Two sequencing traps worth knowing:

- `NoUpdateInProgress` means *either* "finished" *or* "never started". A single idle reading can therefore pass before a just-triggered apply registers; require two consecutive idle readings.
- Applying before the commit is observable answers `409 Ontology version N is already applied.` Wait until `pending_version().is_empty` before applying.

### Inverse relations are materialized by the service

When the ontology declares an `inverseOf` partner, **one** `create_relation` produces all four views of the edge:

```python
knowledge_client.create_relation(artist_uri, IS_INSPIRED_BY, person_uri)

knowledge_client.relations(artist_uri)[IS_INSPIRED_BY].outgoing_uris  # [person_uri]
knowledge_client.relations(artist_uri)[INSPIRED].incoming_uris        # [person_uri]
knowledge_client.relations(person_uri)[IS_INSPIRED_BY].incoming_uris  # [artist_uri]
knowledge_client.relations(person_uri)[INSPIRED].outgoing_uris        # [artist_uri]
```

Creating the reciprocal explicitly is rejected with `409 The relation already exists`.

> :pushpin: `outgoing_relations` / `incoming_relations` are typed `List[Union[str, ThingObject]]` and hold whichever form the service sent — the graph service answers with full entity objects, the bulk-import format with bare URIs. Use **`outgoing_uris` / `incoming_uris`** when comparing against a URI.

### Deletion is guarded

The service refuses to remove ontology types that are still in use, so a delete can fail for reasons that live in the graph rather than the ontology:

| Operation | Refused when |
|---|---|
| `delete_concept` | entities of that type exist; the concept has subclasses; it is used in a property's domain or range |
| `delete_property` | entities or relations use it; it has sub-properties; it is referenced by vector-search settings |
| `remove_property_domains` / `remove_property_ranges` | instance data uses them; the value is base-origin; the removal would leave none |

Base-property extensions follow one rule: on a base property you may only remove what the tenant added — base-origin domains and ranges are permanent.

### Resetting a context

`reset_context()` returns the context to the base ontology. It removes **all** tenant customizations — concepts, properties, base-property extensions, NEL settings and the version history — and restarts version numbering:

```python
diff = ontology_client.context_diff(context)   # review what will be destroyed
ontology_client.reset_context(context)         # auto-commits a fresh version
knowledge_client.ontology_update()             # mandatory: finish the reset
while not knowledge_client.ontology_update_status().is_idle:
    time.sleep(2.0)
```

Two things to plan for:

- A reset is **blocked with 409** while anything still depends on the ontology — entities of the tenant's concept types, relations or values using its properties, vector-search references, a running import job, or a pending update. The message names the blocker; delete the offending data and retry.
- A successful reset leaves the tenant **locked at ontology version 0**. Until the apply completes, every graph write is refused *and the tenant cannot be deleted*.

---

# Entity API

The entities used within the knowledge graph and the relationship among them are defined within an ontology managed with Wacom Ontology Management System (WOMS).

An entity within the personal knowledge graphs consists of these major parts:

- **Icon—** a visual representation of the entity, for instance, a portrait of a person.
- **URI—** a unique resource identifier of an entity in the graph.
- **Type—** the type links to the defined concept class in the ontology.
- **Labels—** labels are the word(s) used in a language for the concept.
- **Description—** a short abstract that describes the entity.
- **Literals—** literals are properties of an entity, such as the first name of a person. The ontology defines all literals of the concept class as well as its data type.
- **Relations—** the relationship among different entities is described using relations.

The following illustration provides an example of an entity:

![Entity description](https://github.com/Wacom-Developer/personal-knowledge-library/blob/main/assets/entity-description.png)

## Entity content

Entities in general are language-independent as across nationalities or cultures we only use different scripts and words for a shared instance of a concept.

Let's take Leonardo da Vinci as an example.
The ontology defines the concept of a Person, a human being.
Now, in English its label would be _Leonardo da Vinci_, while in Japanese _レオナルド・ダ・ヴィンチ_.
Moreover, he is also known as _Leonardo di ser Piero da Vinci_ or _ダ・ビンチ_.

### Labels

Now, in the given example all words that are assigned to the concept are labels.
The label _Leonardo da Vinci_ is stored in the backend with an additional language code, e.g. _en_.

There is always a main label, which refers to the most common or official name of an entity.
Another example would be Wacom, where _Wacom Co., Ltd._ is the official name while _Wacom_ is commonly used and be considered as an alias.

>  :pushpin: For the language code the **ISO 639-1:2002**, codes for the representation language names —Part 1: Alpha-2 code. Read more, [here](https://www.iso.org/standard/22109.html)

---

## Choosing Between Sync and Async Clients

Every user-facing service client ships in two flavours: the synchronous client in `knowledge.services.*` and the async counterpart in `knowledge.services.asyncio.*`.
Both expose the same methods with the same parameters and return types — switching only changes the call style.

### When to use the sync client

- **Scripts, CLIs, one-off tools, and notebooks.** No event loop required, easier to reason about, and `pdb` works as expected. All samples in this repository use the sync client.
- **Single-shot calls embedded in otherwise synchronous code.** Mixing `asyncio.run(...)` into a sync codebase just to make one request is rarely worth it.
- **Callers that want transparent recovery from transient failures.** Sync clients install a `urllib3.Retry(total=3, backoff_factor=0.1, status_forcelist=[502, 503, 504])` at the transport layer, so 5xx blips are retried for you.

### When to use the async client

- **Backend services that hold many concurrent connections** — FastAPI, aiohttp, Starlette, etc. Mixing blocking I/O into an async event loop blocks every other request; use the async client to keep the loop free.
- **High-throughput batch jobs** that benefit from issuing many requests in parallel via `asyncio.gather(...)`.
- **Callers that already own a retry / circuit-breaker / idempotency layer.** The async clients deliberately ship **no transport-level retry** — backend callers typically have their own policies (back-pressure, circuit breakers, idempotency keys), and a hidden retry layer would interfere with them.

> :pushpin: The retry asymmetry between the sync and async clients is intentional. If your async caller does not already implement retries, wrap the failing call yourself rather than asking for retries inside the SDK.

### Mixed availability

Most service clients exist in both forms, with one exception:

| Client                       | Sync | Async |
|------------------------------|:----:|:-----:|
| `WacomKnowledgeService`      |  ✅  |   ✅  |
| `OntologyService`            |  ✅  |   ❌  |
| `UserManagementServiceAPI`   |  ✅  |   ✅  |
| `GroupManagementService`     |  ✅  |   ✅  |
| `SemanticSearchClient`       |  ✅  |   ✅  |
| `IndexManagementClient`      |  ✅  |   ✅  |
| `QueueManagementClient`      |  ✅  |   ✅  |
| `InkServices`                |  ✅  |   ✅  |
| `ContentClient`              |  ✅  |   ✅  |
| `WacomEntityLinkingEngine`   |  ✅  |   ✅  |

Ontology management is sync-only; everything else is available as both `Foo` and `AsyncFoo`.
The infrastructure modules `session.py`, `tenant.py`, and `helper.py` are also sync-only by design — they are not service clients.

### Reusing a token across clients

Each client owns its own `TokenManager`; there is no global session registry, and `use_session(session_id)` only resolves IDs that live in **that** client's manager.
A session created by `knowledge_client.login(...)` is therefore **not** visible to `content_client` — calling `content_client.use_session(session.id)` raises `WacomServiceException("Unknown session id:= …")`.

To avoid a second login round-trip when multiple clients work against the same user, use one of these two patterns instead.

**Pattern 1 — per-call `auth_key=` override.** Most service methods accept an optional `auth_key=` parameter that bypasses the bound session for a single call:

```python
session = knowledge_client.login(tenant_api_key, external_user_id)
# Use the same token in another client without registering a session there
items = content_client.list_content(uri=entity_uri, auth_key=session.auth_token)
```

**Pattern 2 — `register_token()` on the second client.** Reuse the auth token (and refresh token, if any) obtained from the first login to register a `RefreshableSession` in the second client's token manager. No second network call to `/user/login` is made:

```python
session = knowledge_client.login(tenant_api_key, external_user_id)
content_client.register_token(
    auth_key=session.auth_token,
    refresh_token=session.refresh_token,
)
# content_client now uses that session for subsequent calls
content_client.list_content(uri=entity_uri)
```

> :pushpin: `register_token` produces a `RefreshableSession`, not a `PermanentSession`. The two clients refresh independently after this point — refreshing on one does not propagate the new token to the other. If long-lived auto re-login (the `PermanentSession` behavior) is required on the second client too, call `client.login(tenant_api_key, external_user_id)` on it directly.

### Closing async clients

Async clients hold an `aiohttp.ClientSession`. Always close it before the program exits:

```python
async_client: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(...)
await async_client.login(tenant_api_key, external_user_id)
try:
    ...
finally:
    await async_client.close_all_sessions()
```

---

## Samples

### Entity handling

This samples shows how to work with the graph service.

```python
import argparse
from typing import Optional, Dict, List

from knowledge.base.entity import Description, Label
from knowledge.base.language import LocaleCode, EN_US, DE_DE
from knowledge.base.ontology import OntologyClassReference, OntologyPropertyReference, ThingObject, ObjectProperty
from knowledge.services.graph import WacomKnowledgeService

# ------------------------------- Knowledge entities -------------------------------------------------------------------
LEONARDO_DA_VINCI: str = 'Leonardo da Vinci'
SELF_PORTRAIT_STYLE: str = 'self-portrait'
ICON: str = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Mona_Lisa_%28copy%2C_Thalwil%2C_Switzerland%29."\
            "JPG/1024px-Mona_Lisa_%28copy%2C_Thalwil%2C_Switzerland%29.JPG"
# ------------------------------- Ontology class names -----------------------------------------------------------------
THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')
"""
The Ontology will contain a Thing class where is the root class in the hierarchy. 
"""
ARTWORK_CLASS: OntologyClassReference = OntologyClassReference('wacom', 'creative', 'VisualArtwork')
PERSON_CLASS: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Person')
ART_STYLE_CLASS: OntologyClassReference = OntologyClassReference.parse('wacom:creative#ArtStyle')
IS_CREATOR: OntologyPropertyReference = OntologyPropertyReference('wacom', 'core', 'created')
HAS_TOPIC: OntologyPropertyReference = OntologyPropertyReference.parse('wacom:core#hasTopic')
CREATED: OntologyPropertyReference = OntologyPropertyReference.parse('wacom:core#created')
HAS_ART_STYLE: OntologyPropertyReference = OntologyPropertyReference.parse('wacom:creative#hasArtstyle')


def print_entity(display_entity: ThingObject, list_idx: int, client: WacomKnowledgeService,
                 short: bool = False):
    """
    Printing entity details.

    Parameters
    ----------
    display_entity: ThingObject
        Entity with properties
    list_idx: int
        Index with a list
    client: WacomKnowledgeService
        Knowledge graph client
    short: bool
        Short summary
    """
    print(f'[{list_idx}] : {display_entity.uri} <{display_entity.concept_type.iri}>')
    if len(display_entity.label) > 0:
        print('    | [Labels]')
        for la in display_entity.label:
            print(f'    |     |- "{la.content}"@{la.language_code}')
        print('    |')
    if not short:
        if len(display_entity.alias) > 0:
            print('    | [Alias]')
            for la in display_entity.alias:
                print(f'    |     |- "{la.content}"@{la.language_code}')
            print('    |')
        if len(display_entity.data_properties) > 0:
            print('    | [Attributes]')
            for data_property, labels in display_entity.data_properties.items():
                print(f'    |    |- {data_property.iri}:')
                for li in labels:
                    print(f'    |    |-- "{li.value}"@{li.language_code}')
            print('    |')

        relations_obj: Dict[OntologyPropertyReference, ObjectProperty] = client.relations(uri=display_entity.uri)
        if len(relations_obj) > 0:
            print('    | [Relations]')
            for r_idx, re in enumerate(relations_obj.values()):
                last: bool = r_idx == len(relations_obj) - 1
                print(f'    |--- {re.relation.iri}: ')
                print(f'    {"|" if not last else " "}       |- [Incoming]: {re.incoming_relations} ')
                print(f'    {"|" if not last else " "}       |- [Outgoing]: {re.outgoing_relations}')
        print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default='https://private-knowledge.wacom.com',
                        help="URL of instance")
    args = parser.parse_args()
    TENANT_KEY: str = args.tenant
    EXTERNAL_USER_ID: str = args.user
    # Wacom personal knowledge REST API Client
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(service_url=args.instance, application_name="Wacom Knowledge Listing")
    knowledge_client.login(args.tenant, args.user)
    page_id: Optional[str] = None
    page_number: int = 1
    entity_count: int = 0
    print('-----------------------------------------------------------------------------------------------------------')
    print(' First step: Find Leonardo da Vinci in the knowledge graph.')
    print('-----------------------------------------------------------------------------------------------------------')
    res_entities, next_search_page = knowledge_client.search_labels(search_term=LEONARDO_DA_VINCI,
                                                                    language_code=LocaleCode('en_US'), limit=1000)
    leo: Optional[ThingObject] = None
    s_idx: int = 1
    for res_entity in res_entities:
        #  Entity must be a person and the label matches with full string
        if res_entity.concept_type == PERSON_CLASS and LEONARDO_DA_VINCI in [la.content for la in res_entity.label]:
            leo = res_entity
            break

    print('-----------------------------------------------------------------------------------------------------------')
    print(' What artwork exists in the knowledge graph.')
    print('-----------------------------------------------------------------------------------------------------------')
    relations_dict: Dict[OntologyPropertyReference, ObjectProperty] = knowledge_client.relations(uri=leo.uri)
    print(f' Artwork of {leo.label}')
    print('-----------------------------------------------------------------------------------------------------------')
    idx: int = 1
    if CREATED in relations_dict:
        for e in relations_dict[CREATED].outgoing_relations:
            print(f' [{idx}] {e.uri}: {e.label}')
            idx += 1
    print('-----------------------------------------------------------------------------------------------------------')
    print(' Let us create a new piece of artwork.')
    print('-----------------------------------------------------------------------------------------------------------')

    # Main labels for entity
    artwork_labels: List[Label] = [
        Label('Ginevra Gherardini', EN_US),
        Label('Ginevra Gherardini', DE_DE)
    ]
    # Alias labels for entity
    artwork_alias: List[Label] = [
        Label("Ginevra", EN_US),
        Label("Ginevra", DE_DE)
    ]
    # Topic description
    artwork_description: List[Description] = [
        Description('Oil painting of Mona Lisa\' sister', EN_US),
        Description('Ölgemälde von Mona Lisa\' Schwester', DE_DE)
    ]
    # Topic
    artwork_object: ThingObject = ThingObject(label=artwork_labels, concept_type=ARTWORK_CLASS,
                                              description=artwork_description,
                                              icon=ICON)
    artwork_object.alias = artwork_alias
    print(f' Create: {artwork_object}')
    # Create artwork
    artwork_entity_uri: str = knowledge_client.create_entity(artwork_object)
    print(f' Entity URI: {artwork_entity_uri}')
    # Create relation between Leonardo da Vinci and artwork
    knowledge_client.create_relation(source=leo.uri, relation=IS_CREATOR, target=artwork_entity_uri)

    relations_dict = knowledge_client.relations(uri=artwork_entity_uri)
    for ontology_property, object_property in relations_dict.items():
        print(f'  {object_property}')
    # You will see that wacom:core#isCreatedBy is automatically inferred as a relation as it is the inverse property of
    # wacom:core#created.

    # Now, more search options
    res_entities, next_search_page = knowledge_client.search_description('Michelangelo\'s Sistine Chapel',
                                                                         EN_US, limit=1000)
    print('-----------------------------------------------------------------------------------------------------------')
    print(' Search results.  Description: "Michelangelo\'s Sistine Chapel"')
    print('-----------------------------------------------------------------------------------------------------------')
    s_idx: int = 1
    for e in res_entities:
        print_entity(e, s_idx, knowledge_client)

    # Now, let's search all artwork that has the art style self-portrait
    res_entities, next_search_page = knowledge_client.search_labels(search_term=SELF_PORTRAIT_STYLE,
                                                                    language_code=EN_US, limit=1000)
    art_style: Optional[ThingObject] = None
    s_idx: int = 1
    for entity in res_entities:
        #  Entity must be a person and the label matches with full string
        if entity.concept_type == ART_STYLE_CLASS and SELF_PORTRAIT_STYLE in [la.content for la in entity.label]:
            art_style = entity
            break
    res_entities, next_search_page = knowledge_client.search_relation(subject_uri=None,
                                                                      relation=HAS_ART_STYLE,
                                                                      object_uri=art_style.uri,
                                                                      language_code=EN_US)
    print('-----------------------------------------------------------------------------------------------------------')
    print(' Search results.  Relation: relation:=has_topic  object_uri:= unknown')
    print('-----------------------------------------------------------------------------------------------------------')
    s_idx: int = 1
    for e in res_entities:
        print_entity(e, s_idx, knowledge_client, short=True)
        s_idx += 1

    # Finally, the activation function retrieving the related identities to a pre-defined depth.
    entities, relations = knowledge_client.activations(uris=[leo.uri], depth=1)
    print('-----------------------------------------------------------------------------------------------------------')
    print(f'Activation.  URI: {leo.uri}')
    print('-----------------------------------------------------------------------------------------------------------')
    s_idx: int = 1
    for e in res_entities:
        print_entity(e, s_idx, knowledge_client)
        s_idx += 1
    # All relations
    print('-----------------------------------------------------------------------------------------------------------')
    for r in relations:
        print(f'Subject: {r[0]} Predicate: {r[1]} Object: {r[2]}')
    print('-----------------------------------------------------------------------------------------------------------')
    page_id = None

    # Listing all entities that have the type
    idx: int = 1
    while True:
        # pull
        entities, total_number, next_page_id = knowledge_client.listing(ART_STYLE_CLASS, page_id=page_id, limit=100)
        pulled_entities: int = len(entities)
        entity_count += pulled_entities
        print('-------------------------------------------------------------------------------------------------------')
        print(f' Page: {page_number} Number of entities: {len(entities)}  ({entity_count}/{total_number}) '
              f'Next page id: {next_page_id}')
        print('-------------------------------------------------------------------------------------------------------')
        for e in entities:
            print_entity(e, idx, knowledge_client)
            idx += 1
        if pulled_entities == 0:
            break
        page_number += 1
        page_id = next_page_id
    print()
    # Delete all personal entities for this user
    while True:
        # pull
        entities, total_number, next_page_id = knowledge_client.listing(THING_OBJECT, page_id=page_id,
                                                                        limit=100)
        pulled_entities: int = len(entities)
        if pulled_entities == 0:
            break
        delete_uris: List[str] = [e.uri for e in entities]
        print(f'Cleanup. Delete entities: {delete_uris}')
        knowledge_client.delete_entities(uris=delete_uris, force=True)
        page_number += 1
        page_id = next_page_id
    print('-----------------------------------------------------------------------------------------------------------')
```

### Named Entity Linking 

Performing Named Entity Linking (NEL) on text and Universal Ink Model.

```python
import argparse
from typing import List, Dict

import urllib3

from knowledge.base.language import EN_US
from knowledge.base.ontology import OntologyPropertyReference, ThingObject, ObjectProperty
from knowledge.nel.base import KnowledgeGraphEntity
from knowledge.nel.engine import WacomEntityLinkingEngine
from knowledge.services.graph import WacomKnowledgeService

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


TEXT: str = "Leonardo da Vinci painted the Mona Lisa."


def print_entity(entity: KnowledgeGraphEntity, list_idx: int, auth_key: str, client: WacomKnowledgeService):
    """
    Printing entity details.

    Parameters
    ----------
    entity: KnowledgeGraphEntity
        Named entity
    list_idx: int
        Index with a list
    auth_key: str
        Authorization key
    client: WacomKnowledgeService
        Knowledge graph client
    """
    thing: ThingObject = knowledge_client.entity(auth_key=user_token, uri=entity.entity_source.uri)
    print(f'[{list_idx}] - {entity.ref_text} [{entity.start_idx}-{entity.end_idx}] : {thing.uri}'
          f' <{thing.concept_type.iri}>')
    if len(thing.label) > 0:
        print('    | [Labels]')
        for la in thing.label:
            print(f'    |     |- "{la.content}"@{la.language_code}')
        print('    |')
    if len(thing.label) > 0:
        print('    | [Alias]')
        for la in thing.alias:
            print(f'    |     |- "{la.content}"@{la.language_code}')
        print('    |')
    relations: Dict[OntologyPropertyReference, ObjectProperty] = client.relations(auth_key=auth_key, uri=thing.uri)
    if len(thing.data_properties) > 0:
        print('    | [Attributes]')
        for data_property, labels in thing.data_properties.items():
            print(f'    |    |- {data_property.iri}:')
            for li in labels:
                print(f'    |    |-- "{li.value}"@{li.language_code}')
        print('    |')
    if len(relations) > 0:
        print('    | [Relations]')
        for re in relations.values():
            print(f'    |--- {re.relation.iri}: ')
            print(f'           |- [Incoming]: {re.incoming_relations} ')
            print(f'           |- [Outgoing]: {re.outgoing_relations}')
    print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()
    TENANT_KEY: str = args.tenant
    EXTERNAL_USER_ID: str = args.user
    # Wacom personal knowledge REST API Client
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Named Entity Linking Knowledge access",
        service_url=args.instance)
    #  Wacom Named Entity Linking
    nel_client: WacomEntityLinkingEngine = WacomEntityLinkingEngine(
        service_url=args.instance,
        service_endpoint=WacomEntityLinkingEngine.SERVICE_ENDPOINT
    )
    # Use special tenant for testing: Unit-test tenant
    user_token, refresh_token, expiration_time = nel_client.request_user_token(TENANT_KEY, EXTERNAL_USER_ID)
    entities: List[KnowledgeGraphEntity] = nel_client.\
        link_personal_entities(text=TEXT, language_code=EN_US, auth_key=user_token)
    idx: int = 1
    print('-----------------------------------------------------------------------------------------------------------')
    print(f'Text: "{TEXT}"@{EN_US}')
    print('-----------------------------------------------------------------------------------------------------------')
    for e in entities:
        print_entity(e, idx, user_token, knowledge_client)
        idx += 1

```

### Access Management

The sample shows how access to entities can be shared with a group of users or the tenant.

```python
import argparse
from typing import List

from knowledge.base.entity import Label, Description
from knowledge.base.language import EN_US, DE_DE, JA_JP
from knowledge.base.ontology import OntologyClassReference, ThingObject
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.group import GroupManagementService, Group
from knowledge.services.users import UserManagementServiceAPI

# ------------------------------- User credential ----------------------------------------------------------------------
TOPIC_CLASS: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Topic')


def create_entity() -> ThingObject:
    """Create a new entity.

    Returns
    -------
    entity: ThingObject
        Entity object
    """
    # Main labels for entity
    topic_labels: List[Label] = [
        Label('Hidden', EN_US),
        Label('Versteckt', DE_DE),
        Label('隠れた', JA_JP),
    ]

    # Topic description
    topic_description: List[Description] = [
        Description('Hidden entity to explain access management.', EN_US),
        Description('Verstecke Entität, um die Zugriffsteuerung zu erklären.', DE_DE)
    ]
    # Topic
    topic_object: ThingObject = ThingObject(label=topic_labels, concept_type=TOPIC_CLASS, description=topic_description)
    return topic_object


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default='https://private-knowledge.wacom.com',
                        help="URL of instance")
    args = parser.parse_args()
    TENANT_KEY: str = args.tenant
    EXTERNAL_USER_ID: str = args.user
    # Wacom personal knowledge REST API Client
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(application_name="Wacom Knowledge Listing",
                                                                    service_url=args.instance)
    # User Management
    user_management: UserManagementServiceAPI = UserManagementServiceAPI(service_url=args.instance)
    # Group Management
    group_management: GroupManagementService = GroupManagementService(service_url=args.instance)
    admin_token, refresh_token, expiration_time = user_management.request_user_token(TENANT_KEY, EXTERNAL_USER_ID)
    # Now, we create a user
    u1, u1_token, _, _ = user_management.create_user(TENANT_KEY, "u1")
    u2, u2_token, _, _ = user_management.create_user(TENANT_KEY, "u2")
    u3, u3_token, _, _ = user_management.create_user(TENANT_KEY, "u3")

    # Now, let's create an entity
    thing: ThingObject = create_entity()
    entity_uri: str = knowledge_client.create_entity(thing, auth_key=u1_token)
    # Only user 1 can access the entity from cloud storage
    my_thing: ThingObject = knowledge_client.entity(entity_uri, auth_key=u1_token)
    print(f'User is the owner of {my_thing.owner}')
    # Now only user 1 has access to the personal entity
    knowledge_client.entity(entity_uri, auth_key=u1_token)
    # Try to access the entity
    try:
        knowledge_client.entity(entity_uri, auth_key=u2_token)
    except WacomServiceException as we:
        print(f"Expected exception as user 2 has no access to the personal entity of user 1. Exception: {we}")
        print(f"Status code: {we.status_code}")
        print(f"Response text: {we.service_response}")
    # Try to access the entity
    try:
        knowledge_client.entity(entity_uri, auth_key=u3_token)
    except WacomServiceException as we:
        print(f"Expected exception as user 3 has no access to the personal entity of user 1. Exception: {we}")
    # Now, user 1 creates a group
    g: Group = group_management.create_group("test-group", auth_key=u1_token)
    # Shares the join key with user 2 and user 2 joins
    group_management.join_group(g.id, g.join_key, auth_key=u2_token)
    # Share entity with a group
    group_management.add_entity_to_group(g.id, entity_uri, auth_key=u1_token)
    # Now, user 2 should have access
    other_thing: ThingObject = knowledge_client.entity(entity_uri, auth_key=u2_token)
    print(f'User 2 is the owner of the thing: {other_thing.owner}')
    # Try to access the entity
    try:
        knowledge_client.entity(entity_uri, auth_key=u3_token)
    except WacomServiceException as we:
        print(f"Expected exception as user 3 still has no access to the personal entity of user 1. Exception: {we}")
        print(f"URL: {we.url}, method: {we.method}")
        print(f"Status code: {we.status_code}")
        print(f"Response text: {we.service_response}")
        print(f"Message: {we.message}")
    # Un-share the entity
    group_management.remove_entity_to_group(g.id, entity_uri, auth_key=u1_token)
    # Now, again no access
    try:
        knowledge_client.entity(entity_uri, auth_key=u2_token)
    except WacomServiceException as we:
        print(f"Expected exception as user 2 has no access to the personal entity of user 1. Exception: {we}")
        print(f"URL: {we.url}, method: {we.method}")
        print(f"Status code: {we.status_code}")
        print(f"Response text: {we.service_response}")
        print(f"Message: {we.message}")
    group_management.leave_group(group_id=g.id, auth_key=u2_token)
    # Now, share the entity with the whole tenant
    my_thing.tenant_access_right.read = True
    knowledge_client.update_entity(my_thing, auth_key=u1_token)
    # Now, all users can access the entity
    knowledge_client.entity(entity_uri, auth_key=u2_token)
    knowledge_client.entity(entity_uri, auth_key=u3_token)
    # Finally, clean up
    knowledge_client.delete_entity(entity_uri, force=True, auth_key=u1_token)
    # Remove users
    user_management.delete_user(TENANT_KEY, u1.external_user_id, u1.id, force=True)
    user_management.delete_user(TENANT_KEY, u2.external_user_id, u2.id, force=True)
    user_management.delete_user(TENANT_KEY, u3.external_user_id, u3.id, force=True)

```

### Ontology Creation

The sample walks the full edit-commit-apply cycle of the ontology service and then uses the new types in the graph. See [Ontology API](#ontology-api) for the concepts behind it.

```python
# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language_code governing permissions and
#  limitations under the License.
"""
Extending the ontology and using the new types
==============================================

Walks the full edit-commit-apply cycle of the ontology service and then uses the new
types in the knowledge graph:

1. Read the tenant's ontology context.
2. Create a concept class, a data property, and a pair of mutually inverse object
   properties.
3. Review the uncommitted changes (`pending_version`) and what the tenant has added on
   top of the base ontology (`context_diff`).
4. Commit the ontology, apply it to the graph, and wait for the apply to finish.
5. Create an entity of the new class and relate it through the new object property.

Requires a shadow user with the **TenantAdmin** role; ordinary users may read the
ontology but not change it.

Usage
-----
>>> python ontology_creation.py -t <tenant-api-key> -u <external-user-id>
"""

import argparse
import sys
import time
from typing import List, Optional

from knowledge.base.entity import Label, Description
from knowledge.base.language import EN_US, DE_DE
from knowledge.base.ontology import (
    DataProperty,
    DataPropertyType,
    ObjectProperty,
    OntologyClassReference,
    OntologyContext,
    OntologyDiff,
    OntologyPropertyReference,
    OntologyUpdateStatus,
    PendingOntologyVersion,
    ThingObject,
)
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.services.session import PermanentSession

# ------------------------------- Constants ----------------------------------------------------------------------------
LEONARDO_DA_VINCI: str = "Leonardo da Vinci"
CONTEXT_NAME: str = "core"
ADMIN_ROLE: str = "TenantAdmin"

# Wacom base ontology type. Base concepts and properties are read-only: the service answers
# 403 to any attempt to change or delete them.
PERSON_TYPE: OntologyClassReference = OntologyClassReference.parse("wacom:core#Person")

# Local names of the types this sample adds. They are resolved against the base URI of the
# tenant's own context, because a concept has to live inside it.
ARTIST_NAME: str = "Artist"
STAGE_NAME_NAME: str = "stageName"
IS_INSPIRED_BY_NAME: str = "isInspiredBy"
INSPIRED_NAME: str = "inspired"

REQUIRED_IDLE_POLLS: int = 2
"""Consecutive idle readings needed before an apply counts as finished."""


def create_artist(artist_type: OntologyClassReference, stage_name: OntologyPropertyReference) -> ThingObject:
    """
    Create a new artist entity.

    Parameters
    ----------
    artist_type: OntologyClassReference
        Concept class of the entity.
    stage_name: OntologyPropertyReference
        Data property holding the stage name.

    Returns
    -------
    instance: ThingObject
        Artist entity
    """
    # Main labels for entity
    topic_labels: List[Label] = [
        Label("Gian Giacomo Caprotti", EN_US),
    ]

    # Topic description
    topic_description: List[Description] = [
        Description("Hidden entity to explain access management.", EN_US),
        Description("Verstecke Entität, um die Zugriffsteuerung zu erlären.", DE_DE),
    ]

    data_property: DataProperty = DataProperty(content="Salaj", property_ref=stage_name, language_code=EN_US)
    # Topic
    artist: ThingObject = ThingObject(label=topic_labels, concept_type=artist_type, description=topic_description)
    artist.add_data_property(data_property)
    return artist


def wait_until_applied(client: WacomKnowledgeService, attempts: int = 30, delay: float = 2.0) -> None:
    """Wait until the tenant's ontology update has finished.

    `ontology_update` only **accepts** the apply; the work continues in the background
    while the tenant is locked, and every graph write is rejected until it completes.

    **Remark:**
    The service reports 'NoUpdateInProgress' both when an apply has completed and when
    none was ever started. A single idle reading would therefore return before a
    just-triggered apply registers, so two consecutive idle readings are required.

    Parameters
    ----------
    client: WacomKnowledgeService
        Graph client bound to the tenant admin.
    attempts: int (default:= 30)
        Number of status polls before giving up.
    delay: float (default:= 2.0)
        Delay between two polls, in seconds.

    Raises
    ------
    RuntimeError
        If the update failed, or did not finish within the allotted attempts.
    """
    idle_streak: int = 0
    for _ in range(attempts):
        status: OntologyUpdateStatus = client.ontology_update_status()
        if status.has_failed:
            raise RuntimeError("The ontology update failed. Resume it with ontology_update(fix=True).")
        idle_streak = idle_streak + 1 if status.is_idle else 0
        if idle_streak >= REQUIRED_IDLE_POLLS:
            return
        time.sleep(delay)
    raise RuntimeError(f"The ontology update did not finish within {attempts * delay:.0f}s.")


def wait_until_committed(client: OntologyService, context: str, attempts: int = 15, delay: float = 2.0) -> None:
    """Wait until a commit is observable, i.e. the context has no pending changes left.

    The apply refuses a version it has already applied, so triggering it before the commit
    is visible reports 'already applied' instead of doing the work.

    Parameters
    ----------
    client: OntologyService
        Ontology client bound to the tenant admin.
    context: str
        Name of the context.
    attempts: int (default:= 15)
        Number of polls before giving up.
    delay: float (default:= 2.0)
        Delay between two polls, in seconds.

    Raises
    ------
    RuntimeError
        If pending changes remain after the allotted attempts.
    """
    for _ in range(attempts):
        pending: PendingOntologyVersion = client.pending_version(context)
        if pending.is_empty:
            return
        time.sleep(delay)
    raise RuntimeError(f"Pending changes remained {attempts * delay:.0f}s after the commit.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument(
        "-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()
    TENANT_KEY: str = args.tenant
    EXTERNAL_USER_ID: str = args.user
    # Wacom Ontology REST API Client
    ontology_client: OntologyService = OntologyService(service_url=args.instance)
    knowledge_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Ontology Creation Demo", service_url=args.instance
    )
    # Login as admin user
    session: PermanentSession = ontology_client.login(TENANT_KEY, EXTERNAL_USER_ID)
    if ADMIN_ROLE not in session.roles:
        print(f"User {EXTERNAL_USER_ID} is not an admin user.")
        sys.exit(1)
    # Each client keeps its own session table, so use_session cannot resolve a session id
    # minted by another client. Hand the token over instead.
    knowledge_client.register_token(auth_key=session.auth_token, refresh_token=session.refresh_token)

    # ------------------------------- Context ------------------------------------------------------------------------
    context: Optional[OntologyContext] = ontology_client.context()
    if context is None:
        # The tenant has no ontology context yet; create one.
        ontology_client.create_context(name=CONTEXT_NAME, base_uri=f"wacom:{CONTEXT_NAME}")
        context = ontology_client.context()
    context_name: str = context.context
    print(f"Context: {context_name} (base URI {context.base_uri}, version {context.version})")

    # New types must live under the base URI of the context that owns them.
    ARTIST_TYPE: OntologyClassReference = OntologyClassReference.parse(f"{context.base_uri}{ARTIST_NAME}")
    STAGE_NAME: OntologyPropertyReference = OntologyPropertyReference.parse(f"{context.base_uri}{STAGE_NAME_NAME}")
    IS_INSPIRED_BY: OntologyPropertyReference = OntologyPropertyReference.parse(
        f"{context.base_uri}{IS_INSPIRED_BY_NAME}"
    )
    INSPIRED: OntologyPropertyReference = OntologyPropertyReference.parse(f"{context.base_uri}{INSPIRED_NAME}")

    # ------------------------------- Ontology changes ---------------------------------------------------------------
    # Creating a class which is a subclass of a person
    ontology_client.create_concept(context_name, reference=ARTIST_TYPE, subclass_of=PERSON_TYPE)

    # Data property. A literal property takes exactly one XSD data type as its range and
    # must not declare an inverse.
    ontology_client.create_data_property(
        context=context_name,
        reference=STAGE_NAME,
        domains_cls=[ARTIST_TYPE],
        ranges_cls=[DataPropertyType.STRING],
        subproperty_of=None,
    )
    # Object properties. Declaring the second one as the inverse of the first makes the
    # service maintain the pair: it also records isInspiredBy as the inverse of inspired.
    ontology_client.create_object_property(
        context=context_name,
        reference=IS_INSPIRED_BY,
        domains_cls=[ARTIST_TYPE],
        ranges_cls=[PERSON_TYPE],
        inverse_of=None,
        subproperty_of=None,
    )
    ontology_client.create_object_property(
        context=context_name,
        reference=INSPIRED,
        domains_cls=[PERSON_TYPE],
        ranges_cls=[ARTIST_TYPE],
        inverse_of=IS_INSPIRED_BY,
        subproperty_of=None,
    )

    # ------------------------------- Review before committing -------------------------------------------------------
    # The pending version is the change log a commit would turn into the next version.
    pending_version: PendingOntologyVersion = ontology_client.pending_version(context_name)
    print(f"Pending version {pending_version.version} with {len(pending_version.changes)} change(s):")
    for change in pending_version.changes:
        print(f"  {change.operation} {change.element_kind} -> {change.element_uri}")

    # ------------------------------- Commit and apply ---------------------------------------------------------------
    # Committing persists the schema change on the ontology side only.
    ontology_client.commit(context=context_name)
    wait_until_committed(ontology_client, context_name)
    # Applying it makes the graph service respect the new version. The call returns as soon
    # as the apply is accepted, so wait for it before writing entities.
    knowledge_client.ontology_update()
    wait_until_applied(knowledge_client)

    # The diff reports everything the tenant added on top of the base ontology - which is
    # also everything a reset_context would destroy.
    diff: OntologyDiff = ontology_client.context_diff(context_name)
    print(f"Tenant added {len(diff.added_concepts)} concept(s) and {len(diff.added_properties)} property(ies).")

    # ------------------------------- Using the new types ------------------------------------------------------------
    res_entities, next_search_page = knowledge_client.search_labels(
        search_term=LEONARDO_DA_VINCI, language_code=EN_US, limit=1000
    )
    leo: Optional[ThingObject] = None
    for entity in res_entities:
        #  Entities must be a person and the label matches with full string
        if entity.concept_type == PERSON_TYPE and LEONARDO_DA_VINCI in [la.content for la in entity.label]:
            leo = entity
            break
    if leo is None:
        print(f"No person labelled '{LEONARDO_DA_VINCI}' found; nothing to relate the artist to.")
        sys.exit(1)

    artist_student: ThingObject = create_artist(ARTIST_TYPE, STAGE_NAME)
    artist_student_uri: str = knowledge_client.create_entity(artist_student)
    # One call is enough: because isInspiredBy and inspired are declared inverse, the
    # service also records the reciprocal edge. Creating it explicitly would be rejected
    # with '409 The relation already exists'.
    knowledge_client.create_relation(artist_student_uri, IS_INSPIRED_BY, leo.uri)

    # Relations come back as entity objects rather than bare URIs, so compare on the URIs.
    relations = knowledge_client.relations(leo.uri)
    inspired_relation: Optional[ObjectProperty] = relations.get(INSPIRED)
    if inspired_relation is not None and artist_student_uri in inspired_relation.outgoing_uris:
        print(f"The service materialized the inverse: {leo.uri} --{INSPIRED.iri}--> {artist_student_uri}")
```

### Asynchronous Client 

The sample shows how to use the asynchronous client. 
Most of the methods are available in the asynchronous client(s).
Only for the ontology management the asynchronous client is not available.

```python
import argparse
import asyncio
import uuid
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

from knowledge.base.entity import Label
from knowledge.base.language import LanguageCode, EN, SUPPORTED_LOCALES, EN_US
from knowledge.base.ontology import ThingObject
from knowledge.ontomapping import load_configuration
from knowledge.ontomapping.manager import wikidata_to_thing
from knowledge.public.relations import wikidata_relations_extractor
from knowledge.public.wikidata import WikidataSearchResult, WikidataThing
from knowledge.public.client import WikiDataAPIClient
from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
from knowledge.services.asyncio.group import AsyncGroupManagementService
from knowledge.services.asyncio.users import AsyncUserManagementService
from knowledge.services.base import WacomServiceException, format_exception
from knowledge.services.group import Group
from knowledge.services.session import PermanentSession, RefreshableSession
from knowledge.services.users import UserRole, User


def import_entity_from_wikidata(search_term: str, locale: LanguageCode) -> Dict[str, ThingObject]:
    """
    Import entity from Wikidata.
    Parameters
    ----------
    search_term: str
        Search term
    locale: LanguageCode
        Language code

    Returns
    -------
    things: Dict[str, ThingObject]
        Mapping qid to a thing object
    """
    search_results: List[WikidataSearchResult] = WikiDataAPIClient.search_term(search_term, locale)
    # Load mapping configuration
    load_configuration(Path(__file__).parent.parent / 'pkl-cache' / 'ontology_mapping.json')
    # Search wikidata for entities
    qid_entities: List[WikidataThing] = WikiDataAPIClient.retrieve_entities([sr.qid for sr in search_results])
    qid_things: Dict[str, WikidataThing] = {qt.qid: qt for qt in qid_entities}
    relations: Dict[str, List[Dict[str, Any]]] = wikidata_relations_extractor(qid_things)
    # Now, let's create the things
    things: Dict[str, ThingObject] = {}
    for res in qid_entities:
        wikidata_thing, import_warnings = wikidata_to_thing(res, all_relations=relations,
                                                            supported_locales=SUPPORTED_LOCALES,
                                                            pull_wikipedia=True,
                                                            all_wikidata_objects=qid_things)
        things[res.qid] = wikidata_thing
    return things


async def user_management_sample(tenant_api_key: str, instance: str) -> Tuple[User, str, str]:
    """
    User management sample.
    Parameters
    ----------
    tenant_api_key: str
        Session
    instance: str
        Instance URL

    Returns
    -------
    user: User
        User object
    user_token: str
        User token
    refresh_token: str
        Refresh token
    """
    user_management: AsyncUserManagementService = AsyncUserManagementService(
                                                    application_name="Async user management sample",
                                                    service_url=instance)
    meta_data: dict = {'user-type': 'demo'}
    user, user_token, refresh_token, _ = await user_management.create_user(tenant_key=tenant_api_key,
                                                                           external_id=uuid.uuid4().hex,
                                                                           meta_data=meta_data,
                                                                           roles=[UserRole.USER])
    return user, user_token, refresh_token


async def clean_up(instance: str, tenant_api_key: str):
    """
    Cleanup sample.
    Parameters
    ----------
    instance: str
        Instance URL
    tenant_api_key: str
        Tenant API key
    """
    user_management: AsyncUserManagementService = AsyncUserManagementService(
                                                    application_name="Async user management sample",
                                                    service_url=instance)
    users: List[User] = await user_management.listing_users(tenant_api_key)
    for user in users:
        if 'user-type' in user.meta_data and user.meta_data['user-type'] == 'demo':
            await user_management.delete_user(tenant_key=tenant_api_key, external_id=user.external_user_id,
                                              internal_id=user.id, force=True)


async def main(external_user_id: str, tenant_api_key: str, instance: str):
    """
    Main function for the async sample.

    Parameters
    ----------
    external_user_id: str
        External id of the shadow user within the Wacom Personal Knowledge.
    tenant_api_key: str
        Tenant api key of the shadow user within the Wacom Personal Knowledge.
    instance: str
        URL of instance
    """
    async_client: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(application_name="Async sample",
                                                                          service_url=instance)
    permanent_session: PermanentSession = await async_client.login(tenant_api_key=tenant_api_key,
                                                                   external_user_id=external_user_id)
    """
    The permanent session contains the external user id, the tenant id, thus it is capable to refresh the token and 
    re-login if needed. The functions check if the token is expired and refresh it if needed. Internally, the token 
    manager handles the session. There are three different session types:
    - Permanent session: The session is refreshed automatically if needed.
    - Refreshable session: The session is not refreshed automatically using the refresh token, 
                           but if the session is not used for a day the refresh token is invalidated.
    - Timed session: The session is only has the authentication token and no refresh token. Thus, it times out after
                     one hour.
    """
    print(f'Service instance: {async_client.service_url}')
    print('-' * 100)
    print(f'Logged in as {permanent_session.external_user_id} (tenant id: {permanent_session.tenant_id}) ')
    is_ten_admin: bool = permanent_session.roles == "TenantAdmin"
    print(f'Is tenant admin: {is_ten_admin}')
    print('-' * 100)
    print(f'Token information')
    print('-' * 100)
    print(f'Refreshable: {permanent_session.refreshable}')
    print(f'Token must be refreshed before: {permanent_session.expiration} UTC')
    print(f'Token expires in {permanent_session.expires_in} seconds)')
    print('-' * 100)
    print(f'Creating two users')
    print('-' * 100)
    # User management sample
    user_1, user_token_1, refresh_token_1 = await user_management_sample(tenant_api_key, instance)
    print(f'User: {user_1}')
    user_2, user_token_2, refresh_token_2 = await user_management_sample(tenant_api_key, instance)
    print(f'User: {user_2}')
    print('-' * 100)
    async_client_user_1: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(application_name="Async user 1",
                                                                                 service_url=instance)
    refresh_session_1: RefreshableSession = await async_client_user_1.register_token(auth_key=user_token_1,
                                                                                     refresh_token=refresh_token_1)
    async_client_user_2: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(application_name="Async sample",
                                                                                 service_url=instance)
    await async_client_user_2.register_token(auth_key=user_token_2, refresh_token=refresh_token_2)
    """
    Now, let's create some entities.
    """
    print('Creation of entities')
    print('-' * 100)
    things_objects: Dict[str, ThingObject] = import_entity_from_wikidata('Leonardo da Vinci', EN)
    created: List[ThingObject] = await async_client_user_1.create_entity_bulk(list(things_objects.values()))
    for thing in created:
        try:
            await async_client_user_2.entity(thing.uri)
        except WacomServiceException as we:
            print(f'User 2 cannot see entity {thing.uri}.\n{format_exception(we)}')

    # Now using the group management service
    group_management: AsyncGroupManagementService = AsyncGroupManagementService(application_name="Group management",
                                                                                service_url=instance)
    await group_management.use_session(refresh_session_1.id)
    # User 1 creates a group
    new_group: Group = await group_management.create_group("sample-group")
    for thing in created:
        try:
            await group_management.add_entity_to_group(new_group.id, thing.uri)
        except WacomServiceException as we:
            print(f'User 1 cannot delete entity {thing.uri}.\n{format_exception(we)}')
    await group_management.add_user_to_group(new_group.id, user_2.id)
    print(f'User 2 can see the entities now. Let us check with async client 2. '
          f'Id of the user: {async_client_user_2.current_session.external_user_id}')
    for thing in created:
        iter_thing: ThingObject = await async_client_user_2.entity(thing.uri)
        label: Optional[Label] = iter_thing.label_lang(EN_US)
        print(f'User 2 can see entity {label.content if label else "UNKNOWN"} {iter_thing.uri}.'
              f'Ownership: owner flag:={iter_thing.owner}, owner is {iter_thing.owner_id}.')
    print('-' * 100)
    await clean_up(instance=instance, tenant_api_key=tenant_api_key)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default='https://private-knowledge.wacom.com',
                        help="URL of instance")
    args = parser.parse_args()
    asyncio.run(main(args.user, args.tenant, args.instance))
```
### Semantic Search

The sample shows how to use the semantic search.
There are two types of search:
- Label search
- Document search

The label search is used to find entities based on the label.
The document search is used to find documents based on the content.


```python
import argparse
import re
import time
from typing import List, Dict, Any

from knowledge.base.language import EN_US
from knowledge.base.search import LabelMatchingResponse, DocumentSearchResponse, VectorDBDocument
from knowledge.services.search import SemanticSearchClient


def clean_text(text: str, max_length: int = -1) -> str:
    """
    Clean text from new lines and multiple spaces.

    Parameters
    ----------
    text: str
        Text to clean.
    max_length: int [default=-1]
        Maximum length of the cleaned text. If the length is-1, then the text is not truncated.

    Returns
    -------
    str
        Cleaned text.
    """
    # First, remove new lines
    text = text.strip().replace('\n', ' ')
    # Then remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    if 0 < max_length < len(text):
        return text[:max_length] + '...'
    return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()
    client: SemanticSearchClient = SemanticSearchClient(service_url=args.instance)
    session = client.login(args.tenant, args.user)
    max_results: int = 10
    labels_count: int = client.count_documents(locale=EN_US)
    print(f"Tenant ID: {client.current_session.tenant_id} | Labels count: {labels_count} for [locale:={EN_US}]")
    t0: float = time.time()
    results: LabelMatchingResponse = client.labels_search(query="Leonardo Da Vinci", locale=EN_US,
                                                          max_results=max_results)
    t1: float = time.time()
    if len(results.results) > 0:
        print("=" * 120)
        for idx, res in enumerate(results.results):
            print(f"{idx + 1}. {res.label} | Relevance: ({res.score:.2f}) | URI: {res.entity_uri}")
        all_labels: List[VectorDBDocument] = client.retrieve_labels(EN_US, results.results[0].entity_uri)
        print("=" * 120)
        print(f"Labels for best match: {results.results[0].entity_uri}")
        for idx, label in enumerate(all_labels):
            print(f"{idx + 1}. {label.content}")
    print("=" * 120)
    print(f"Time: {(t1 - t0) * 1000:.2f} ms")
    print("=" * 120)
    document_count: int = client.count_documents(locale=EN_US)
    print(f"Document count: {document_count} for [locale:={EN_US}]")
    t2: float = time.time()
    document_results: DocumentSearchResponse = client.document_search(query="Leonardo Da Vinci artwork", locale=EN_US,
                                                                      max_results=max_results)
    t3: float = time.time()
    print("=" * 120)
    if len(document_results.results) > 0:

        for idx, res in enumerate(document_results.results):
            print(f"{idx + 1}.  URI: {res.content_uri} | Relevance: {res.score:.2f} | Chunk:"
                  f"\n\t{clean_text(res.content_chunk, max_length=100)}")
        print(f"\n All document chunks for best match: {document_results.results[0].content_uri}")
        print("=" * 120)
        # If you need all document chunks, you can retrieve them using the content_uri.
        best_match_uri: str = document_results.results[0].content_uri
        chunks: List[VectorDBDocument] = client.retrieve_documents_chunks(locale=EN_US, uri=best_match_uri)
        metadata: Dict[str, Any] = document_results.results[0].metadata
        for idx, chunk in enumerate(chunks):
            print(f"{idx + 1}. {clean_text(chunk.content)}")
        print("\n\tMetadata:\n\t---------")
        for key, value in metadata.items():
            print(f"\t- {key}: {clean_text(value, max_length=100) if isinstance(value, str) else value }")
    print("=" * 120)
    print(f"Time: {(t3 - t2) * 1000:.2f} ms")
    print("=" * 120)
```

### Ink Services

The `InkServices` client provides access to Wacom's ink processing pipeline, covering handwriting recognition (HWR),
math recognition, Named Entity Linking on ink content, and format conversion.
All operations accept a Universal Ink Model (UIM) binary file as input.

#### Handwriting Recognition

`perform_ink_to_text` enriches the UIM with recognition results embedded in the model itself.
`perform_ink_to_text_plain` is a convenience wrapper that returns only the recognized plain text string.

```python
from pathlib import Path
from knowledge.base.ink import HWRMode, Priority, Provider, Schema
from knowledge.base.language import EN_US
from knowledge.services.ink import InkServices

client: InkServices = InkServices(service_url="https://private-knowledge.wacom.com")
client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")

uim_content: bytes = Path("uims/text/en_US/text.uim").read_bytes()

# Enriched UIM with recognition results
enriched_uim: bytes = client.perform_ink_to_text(
    content=uim_content,
    locale=EN_US,
    hwr_mode=HWRMode.TEXT_MODE,
    priority=Priority.LOWEST,
    provider=Provider.MYSCRIPT,
    schema=Schema.SEGMENTATION_V03,
)

# Plain recognized text
text: str = client.perform_ink_to_text_plain(
    content=uim_content,
    locale=EN_US,
    hwr_mode=HWRMode.TEXT_MODE,
    priority=Priority.LOWEST,
    provider=Provider.MYSCRIPT,
    schema=Schema.SEGMENTATION_V03,
)
print(f"Recognized text: {text!r}")
```

#### Math Recognition

`perform_ink_to_math` runs math recognition on a UIM containing handwritten mathematical expressions
and returns an enriched UIM with the recognition results.

```python
from pathlib import Path
from knowledge.base.ink import Priority, Provider, Schema
from knowledge.services.ink import InkServices

client: InkServices = InkServices(service_url="https://private-knowledge.wacom.com")
client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")

math_uim: bytes = Path("uims/math/en_US/math.uim").read_bytes()

math_enriched: bytes = client.perform_ink_to_math(
    content=math_uim,
    schema=Schema.MATH_V06,
    provider=Provider.MYSCRIPT,
    priority=Priority.LOWEST,
)
print(f"Math-enriched UIM: {len(math_enriched):,} bytes")
```

#### Named Entity Linking on Ink

`perform_named_entity_linking` links recognized text spans in an already HWR-enriched UIM to entities
in the personal knowledge graph.
Pass the output of `perform_ink_to_text` as input.

```python
from knowledge.base.language import EN_US
from knowledge.services.ink import InkServices

client: InkServices = InkServices(service_url="https://private-knowledge.wacom.com")
client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")

nel_uim: bytes = client.perform_named_entity_linking(content=enriched_uim, locale=EN_US)
print(f"NEL-enriched UIM: {len(nel_uim):,} bytes")
```

#### Format Conversion

`convert_to` exports a UIM to PNG, JPG, or SVG. `convert_to_pdf` exports to PDF in either vector
or raster mode.

```python
from pathlib import Path
from knowledge.base.ink import ExportFormat, PDFType
from knowledge.services.ink import InkServices

client: InkServices = InkServices(service_url="https://private-knowledge.wacom.com")
client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")

uim_content: bytes = Path("uims/text/en_US/text.uim").read_bytes()

# Raster formats
png_bytes: bytes = client.convert_to(uim_content, ExportFormat.PNG)
jpg_bytes: bytes = client.convert_to(uim_content, ExportFormat.JPG)

# Vector format
svg_bytes: bytes = client.convert_to(uim_content, ExportFormat.SVG)

# PDF — vector or raster rendering
pdf_vector: bytes = client.convert_to_pdf(uim_content, PDFType.VECTOR)
pdf_raster: bytes = client.convert_to_pdf(uim_content, PDFType.RASTER)

Path("output.png").write_bytes(png_bytes)
Path("output.svg").write_bytes(svg_bytes)
Path("output.pdf").write_bytes(pdf_vector)
```

Run the full ink services sample:

```bash
python samples/ink_services.py --user <user-id> --tenant <tenant-key>
```

---

### Content API

The `ContentClient` (sync, in `knowledge.services.content`) and `AsyncContentClient` (async, in `knowledge.services.asyncio.content`) provide access to the Wacom Content API.
Content items are binary blobs — images, PDFs, ink files, audio, and so on — attached to an entity in the knowledge graph by its URI.
The Content API enforces only the mechanical rules (access rights on the owning entity, MIME-type integrity on file replacement, and soft/hard delete primitives); tenant- and product-specific policy belongs in the business layer above (see [Business Logic Recommendations](#content-api--business-logic-recommendations)).

#### Upload, list, download

```python
from pathlib import Path
from knowledge.services.content import ContentClient

client: ContentClient = ContentClient(service_url="https://private-knowledge.wacom.com")
client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")

file_bytes: bytes = Path("report.pdf").read_bytes()

content_id: str = client.upload_content(
    uri="wacom:entity:abc-123",
    file_content=file_bytes,
    filename="report.pdf",
    mimetype="application/pdf",
)

# All content items attached to an entity
items = client.list_content(uri="wacom:entity:abc-123")
for item in items:
    print(f"{item.id} ({item.mime_type}) tags={item.tags} deleted={item.is_deleted}")

# Download the raw file
file_bytes_back: bytes = client.download_content(content_id)

# Metadata only (no blob)
info = client.get_content_info(content_id)
print(info.date_added, info.date_modified, info.metadata)
```

#### Update tags, metadata, or the file itself

```python
# Patch tags and metadata in a single call
client.update_content(
    content_id=content_id,
    tags=["report", "Q4-2026"],
    metadata={"author": "ada.lovelace", "status": "reviewed"},
)

# Replace just the metadata
client.update_content_metadata(content_id, metadata={"status": "archived"})

# Replace just the tags
client.update_content_tags(content_id, tags=["report", "archived"])

# Replace the stored file. The replacement must have the same MIME type;
# otherwise the service returns 409 Conflict.
client.update_content_file(
    content_id=content_id,
    file_content=Path("report-v2.pdf").read_bytes(),
    filename="report-v2.pdf",
)
```

#### Delete

`force=False` (the default) performs a **soft delete**: the item is flagged with `isDeleted=true` but the blob and metadata are kept.
`force=True` performs a **hard delete**, removing the blob from premium storage irreversibly.
Soft-deleted items are returned by `list_content(..., show_deleted=True)` only when called by a tenant admin.

```python
# Soft delete (reversible)
client.delete_content(content_id)

# Hard delete (irreversible; gate this in the business layer — see below)
client.delete_content(content_id, force=True)

# Cascade: delete every content item attached to an entity
client.delete_all_content(uri="wacom:entity:abc-123")
```

#### Async equivalent

```python
import asyncio
from pathlib import Path
from knowledge.services.asyncio.content import AsyncContentClient

async def main() -> None:
    client: AsyncContentClient = AsyncContentClient(
        service_url="https://private-knowledge.wacom.com",
    )
    await client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")
    try:
        content_id: str = await client.upload_content(
            uri="wacom:entity:abc-123",
            file_content=Path("report.pdf").read_bytes(),
            filename="report.pdf",
        )
        items = await client.list_content(uri="wacom:entity:abc-123")
        for item in items:
            print(item.id, item.mime_type)
    finally:
        await client.close_all_sessions()

asyncio.run(main())
```

#### `ContentObject` fields

`list_content`, `get_content_info`, and `update_content` return `ContentObject` instances (`knowledge.base.content`):

| Field           | Type             | Description                                                          |
|-----------------|------------------|----------------------------------------------------------------------|
| `id`            | `str`            | Unique identifier returned at upload time.                           |
| `mime_type`     | `str`            | MIME type of the stored file.                                        |
| `tags`          | `List[str]`      | Tags attached to the content item.                                   |
| `metadata`      | `Dict[str, str]` | Key-value metadata.                                                  |
| `date_added`    | `datetime`       | UTC creation timestamp.                                              |
| `date_modified` | `datetime`       | UTC last-modified timestamp.                                         |
| `is_deleted`    | `bool`           | `True` for soft-deleted items returned via `show_deleted=True`.      |

Run the full content API sample:

```bash
python samples/content_handling.py \
    --tenant <TENANT_API_KEY> \
    --user   <EXTERNAL_USER_ID> \
    --file   /path/to/original.png \
    --update-file /path/to/replacement.png
```

#### Content API — Business Logic Recommendations

This section captures guidance for the business-level REST API that sits on top of the Content API.
The Content API deliberately exposes broad primitives (Read / Write / Delete rights, `force`, `showDeleted`, MIME-type integrity) so that tenant- and product-specific policy can be implemented once, in the business layer, without changing the core.

The recommendations below are **non-normative defaults**. A given deployment may choose a stricter or looser policy; the Content API will honor whatever the business layer forwards.

##### Why the split

The two layers have different jobs:

| Layer                          | Responsibility                                                                                                                                                                                                   |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Content API** (this SDK)     | Mechanical correctness: storage, rights enforcement on the owning entity, soft/hard delete primitives, MIME-type integrity, audit timestamps.                                                                    |
| **Business REST API** (upstream) | Product and tenant policy: who may hard-delete, restore flow, trash UX, retention windows, GDPR erasure, quotas, rate limits, virus scanning, derivative generation (thumbnails, text extraction), notifications. |

Keeping policy out of the Content API means a tenant can change its rules (for example, "Delete right means soft delete only, hard delete is admin-only") by changing the business layer without touching the data plane.

##### Gating hard delete

The Content API grants `force=true` to any caller holding the Delete right on the owning entity.
The business API should typically **not** expose this directly.

Recommended default:

| Caller                                                  | Soft delete (`force=false`) | Hard delete (`force=true`)        |
|---------------------------------------------------------|:---------------------------:|:---------------------------------:|
| Content uploader                                        |             ✅              |                ✅                 |
| Entity owner                                            |             ✅              |                ✅                 |
| Group member with Delete right on a `Shared` entity     |             ✅              | ❌ (defer to owner/admin)         |
| Tenant user with Delete right on a `Public` entity      |             ✅              | ❌ (defer to owner/admin)         |
| TenantAdmin                                             |             ✅              |                ✅                 |

**Rationale:** soft delete is reversible and its blast radius is bounded; hard delete destroys the blob and its history.
A careless or hostile collaborator should not be able to permanently erase someone else's uploaded work.
The business layer should therefore translate an ordinary "Delete" action into `DELETE /content/{id}` (no `force`), and only forward `force=true` when the caller is the uploader, the entity owner, or a TenantAdmin.

##### Offering a trash / restore experience

`showDeleted=true` is honored only for **TenantAdmins** at the core. To build a self-service "Trash" feature, the business layer should:

1. Call `GET /content?uri=…&showDeleted=true` with an admin or service token.
2. Filter the result to items whose uploader (or entity owner) matches the calling user.
3. Return that filtered list as the user's trash.
4. Offer a **Restore** action that flips `isDeleted` back to `false`. A dedicated `POST /content/{id}/restore` primitive in the Content API is recommended; until it exists, the business layer has no lossless way to restore a soft-deleted item.
5. Offer a **Delete permanently** action that issues `DELETE /content/{id}?force=true`, subject to the gating above.

##### Retention and scheduled hard-delete

Soft-deleted items still occupy premium blob storage.
The business layer should enforce a retention policy — for example, automatically hard-deleting soft-deleted items after N days — by running a scheduled job that:

1. Lists soft-deleted items per tenant via `GET /content?…&showDeleted=true`.
2. Selects items whose `dateModified` is older than the retention window.
3. Issues `DELETE /content/{id}?force=true` for each.

**Recommended defaults:** 30 days for user-initiated soft deletes, 7 days for cascaded deletes originating from an entity removal.

##### GDPR / right-to-erasure

When a user exercises a right-to-erasure request, soft delete is insufficient — the content must actually leave premium storage. The business layer should:

1. Enumerate all entities owned by the subject.
2. For each entity, call `DELETE /content?uri={entityUri}` (cascading to every attached content item).
3. Follow up with `DELETE /content/{id}?force=true` on any remaining items returned under `showDeleted=true` to guarantee hard deletion.
4. Record the operation in an auditable log kept outside the knowledge graph.

##### MIME-type integrity on file replacement

`PUT /content/{id}/file` returns **409 Conflict** when the replacement file's MIME type differs from the stored one.
The business layer should surface this to the user as "upload a file of the same type, or create a new content item instead" rather than retrying blindly.
If a true type change is intended, the correct pattern is: upload a new content item via `POST /content/{uri}`, copy over the tags and metadata, then delete the old item.

##### Quotas, rate limits, and scanning

The Content API does **not** enforce per-tenant storage quotas, upload rate limits, virus scanning, or content-type whitelists.
These belong to the business layer and should run **before** the request is forwarded to the Content API, so that rejected uploads never touch premium storage.

##### Derived artefacts

Thumbnails, extracted text for full-text search, embeddings for vector search, and similar derivatives should be produced by the business layer (or a downstream worker triggered by it) rather than being stored as first-class content items — unless they are themselves user-facing.
When derivatives are stored via this API, tag them (e.g. `derivative:thumbnail`) so that lifecycle operations can cascade cleanly.

##### Audit trail

`dateAdded`, `dateModified`, and `isDeleted` provide a minimal audit surface.
For a full audit trail (who uploaded, who deleted, who restored, from which IP, under which business action), the business layer should emit audit events to a separate store at the moment it calls the Content API, rather than relying on the core timestamps alone.

---

### Index Management

The `IndexManagementClient` extends `SemanticSearchClient` with administrative operations for the
vector search index. It allows operators to inspect index health, stream all indexed documents,
refresh or optimize the index, and delete individual documents by ID.

#### Index health

```python
from knowledge.base.index import HealthResponse
from knowledge.base.language import EN_US
from knowledge.services.index_management import IndexManagementClient

client: IndexManagementClient = IndexManagementClient(service_url="https://private-knowledge.wacom.com")
client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")

health: HealthResponse = client.index_health(index_mode="document", locale=EN_US)
print(f"Healthy: {health.healthy}")
print(f"Cluster status: {health.condition.cluster.status} | Nodes: {health.condition.cluster.number_of_nodes}")
for shard in health.condition.shards:
    print(f"  Shard [{shard.shard_id}] state={shard.shard_state} docs={shard.num_docs} size={shard.store_size}")
```

#### Streaming documents

`iterate_documents` streams all indexed documents as NDJSON without loading everything into memory,
making it suitable for large indices.

```python
from knowledge.base.index import IndexDocument
from knowledge.base.language import EN_US
from knowledge.services.index_management import IndexManagementClient

client: IndexManagementClient = IndexManagementClient(service_url="https://private-knowledge.wacom.com")
client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")

for doc in client.iterate_documents(index_mode="document", locale=EN_US):
    doc: IndexDocument
    print(f"ID: {doc.id} | URI: {doc.content_uri} | Locale: {doc.meta.locale}")
    print(f"  Created: {doc.meta.creation} | Chunk: {doc.meta.chunk_index}")
    print(f"  Preview: {doc.content[:100].strip()}...")
```

#### Refresh, force-merge, and delete

```python
from knowledge.base.language import EN_US
from knowledge.services.index_management import IndexManagementClient

client: IndexManagementClient = IndexManagementClient(service_url="https://private-knowledge.wacom.com")
client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")

# Make recent writes searchable immediately
client.refresh_index(index_mode="document", locale=EN_US)

# Remove a specific document from the index
client.delete_document_by_id(index_mode="document", locale=EN_US, document_ids=["<doc-id>"])

# Optimise storage after bulk deletions
client.force_merge_index(index_mode="document", locale=EN_US)
```

Run the full index management sample:

```bash
python samples/index_management.py --user <user-id> --tenant <tenant-key>
```

---

### Queue Management

The `QueueManagementClient` exposes monitoring information for the message queues that back the
asynchronous processing pipeline of the semantic search service.
It is a read-only observability client — it does not enqueue or dequeue messages.

#### List queues

```python
from typing import List
from knowledge.base.queue import QueueMonitor, QueueNames
from knowledge.services.queue_management import QueueManagementClient

client: QueueManagementClient = QueueManagementClient(service_url="https://private-knowledge.wacom.com")
client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")

# Names only
queue_names: QueueNames = client.list_queue_names()
print(queue_names.names)

# Full monitoring information for every queue
queues: List[QueueMonitor] = client.list_queues()
for queue in queues:
    print(f"{queue.name} | state={queue.state} | messages={queue.messages} | consumers={queue.consumers}")
```

#### Per-queue details

```python
from knowledge.base.queue import QueueCount, QueueMonitor
from knowledge.services.queue_management import QueueManagementClient

client: QueueManagementClient = QueueManagementClient(service_url="https://private-knowledge.wacom.com")
client.login(tenant_api_key="<tenant-key>", external_user_id="<user-id>")

queue_name: str = "my-queue"

is_empty: bool = client.queue_is_empty(queue_name)
size: QueueCount = client.queue_size(queue_name)
monitor: QueueMonitor = client.queue_monitor_information(queue_name)

print(f"Empty: {is_empty}")
print(f"Size : {size.count} messages")
print(f"State: {monitor.state} | Ready: {monitor.messages_ready} | Unacknowledged: {monitor.messages_unacknowledged}")
if monitor.message_stats:
    print(f"Stats: publish={monitor.message_stats.publish} deliver={monitor.message_stats.deliver} "
          f"ack={monitor.message_stats.ack}")
```

Run the full queue management sample:

```bash
python samples/queue_management.py --user <user-id> --tenant <tenant-key>
```

---

### Wikidata Scrapping

`samples/wikidata_scrapping.py` builds an import file from Wikidata without touching a tenant:
it crawls Wikidata, maps the entities onto `ThingObject`s through the ontology mapping
configuration, and writes NDJSON that `samples/import_entities.py` can push.

The crawl seeds either from an explicit list of QIDs or from a SPARQL query, then expands by
following the object properties the mapping configuration knows about — which is what keeps it
from wandering into unrelated corners of Wikidata.

```json
{"name": "artwork", "entity-list": ["Q762", "Q5582", "Q296"]}
```

```json
{
  "name": "painters",
  "query": {
    "filters": [{"property": "P31", "target": "Q5"}],
    "dynamic-filters": {"property": "P106", "targets": ["Q1028181"]},
    "limit": 1000,
    "language_code": "en"
  }
}
```

Scrape the seeds only (`--max-depth 0`), keeping English and German:

```bash
python samples/wikidata_scrapping.py -c scrapping/artwork.json -o ./out --languages en de --max-depth 0
```

One hop of expansion, with Wikipedia summaries as descriptions and every index enabled:

```bash
python samples/wikidata_scrapping.py -c scrapping/artwork.json -o ./out \
    --languages en de --max-depth 1 --wikipedia-summary --nel --full-text --vector-search
```

`--max-depth -1` (the default) crawls until no new QIDs are discovered; on a broad seed set that
is a very long run, so start bounded.

The script writes two files into the output directory:

| File | Content |
|------|---------|
| `<name>_<depth>.ndjson` | Entities in the import format, ready for `samples/import_entities.py` |
| `<name>_warnings.json` | Properties that could not be mapped, aggregated per PID with the QIDs and classes involved |

Then import the result:

```bash
python samples/import_entities.py -p ./out/artwork_0.ndjson --user <user-id> --tenant <tenant-key>
```

Two things are worth knowing before a large run:

- **The Wikidata cache is shared and persistent.** `WikiDataAPIClient.retrieve_entities` consults
  the `WikidataCache` before going to the network, and the sample loads and saves it around the
  crawl (`--cache`, default `pkl-cache/`). A second run over overlapping seeds is largely local.
- **Only the requested locales survive.** `--languages` is enforced on labels, aliases and
  descriptions after mapping. This matters because `wikidata_to_thing` falls back to copying
  *every* Wikidata description when no Wikipedia summary was pulled, including locales outside
  `SUPPORTED_LOCALES` that `load_import_format` then refuses to read back.
- **`--wikipedia-summary` costs a request per entity per language.** It replaces the short
  Wikidata description with the Wikipedia lead section, so it is the slowest flag here by a wide
  margin. When an article has no summary the Wikidata description is kept, so the flag never
  leaves an entity with less than it started with.

---

# Development

## Requirements

### Core Dependencies

| Package | Version | Description |
|---------|---------|-------------|
| `aiohttp` | Latest | Async HTTP client/server |
| `requests` | >=2.32.0, <3.0.0 | HTTP library |
| `PyJWT` | >=2.10.1, <3.0.0 | JSON Web Token |
| `rdflib` | >=7.1.0 | RDF library |
| `orjson` | >=3.10.0 | Fast JSON library |
| `cachetools` | >=5.3.0 | Caching utilities |
| `loguru` | 0.7.3 | Logging |
| `tqdm` | >=4.65.0 | Progress bars |

### Development Dependencies

Install with: `pip install personal-knowledge-library[dev]`

| Package | Purpose |
|---------|---------|
| `pytest` | Testing framework |
| `pytest-asyncio` | Async test support |
| `pytest-cov` | Coverage reporting |
| `mypy` | Type checking |
| `pylint` | Code analysis |
| `black` | Code formatting |
| `flake8` | Linting |

## Setting Up Development Environment

1. **Clone the repository:**

```bash
git clone https://github.com/Wacom-Developer/personal-knowledge-library.git
cd personal-knowledge-library
```

2. **Create and activate a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install the package with development dependencies:**

```bash
pip install -e ".[dev]"
```

## Running Tests

Run the full test suite:

```bash
pytest
```

Run tests with coverage report:

```bash
pytest --cov=knowledge --cov-report=term-missing
```

Run specific test files:

```bash
pytest tests/test_ontology_unit.py -v
```

## Code Quality

### Type Checking with mypy

```bash
mypy knowledge --ignore-missing-imports
```

### Linting with pylint

```bash
pylint knowledge
```

### Code Formatting with black

```bash
black knowledge tests
```

### Linting with flake8

```bash
flake8 knowledge
```

---

# Documentation

You can find more detailed technical documentation [here](https://developer-docs.wacom.com/preview/semantic-ink/).

API documentation is available in the [docs/knowledge](./docs/knowledge) directory.

## Contributing
Contribution guidelines are still a work in progress.

## License
[Apache License 2.0](LICENSE)
