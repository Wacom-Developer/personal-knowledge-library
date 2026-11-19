# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom Authors. All Rights Reserved.
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
"""
Exporting a tenant ontology as RDF
==================================

Saves the ontology of a tenant to an RDFS / OWL file:

1. Read the tenant's ontology contexts.
2. Optionally list the version history of the chosen context.
3. Export the ontology as RDF and write it to disk.

Unlike importing or changing an ontology, exporting needs no special role: any shadow user
may read the ontology of its tenant. The file this produces is the input format of
``ontology_alignment.py``, so exporting a tenant and aligning another one against the result
copies an ontology between tenants.

Usage
-----
>>> python ontology_export.py -t <tenant-api-key> -u <external-user-id>
>>> python ontology_export.py -t <key> -u <user> --list-versions
>>> python ontology_export.py -t <key> -u <user> -v 3 -o ontology-v3.rdf
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from knowledge.base.ontology import OntologyContext
from knowledge.services.base import WacomServiceException
from knowledge.services.ontology import OntologyService

# ------------------------------- Constants ----------------------------------------------------------------------------
LATEST_VERSION: int = 0
"""Version number the export endpoint reads as 'whatever is committed right now'."""

VERSION_TAG: str = "version"
KIND_TAG: str = "kind"
TIMESTAMP_TAG: str = "timeStamp"


def resolve_context(client: OntologyService, requested: Optional[str]) -> Optional[OntologyContext]:
    """Pick the context to export and report what else the tenant has.

    Parameters
    ----------
    client: OntologyService
        Ontology client bound to the shadow user.
    requested: Optional[str]
        Name of the wanted context, or None to use the tenant's default.

    Returns
    -------
    context: Optional[OntologyContext]
        Context to export, or None if the tenant has none or the requested one is unknown.
    """
    contexts: List[OntologyContext] = client.contexts()
    if not contexts:
        print("The tenant has no ontology context.")
        return None
    if len(contexts) > 1:
        print(f"Contexts of the tenant: {', '.join(c.context for c in contexts)}")
    if requested is None:
        # The default context is the one the service hands out without being asked.
        return client.context() or contexts[0]
    for candidate in contexts:
        if candidate.context == requested:
            return candidate
    print(f"Context '{requested}' does not exist. Available: {', '.join(c.context for c in contexts)}")
    return None


def print_versions(client: OntologyService, context: str) -> None:
    """Print the version history of a context.

    **Remark:**
    The ontology service defines no response schema for this operation, so the entries are
    plain dictionaries. Each one carries a ``body`` holding the full change as nested JSON,
    which is far too long to print; only the identifying fields are shown.

    Parameters
    ----------
    client: OntologyService
        Ontology client bound to the shadow user.
    context: str
        Name of the context.
    """
    versions: List[Dict[str, Any]] = client.versions(context)
    print("-" * 120)
    print(f" {len(versions)} version(s) of context '{context}'")
    print("-" * 120)
    print(f"  {'VERSION':<10}{'KIND':<26}TIMESTAMP")
    for entry in sorted(versions, key=lambda v: v.get(VERSION_TAG, 0)):
        version: str = str(entry.get(VERSION_TAG, "?"))
        kind: str = str(entry.get(KIND_TAG, "?"))
        timestamp: str = str(entry.get(TIMESTAMP_TAG, "?"))
        print(f"  {version:<10}{kind:<26}{timestamp}")


def main() -> int:
    """Export the ontology of a tenant as an RDF file.

    Returns
    -------
    exit_code: int
        0 if the ontology was exported, 1 otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-u", "--user", help="External Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument(
        "-t", "--tenant", help="Tenant Id of the shadow user within the Wacom Personal Knowledge.", required=True
    )
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    parser.add_argument("-c", "--context", help="Context to export. Defaults to the tenant's context.")
    parser.add_argument(
        "-v", "--version", type=int, default=LATEST_VERSION, help="Version to export. Defaults to the latest."
    )
    parser.add_argument("-o", "--output", type=Path, help="File to write. Defaults to '<context>_v<version>.rdf'.")
    parser.add_argument("-l", "--list-versions", action="store_true", help="List the versions of the context and exit.")
    args = parser.parse_args()

    client: OntologyService = OntologyService(service_url=args.instance)
    # Exporting is a read operation: the role of the shadow user does not matter.
    client.login(args.tenant, args.user)

    context: Optional[OntologyContext] = resolve_context(client, args.context)
    if context is None:
        return 1
    context_name: str = context.context
    print(f"Context '{context_name}' (base URI {context.base_uri}, committed version {context.version})")

    if args.list_versions:
        print_versions(client, context_name)
        return 0

    # Version 0 asks the service for the latest, which is the version the context reports.
    exported_version: int = args.version if args.version > LATEST_VERSION else context.version
    output: Path = args.output or Path(f"{context_name}_v{exported_version}.rdf")
    # An explicit -o is taken as permission to overwrite; the generated name is not.
    if args.output is None and output.exists():
        print(f"'{output}' already exists. Pass -o to choose a different file.")
        return 1

    try:
        rdf: str = client.rdf_export(context_name, version=args.version)
    except WacomServiceException as exception:
        print(
            f"Exporting version {args.version} failed [status:={exception.status_code}]: {exception.service_response}"
        )
        return 1

    output.write_text(rdf, encoding="utf-8")
    print(f"Version {exported_version} of '{context_name}' written to '{output}' ({output.stat().st_size} bytes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
