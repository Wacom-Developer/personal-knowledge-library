# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from faker import Faker

from knowledge.base.entity import Label
from knowledge.base.language import JA_JP, EN_US, DE_DE, BG_BG, FR_FR, IT_IT, ES_ES, SUPPORTED_LOCALES
from knowledge.base.ontology import (
    ThingObject,
    OntologyClassReference,
    OntologyPropertyReference,
    DataProperty,
    ObjectProperty,
    LAST_UPDATE_DATE,
    SYSTEM_SOURCE_REFERENCE_ID,
    SYSTEM_SOURCE_SYSTEM,
)
from knowledge.base.response import JobStatus, NewEntityUrisResponse
from knowledge.nel.base import KnowledgeGraphEntity
from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
from knowledge.services.asyncio.group import AsyncGroupManagementService
from knowledge.services.asyncio.users import AsyncUserManagementService
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import Visibility, SearchPattern
from knowledge.services.group import Group, GroupInfo
from knowledge.services.users import User, UserRole
from knowledge.utils.graph import async_things_iter, async_count_things, async_things_session_iter

THING_OBJECT: OntologyClassReference = OntologyClassReference("wacom", "core", "Thing")
LEONARDO_DA_VINCI: str = "Leonardo da Vinci"
MONA_LISA: str = "Mona Lisa"
FIRST_NAME: str = "Leonardo"
LAST_NAME: str = "da Vinci"
LEONARDO_QID: str = "Q762"
dummy_image: Path = Path(__file__).parent / ".." / "assets" / "dummy.png"
tenant_api_key: str = os.environ.get("TENANT_API_KEY")
# Create an external user id
external_id: str = str(uuid.uuid4())
external_id_2: str = str(uuid.uuid4())
LIMIT: int = 10000
HAS_ART_STYLE: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:creative#hasArtstyle")
IS_RELATED: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#isRelated")
LINKS: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#links")


def create_thing(concept_type: OntologyClassReference) -> ThingObject:
    """
    Create a thing object with random data.
    Returns
    -------
    instance: ThingObject
        Thing object with random data.
    """
    thing: ThingObject = ThingObject(concept_type=concept_type)
    for lang_inst in [JA_JP, EN_US, DE_DE, BG_BG, FR_FR, IT_IT, ES_ES]:
        fake: Faker = Faker(lang_inst)
        name: str = fake.name()
        thing.add_label(name, lang_inst)
        thing.add_description(fake.text(), lang_inst)
        names: List[str] = name.split()
        if len(names) == 2:
            thing.add_data_property(
                DataProperty(names[0], OntologyPropertyReference.parse("wacom:core#firstName"), language_code=lang_inst)
            )
            thing.add_data_property(
                DataProperty(names[1], OntologyPropertyReference.parse("wacom:core#lastName"), language_code=lang_inst)
            )
        elif len(names) == 3:
            thing.add_data_property(
                DataProperty(names[1], OntologyPropertyReference.parse("wacom:core#firstName"), language_code=lang_inst)
            )
            thing.add_data_property(
                DataProperty(names[2], OntologyPropertyReference.parse("wacom:core#lastName"), language_code=lang_inst)
            )
    return thing


def create_random_thing(reference_id: str, uri: str) -> ThingObject:
    """
    Create a random thing object with random data.
    Parameters
    ----------
    reference_id: str
        Reference id of the thing object.
    uri: str
        URI of the thing object.

    Returns
    -------
    random_thing: ThingObject
        Thing object with random data.
    """
    thing: ThingObject = ThingObject(concept_type=OntologyClassReference.parse("wacom:core#Topic"))
    for lang_inst in SUPPORTED_LOCALES:
        fake: Faker = Faker(lang_inst)
        name: str = fake.name()
        thing.add_label(name, lang_inst)
        thing.add_description(fake.text(), lang_inst)
    thing.add_data_property(DataProperty(reference_id, SYSTEM_SOURCE_REFERENCE_ID, language_code=EN_US))
    thing.add_data_property(DataProperty("test-case", SYSTEM_SOURCE_SYSTEM, language_code=EN_US))
    thing.add_relation(ObjectProperty(relation=LINKS, outgoing=[uri]))
    return thing


def create_faulty_thing() -> ThingObject:
    """
    Create a faulty thing object with random data.
    Returns
    -------
    instance: ThingObject
        Thing object wrong.
    """
    thing: ThingObject = ThingObject(concept_type=OntologyClassReference.parse("wacom:core#NOT_EXISTING"))
    thing.add_label("Test", EN_US)
    return thing


# ----------------------------------------------------------------------------------------------------------------------
instance: str = os.environ.get("INSTANCE")
content_user_id: str = os.environ.get("EXTERNAL_USER_ID")

async_client: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(
    application_name="Async client test", service_url=instance,
)
group_management: AsyncGroupManagementService = AsyncGroupManagementService(
    application_name="Async client test", service_url=instance,
)
user_management: AsyncUserManagementService = AsyncUserManagementService(
    application_name="Async client test", service_url=instance,
)

# ----------------------------------------------------------------------------------------------------------------------


async def test_01_handle_user():
    """
    Handles operations related to user management such as creating, validating
    existence, and updating user information and metadata within a tenant scope.

    The function first verifies if a user characterized by the external identifier exists
    in the system. If the user does not exist, it creates the user with specified attributes,
    validates their creation, and subsequently updates their metadata. This operation focuses
    on correctly managing user lifecycle using asynchronous operations and ensures
    consistency within the user repository.

    Raises
    ------
    AssertionError
        If the user already exists with the given external identifier.
    AssertionError
        If the user creation operation is unsuccessful.
    AssertionError
        If the user metadata update is not reflected as expected.
    """
    users: List[User] = await user_management.listing_users(tenant_api_key, limit=LIMIT)
    for user in users:
        if user.external_user_id == external_id:
            raise AssertionError("User already exists")
    # Create user
    _, token, refresh, expire = await user_management.create_user(
        tenant_api_key, external_id=external_id, meta_data={"account-type": "qa-test"}, roles=[UserRole.CONTENT_MANAGER]
    )
    assert token is not None
    assert refresh is not None
    assert expire is not None
    users: List[User] = await user_management.listing_users(tenant_api_key, limit=LIMIT)
    if external_id not in [u.external_user_id for u in users]:
        raise AssertionError("User not created")
    new_user: Optional[User] = None
    for user in users:
        if user.external_user_id == external_id:
            new_user = user

    # Update user
    await user_management.update_user(
        tenant_api_key,
        internal_id=new_user.id,
        external_id=new_user.external_user_id,
        roles=[UserRole.CONTENT_MANAGER],
        meta_data={"account-type": "qa-test", "updated": True},
    )
    users: List[User] = await user_management.listing_users(tenant_api_key, limit=LIMIT)
    for u in users:
        if u.external_user_id == external_id:
            assert u.meta_data.get("updated") == "true"


async def test_02_push_entity():
    """
    Tests the ability to create, modify, and validate entities in the Wacom Knowledge service via
    asynchronous API calls. The function performs entity creation, retrieval, image updates,
    and ensures proper handling of erroneous inputs.

    Assertions:
        - Ensure the created entity URI is not None.
        - Verify that the newly created entity has the specified concept type.
        - Confirm that the initial image of the entity is None.
        - Validate the entity's updated image is set correctly with both local and URL methods.
        - Properly handle exceptions for faulty entities with expected HTTP status code and URL.

    Raises:
        AssertionError: If any of the conditions for assertions are not met.
        WacomServiceException: If an error occurs during the creation of a faulty entity.
    """
    thing: ThingObject = create_thing(OntologyClassReference.parse("wacom:core#Person"))
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    await async_client.handle_token(force_refresh=True)
    thing_uri: str = await async_client.create_entity(thing)
    assert thing_uri is not None
    new_thing: ThingObject = await async_client.entity(thing_uri)
    assert new_thing is not None
    assert new_thing.concept_type == OntologyClassReference.parse("wacom:core#Person")
    assert new_thing.image is None
    await async_client.set_entity_image_local(thing_uri, dummy_image)
    new_image_thing: ThingObject = await async_client.entity(thing_uri)
    assert new_image_thing is not None
    image_url: str = new_image_thing.image
    await async_client.set_entity_image_url(thing_uri, image_url, mime_type="image/png")
    wrong_thing: ThingObject = create_faulty_thing()
    try:
        await async_client.create_entity(wrong_thing)
        raise AssertionError("Exception not raised")
    except WacomServiceException as e:
        assert e.status_code == 400
        assert e.url == async_client.service_base_url + AsyncWacomKnowledgeService.ENTITY_ENDPOINT
        assert isinstance(e, WacomServiceException)


async def test_03_get_entity():
    """
    Get entity.

    This function handles the process of acquiring and verifying a single entity for a
    specified user within a private visibility context. It includes the management of
    user token authentication, token handling, entity counting, and testing of an
    asynchronous iterator for accessing entities. The function ensures that the
    retrieved entity matches a specified ontology class reference and validates
    the non-emptiness of the resultant entity.

    Raises
    ------
    AssertionError
        If the entity count is not equal to 1 for the specified user or if the retrieved
        entity does not match the ontology class reference.
    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    """Get entity."""
    count: int = await async_count_things(async_client, user_token, THING_OBJECT, visibility=Visibility.PRIVATE)
    # This user only created one entity
    assert count == 1
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(
        async_client, user_token, refresh_token, THING_OBJECT, only_own=True
    ):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        # This user only created one entity
        assert full_entity.concept_type == OntologyClassReference.parse("wacom:core#Person")
        # Entities must not be empty
        assert full_entity is not None


async def test_04_update_entity():
    """
    Async function that tests updating an entity using an asynchronous client.

    This function verifies the process of logging in, handling tokens, and updating
    entities with new data properties. It uses an async iterator to traverse through
    entities and performs assertions to ensure the integrity of the operations. The
    function specifically checks the addition of data properties and validates it by
    re-pulling the updated entity.

    Raises
    ------
    AssertionError
        If the entity is `None` during the pull, or if the updated property value
        does not match the expected timestamp.
    """
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(
        async_client, user_token, refresh_token, THING_OBJECT, only_own=True
    ):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        # Entities must not be empty
        assert full_entity is not None
        # Update entity
        update_time: str = datetime.now().isoformat()
        full_entity.add_data_property(DataProperty(update_time, LAST_UPDATE_DATE))
        await async_client.update_entity(full_entity, auth_key=user_token)
        # Pull entity again
        full_entity_2: ThingObject = await async_client.entity(full_entity.uri)
        assert full_entity_2 is not None
        assert full_entity_2.data_properties.get(LAST_UPDATE_DATE)[0].value == update_time


async def test_05_literal_entity():
    """
    Test the retrieval and handling of literal entities using an asynchronous client.

    This function tests the ability of the `async_client` to:
    1. Log in with an external user ID and tenant API key.
    2. Retrieve and manage user and refresh tokens.
    3. Iterate over asynchronous data (`async_things_iter`) and ensure that the
       retrieved entities are fully populated.
    4. Ensure that each entity has associated literals that are non-empty.
    5. Validate that requesting literals for non-existent entities raises the expected exception.

    Raises
    ------
    AssertionError
        If the condition `await async_client.literals(uuid.uuid4().hex, auth_key=user_token)`
        does not raise an exception.
    WacomServiceException
        If an invalid literal request or entity results in the expected error handling,
        specifically when the status code is 404.
    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(
        async_client, user_token, refresh_token, THING_OBJECT, only_own=True
    ):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        # Entities must not be empty
        assert full_entity is not None
        literals: List[DataProperty] = await async_client.literals(full_entity.uri, auth_key=user_token)
        assert len(literals) > 0
        try:
            await async_client.literals(uuid.uuid4().hex, auth_key=user_token)
            raise AssertionError("Exception not raised")
        except WacomServiceException as e:
            assert e.status_code == 404
            assert isinstance(e, WacomServiceException)


async def test_06_labels_entity():
    """
    Tests the functionality of labels retrieval and entity validation in an asynchronous
    workflow. This includes testing async iteration over entities, fetching full entity
    details, and retrieving associated labels for entities.

    The test verifies that entities are not empty and ensures that labels are successfully
    retrieved. It also checks error handling by attempting to retrieve labels for a
    non-existent entity and asserting the expected exception behavior.

    Raises
    ------
    AssertionError
        If the expected exception is not raised when accessing labels for an invalid entity.
        This ensures proper error handling behavior.
    WacomServiceException
        When attempting to fetch labels for a non-existent entity URI, with a status code
        of 404, indicating the entity was not found.
    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(
        async_client, user_token, refresh_token, THING_OBJECT, only_own=True
    ):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        # Entities must not be empty
        assert full_entity is not None
        labels: List[Label] = await async_client.labels(full_entity.uri, auth_key=user_token)
        assert len(labels) > 0
        try:
            await async_client.labels(uuid.uuid4().hex, auth_key=user_token)
            raise AssertionError("Exception not raised")
        except WacomServiceException as e:
            assert e.status_code == 404
            assert isinstance(e, WacomServiceException)


async def test_07_relations_entity():
    """
    Test asynchronous relations functionality in an entity.

    This function tests the ability to fetch and handle relations for an entity
    using asynchronous methods. It verifies the process of logging in, handling
    tokens, fetching entities, pulling relations, and creating new relations
    between entities. The test includes checks to ensure that entities and
    relations meet the expected criteria.
    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(
        async_client, user_token, refresh_token, THING_OBJECT, only_own=True
    ):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        # Entities must not be empty
        assert full_entity is not None
        # Pull relations if configured
        relations: Dict[OntologyPropertyReference, ObjectProperty] = await async_client.relations(
            uri=full_entity.uri, auth_key=user_token
        )
        # Assert relations are
        assert len(relations) == 0
        await async_client.create_relation(full_entity.uri, IS_RELATED, full_entity.uri, auth_key=user_token)
        # Pull relations if configured
        relations: Dict[OntologyPropertyReference, ObjectProperty] = await async_client.relations(
            uri=full_entity.uri, auth_key=user_token
        )
        # Assert relations are
        assert len(relations) == 1


async def test_08_delete_entity():
    """
    Tests the deletion of an entity using an asynchronous client.

    This function performs the following:
    1. Logs into the asynchronous client using provided credentials.
    2. Iterates over the entities of a specific type using an asynchronous
       session iterator. It filters the entities to retrieve only those that
       are associated with the logged-in user.
    3. Retrieves the full entity details asynchronously for each entity.
    4. Deletes the entities forcefully from the system.

    This is intended to verify the ability of the client to locate and remove
    entities asynchronously.

    Raises
    ------
    No explicit exceptions are raised in the docstring since any exceptions
    related to login, iteration, or deletion are implementation-specific.
    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    # Test async iterator
    async for thing in async_things_session_iter(async_client, THING_OBJECT, only_own=True):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        await async_client.delete_entity(full_entity.uri, force=True)


async def test_09_search_labels():
    """
    Tests the functionality of searching labels through an asynchronous client.

    This test checks the behavior of the `search_labels` endpoint by performing
    searches with varying parameters, including general and exact matches. It verifies
    that the correct number of results are returned and tests the login-to-search
    workflow. Multiple test cases are executed to ensure the search functionality works
    as expected under different conditions.

    Raises
    ------
    AssertionError
        If the length of the returned entities list does not meet the expected
        conditions.

    Notes
    -----
    - The test requires an active tenant API key and a valid external user ID to
      authenticate and perform searches. These values must be provided at runtime.
    - The `search_labels` operation limits results according to the specified
      `limit` parameter and supports options such as exact matching and
      language-specific filters.

    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=content_user_id)
    res_entities, next_search_page = await async_client.search_labels(
        search_term=LEONARDO_DA_VINCI, language_code=EN_US, limit=10
    )
    assert len(res_entities) > 1
    res_entities, next_search_page = await async_client.search_labels(
        search_term=LEONARDO_DA_VINCI, language_code=EN_US, exact_match=True, limit=10
    )
    assert len(res_entities) >= 1


async def test_10_search_description():
    """
    Tests search functionality for a description query using the `search_description` method of the
    `async_client`. Logs in with the provided API key and user ID before performing the search query.

    The test validates that at least one entity is returned when searching descriptions
    related to "Michelangelo's Sistine Chapel" in the English language, with a specified limit.

    Raises
    ------
    AssertionError
        If the search does not return at least one entity.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=content_user_id)
    res_entities, next_search_page = await async_client.search_description(
        "Michelangelo's Sistine Chapel", EN_US, limit=10
    )

    assert len(res_entities) >= 1


async def test_11_search_relations():
    """
    Tests the search relations functionality of the async client.

    This function performs a series of operations to validate the behavior and correctness
    of the `search_labels`, `relations`, and `search_relation` methods. It ensures that the
    methods return expected results, handle exceptions appropriately, and comply with the
    specified constraints. Various scenarios, including valid and invalid inputs, are tested
    to ensure robustness and correctness.

    Raises
    ------
    AssertionError
        Raised when any assertion in the test fails, including unexpected absence
        of results or deviation from expected behavior.

    WacomServiceException
        Raised when the `search_relation` method is called with invalid input
        parameters violating constraints such as allowing only one valid parameter
        or requiring at least one parameter.
    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=content_user_id)
    art_style: Optional[ThingObject] = None
    results, _ = await async_client.search_labels("portrait", EN_US, limit=1)
    for entity in results:
        art_style = entity
    assert art_style is not None
    art_style.object_properties = await async_client.relations(art_style.uri)
    res_entities, next_search_page = await async_client.search_relation(
        relation=HAS_ART_STYLE, object_uri=art_style.uri, language_code=EN_US
    )
    assert len(res_entities) >= 1
    for entity in res_entities:
        results, _ = await async_client.search_relation(
            subject_uri=entity.uri, relation=HAS_ART_STYLE, language_code=EN_US
        )
        assert len(results) >= 1

    try:
        # Only one parameter is allowed: either subject_uri or object_uri
        r, _ = await async_client.search_relation(
            subject_uri=art_style.uri, relation=HAS_ART_STYLE, object_uri=art_style.uri, language_code=EN_US
        )
        raise AssertionError("Exception not raised")
    except WacomServiceException as e:
        assert e.message == "Only one parameter is allowed: either subject_uri or object_uri!"
        assert isinstance(e, WacomServiceException)
    try:
        # at least one parameter is allowed: either subject_uri or object_uri
        r, _ = await async_client.search_relation(
            subject_uri=None, relation=HAS_ART_STYLE, object_uri=None, language_code=EN_US
        )
        raise AssertionError("Exception not raised")
    except WacomServiceException as e:
        assert e.message == "At least one parameters is must be defined: either subject_uri or object_uri!"
        assert isinstance(e, WacomServiceException)


async def test_12_search_literals():
    """
    Executes an asynchronous test to search for literals using specified
    parameters and validates the result.

    This function first logs in the `async_client` using the given tenant API
    key and external user ID. Subsequently, it performs a search for literals
    using the specified search term, regular expression pattern, literal, and
    language code. The function then asserts whether the number of resulting
    entities matches the expected condition.

    Raises
    ------
    AssertionError
        If the number of entities in the result does not meet the assertion
        condition.
    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=content_user_id)
    res_entities, next_search_page = await async_client.search_literal(
        search_term=LEONARDO_QID, pattern=SearchPattern.REGEX, literal=SYSTEM_SOURCE_REFERENCE_ID, language_code=EN_US
    )
    assert len(res_entities) >= 1


async def test_13_named_entity_linking():
    """
    Tests the named entity linking functionality of the async client.

    This asynchronous function tests the ability of the async client to link personal
    entities to a given text using the named entity linking (NEL) feature. It logs in
    to the client, retrieves a list of entities, generates fake textual content, and
    links any discovered personal entities within the text. Assertions are made to
    ensure valid entity linking results.

    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=content_user_id)
    entities, _, _ = await async_client.listing(THING_OBJECT, page_id=None, limit=100, locale=EN_US)
    fake: Faker = Faker(EN_US)
    for ent in entities:
        if ent.use_for_nel and ent.label_lang(EN_US) is not None:
            text: str = f"{fake.text()} Do not forget about {ent.label_lang(EN_US).content}."
            linked_entities: List[KnowledgeGraphEntity] = await async_client.link_personal_entities(
                text, language_code=EN_US
            )
            assert len(linked_entities) >= 1


async def test_14_activations():
    """
    Test function to validate the activation and search API functionalities. This function performs
    login into the asynchronous test client, searches for a specific entity, retrieves its URI,
    and validates the activation structure and relations associated with that entity.

    Raises
    ------
    No explicit exceptions are raised but may propagate exceptions from underlying API functionalities.

    Notes
    -----
    - Logs in to the async client using specified tenant and user identifiers.
    - Performs search for a predefined entity and retrieves its unique URI.
    - Fetches interconnected entities and their relations to validate activation data.
    - Verifies non-empty results for the specified entity relationship queries.
    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=content_user_id)
    leo_uri: Optional[str] = None
    search_results, _ = await async_client.search_labels(LEONARDO_DA_VINCI, EN_US, limit=1)
    for entity in search_results:
        leo_uri = entity.uri
        break
    assert leo_uri is not None
    things, relations = await async_client.activations([leo_uri], depth=2)
    assert len(things) > 0
    assert len(relations) > 0


async def test_15_create_group_users():
    """
    Tests the creation of group users through the user management service.

    This function validates the process of creating a user associated with a
    specific group by invoking the `create_user` method from the user management
    module. It ensures that the returned token, refresh token, and expiration
    timestamp are not null, confirming the successful user creation.

    Raises
    ------
    AssertionError
        If the returned token, refresh token, or expiration timestamp is null.
    """
    info, token, refresh, expire = await user_management.create_user(
        tenant_api_key, external_id=external_id_2, meta_data={"account-type": "qa-test"}, roles=[UserRole.USER]
    )
    assert token is not None
    assert refresh is not None
    assert expire is not None


async def test_16_group_flows():
    """
    Tests group creation, user addition, entity sharing, access management, and group re-joining by
    multiple users in the system. The test mimics the lifecycle of a group and its interactions
    with external entities and users.

    Summary:
    This function is an asynchronous automated test case that validates various functionalities of
    the group management and entity sharing processes in the system. The scenarios tested include
    group creation, user additions to the group, joining the group using a join key, sharing entities
    within the group, revocation of group membership, validation of entity access permissions,
    and re-joining groups. By simulating these interactions, this test ensures the system performs
    as expected under normal usage scenarios.

    Raises
    ------
    AssertionError
        If any assertion for the test flow fails.
    WacomServiceException
        When a user tries to access unauthorized entities or perform unauthorized operations.
    """
    # Now, user 1 creates a group
    await group_management.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    # User 1 creates a group
    new_group: Group = await group_management.create_group("qa-test-group")
    assert new_group.id is not None
    assert new_group.join_key is not None
    pull_group: GroupInfo = await group_management.group(new_group.id)
    assert pull_group.id == new_group.id
    assert pull_group.name == new_group.name
    assert pull_group.join_key == new_group.join_key

    # User 2 joins the group
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    thing: ThingObject = create_thing(OntologyClassReference.parse("wacom:core#Person"))
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    thing.uri = await async_client.create_entity(thing)
    second_user_token, second_refresh_token, _ = await async_client.request_user_token(
        tenant_api_key=tenant_api_key, external_id=external_id_2
    )
    try:
        await async_client.entity(thing.uri, auth_key=second_user_token)
        raise AssertionError("User 2 should not have access to the entity.")
    except WacomServiceException as we:
        assert we.status_code == 403
    group: Optional[Group] = None
    groups: List[Group] = await group_management.listing_groups()
    for gr in groups:
        if gr.name == "qa-test-group":
            group = gr
            break
    assert group.id == new_group.id
    # Shares the join key with user 2 and user 2 joins
    await group_management.join_group(new_group.id, new_group.join_key, auth_key=second_user_token)
    groups: List[Group] = await group_management.listing_groups(auth_key=second_user_token)
    assert len(groups) == 1
    assert groups[0].id == new_group.id
    # Add user to group
    external_id_3 = str(uuid.uuid4())
    info, token, _, _ = await user_management.create_user(
        tenant_api_key, external_id=external_id_3, meta_data={"account-type": "qa-test"}, roles=[UserRole.USER]
    )
    await group_management.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    groups: List[Group] = await group_management.listing_groups()
    assert len(groups) == 1
    group: Group = groups[0]
    await group_management.add_user_to_group(group.id, info.id)
    # Adding entity to group
    await group_management.login(tenant_api_key=tenant_api_key, external_user_id=external_id_2)
    user_token, refresh_token, _ = await group_management.request_user_token(
        tenant_api_key=tenant_api_key, external_id=external_id
    )
    groups: List[Group] = await group_management.listing_groups()
    thing_uri: Optional[str] = None
    async for entity, user_token, refresh_token in async_things_iter(
        async_client, concept_type=THING_OBJECT, user_token=user_token, refresh_token=refresh_token, only_own=True
    ):
        thing_uri = entity.uri
        break
    assert thing_uri is not None
    group: Group = groups[0]
    # First user adds entity to group
    await group_management.add_entity_to_group(group.id, thing_uri, auth_key=user_token)
    entity: ThingObject = await async_client.entity(thing_uri)
    assert groups[0].id == entity.group_ids[0]
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id_2)
    await async_client.entity(thing_uri)
    user_2_id = await user_management.user_internal_id(tenant_api_key, external_id=external_id_2)
    # Now user 1 removes user 2 from the group
    await group_management.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    await group_management.remove_user_from_group(group.id, user_2_id, force=True)
    try:
        await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id_2)
        await async_client.entity(thing_uri)
        raise AssertionError("User 2 should not have access to the entity.")
    except WacomServiceException as we:
        assert isinstance(we, WacomServiceException)
        assert we.status_code == 403
    await group_management.login(tenant_api_key=tenant_api_key, external_user_id=external_id_2)
    # Now user 2 has no groups anymore
    groups: List[Group] = await group_management.listing_groups()
    assert len(groups) == 0
    # User 2 joins the group again
    await group_management.join_group(new_group.id, new_group.join_key)
    groups: List[Group] = await group_management.listing_groups()
    assert new_group.id == groups[0].id
    group_info: GroupInfo = await group_management.group(new_group.id)
    assert group_info.id == new_group.id
    assert group_info.name == new_group.name
    assert group_info.join_key is None
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id_2)
    # Now user 2 has access again
    await async_client.entity(thing_uri)
    await group_management.leave_group(new_group.id)
    try:
        await async_client.entity(thing_uri)
        raise AssertionError("User 2 should not have access to the entity.")
    except WacomServiceException as we:
        assert isinstance(we, WacomServiceException)
        assert we.status_code == 403


async def test_17_public_entity():
    """
    Test the behavior of a public entity within an asynchronous environment. The test
    validates read/write permissions and access handling for two different users under
    the same tenant servicing a specific entity.

    The function ensures:
    - Proper authentication and token issuance for users.
    - Validation of read and write access control for entities.
    - Testing restricted access based on permissions of another user in the system.
    - Verifying updates and modifications for entities based on roles and access.

    Raises
    ------
    AssertionError
        If unexpected access is granted or restricted based on specified permissions.
    WacomServiceException
        If there are permission violations such as restricted write access due to
        forbidden roles, indicated by a 403 status code.

    """
    thing: Optional[ThingObject] = None
    user_token, refresh_token, _ = await async_client.request_user_token(
        tenant_api_key=tenant_api_key, external_id=external_id
    )
    async for entity, user_token, refresh_token in async_things_iter(
        async_client, concept_type=THING_OBJECT, user_token=user_token, refresh_token=refresh_token, only_own=True
    ):
        thing = entity
        break
    assert thing is not None
    # Entities must not be empty
    thing.tenant_access_right.read = True
    await async_client.update_entity(thing, auth_key=user_token)
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id_2)
    pull_entity: ThingObject = await async_client.entity(thing.uri)
    assert pull_entity is not None
    # This must fail
    try:
        await async_client.update_entity(pull_entity)
        raise AssertionError("User 2 should not have access to the entity.")
    except WacomServiceException as we:
        assert isinstance(we, WacomServiceException)
        assert we.status_code == 403
    thing.tenant_access_right.write = True
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    await async_client.update_entity(thing)
    # Now we should have access
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id_2)
    pull_entity: ThingObject = await async_client.entity(thing.uri)
    assert pull_entity is not None
    pull_entity.add_alias("Alias", EN_US)
    await async_client.update_entity(pull_entity)


async def test_18_import_test():
    """
    Tests the process of creating, importing, and validating entities using an asynchronous client.

    The function simulates the process of creating an entity, importing multiple randomized entities linked to
    the initially created entity, monitoring the progress of the import job, retrieving the newly created entity URIs,
    validating the created entities by fetching their details and their object properties, and verifying the
    accuracy of the relations established between the entities. If the import fails, an exception is raised with
    the associated error log.

    Raises
    ------
    Exception
        If no new entity URIs are found, indicating the import has failed.
    """
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    entity: ThingObject = ThingObject(
        label=[Label(content="Test", language_code=EN_US, main=True)], concept_type=THING_OBJECT, use_for_nel=True
    )
    uri_thing: str = await async_client.create_entity(entity)
    things: List[ThingObject] = [create_random_thing(f"ref-{i}", uri_thing) for i in range(10)]
    job_id: str = await async_client.import_entities(things)
    new_uris: List[str] = []
    while True:
        job_status: JobStatus = await async_client.job_status(job_id)
        if job_status.status == JobStatus.COMPLETED:
            break
    next_page_id = None
    while True:
        resp: NewEntityUrisResponse = await async_client.import_new_uris(job_id, next_page_id=next_page_id)
        new_uris.extend(resp.new_entities_uris.values())
        if resp.next_page_id is None:
            break
        next_page_id = resp.next_page_id

    errors = await async_client.import_error_log(job_id)
    if len(new_uris) == 0:
        raise Exception(f"Import failed with errors: {errors}")
    for uri in new_uris:
        thing: ThingObject = await async_client.entity(uri)
        thing.object_properties = await async_client.relations(uri)
        assert thing is not None
        assert thing.use_for_nel
        assert LINKS in thing.object_properties
        assert thing.object_properties[LINKS].outgoing_relations[0].uri == uri_thing


async def test_19_delete_users():
    """
    Deletes users with a specific account type from the database.

    This asynchronous function retrieves a list of all users using the
    `user_management.listing_users` method for a given tenant API key. It
    then iterates through the users, identifies those whose metadata
    contains the key "account-type" with a value of "qa-test", and
    removes them using the `user_management.delete_user` method. The
    deletion is performed forcefully for such accounts.
    """
    list_user_all: List[User] = await user_management.listing_users(tenant_api_key, limit=LIMIT)
    for u_i in list_user_all:
        if "account-type" in u_i.meta_data and u_i.meta_data.get("account-type") == "qa-test":
            logging.info(f"Clean user {u_i.external_user_id}")
            await user_management.delete_user(
                tenant_api_key, external_id=u_i.external_user_id, internal_id=u_i.id, force=True
            )
