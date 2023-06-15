# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
import argparse
from typing import List

from knowledge.public.wikidata import WikiDataAPIClient, WikidataSearchResult

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--term", help="Search term.")
    parser.add_argument("-l", "--language", help="Language code", type=str)
    args = parser.parse_args()
    qid_references: List[str] = []
    print("---------------------------------------------------------------------------------------------------")
    print(f"Search term: {args.term}@{args.language}")
    print("---------------------------------------------------------------------------------------------------")
    search_results: List[WikidataSearchResult] = WikiDataAPIClient.search_term(args.term, args.language)
    if len(search_results) > 0:
        for sr in search_results:
            print(sr)
            qid_references.append(sr.qid)
        print("---------------------------------------------------------------------------------------------------")
        print(f"Retrieving entities for {len(qid_references)} QIDs.")
        print("---------------------------------------------------------------------------------------------------")
        for idx, wikidata_entity in enumerate(WikiDataAPIClient.retrieve_entities(qid_references)):
            print(f"{idx + 1}. : QID:={wikidata_entity.qid}")
            print("[Labels]:")
            for lo, la in wikidata_entity.label.items():
                print(f" - {la}")