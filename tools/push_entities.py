# -*- coding: utf-8 -*-
# Copyright © 2022 Wacom. All rights reserved.
import argparse
import json
import os
import uuid
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import ndjson
import requests
from requests import Response
from tqdm import tqdm

from knowledge import logger
from knowledge.base.access import TenantAccessRight
from knowledge.base.entity import LanguageCode, OBJECT_PROPERTIES_TAG, TENANT_RIGHTS_TAG, DATA_PROPERTY_TAG, VALUE_TAG,\
    DATA_PROPERTIES_TAG, LOCALE_TAG, USE_NEL_TAG, IMAGE_TAG, URI_TAG, TYPE_TAG, OWNER_TAG, Description, \
    DESCRIPTIONS_TAG, Label, IS_MAIN_TAG, LABELS_TAG
from knowledge.base.ontology import SYSTEM_SOURCE_REFERENCE_ID, OntologyPropertyReference, ThingObject, ObjectProperty,\
    DataProperty, OntologyClassReference
from knowledge.services.base import WacomServiceException, USER_AGENT_HEADER_FLAG
from knowledge.services.graph import WacomKnowledgeService, SearchPattern
from knowledge.services.group import GroupManagementServiceAPI, Group

MIME_TYPE: Dict[str, str] = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png'
}

# So far only these locales are supported
SUPPORTED_LANGUAGES: List[str] = ['ja_JP', 'en_US', 'de_DE', 'bg_BG', 'fr_FR', 'it_IT', 'es_ES', 'ru_RU']


def log_issue(error_path: Path, param: Dict[str, Any]):
    """
    Logs the given parameter to the given error path.

    Parameters
    ----------
    error_path: Path
        Path to the error file.
    param: Dict[str, Any]
        Parameter to be logged.
    """
    with error_path.open('a') as f_writer:
        writer = ndjson.writer(f_writer, ensure_ascii=False)
        writer.writerow(param)


def cache_image(image_url: str, path: Path) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
    """
    Caches the image from the given URL to the given path.
    Parameters
    ----------
    image_url: str
        URL of the image to be cached.
    path: Path
        Path to the cache directory.

    Returns
    -------
    cache_image: Tuple[Optional[bytes], Optional[str], Optional[str]]
        Returns the image bytes, the image cache name and the file extension.
    """
    with requests.session() as session:
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG:
                'ImageFetcher/0.1 (https://github.com/Wacom-Developer/personal-knowledge-library)'
                ' personal-knowledge-library/0.2.4'
        }
        response: Response = session.get(image_url, headers=headers)
        if response.ok:
            index_path: Path = path / 'index.json'
            cache: Dict[str, Dict[str]] = {}
            if index_path.exists():
                cache = json.loads(index_path.open('r').read())
            image_bytes: bytes = response.content
            image_cache_name: str = str(uuid.uuid4())
            file_name: str = image_url
            _, file_extension = os.path.splitext(file_name.lower())
            mime_type = MIME_TYPE[file_extension]
            with (path / f'{image_cache_name}{file_extension}').open('wb') as fp:
                fp.write(image_bytes)
            cache[image_url] = {
                'mime-type': mime_type,
                'file': str((path / f'{image_cache_name}{file_extension}').absolute())
            }
            with index_path.open('w') as fp:
                fp.write(json.dumps(cache))
            return image_bytes, mime_type, file_name
        else:
            return None, None, None


def from_dict(entity: Dict[str, Any]) -> 'ThingObject':
    """
    Creates a ThingObject from the given dictionary.
    Parameters
    ----------
    entity: Dict[str, Any]
        Dictionary containing the entity data.
    Returns
    -------
    thing: ThingObject
        Instance of ThingObject.
    """
    labels: List[Label] = []
    alias: List[Label] = []
    descriptions: List[Description] = []

    for label in entity[LABELS_TAG]:
        if label[LOCALE_TAG] in SUPPORTED_LANGUAGES:
            if label[IS_MAIN_TAG]:
                labels.append(Label.create_from_dict(label))
            else:
                alias.append(Label.create_from_dict(label))

    for desc in entity[DESCRIPTIONS_TAG]:
        if desc[LOCALE_TAG] in SUPPORTED_LANGUAGES:
            descriptions.append(Description.create_from_dict(desc))

    use_nel: bool = entity.get(USE_NEL_TAG, True)

    thing: ThingObject = ThingObject(label=labels, icon=entity[IMAGE_TAG], description=descriptions,
                                     uri=entity[URI_TAG],
                                     concept_type=OntologyClassReference.parse(entity[TYPE_TAG]),
                                     owner=entity.get(OWNER_TAG, True), use_for_nel=use_nel)
    if DATA_PROPERTIES_TAG in entity:
        if isinstance(entity[DATA_PROPERTIES_TAG], dict):
            for data_property_type_str, data_properties in entity[DATA_PROPERTIES_TAG].items():
                data_property_type: OntologyPropertyReference = \
                    OntologyPropertyReference.parse(data_property_type_str)
                for data_property in data_properties:
                    language_code: LanguageCode = LanguageCode(data_property[LOCALE_TAG])
                    value: str = data_property[VALUE_TAG]
                    thing.add_data_property(DataProperty(value, data_property_type, language_code))
        elif isinstance(entity[DATA_PROPERTIES_TAG], list):
            for data_property in entity[DATA_PROPERTIES_TAG]:
                language_code: LanguageCode = LanguageCode(data_property[LOCALE_TAG])
                value: str = data_property[VALUE_TAG]
                data_property_type: OntologyPropertyReference = \
                    OntologyPropertyReference.parse(data_property[DATA_PROPERTY_TAG])
                thing.add_data_property(DataProperty(value, data_property_type, language_code))
    if OBJECT_PROPERTIES_TAG in entity:
        for object_property in entity[OBJECT_PROPERTIES_TAG].values():
            _, obj = ObjectProperty.create_from_dict(object_property)
            thing.add_relation(obj)
    thing.alias = alias
    # Finally, retrieve rights
    if TENANT_RIGHTS_TAG in entity:
        thing.tenant_access_right = TenantAccessRight.parse(entity[TENANT_RIGHTS_TAG])
    return thing


def check_cache_image(image_url: str, path: Path) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
    """
    Checks if the image is already cached and returns the image bytes, the mime type and the file name.
    Parameters
    ----------
    image_url: str
        URL of the image to be cached.
    path: Path
        Path to the cache directory.

    Returns
    -------
    cache_image: Tuple[Optional[bytes], Optional[str], Optional[str]]
        Returns the image bytes, the image cache name and the file extension.
    """
    index_path: Path = path / 'index.json'
    if index_path.exists():
        cache: Dict[str, Dict[str, str]] = json.loads(index_path.open('r').read())
        if image_url in cache:
            entry: Dict[str, str] = cache[image_url]
            with Path(entry['file']).open('rb') as fp:
                image_bytes: bytes = fp.read()
                file_name: str = image_url
                mime_type = entry['mime-type']
                return image_bytes, mime_type, file_name
    return None, None, None


def main(client: WacomKnowledgeService, management: GroupManagementServiceAPI, auth_key: str, cache_file: Path,
         user: str, public: bool, group_name: Optional[str]):
    """
    Main function of the script.
    Parameters
    ----------
    client: WacomKnowledgeService
        Instance of the WacomKnowledgeService.
    management: GroupManagementServiceAPI
        Instance of the GroupManagementServiceAPI.
    auth_key: str
        Authentication key.
    cache_file: Path
        Path to the cache file.
    user: str
        User name.
    public: bool
        If True, the things will be public.
    group_name: Optional[str]
        Name of the group to which the things will be added.
    """
    cache_path_dir: Path = cache_file.parent
    session_path: Path = Path(f'{str(cache_file)}.{user}.session')
    error_path: Path = Path(f'{str(cache_file)}.{user}.errors')
    image_cache: Path = cache_path_dir / 'image_cache'
    image_cache.mkdir(parents=True, exist_ok=True)
    session: Dict[str, str] = {}
    errors: List[Dict[str, Any]] = []
    # Check if the has been a previous session
    if session_path.exists():
        with session_path.open('r') as sf:
            reader = ndjson.reader(sf)
            for w in reader:
                session[w['uri']] = w['wacom_uri']
    if error_path.exists():
        with error_path.open('r') as sf:
            reader = ndjson.reader(sf)
            for w in reader:
                errors.append(w)
    group: Optional[Group] = None
    if group_name:
        list_groups: List[Group] = management.listing_groups(auth_key)
        for g in list_groups:
            if g.name == group_name:
                group = g
        if group is None:
            group = management.create_group(user_auth_key, group_name)

    relations: List[Tuple[str, OntologyPropertyReference, str]] = []
    with cache_file.open(encoding="utf8") as f:
        reader = ndjson.reader(f)
        pbar = tqdm(reader)
        for entity in pbar:
            thing: ThingObject = from_dict(entity)
            if public:
                thing.tenant_access_right.read = True
            if len(thing.description) == 0 or thing.description[0].content is None:
                continue
            # Check if there already exists and entity that has been imported, e.g., from Wikidata
            org_uri: str = thing.default_source_reference_id()
            if org_uri not in session:
                # search for existing entity in graph with original QID
                entities, _ = wacom_client.search_literal(auth_key, org_uri, SYSTEM_SOURCE_REFERENCE_ID,
                                                                  SearchPattern.REGEX, LanguageCode('en_US'))
                if len(entities) > 0:
                    existing_thing: ThingObject = entities[0]
                    wacom_uri: str = existing_thing.uri
                    pbar.set_description_str(f'Entity with system source reference id: {org_uri} already exists')
                else:
                    try:
                        wacom_uri: str = client.create_entity(auth_key, thing)
                        if group:
                            group_management.add_entity_to_group(user_auth_key, group.id, wacom_uri)

                        img_id: str = ''
                        if thing.image is not None and thing.image != '':
                            image_bytes, mime_type, file_name = check_cache_image(image_url=thing.image,
                                                                                  path=image_cache)
                            if image_bytes is None:
                                image_bytes, mime_type, file_name = cache_image(thing.image, image_cache)
                            img_id = client.set_entity_image(auth_key, entity_uri=wacom_uri, image_byte=image_bytes,
                                                             file_name=file_name, mime_type=mime_type)

                        pbar.set_description_str(f'Entity with system source reference id: {org_uri} imported. '
                                                 f'URI:= {wacom_uri} ImageID: {img_id} (public:={public})')
                    except WacomServiceException as wse:
                        logger.error(wse)
                        log_issue(error_path, {'org-uri': org_uri, 'exception': str(wse)})
                        continue
                # Adding mapping of Wacom ID to original source.
                session[org_uri] = wacom_uri
                with session_path.open('a') as f_writer:
                    writer = ndjson.writer(f_writer, ensure_ascii=False)
                    writer.writerow({'uri': org_uri, 'wacom_uri': wacom_uri})
            else:
                wacom_uri: str = session[org_uri]
            for relation_type, relation in thing.object_properties.items():
                for item in relation.outgoing_relations:
                    relations.append((wacom_uri, relation_type, item))
        # Finally, create the relations
        pbar = tqdm(relations)
        for rel in pbar:
            source: str = rel[0]
            predicate: OntologyPropertyReference = rel[1]
            target: str = session.get(rel[2])
            try:
                rels_source: Dict[OntologyPropertyReference, ObjectProperty] = client.relations(auth_key, source)
                if predicate in rels_source:
                    rel_source: ObjectProperty = rels_source[predicate]
                    if target in [t.uri for t in rel_source.outgoing_relations] or \
                            target in [t.uri for t in rel_source.incoming_relations]:
                        continue
            except WacomServiceException as we:
                logger.error(we)
                log_issue(error_path, {
                    'type': 'relation', 'relation': predicate.iri, 'source': source, 'target': target,
                    'exception': str(we)
                })
                continue

            if target is not None:
                try:
                    client.create_relation(auth_key, source, predicate, target)
                    pbar.set_description_str(f'Relation source:={source} predicate:= {predicate} target:= {target}')
                except WacomServiceException as exp:
                    logger.error(exp)
                    log_issue(error_path, {'type': 'relation', 'relation': predicate.iri,
                                           'source': source, 'target': target, 'exception': str(exp)})
            else:
                logger.warning(f'{rel[2]} has no mapping.')
                log_issue(error_path, {'type': 'mapping', 'class': rel[2],
                                       "exception": 'There is no mapping for the entity.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-c", "--cache", help="Path to dump ndjson file that should be imported .",
                        required=True)
    parser.add_argument("-p", "--public", action="store_true",
                        help="All entities must be push  with tenant right read.")
    parser.add_argument("-n", "--group", help="Adds the entities to group.")
    parser.add_argument("-i", "--instance", default='https://stage-private-knowledge.wacom.com',
                        help="URL of instance")
    args = parser.parse_args()

    cache_path: Path = Path(args.cache)
    # Wacom personal knowledge REST API Client
    wacom_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Push Entities",
        service_url=args.instance)
    group_management: GroupManagementServiceAPI = GroupManagementServiceAPI(service_url=args.instance)
    user_auth_key, refresh_token, expiration_time = wacom_client.request_user_token(args.tenant, args.user)
    if cache_path.exists():
        try:
            main(wacom_client, group_management, user_auth_key, cache_path, args.user, args.public, args.group)
        except Exception as e:
            logger.error(e)
            import traceback
            traceback.print_exc()
