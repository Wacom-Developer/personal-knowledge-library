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

from knowledge.services.tenant import TenantManagementServiceAPI

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--token", help="Tenant API token.", required=True)
    parser.add_argument("-i", "--instance", default="https://private-knowledge.wacom.com", help="URL of instance")
    args = parser.parse_args()
    tenant_manager: TenantManagementServiceAPI = TenantManagementServiceAPI(
        tenant_token=args.token, service_url=args.instance
    )

    print("Tenants")
    print("=" * 120)
    # List all tenants
    for tidx, tenant in enumerate(tenant_manager.listing_tenant()):
        if tidx > 0:
            print("-" * 120)
        print(f"{tidx}. Identifier: {tenant.identifier}, name: {tenant.name}")
        print("   - Ontology Name: {tenant.ontology_name}, version: {tenant.ontology_version}")
        print("   - Locked: {tenant.is_locked}")
        print("   - Rights: ")
        for r in tenant.rights:
            print(f"      ◦ {r} ")
        print("   - Vector Search metadata (data properties):")
        for dp in tenant.vector_search_data_properties:
            print(f"      ◦ {dp} ")
        print("   - Vector Search metadata (object properties):")
        for op in tenant.vector_search_object_properties:
            print(f"      ◦ {op} ")
        print(f"   - Content data-property: {tenant.content_data_property_name}")
    print("=" * 120)
