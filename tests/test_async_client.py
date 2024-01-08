# -*- coding: utf-8 -*-
# Copyright © 2024 Wacom. All rights reserved.
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from faker import Faker

from knowledge.base.entity import Label
from knowledge.base.language import JA_JP, EN_US, DE_DE, BG_BG, FR_FR, IT_IT, ES_ES
from knowledge.base.ontology import ThingObject, OntologyClassReference, OntologyPropertyReference, DataProperty, \
    ObjectProperty, LAST_UPDATE_DATE, SYSTEM_SOURCE_REFERENCE_ID
from knowledge.ontomapping import IS_RELATED
from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
from knowledge.services.asyncio.group import AsyncGroupManagementServiceAPI
from knowledge.services.asyncio.users import AsyncUserManagementService
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import Visibility, SearchPattern
from knowledge.services.group import Group
from knowledge.services.users import User, UserRole
from knowledge.utils.graph import async_things_iter, async_count_things

THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')
LEONARDO_DA_VINCI: str = 'Leonardo da Vinci'
MONA_LISA: str = 'Mona Lisa'
FIRST_NAME: str = 'Leonardo'
LAST_NAME: str = 'da Vinci'
LEONARDO_QID: str = "Q762"
dummy_image: Path = Path(__file__).parent / '..' / 'assets' / 'dummy.png'
tenant_api_key: str = os.environ.get('TENANT_API_KEY')
# Create an external user id
external_id: str = str(uuid.uuid4())
external_id_2: str = str(uuid.uuid4())
LIMIT: int = 10000
HAS_ART_STYLE: OntologyPropertyReference = OntologyPropertyReference.parse('wacom:creative#hasArtstyle')


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
            thing.add_data_property(DataProperty(names[0],  OntologyPropertyReference.parse('wacom:core#firstName'),
                                                 language_code=lang_inst))
            thing.add_data_property(DataProperty(names[1],  OntologyPropertyReference.parse('wacom:core#lastName'),
                                                 language_code=lang_inst))
        elif len(names) == 3:
            thing.add_data_property(DataProperty(names[1],  OntologyPropertyReference.parse('wacom:core#firstName'),
                                                 language_code=lang_inst))
            thing.add_data_property(DataProperty(names[2],  OntologyPropertyReference.parse('wacom:core#lastName'),
                                                 language_code=lang_inst))
    return thing


def create_faulty_thing() -> ThingObject:
    """
    Create a faulty thing object with random data.
    Returns
    -------
    instance: ThingObject
        Thing object wrong.
    """
    thing: ThingObject = ThingObject(concept_type=OntologyClassReference.parse('wacom:core#NOT_EXISTING'))
    thing.add_label('Test', EN_US)
    return thing


# ----------------------------------------------------------------------------------------------------------------------
instance: str = os.environ.get('INSTANCE')
async_client: AsyncWacomKnowledgeService = AsyncWacomKnowledgeService(application_name="Async client test",
                                                                      service_url=instance,
                                                                      service_endpoint="graph/v1")
group_management: AsyncGroupManagementServiceAPI = AsyncGroupManagementServiceAPI(application_name="Async client test",
                                                                                  service_url=instance,
                                                                                  service_endpoint="graph/v1")
user_management: AsyncUserManagementService = AsyncUserManagementService(application_name="Async client test",
                                                                         service_url=instance,
                                                                         service_endpoint="graph/v1")
# ----------------------------------------------------------------------------------------------------------------------


async def test_01_handle_user():
    """Create user."""
    global tenant_api_key, external_id
    users: List[User] = await user_management.listing_users(tenant_api_key, limit=LIMIT)
    for user in users:
        if user.external_user_id == external_id:
            raise AssertionError('User already exists')
    # Create user
    _, token, refresh, expire = await user_management.create_user(tenant_api_key,
                                                                  external_id=external_id,
                                                                  meta_data={'account-type': 'qa-test'},
                                                                  roles=[UserRole.USER])
    assert token is not None
    assert refresh is not None
    assert expire is not None
    users: List[User] = await user_management.listing_users(tenant_api_key, limit=LIMIT)
    if external_id not in [u.external_user_id for u in users]:
        raise AssertionError('User not created')
    new_user: Optional[User] = None
    for user in users:
        if user.external_user_id == external_id:
            new_user = user

    # Update user
    await user_management.update_user(tenant_api_key, internal_id=new_user.id, external_id=new_user.external_user_id,
                                      meta_data={'account-type': 'qa-test', "updated": True})
    users: List[User] = await user_management.listing_users(tenant_api_key, limit=LIMIT)
    for u in users:
        if u.external_user_id == external_id:
            assert u.meta_data.get('updated') == 'true'


async def test_02_push_entity():
    """Push entity."""
    global tenant_api_key, external_id, dummy_image
    thing: ThingObject = create_thing(OntologyClassReference.parse('wacom:core#Person'))
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    thing_uri: str = await async_client.create_entity(thing)
    assert thing_uri is not None
    new_thing: ThingObject = await async_client.entity(thing_uri)
    assert new_thing is not None
    assert new_thing.concept_type == OntologyClassReference.parse('wacom:core#Person')
    assert new_thing.image is None
    await async_client.set_entity_image_local(thing_uri, dummy_image)
    new_image_thing: ThingObject = await async_client.entity(thing_uri)
    assert new_image_thing is not None
    image_url: str = new_image_thing.image
    await async_client.set_entity_image_url(thing_uri, image_url, mime_type='image/png')
    wrong_thing: ThingObject = create_faulty_thing()
    try:
        await async_client.create_entity(wrong_thing)
        raise AssertionError('Exception not raised')
    except WacomServiceException as e:
        assert e.status_code == 400
        assert e.url == async_client.service_base_url + AsyncWacomKnowledgeService.ENTITY_ENDPOINT
        assert isinstance(e, WacomServiceException)


async def test_03_get_entity():
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    """Get entity."""
    count: int = await async_count_things(async_client, user_token, THING_OBJECT, visibility=Visibility.PRIVATE)
    # This user only created one entity
    assert count == 1
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(async_client, user_token, refresh_token,
                                                                    THING_OBJECT, only_own=True):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        # This user only created one entity
        assert full_entity.concept_type == OntologyClassReference.parse('wacom:core#Person')
        # Entity must not be empty
        assert full_entity is not None


async def test_04_update_entity():
    """Update entity. """
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(async_client, user_token, refresh_token,
                                                                    THING_OBJECT, only_own=True):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        # Entity must not be empty
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
    """Pull literals from the entity."""
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(async_client, user_token, refresh_token,
                                                                    THING_OBJECT, only_own=True):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        # Entity must not be empty
        assert full_entity is not None
        literals: List[DataProperty] = await async_client.literals(full_entity.uri, auth_key=user_token)
        assert len(literals) > 0
        try:
            await async_client.literals(uuid.uuid4().hex, auth_key=user_token)
            raise AssertionError('Exception not raised')
        except WacomServiceException as e:
            assert e.status_code == 404
            assert isinstance(e, WacomServiceException)


async def test_06_labels_entity():
    """Pull labels from the entity."""
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(async_client, user_token, refresh_token,
                                                                    THING_OBJECT, only_own=True):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        # Entity must not be empty
        assert full_entity is not None
        labels: List[Label] = await async_client.labels(full_entity.uri, auth_key=user_token)
        assert len(labels) > 0
        try:
            await async_client.labels(uuid.uuid4().hex, auth_key=user_token)
            raise AssertionError('Exception not raised')
        except WacomServiceException as e:
            assert e.status_code == 404
            assert isinstance(e, WacomServiceException)


async def test_07_relations_entity():
    """Pull relations from the entity."""
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(async_client, user_token, refresh_token,
                                                                    THING_OBJECT, only_own=True):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        # Entity must not be empty
        assert full_entity is not None
        # Pull relations if configured
        relations: Dict[OntologyPropertyReference, ObjectProperty] = await async_client.relations(uri=full_entity.uri,
                                                                                                  auth_key=user_token)
        # Assert relations are
        assert len(relations) == 0
        await async_client.create_relation(full_entity.uri, IS_RELATED, full_entity.uri, auth_key=user_token)
        # Pull relations if configured
        relations: Dict[OntologyPropertyReference, ObjectProperty] = await async_client.relations(uri=full_entity.uri,
                                                                                                  auth_key=user_token)
        # Assert relations are
        assert len(relations) == 1


async def test_08_delete_entity():
    """Delete the entity."""
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    user_token, refresh_token = await async_client.handle_token()
    # Test async iterator
    async for thing, user_token, refresh_token in async_things_iter(async_client, user_token, refresh_token,
                                                                    THING_OBJECT, only_own=True):
        full_entity: ThingObject = await async_client.entity(thing.uri)
        await async_client.delete_entity(full_entity.uri, force=True, auth_key=user_token)


async def test_09_search_labels():
    """Search for labels."""
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    res_entities, next_search_page = await async_client.search_labels(search_term=LEONARDO_DA_VINCI,
                                                                      language_code=EN_US,
                                                                      limit=10)
    assert len(res_entities) > 1
    res_entities, next_search_page = await async_client.search_labels(search_term=LEONARDO_DA_VINCI,
                                                                      language_code=EN_US,
                                                                      exact_match=True,
                                                                      limit=10)
    assert len(res_entities) >= 1


async def test_10_search_description():
    """Test the search for descriptions."""
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    res_entities, next_search_page = await async_client.search_description('Michelangelo\'s Sistine Chapel',
                                                                           EN_US, limit=10)

    assert len(res_entities) >= 1


async def test_11_search_relations():
    """Test the search for relations."""
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    art_style: Optional[ThingObject] = None
    results, _ = await async_client.search_labels("portrait", EN_US, limit=1)
    for entity in results:
        art_style = entity
    assert art_style is not None
    res_entities, next_search_page = await async_client.search_relation(relation=HAS_ART_STYLE,
                                                                        object_uri=art_style.uri, language_code=EN_US)

    assert len(res_entities) >= 1
    for entity in res_entities:
        results, _ = await async_client.search_relation(subject_uri=entity.uri, relation=HAS_ART_STYLE,
                                                        language_code=EN_US)
        assert len(results) >= 1

    try:
        # Only one parameter is allowed: either subject_uri or object_uri
        r, _ = await async_client.search_relation(subject_uri=art_style.uri, relation=HAS_ART_STYLE,
                                                  object_uri=art_style.uri, language_code=EN_US)
        raise AssertionError('Exception not raised')
    except WacomServiceException as e:
        assert e.message == 'Only one parameter is allowed: either subject_uri or object_uri!'
        assert isinstance(e, WacomServiceException)
    try:
        # at least one parameter is allowed: either subject_uri or object_uri
        r, _ = await async_client.search_relation(subject_uri=None, relation=HAS_ART_STYLE,
                                                  object_uri=None, language_code=EN_US)
        raise AssertionError('Exception not raised')
    except WacomServiceException as e:
        assert e.message == 'At least one parameters is must be defined: either subject_uri or object_uri!'
        assert isinstance(e, WacomServiceException)


async def test_12_search_literals():
    """Test the search for literals."""
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    res_entities, next_search_page = await async_client.search_literal(search_term=LEONARDO_QID,
                                                                       pattern=SearchPattern.REGEX,
                                                                       literal=SYSTEM_SOURCE_REFERENCE_ID,
                                                                       language_code=EN_US)

    assert len(res_entities) >= 1


async def test_13_named_entity_linking():
    """Test the search for literals."""
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    leo: Optional[ThingObject] = None
    search_results, _ = await async_client.search_labels(LEONARDO_DA_VINCI, EN_US, limit=1)
    for entity in search_results:
        leo = entity
        break
    assert leo is not None
    for label_lang in leo.label:
        res_entities = await async_client.link_personal_entities(text=label_lang.content,
                                                                 language_code=label_lang.language_code)
        assert len(res_entities) >= 1


async def test_14_activations():
    """Test activations."""
    global tenant_api_key, external_id
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
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
    """ Create users."""
    global tenant_api_key, external_id, external_id_2

    info, token, refresh, expire = await user_management.create_user(tenant_api_key,
                                                                     external_id=external_id_2,
                                                                     meta_data={'account-type': 'qa-test'},
                                                                     roles=[UserRole.USER])
    assert token is not None
    assert refresh is not None
    assert expire is not None


async def test_16_group_flows():
    """ Create group."""
    # Now, user 1 creates a group
    global tenant_api_key, external_id, external_id_2
    await group_management.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    # User 1 creates a group
    new_group: Group = await group_management.create_group("qa-test-group")
    # User 2 joins the group
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    thing: ThingObject = create_thing(OntologyClassReference.parse('wacom:core#Person'))
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    thing.uri = await async_client.create_entity(thing)
    second_user_token, second_refresh_token, _ = await async_client.request_user_token(tenant_api_key=tenant_api_key,
                                                                                       external_id=external_id_2)
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
    info, token, _, _ = await user_management.create_user(tenant_api_key, external_id=external_id_3,
                                                          meta_data={'account-type': 'qa-test'},
                                                          roles=[UserRole.USER])
    await group_management.login(tenant_api_key=tenant_api_key, external_user_id=external_id)
    groups: List[Group] = await group_management.listing_groups()
    assert len(groups) == 1
    group: Group = groups[0]
    await group_management.add_user_to_group(group.id, info.id)
    # Adding entity to group
    await group_management.login(tenant_api_key=tenant_api_key, external_user_id=external_id_2)
    user_token, refresh_token, _ = await group_management.request_user_token(tenant_api_key=tenant_api_key,
                                                                             external_id=external_id)
    groups: List[Group] = await group_management.listing_groups()
    thing_uri: Optional[str] = None
    async for entity, user_token, refresh_token in async_things_iter(async_client, concept_type=THING_OBJECT,
                                                                     user_token=user_token,
                                                                     refresh_token=refresh_token,
                                                                     only_own=True):
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
    await async_client.login(tenant_api_key=tenant_api_key, external_user_id=external_id_2)
    # Now user 2 has access again
    await async_client.entity(thing_uri)


async def test_17_public_entity():
    """ Public entity."""
    global tenant_api_key, external_id, external_id_2
    thing: Optional[ThingObject] = None
    user_token, refresh_token, _ = await async_client.request_user_token(tenant_api_key=tenant_api_key,
                                                                         external_id=external_id)
    async for entity, user_token, refresh_token in async_things_iter(async_client, concept_type=THING_OBJECT,
                                                                     user_token=user_token,
                                                                     refresh_token=refresh_token,
                                                                     only_own=True):
        thing = entity
        break
    assert thing is not None
    # Entity must not be empty
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


async def test_18_delete_users():
    """Clean up the test environment."""
    list_user_all: List[User] = await user_management.listing_users(tenant_api_key, limit=LIMIT)
    for u_i in list_user_all:
        if 'account-type' in u_i.meta_data and u_i.meta_data.get('account-type') == 'qa-test':
            logging.info(f'Clean user {u_i.external_user_id}')
            await user_management.delete_user(tenant_api_key, external_id=u_i.external_user_id, internal_id=u_i.id,
                                              force=True)
