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
import time
from typing import List

from knowledge.base.language import LocaleCode, EN_US
from knowledge.base.search import LabelMatchingResponse, VectorDBDocument
from knowledge.services.search import SemanticSearchClient


def search_words(query: str, locale: LocaleCode, tenant_api_key: str, external_user_id: str, instance_url: str,
                 max_results: int):
    """
    Search for words in the knowledge graph.

    Parameters
    ----------
    query: str
        Word to search for.
    locale: str
        Locale of the word.
    tenant_api_key: str
        Tenant API key.
    external_user_id: str
        External user id.
    instance_url: str
        URL of the instance.
    max_results: int
        Maximum number of results.
    """
    client: SemanticSearchClient = SemanticSearchClient(service_url=instance_url)
    client.login(tenant_api_key, external_user_id)
    t0: float = time.time()
    results: LabelMatchingResponse = client.labels_search(query=query, locale=locale, max_results=max_results)
    t1: float = time.time()
    print(f"Results for query: {query} (locale: {locale})")
    if len(results.results) > 0:
        print("=" * 120)
        for idx, res in enumerate(results.results):
            print(f"{idx + 1}. {res.label} | Relevance: ({res.score:.2f}) | URI: {res.entity_uri}")
        all_labels: List[VectorDBDocument] = client.retrieve_labels(EN_US, results.results[0].entity_uri)
        print("=" * 120)
        print(f"Labels for best match: {results.results[0].entity_uri}")
        for idx, label in enumerate(all_labels):
            print(f"{idx + 1}. {label.content}")
    print("=" * 120)
    print(f"Time: {(t1 - t0) * 1000:.2f} ms")
    print("=" * 120)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.",
                        required=True)
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    parser.add_argument("-q", "--query", help="Query to search for.", required=True)
    parser.add_argument("-l", "--locale", help="Locale for the word index.", type=LocaleCode,
                        default=EN_US)
    parser.add_argument("-m", "--max_results", help="Maximum number of results.", type=int, required=True)
    args = parser.parse_args()
    search_words(args.query, args.locale, args.tenant, args.user, args.instance, max_results=args.max_results)
