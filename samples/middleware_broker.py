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
"""Serving tens of thousands of PKS users from one backend process.

The pattern this sample shows
-----------------------------
A middleware serving many end users must not log in once per request, and must not create a service client per user.
:class:`AsyncTokenBroker` hands out a bare access token for an external user id, cached and refreshed behind the
scenes. The token is passed to any service method through the per-method ``auth_key=`` override, so a *single*
:class:`AsyncWacomKnowledgeService` is created once and shared by the whole process: no ``login()``, no
``use_session()``, and nothing mutable per request.

When to use the broker, and when not to
---------------------------------------
* Per-user work (reads and writes on behalf of an end user): use the broker. Entity ownership follows the token that
  created the entity, so writes need per-user tokens.
* A read-only sweep over all entities: do not use the broker at all. A ``TenantAdmin`` token bypasses the per-user
  visibility filter in the PKS backend, so one token replaces tens of thousands. If you do sweep per user, pass
  ``paced=True`` to ``token_for`` together with the ``rate_limit=`` constructor argument (``--rate-limit`` in this
  driver): every user in a sweep is a cold miss by definition, and only the limiter can flatten that burst of logins.

Warning: this driver creates shadow users
-----------------------------------------
Every simulated user is logged in, which creates a real shadow user (``middleware-sample-user-N``) in the tenant of
the API key, on whichever instance ``--instance`` points at. The default is the stage instance. Do not point it at a
production tenant unless you want ``--users`` new users there.

ASGI lifespan wiring (documentation, not executed)
--------------------------------------------------
The library has no web-framework dependency, and the pattern is the same under FastAPI, Starlette or any other ASGI
framework. Build the broker and the shared service client at startup and close them at shutdown. Ownership is split:
the broker closes only what it created itself (its aiohttp client); the Redis client is yours, so you close it.

.. code-block:: python

    from contextlib import asynccontextmanager

    import redis.asyncio
    from fastapi import FastAPI, Request

    from knowledge.base.ontology import OntologyClassReference
    from knowledge.services.asyncio.broker import AsyncTokenBroker
    from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
    from knowledge.services.cache.crypto import AesGcmCipher
    from knowledge.services.cache.memory import AsyncInMemoryTokenStore
    from knowledge.services.cache.redis import AsyncRedisLock, AsyncRedisTokenStore
    from knowledge.services.cache.tiered import AsyncTieredTokenStore

    THING_OBJECT = OntologyClassReference("wacom", "core", "Thing")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # --- startup: one broker and one service client per process, built from your configuration ------------
        redis_client = redis.asyncio.Redis.from_url(settings.redis_url, decode_responses=False)  # binary client!
        app.state.knowledge_client = AsyncWacomKnowledgeService(settings.pks_instance, "my-middleware")
        app.state.broker = AsyncTokenBroker(
            settings.pks_instance,
            settings.tenant_api_key,
            store=AsyncTieredTokenStore(l1=AsyncInMemoryTokenStore(), l2=AsyncRedisTokenStore(redis_client)),
            lock=AsyncRedisLock(redis_client),
            cipher=AesGcmCipher("2026-01", settings.token_cache_key),  # 32 bytes, from your secret store
            rate_limit=settings.sweep_logins_per_second,
        )
        try:
            yield
        finally:
            # --- shutdown: the broker closes its own aiohttp client; the Redis client and the service client
            # are yours to close ---------------------------------------------------------------------------
            await app.state.broker.aclose()
            await redis_client.aclose()
            await app.state.knowledge_client.close()

    app = FastAPI(lifespan=lifespan)

    @app.get("/things")
    async def things(request: Request, user: str):
        token = await get_token(request.app.state.broker, user)  # defined below
        found, _, _ = await request.app.state.knowledge_client.listing(THING_OBJECT, limit=10, auth_key=token)
        return [thing.uri for thing in found]

Run the driver below with::

    python samples/middleware_broker.py --tenant-api-key <key> --users 200 --concurrency 20
    python samples/middleware_broker.py --tenant-api-key <key> --redis-url redis://localhost:6379/0
"""

import argparse
import asyncio
import dataclasses
import os
import sys
import time
from typing import Any, List, Optional, Tuple

import aiohttp

from knowledge import logger
from knowledge.base.ontology import OntologyClassReference
from knowledge.services.asyncio.broker import AsyncTokenBroker
from knowledge.services.asyncio.graph import AsyncWacomKnowledgeService
from knowledge.services.base import WacomServiceException
from knowledge.services.cache.base import BrokerStats
from knowledge.services.cache.memory import AsyncInMemoryTokenStore

THING_OBJECT: OntologyClassReference = OntologyClassReference("wacom", "core", "Thing")
DEFAULT_INSTANCE: str = "https://stage-private-knowledge.wacom.com"
APPLICATION_NAME: str = "middleware-broker-sample"


async def get_token(broker: AsyncTokenBroker, external_user_id: str, *, paced: bool = False) -> str:
    """Return a PKS access token for a user: the integration seam a request handler calls.

    Served from the cache in steady state; a login or refresh happens at most once per user per token lifetime.

    Parameters
    ----------
    broker: AsyncTokenBroker
        The process-wide broker, built once at startup.
    external_user_id: str
        External user id of the end user the request is made for.
    paced: bool
        Queue behind the broker's rate limiter. Use for sweeps and other bulk work, not for interactive requests.

    Returns
    -------
    token: str
        Access token, to be passed to a service method as ``auth_key``.
    """
    return await broker.token_for(external_user_id, paced=paced)


def build_broker(
    instance: str, tenant_api_key: str, redis_url: Optional[str], rate_limit: Optional[float]
) -> Tuple[AsyncTokenBroker, Optional[Any]]:
    """Build the broker, with a Redis-backed shared store if a URL is given, else a process-local one.

    Returns
    -------
    broker: AsyncTokenBroker
        The broker. It closes only its own aiohttp client.
    redis_client: Optional[redis.asyncio.Redis]
        The Redis client the caller must close, or ``None`` for the in-memory store.
    """
    if redis_url is None:
        print("No --redis-url: using the in-memory store. Tokens are cached per process only.")
        broker = AsyncTokenBroker(instance, tenant_api_key, store=AsyncInMemoryTokenStore(), rate_limit=rate_limit)
        return broker, None
    # Imported here and not at module scope: ``redis`` and ``cryptography`` belong to the optional ``cache`` extra,
    # and ``--help`` and the in-memory path must work without them.
    # pylint: disable=import-outside-toplevel
    import redis.asyncio

    from knowledge.services.cache.crypto import AesGcmCipher
    from knowledge.services.cache.redis import AsyncRedisLock, AsyncRedisTokenStore
    from knowledge.services.cache.tiered import AsyncTieredTokenStore

    # pylint: enable=import-outside-toplevel

    # The store handles raw bytes (``bytes(value)``), so the client must NOT decode responses to str.
    redis_client = redis.asyncio.Redis.from_url(redis_url, decode_responses=False)
    # A shared store requires a real cipher. This key is generated for the demo only and is not printed.
    cipher = AesGcmCipher("sample", os.urandom(32))
    print(
        "Generated a throwaway AES-256 key for the demo. A real deployment supplies its own 32-byte key from a "
        "secret store and rotates it by moving the old one to retired_keys."
    )
    broker = AsyncTokenBroker(
        instance,
        tenant_api_key,
        # Process-local L1 in front of Redis: a Redis outage degrades to per-pod caching, not a login per request.
        store=AsyncTieredTokenStore(l1=AsyncInMemoryTokenStore(), l2=AsyncRedisTokenStore(redis_client)),
        # A shared store needs a shared lock; a process-local lock would let every pod believe it holds the lock.
        lock=AsyncRedisLock(redis_client),
        cipher=cipher,
        rate_limit=rate_limit,
    )
    return broker, redis_client


async def simulate_user(
    client: AsyncWacomKnowledgeService, broker: AsyncTokenBroker, external_user_id: str, paced: bool
) -> bool:
    """Make one cheap authenticated read on behalf of a user; returns whether it succeeded."""
    try:
        token = await get_token(broker, external_user_id, paced=paced)
        await client.listing(THING_OBJECT, limit=1, auth_key=token)
        return True
    except (WacomServiceException, aiohttp.ClientError) as exc:
        if logger:
            logger.warning(f"Request for {external_user_id} failed: {exc}")
        return False


async def worker(
    client: AsyncWacomKnowledgeService,
    broker: AsyncTokenBroker,
    queue: "asyncio.Queue[str]",
    paced: bool,
    results: List[bool],
) -> None:
    """Take users off the queue until it is empty."""
    while True:
        try:
            external_user_id = queue.get_nowait()
        except asyncio.QueueEmpty:
            return
        results.append(await simulate_user(client, broker, external_user_id, paced))


def stats_delta(after: BrokerStats, before: BrokerStats) -> BrokerStats:
    """Return the counters accumulated between two snapshots."""
    return BrokerStats(
        **{f.name: getattr(after, f.name) - getattr(before, f.name) for f in dataclasses.fields(BrokerStats)}
    )


def print_stats(stats: BrokerStats, calls: int, failures: int, elapsed: float) -> None:
    """Print the broker counters of one pass as a table."""
    served = stats.hits + stats.misses
    rows = [
        ("calls", calls),
        ("failed calls", failures),
        ("elapsed seconds", f"{elapsed:.2f}"),
        ("hit rate", f"{stats.hits / served:.1%}" if served else "n/a"),
        ("logins", stats.logins),
        ("refreshes", stats.refreshes),
        ("refresh failures", stats.refresh_failures),
        ("lock contention", stats.lock_contentions),
    ]
    print(f"\n{'metric':<20}{'value':>12}")
    print("-" * 32)
    for name, value in rows:
        print(f"{name:<20}{value!s:>12}")


async def run(args: argparse.Namespace) -> int:
    """Fan the simulated users across the workers, twice, and print per-pass statistics.

    The first pass is cold unless ``--redis-url`` points at a Redis that already holds tokens from an earlier run;
    the second is served from the cache.

    Returns
    -------
    exit_code: int
        ``0``, or ``1`` if every call of a pass failed, in which case the statistics mean nothing.
    """
    paced: bool = args.rate_limit is not None
    users: List[str] = [f"middleware-sample-user-{i}" for i in range(args.users)]
    exit_code = 0
    # The one shared service client, built from configuration and closed at shutdown, as in the lifespan block above.
    client = AsyncWacomKnowledgeService(args.instance, APPLICATION_NAME)
    broker, redis_client = build_broker(args.instance, args.tenant_api_key, args.redis_url, args.rate_limit)
    try:
        async with broker:
            for label in ("first pass (cold unless Redis already holds tokens)", "second pass (served from the cache)"):
                queue: "asyncio.Queue[str]" = asyncio.Queue()
                for user in users:
                    queue.put_nowait(user)
                results: List[bool] = []
                before = broker.stats()
                started = time.monotonic()
                await asyncio.gather(*(worker(client, broker, queue, paced, results) for _ in range(args.concurrency)))
                print(f"\n== {label} ==")
                print_stats(
                    stats_delta(broker.stats(), before), len(results), results.count(False), time.monotonic() - started
                )
                if results and not any(results):
                    print(f"\n!!! EVERY CALL FAILED in the {label}. The numbers above are meaningless. !!!")
                    print("!!! Check --instance, --tenant-api-key and connectivity; see the warnings above.  !!!")
                    exit_code = 1
    finally:
        # The broker has closed its own aiohttp client; the Redis client and the service client are ours to close.
        if redis_client is not None:
            await redis_client.aclose()
        await client.close()
    return exit_code


def main() -> None:
    """Parse the arguments and run the driver."""
    parser = argparse.ArgumentParser(description="Serve many PKS users from one process with an AsyncTokenBroker.")
    parser.add_argument(
        "--instance",
        default=os.environ.get("INSTANCE", DEFAULT_INSTANCE),
        help="URL of the PKS instance (default: $INSTANCE, else stage). The driver creates --users shadow users "
        "on whichever instance this points at.",
    )
    parser.add_argument("--tenant-api-key", required=True, help="Tenant API key used for every user login.")
    parser.add_argument(
        "--redis-url",
        default=None,
        help="Redis URL, e.g. redis://localhost:6379/0. Enables the shared, encrypted store; "
        "omitted, the in-memory store is used and no infrastructure is needed.",
    )
    parser.add_argument("--users", type=int, default=200, help="Number of simulated users (default: 200).")
    parser.add_argument("--concurrency", type=int, default=20, help="Number of concurrent workers (default: 20).")
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=None,
        help="Logins and refreshes per second. Given, the driver calls the broker with paced=True, as a sweep would.",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
