# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""
Integration tests for the dedicated entity-descriptions endpoints (PKA-589).

Confirms the behaviour of ``GET`` / ``PATCH /v1/entity/{uri}/descriptions`` against a live
service, which the stub-level tests in ``test_entity_descriptions_unit.py`` cannot do.

**The `descriptions` key replaces the whole set — it does not merge.** This was verified
against the stage service: an entity holding ``en_US`` and ``de_DE`` descriptions, patched
with only ``en_US``, is left with ``en_US`` alone. The PKA-589 ticket describes the
non-empty case as an "upsert", which reads as if unmentioned locales survive. They do not.
A caller that patches one locale in isolation therefore destroys the others, so every call
has to send the complete set it wants the entity to end up with.

Confirmed states:

===============================  =====================================================
Body                             Effect
===============================  =====================================================
``descriptions`` key absent      no-op, 204, existing descriptions untouched
``descriptions`` non-empty list  replace the full set with the given descriptions
``descriptions`` empty list      delete every description of the entity
===============================  =====================================================

Flow:
    1. Create an isolated test user
    2. Create an entity with descriptions in two locales
    3. GET  — confirm both come back
    4. PATCH None — confirm nothing changes
    5. PATCH a subset — confirm the omitted locale is dropped (replace, not merge)
    6. PATCH an empty list — confirm every description is removed
    7. Delete the entity and the test user

Requires environment variables:
    - INSTANCE: URL of the service instance
    - TENANT_API_KEY: Tenant API key for authentication
"""

import os
import uuid
from typing import Dict, List, Optional, Tuple

import pytest

from knowledge.base.entity import Description
from knowledge.base.language import DE_DE, EN_US, JA_JP
from knowledge.base.ontology import OntologyClassReference, ThingObject
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.users import User, UserManagementServiceAPI, UserRole

PERSON_TYPE: OntologyClassReference = OntologyClassReference.parse("wacom:core#Person")

INSTANCE: Optional[str] = os.environ.get("INSTANCE")
TENANT_API_KEY: Optional[str] = os.environ.get("TENANT_API_KEY")

pytestmark = pytest.mark.skipif(
    not INSTANCE or not TENANT_API_KEY,
    reason="INSTANCE and TENANT_API_KEY must be set to reach a service instance",
)


def _locales(descriptions: List[Description]) -> Dict[str, str]:
    """Reduce a description list to a ``{locale: content}`` mapping for comparison."""
    return {str(desc.language_code): desc.content for desc in descriptions}


@pytest.fixture(scope="module")
def client_and_entity() -> Tuple[WacomKnowledgeService, str, UserManagementServiceAPI, User]:
    """Provision a user and an entity carrying descriptions in two locales."""
    users: UserManagementServiceAPI = UserManagementServiceAPI(
        service_url=INSTANCE,
        service_endpoint="graph/v1",
    )
    external_id: str = f"pkl-descriptions-{uuid.uuid4()}"
    user, token, refresh_token, _ = users.create_user(
        tenant_key=TENANT_API_KEY,
        external_id=external_id,
        roles=[UserRole.USER],
    )
    client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Descriptions integration test",
        service_url=INSTANCE,
        service_endpoint="graph/v1",
    )
    client.register_token(auth_key=token, refresh_token=refresh_token)

    entity: ThingObject = ThingObject(concept_type=PERSON_TYPE)
    entity.add_label("Descriptions Integration Test", EN_US)
    entity.add_description("original english", EN_US)
    entity.add_description("original deutsch", DE_DE)
    entity.use_for_nel = False
    entity.use_full_text_index = False
    entity.use_vector_index = False
    entity.use_vector_index_document = False
    uri: str = client.create_entity(entity)

    yield client, uri, users, user

    try:
        client.delete_entity(uri, force=True)
    except WacomServiceException:
        pass
    try:
        users.delete_user(TENANT_API_KEY, user.external_user_id, user.id, force=True)
    except WacomServiceException:
        pass


def test_the_endpoint_is_available(client_and_entity) -> None:
    """A 404/405 here means the service has not deployed PKA-589 yet."""
    client, uri, _, _ = client_and_entity

    try:
        client.descriptions(uri)
    except WacomServiceException as error:
        if error.status_code in (404, 405):
            pytest.skip(f"the descriptions endpoint is not deployed on this instance ({error.status_code})")
        raise


def test_descriptions_returns_every_locale(client_and_entity) -> None:
    """The entity's descriptions come back for all locales, keyed by locale."""
    client, uri, _, _ = client_and_entity

    assert _locales(client.descriptions(uri)) == {
        "en_US": "original english",
        "de_DE": "original deutsch",
    }


def test_none_is_a_no_op(client_and_entity) -> None:
    """``None`` omits the key, so the service leaves the descriptions alone and answers 204."""
    client, uri, _, _ = client_and_entity
    before: Dict[str, str] = _locales(client.descriptions(uri))

    returned = client.update_descriptions(uri, None)

    assert returned == [], "a 204 carries no body"
    assert _locales(client.descriptions(uri)) == before


def test_a_non_empty_list_replaces_the_whole_set(client_and_entity) -> None:
    """The key finding: a non-empty list is a **replace**, not a merge.

    The entity holds ``en_US`` and ``de_DE``. Patching with ``en_US`` and ``ja_JP`` leaves
    exactly those two — ``de_DE`` is dropped even though the payload never mentioned it.
    Callers must send the complete set they want the entity to end up with.
    """
    client, uri, _, _ = client_and_entity
    client.update_descriptions(uri, [Description("english one", EN_US), Description("deutsch eins", DE_DE)])
    assert set(_locales(client.descriptions(uri))) == {"en_US", "de_DE"}

    client.update_descriptions(uri, [Description("english two", EN_US), Description("日本語", JA_JP)])

    assert _locales(client.descriptions(uri)) == {"en_US": "english two", "ja_JP": "日本語"}


def test_patching_a_single_locale_drops_the_others(client_and_entity) -> None:
    """The same finding stated as the trap a caller falls into."""
    client, uri, _, _ = client_and_entity
    client.update_descriptions(uri, [Description("english one", EN_US), Description("deutsch eins", DE_DE)])

    client.update_descriptions(uri, [Description("english only", EN_US)])

    assert _locales(client.descriptions(uri)) == {"en_US": "english only"}, "de_DE should have been dropped"


def test_the_update_returns_the_stored_descriptions(client_and_entity) -> None:
    """The PATCH response reflects what the entity holds afterwards."""
    client, uri, _, _ = client_and_entity

    returned = client.update_descriptions(uri, [Description("returned value", EN_US)])

    assert _locales(returned) == {"en_US": "returned value"}
    assert _locales(returned) == _locales(client.descriptions(uri))


def test_an_empty_list_deletes_every_description(client_and_entity) -> None:
    """An empty list is meaningful and destructive: it clears the entity."""
    client, uri, _, _ = client_and_entity
    client.update_descriptions(uri, [Description("about to go", EN_US)])
    assert _locales(client.descriptions(uri)) != {}

    client.update_descriptions(uri, [])

    assert client.descriptions(uri) == []


def test_descriptions_of_an_unknown_entity_is_reported(client_and_entity) -> None:
    """A URI the tenant does not hold is an error, not an empty list."""
    client, _, _, _ = client_and_entity

    with pytest.raises(WacomServiceException):
        client.descriptions(f"does-not-exist-{uuid.uuid4()}")
