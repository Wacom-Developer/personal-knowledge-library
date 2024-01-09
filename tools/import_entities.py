# -*- coding: utf-8 -*-
# Copyright © 2023-2024 Wacom. All rights reserved.
import argparse
import json
import os
import uuid
from pathlib import Path
from typing import Optional, Any, List, Dict, Tuple

import ndjson
import requests
from requests import Response
from tqdm import tqdm

from knowledge import logger, __version__
from knowledge.base.ontology import OntologyPropertyReference, ThingObject, ObjectProperty, OntologyClassReference
from knowledge.services.base import WacomServiceException, USER_AGENT_HEADER_FLAG
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.group import GroupManagementService, Group
from knowledge.services.session import PermanentSession
from knowledge.utils.graph import things_session_iter

MIME_TYPE: Dict[str, str] = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png'
}

# Core ontology
THING_OBJECT: OntologyClassReference = OntologyClassReference('wacom', 'core', 'Thing')
CONTENT: OntologyPropertyReference = OntologyPropertyReference.parse("wacom:core#content")

# So far only these locales are supported
SOURCE_ID_TAG: str = "source_reference_id"
GROUP_IDS_TAG: str = "groupIds"
TIMEOUT: int = 60  # seconds


def log_issue(error_path: Path, param: Dict[str, Any]):
    """
    Log an issue to the error file.
    Parameters
    ----------
    error_path: Path
        The path to the error file.
    param: Dict[str, Any]
        Parameters to log.
    """
    with error_path.open('a') as f_writer:
        writer = ndjson.writer(f_writer, ensure_ascii=False)
        writer.writerow(param)


def log_file(thing_path: Path, param: Dict[str, Any]):
    """
    Log thing import format to a file.

    Parameters
    ----------
    thing_path: Path
        The path to the thing file.
    param: Dict[str, Any]
        Parameters to log.
    """
    with thing_path.open('a') as f_writer:
        writer: ndjson.writer = ndjson.writer(f_writer, ensure_ascii=False)
        writer.writerow(param)


def cache_image(image_url: str, path: Path) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
    """
    Pull image from the URL and caches it to the path.

    Parameters
    ----------
    image_url: str
        URL of the image.
    path: Path
        The path to the cache folder.

    Returns
    -------
    image_bytes: Optional[bytes]
        Bytes of the image.
    mime_type: Optional[str]
        Mime type of the image.
    file_name: Optional[str]
        File name of the image.

    Raises
    ------
    WacomServiceException
        If the file extension is unknown.
    """
    with requests.session() as session:
        headers: Dict[str, str] = {
            USER_AGENT_HEADER_FLAG:
                'ImageFetcher/0.1 (https://github.com/Wacom-Developer/personal-knowledge-library)'
                f' personal-knowledge-library/{__version__}'
        }
        response: Response = session.get(image_url, headers=headers)
        if response.ok:
            index_path: Path = path / 'index.json'
            cache: Dict[str, Dict[str, str]] = {}
            if index_path.exists():
                cache = json.loads(index_path.open('r').read())
            image_bytes: bytes = response.content
            image_cache_name: str = str(uuid.uuid4())
            file_name: str = image_url
            _, file_extension = os.path.splitext(file_name.lower())
            if file_extension not in MIME_TYPE:
                raise WacomServiceException(f"Unknown file extension {file_extension}")
            mime_type = MIME_TYPE[file_extension]
            with (path / f'{image_cache_name}{file_extension}').open('wb') as fp_image:
                fp_image.write(image_bytes)
            cache[image_url] = {
                'mime-type': mime_type,
                'file': str((path / f'{image_cache_name}{file_extension}').absolute())
            }
            with index_path.open('w') as fp:
                fp.write(json.dumps(cache))
            return image_bytes, mime_type, file_name
        return None, None, None


def check_cache_image(image_url: str, path: Path) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
    """
    Check if the image is cached.
    Parameters
    ----------
    image_url: str
        URL of the image.
    path: Path
        The path to the cache folder.

    Returns
    -------
    image_bytes: Optional[bytes]
        Bytes of the image.
    mime_type: Optional[str]
        Mime type of the image.
    file_name: Optional[str]
        File name of the image.
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


def imported_uris_own(client: WacomKnowledgeService) -> Dict[str, str]:
    """
    Retrieve all the URIs of the imported objects of the user.

    Parameters
    ----------
    client: WacomKnowledgeService
        The client to use.

    Returns
    -------
    session: Dict[str, str]
        The URIs of the imported objects and the user auth key.
    """
    session: Dict[str, str] = {}
    for entity in things_session_iter(client, concept_type=THING_OBJECT, only_own=True, fetch_size=100,
                                      force_refresh_timeout=360):
        session[entity.default_source_reference_id()] = entity.uri
    return session


def main(client: WacomKnowledgeService, management: GroupManagementService, cache_file: Path, user: str,
         public: bool, group_name: Optional[str]):
    """
    Main function to import the things.
    Parameters
    ----------
    client: WacomKnowledgeService
        The client to use.
    management: GroupManagementService
        The management client to use.
    cache_file: Path
        The cache file.
    user: str
        The external id for private knowledge auth.
    public: bool
        If the things should be public.
    group_name: Optional[str]
        The group name.
    """
    cache_path_dir: Path = cache_file.parent
    error_path: Path = Path(f'{str(cache_file)}.{user}.errors')
    failed_path: Path = Path(f'{str(cache_file)}.{user}.failed.ndjson')
    image_cache: Path = cache_path_dir / 'image_cache'
    image_cache.mkdir(parents=True, exist_ok=True)
    errors: List[Dict[str, Any]] = []
    # Get all imported uris
    session: Dict[str, str] = imported_uris_own(client)

    if error_path.exists():
        with error_path.open('r', encoding='utf-8') as sf_fp:
            reader = ndjson.reader(sf_fp)
            for w in reader:
                errors.append(w)
    group: Optional[Group] = None
    if group_name:
        list_groups: List[Group] = management.listing_groups()
        for g in list_groups:
            if g.name == group_name:
                group = g
        if group is None:
            group = management.create_group(group_name)

    relations: List[Tuple[str, OntologyPropertyReference, str]] = []
    with cache_file.open(encoding="utf8") as f:
        reader = ndjson.reader(f)
        cached_entities: List[ThingObject] = [ThingObject.from_import_dict(entity) for entity in reader]
        pbar: tqdm = tqdm(cached_entities, desc='Importing entities from cache.')
        for thing in pbar:
            if public:
                thing.tenant_access_right.read = True
            if len(thing.description) == 0 or thing.description[0].content is None:
                continue
            # Check if there already exists and entity that has been imported, e.g., from Wikidata
            org_uri: str = thing.default_source_reference_id()
            if org_uri not in session:
                try:
                    wacom_uri: str = client.create_entity(thing, ignore_image=True)
                    if group:
                        management.add_entity_to_group(group.id, wacom_uri)

                    if thing.image is not None and thing.image != '':
                        image_bytes, mime_type, file_name = check_cache_image(image_url=thing.image,
                                                                              path=image_cache)
                        try:
                            if image_bytes is None:
                                image_bytes, mime_type, file_name = cache_image(thing.image, image_cache)
                            client.set_entity_image(entity_uri=wacom_uri, image_byte=image_bytes,
                                                    file_name=file_name, mime_type=mime_type)
                        except WacomServiceException as _:
                            log_issue(error_path,
                                      {'org-uri': org_uri, 'exception': "Setting image failed for entity."})
                except WacomServiceException as wse:
                    logger.error(wse)
                    log_file(failed_path, thing.__import_format_dict__())
                    log_issue(error_path, {'org-uri': org_uri, 'exception': str(wse)})
                    continue

                # Adding mapping of Wacom ID to original source.
                session[org_uri] = wacom_uri
            else:
                wacom_uri: str = session[org_uri]
            pbar.set_description_str(f'Entity with system source reference id: {org_uri} imported. '
                                     f'Imported entities #{len(session)} '
                                     f'URI:= {wacom_uri} (public:={public})')
            for relation_type, relation in thing.object_properties.items():
                for item in relation.outgoing_relations:
                    relations.append((wacom_uri, relation_type, item))
        # Finally, create the relations
        pbar: tqdm = tqdm(relations, desc='Importing relations from cache.')
        for rel in pbar:
            source: str = rel[0]
            predicate: OntologyPropertyReference = rel[1]
            target: str = session.get(rel[2])
            try:
                rels_source: Dict[OntologyPropertyReference, ObjectProperty] = client.relations(source)
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
                    client.create_relation(source, predicate, target)
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
    parser.add_argument("-g", "--group", help="Adds the entities to group.")
    parser.add_argument("-i", "--instance", default='https://stage-private-knowledge.wacom.com',
                        help="URL of instance")
    args = parser.parse_args()

    cache_path: Path = Path(args.cache)
    # Wacom personal knowledge REST API Client
    wacom_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Push Entities",
        service_url=args.instance)
    group_management: GroupManagementService = GroupManagementService(service_url=args.instance)
    permanent_session: PermanentSession = group_management.login(args.tenant, args.user)
    wacom_client.use_session(permanent_session.id)
    if cache_path.exists():
        main(wacom_client, group_management, cache_path, args.user, args.public, args.group)
