# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
import argparse
from pathlib import Path
from typing import Dict, List

import ndjson
from tqdm import tqdm

from knowledge import logger
from knowledge.base.ontology import ThingObject
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService


def main(client: WacomKnowledgeService, auth_key: str, cache_file: Path, public: bool):
    bulk_entities: List[ThingObject] = []
    with cache_file.open() as f:
        reader = ndjson.reader(f)
        for entity in reader:
            thing: ThingObject = ThingObject.from_dict(entity)
            if public:
                thing.tenant_access_right.read = True
            if thing.description[0].content is None:
                continue
            bulk_entities.append(thing)
        # Bulk create
        bulk_entities = client.create_entity_bulk(auth_key, bulk_entities)
        mapping: Dict[str, str] = dict([(t.default_source_reference_id(), t.uri) for t in bulk_entities])
        pbar = tqdm(bulk_entities)
        for thing in pbar:
            for relation_type, relation in thing.object_properties.items():
                for item in relation.outgoing_relations:
                    if item in mapping:
                        try:
                            client.create_relation(auth_key, thing.uri, relation_type, mapping[item])
                            pbar.set_description_str(f'Relation source:={thing.uri} '
                                                     f'predicate:={relation_type} target:= {mapping[item]}')
                        except WacomServiceException as exp:
                            logger.error(exp)


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
            main(wacom_client, user_auth_key, cache_path, args.public)
        except Exception as e:
            logger.error(e)
            import traceback
            traceback.print_exc()
