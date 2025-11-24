# -*- coding: utf-8 -*-
# Copyright © 2025-present Wacom Authors. All Rights Reserved.
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
import json
import time
import uuid
from pathlib import Path
from typing import List, Dict, Optional

import loguru
from tqdm import tqdm

from knowledge.base.ontology import ThingObject, OntologyClassReference
from knowledge.base.response import JobStatus, NewEntityUrisResponse
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.utils.diff import diff_entities
from knowledge.utils.graph import count_things_session, things_session_iter
from knowledge.utils.import_format import load_import_format

logger = loguru.logger
THING_OBJECT: OntologyClassReference = OntologyClassReference("wacom", "core", "Thing")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--input", help="Path to import file", required=True, type=Path)
    parser.add_argument(
        "-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument(
        "-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()
    things: List[ThingObject] = load_import_format(args.input)
    for thing in things:
        if thing.default_source_reference_id() is None:
            thing.reference_id = uuid.uuid4().hex
    thing_map: Dict[str, ThingObject] = {el.default_source_reference_id(): el for el in things}
    knowledge_service = WacomKnowledgeService(
        application_name="Content Importer",
        service_url=args.instance,
    )
    knowledge_service.login(args.tenant, args.user)
    total_before = count_things_session(knowledge_service, THING_OBJECT)
    t1: float = time.perf_counter()
    t2: float = t1
    job_id: str = knowledge_service.import_entities(things)
    new_uris: List[str] = []
    job_running: bool = True
    pbar = tqdm(total=len(things), desc="Importing entities", unit="entity")
    while job_running:
        job_status: JobStatus = knowledge_service.job_status(job_id)
        pbar.update(job_status.processed_entities - pbar.n)
        pbar.set_postfix(
            {
                "status": job_status.status,
                "processed_entities": job_status.processed_entities,
                "processed_relations": job_status.processed_relations,
                "processed_images": job_status.processed_images,
                "failures": job_status.failures,
                "started_at": job_status.started_at,
            }
        )
        if job_status.status == JobStatus.COMPLETED:
            t2 = time.perf_counter()
            logger.info(f"Job finished at: {job_status.finished_at.strftime('%Y-%m-%d %H:%M:%S')}")
            next_page_id: Optional[str] = None
            while True:
                error_log = knowledge_service.import_error_log(job_id, next_page_id=next_page_id)
                for error in error_log.error_log:
                    logger.warning(f"Error: {error.source_reference_id}")
                    for error_detail in error.errors:
                        logger.warning(f"  {error_detail.severity}: {error_detail.reason}")
                        logger.warning(f"  Position: {error_detail.position_offset}")
                        logger.warning(f"  Timestamp: {error_detail.timestamp}")
                if error_log.next_page_id is None:
                    break
                next_page_id = error_log.next_page_id
            next_page_id = None
            while True:
                new_uris_response: NewEntityUrisResponse = knowledge_service.import_new_uris(
                    job_id, next_page_id=next_page_id
                )
                new_uris.extend(new_uris_response.new_entities_uris)
                if new_uris_response.next_page_id is None:
                    break
                next_page_id = new_uris_response.next_page_id
            job_running = False
        time.sleep(1)
    total_after = count_things_session(knowledge_service, THING_OBJECT)
    logger.info(f"Job ID: {job_id}")
    logger.info(f"Number of entities to be imported: {len(things)}")
    logger.info(f"Total before: {total_before}")
    logger.info(f"Total after: {total_after}")
    logger.info(f"Total imported: {total_after - total_before}")
    logger.info(f"Job {job_id} completed in {t2 - t1:.2f} seconds.")
    knowledge_graph_entities: Dict[str, ThingObject] = {
        thing.default_source_reference_id(): thing for thing in things_session_iter(knowledge_service, THING_OBJECT)
    }
    for imported_thing in knowledge_graph_entities.values():
        if imported_thing.default_source_reference_id() in thing_map:
            imported_thing.object_properties = knowledge_service.relations(imported_thing.uri)
            file_thing: ThingObject = thing_map[imported_thing.default_source_reference_id()]
            diffs, diff_data_properties, diff_object_properties = diff_entities(
                knowledge_service, file_thing=file_thing, kg_thing=imported_thing, kg_things=knowledge_graph_entities
            )
            del thing_map[imported_thing.default_source_reference_id()]
            if len(diffs) > 0:
                logger.warning(f"Diff for {imported_thing.default_source_reference_id()}: has {len(diffs)} differences")

    logger.info("Not imported things:")
    for e_idx, thing in enumerate(thing_map.values()):
        try:
            knowledge_service.create_entity(thing)
        except WacomServiceException as e:
            with Path(f"{e_idx}.json").open(mode="w", encoding="utf-8") as f:
                f.write(json.dumps(thing.__import_format_dict__(), indent=4))
            logger.error(f"Error importing {thing.default_source_reference_id()}: {e}")
