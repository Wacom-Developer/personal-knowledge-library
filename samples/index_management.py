# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom Authors. All Rights Reserved.
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

from knowledge.base.index import HealthResponse, IndexDocument, IndexMode
from knowledge.base.language import EN_US
from knowledge.services.index_management import IndexManagementClient

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

    client: IndexManagementClient = IndexManagementClient(service_url=args.instance)
    # Only TenantAdmin users can manage the index
    client.login(args.tenant, args.user)

    index_mode: IndexMode = "document"

    # -----------------------------------------------------------------------
    # Index health
    # -----------------------------------------------------------------------
    print("Index Health")
    print("=" * 120)
    health: HealthResponse = client.index_health(index_mode=index_mode, locale=EN_US)
    print(f"  Healthy: {health.healthy}")
    print(f"  Cluster status:  {health.condition.cluster.status} | Nodes: {health.condition.cluster.number_of_nodes}")
    print(f"  Index status:    {health.condition.index.status}")
    print(f"  Shards ({len(health.condition.shards)}):")
    for shard in health.condition.shards:
        print(
            f"    - [{shard.shard_id}] state: {shard.shard_state} | docs: {shard.num_docs} | size: {shard.store_size}"
        )
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Refresh index
    # -----------------------------------------------------------------------
    print("Refreshing index ...")
    client.refresh_index(index_mode=index_mode, locale=EN_US)
    print("  Index refreshed successfully.")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Stream documents from the index
    # -----------------------------------------------------------------------
    print(f"Streaming documents  [index_mode:={index_mode}, locale:={EN_US}]")
    print("=" * 120)
    doc_count: int = 0
    first_doc_id: str = ""
    for doc in client.iterate_documents(index_mode=index_mode, locale=EN_US):
        doc: IndexDocument
        if doc_count == 0:
            first_doc_id = doc.id
            print(f"  First document ID : {doc.id}")
            print(f"  Content URI       : {doc.content_uri}")
            print(f"  Locale            : {doc.meta.locale}")
            print(f"  Created           : {doc.meta.creation}")
            print(f"  Chunk index       : {doc.meta.chunk_index}")
            print(f"  Content preview   : {doc.content[:120].strip()}...")
            print("-" * 120)
        doc_count += 1
    print(f"  Total documents streamed: {doc_count}")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Delete a document by ID (only if at least one document was found)
    # -----------------------------------------------------------------------
    if first_doc_id:
        print(f"Deleting document  [id:={first_doc_id}]")
        print("=" * 120)
        client.delete_document_by_id(index_mode=index_mode, locale=EN_US, document_ids=[first_doc_id])
        print(f"  Document {first_doc_id!r} deleted successfully.")
        print("=" * 120)

    # -----------------------------------------------------------------------
    # Force-merge index (optimise storage after deletion)
    # -----------------------------------------------------------------------
    print("Force-merging index ...")
    client.force_merge_index(index_mode=index_mode, locale=EN_US)
    print("  Index force-merged successfully.")
    print("=" * 120)
