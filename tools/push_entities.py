# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

import ndjson
from tqdm import tqdm

from knowledge import logger
from knowledge.base.entity import LanguageCode
from knowledge.base.ontology import SYSTEM_SOURCE_REFERENCE_ID, OntologyPropertyReference, ThingObject, ObjectProperty
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService, SearchPattern


def main(client: WacomKnowledgeService, auth_key: str, cache_file: Path, user: str, public: bool):
    session_path: Path = Path(f'{str(cache_file)}.{user}.session')
    session: Dict[str, str] = {}
    if session_path.exists():
        with session_path.open('r') as sf:
            reader = ndjson.reader(sf)
            for w in reader:
                session[w['uri']] = w['wacom_uri']

    relations: List[Tuple[str, OntologyPropertyReference, str]] = []
    with cache_file.open() as f:
        reader = ndjson.reader(f)
        pbar = tqdm(reader)
        for entity in pbar:
            thing: ThingObject = ThingObject.from_dict(entity)
            if public:
                thing.tenant_access_right.read = True
            if thing.description[0].content is None:
                continue
            # Check if there already exists and entity that has been imported, e.g., from Wikidata
            org_uri: str = thing.default_source_reference_id()
            if org_uri not in session:
                # search for existing entity in graph with original QID
                entities, next_page = wacom_client.search_literal(auth_key, org_uri, SYSTEM_SOURCE_REFERENCE_ID,
                                                                  SearchPattern.REGEX, LanguageCode('en_US'))
                if len(entities) > 0:
                    existing_thing: ThingObject = entities[0]
                    wacom_uri: str = existing_thing.uri
                    pbar.set_description_str(f'Entity with system source reference id: {org_uri} already exists')
                else:
                    try:
                        wacom_uri: str = client.create_entity(auth_key, thing)
                        img_id: str = ''
                        if thing.image is not None and thing.image != '':
                            img_id = client.set_entity_image_url(auth_key, entity_uri=wacom_uri, image_url=thing.image)
                        pbar.set_description_str(f'Entity with system source reference id: {org_uri} imported. '
                                                 f'URI:= {wacom_uri} ImageID: {img_id} (public:={public})')
                    except WacomServiceException as wse:
                        logger.error(wse)
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
        pbar = tqdm(relations)
        for rel in pbar:
            source: str = rel[0]
            predicate: OntologyPropertyReference = rel[1]
            target: str = session.get(rel[2])
            try:
                rels_source: Dict[OntologyPropertyReference, ObjectProperty] = client.relations(auth_key, source)
                if predicate in rels_source:
                    rel_source: ObjectProperty = rels_source[predicate]
                    if target in rel_source.outgoing_relations or target in rel_source.incoming_relations:
                        continue
            except WacomServiceException as we:
                logger.error(we)
                continue

            if target is not None:
                try:
                    client.create_relation(auth_key, source, predicate, target)
                    pbar.set_description_str(f'Relation source:={source} predicate:= {predicate} target:= {target}')
                except WacomServiceException as exp:
                    logger.error(exp)
            else:
                logger.warning(f'{rel[2]} has no mapping.')
    # If successful remove the session file
    session_path.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--cache", help="Path to dump ndjson file that should be imported .",
                        required=True)
    parser.add_argument("-p", "--public", action="store_true",
                        help="All entities must be push  with tenant right read.")
    args = parser.parse_args()

    cache_path: Path = Path(args.cache)
    # Wacom personal knowledge REST API Client
    wacom_client: WacomKnowledgeService = WacomKnowledgeService(
        application_name="Push Entities",
        service_url='https://private-knowledge.wacom.com')
    user_auth_key: str = wacom_client.request_user_token(args.tenant, args.user)

    if cache_path.exists():
        try:
            main(wacom_client, user_auth_key, cache_path, args.user, args.public)
        except Exception as e:
            logger.error(e)
            import traceback
            traceback.print_exc()
