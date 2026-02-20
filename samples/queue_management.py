# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom Authors. All Rights Reserved.
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
from typing import List

from knowledge.base.queue import QueueCount, QueueMonitor, QueueNames
from knowledge.services.queue_management import QueueManagementClient

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

    client: QueueManagementClient = QueueManagementClient(service_url=args.instance)
    # Only TenantAdmin users can view the queue information
    client.login(args.tenant, args.user)

    # -----------------------------------------------------------------------
    # List all queue names
    # -----------------------------------------------------------------------
    print("Queue Names")
    print("=" * 120)
    queue_names: QueueNames = client.list_queue_names()
    for idx, name in enumerate(queue_names.names):
        print(f"  {idx + 1}. {name}")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # List all queues with monitoring information
    # -----------------------------------------------------------------------
    print("All Queues")
    print("=" * 120)
    queues: List[QueueMonitor] = client.list_queues()
    for idx, queue in enumerate(queues):
        if idx > 0:
            print("-" * 120)
        print(f"  {idx + 1}. Name: {queue.name} | State: {queue.state} | VHost: {queue.vhost}")
        print(
            f"     Messages total: {queue.messages} | Ready: {queue.messages_ready} "
            f"| Unacknowledged: {queue.messages_unacknowledged}"
        )
        print(f"     Consumers: {queue.consumers} | Memory: {queue.memory} bytes")
        if queue.message_stats:
            stats = queue.message_stats
            print(f"     Message stats: publish={stats.publish} | deliver={stats.deliver} | ack={stats.ack}")
    print("=" * 120)

    # -----------------------------------------------------------------------
    # Per-queue details for each known queue
    # -----------------------------------------------------------------------
    for queue_name in queue_names.names:
        print(f"Queue details  [name:={queue_name!r}]")
        print("=" * 120)

        is_empty: bool = client.queue_is_empty(queue_name)
        print(f"  Is empty: {is_empty}")

        size: QueueCount = client.queue_size(queue_name)
        print(f"  Size    : {size.count} messages")

        monitor: QueueMonitor = client.queue_monitor_information(queue_name)
        print(f"  State   : {monitor.state}")
        print(f"  Ready   : {monitor.messages_ready} | Unacknowledged: {monitor.messages_unacknowledged}")
        print("=" * 120)
