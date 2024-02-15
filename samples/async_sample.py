# -*- coding: utf-8 -*-
# Copyright © 2024 Wacom Authors. All Rights Reserved.
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
from knowledge.public.wikidata import WikidataSearchResult, WikiDataAPIClient, WikidataThing
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
        Mapping qid to thing object
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
        wikidata_thing, _ = wikidata_to_thing(res, all_relations=relations,
                                              supported_locales=SUPPORTED_LOCALES, pull_wikipedia=True,
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
    Clean up sample.
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
        External Id of the shadow user within the Wacom Personal Knowledge.
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
    print('Token information')
    print('-' * 100)
    print(f'Refreshable: {permanent_session.refreshable}')
    print(f'Token must be refreshed before: {permanent_session.expiration} UTC')
    print(f'Token expires in {permanent_session.expires_in} seconds)')
    print('-' * 100)
    print('Creating two users')
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
