# Middleware at scale

How to serve tens of thousands of PKS end users from one backend without flooding `/user/login`.

This guideline is for the engineer deploying a middleware on top of this SDK: a web backend, an ASGI service, a
worker fleet — anything where a single process acts on behalf of many PKS shadow users. It explains what the
`TokenBroker` / `AsyncTokenBroker` do, what you have to configure, what the failure modes are, and what to put on a
dashboard. The runnable counterpart is [`samples/middleware_broker.py`](../samples/middleware_broker.py), which
contains the ASGI lifespan wiring and a load driver.

Every number below is traceable to code: to this SDK, or to the PKS service configuration it talks to. Where a
number is *deployment* configuration rather than a constant, that is said explicitly.

---

## 1. The arithmetic

The first thing to get right is that **authentication load is bounded per user per token lifetime, rather than by
your request count**.

A PKS access token is a JWT whose validity is the service's `TokenValidityMinutes` — **60 in the shipped PKS
configuration**, but it is deployment configuration and a deployment may change it. The broker never assumes it: it
reads the `exp` claim of the token it was handed and uses that as the cache entry's TTL (`TokenBroker._write`).
Nothing in the SDK hard-codes 60 minutes.

Renewal is **lazy**: it happens on a `token_for` call that finds the cached token past its freshness margin, never
on a timer. Two consequences, and you need both of them to size anything correctly.

- Renewals can never exceed requests. There is no background refresher; a user nobody asks for costs nothing.
- For a user who *is* asked for continuously, renewals are capped at one per effective token lifetime.

So the authentication cost per user is `min(that user's requests, the ceiling)`. The ceiling is what you size for,
because it is what a busy population converges on.

**The ceiling.** A cached token is handed out while

```
expires_at - now > early_refresh_seconds + jitter_offset(key)
```

(`TokenBroker._is_fresh`), with `early_refresh_seconds = 300.0` and `jitter_offset` a fixed value in
`[0, early_refresh_jitter_seconds)`, default `120.0`. A token is therefore used for, on average,
`3600 - 300 - 60 = 3240 s` — call it **54 minutes**, or ~26.7 renewals per user per day. For 42,000 users all read
at least once in every such window, that is `42,000 × 86,400 / 3,240 ≈ 1.12 M` renewals a day, or **~13/s**.

Against per-request authentication, at 200 requests/user/day:

| | per day, 42,000 users |
|---|---|
| Logins, authenticating per request | 8,400,000 — and it doubles when your traffic doubles |
| Renewals with the broker, at the defaults below | at most ~1,120,000 (~13/s) — and it does **not** move when your traffic doubles |

That is the point of the broker: above the ceiling it converts an unbounded, traffic-shaped load on `/user/login`
into a bounded, population-shaped load you can size for.

**Below the ceiling it still helps, for a different reason.** A user read less often than once per 54 minutes misses
the cache on most requests, so renewals track requests rather than the ceiling, and the "flat" property does not
apply to them. What they still get is the *kind* of call: a renewal with a live refresh entry is a
`POST /user/refresh`, which rotates one document, where authenticating per request is a `POST /user/login`, which
inserts a new one. The storage arithmetic below is about exactly that difference, and it holds at any request rate.

### The refresh window is sliding, not absolute

A renewal is a `POST /graph/v1/user/refresh`, not a login — and the refresh chain does **not** have a fixed lifetime.
In the PKS backend, `MongoDbRefreshTokenAdapter` validates a refresh token with
`LastUpdated + ValidityInSeconds < UtcNow`, and every rotation sets `LastUpdated = UtcNow`. The Mongo TTL index is
built on the same `LastUpdated` field. `RefreshTokenValidityDays` is **1** in the shipped configuration.

So the window is a **1-day idle timeout**. A chain that is rotated at least once every 24 hours survives
indefinitely; a chain untouched for 24 hours is reaped by Mongo and the next call must log in.

The broker caches the refresh token with `REFRESH_TTL_SECONDS = 23 * 60 * 60` — deliberately just inside that day, so
the cache entry always dies *before* the service's own copy. The cache can therefore never hand out a refresh token
that Mongo has already reaped. A user idle for more than 23 hours costs exactly one login on their next request,
which is what the service would have forced anyway.

### Why the lock exists: it protects PKS storage, not correctness

The two renewal paths write to PKS storage very differently
(`MongoDbRefreshTokenAdapter.AddOrUpdateRefreshTokenAsync`):

- **Refresh** — `FindOneAndUpdateAsync` filtered on the old refresh token: it **rotates and overwrites one
  document**. 42,000 users → ~42,000 live documents, steady.
- **Login** — `InsertOneAsync`: it **inserts a new document** every time. 42,000 users renewing hourly →
  ~1,000,000 live documents, each kept until the TTL index reaps it a day after its last update.

That is a ~24× difference in the service's refresh-token collection, and it is the whole reason the broker takes a
lock around a renewal. **Losing the lock never produces a wrong token** — it costs one duplicate login. The lock is a
storage-pressure control, not a correctness mechanism. Read every statement about the lock below with that in mind.

---

## 2. The three synchronisation hazards

A naive "cache the token with a TTL" gets you most of the way and then fails in three specific ways. A TTL addresses
none of them, because a TTL says *when an entry disappears* and says nothing about *who refills it*, *when the
entries of different users disappear relative to each other*, or *what a cold process does*.

**Cold start.** A fresh pod's cache is empty. Every user's first request is a miss, so a deploy, a scale-out or a pod
restart turns into a burst of logins proportional to your active population, not to anything you controlled. *What
the broker does:* the shared (Redis) tier means a new pod inherits the fleet's tokens instead of minting its own —
this is the main reason to run a shared store at all. What a cold process genuinely cannot avoid is one login: cache
keys are derived from the JWT's `iss` and `tenant` claims, and the tenant *id* is not the tenant *API key*, so the
process has to see one token before it can compute any key. `TokenBroker._bootstrap` does that under a mutex, so
concurrent first callers produce **one** login between them, not one each, and that login is a caller's own — not an
extra one.

**Expiry clustering.** Tokens minted together expire together. A fleet restarted after a deploy mints a cohort of
tokens within seconds of each other; 60 minutes later that entire cohort renews within seconds of each other, and the
pattern repeats every hour because each renewal re-synchronises the cohort. *What the broker does:* each entry gets a
fixed renewal offset in `[0, early_refresh_jitter_seconds)`, so a cohort renews spread across that band instead of at
one instant.

**Cross-pod single-flight.** Ten pods serving the same user all see the same near-expiry token at the same moment and
all renew it. Per-process locking does not help; this is a fleet-level race. *What the broker does:* a best-effort
shared lock (`RedisLock`, `SET NX PX` with a compare-and-delete release) around the renewal. The loser waits
`lock_wait_seconds` (default `0.5`) for the winner's write and otherwise logs in; it never retries.

### The jitter is deterministic per entry, and that is not an implementation detail

`TokenBroker._jitter_for` derives the offset as

```python
digest = hashlib.sha256(key.encode("utf-8")).digest()
fraction = int.from_bytes(digest[:8], "big") / 2**64
return fraction * self._early_refresh_jitter_seconds
```

Constant across reads for one user, different across users, and — this is the part that matters — **identical across
processes**.

The obvious alternative, `random.uniform(0, jitter)` drawn on every read, is actively wrong under middleware traffic.
A user read many times a second gets many draws, and the renewal fires on the *first* draw that exceeds the remaining
life. That draw arrives almost immediately after the earliest edge of the band — for every pod, for every user in the
cohort, at the same instant. A per-read random offset therefore collapses the renewal onto the earliest edge of the
band and reproduces exactly the herd the parameter exists to break. Python's built-in `hash()` would have been just
as unusable, for a different reason: its seed differs per process, so two pods would compute different offsets for
the same user and the shared cache would stop agreeing with itself.

**Tuning the band.** The default 120 s spreads a synchronised cohort of 42,000 users over 120 s, i.e. ~350
renewals/s at the peak. If that is too steep for your deployment, widen `early_refresh_jitter_seconds`; 900 s brings
the cohort peak down to ~47/s. The cost is that a wider band shortens the average effective token life — at 900 s the
average becomes `3600 - 300 - 450 = 2850 s`, so the ceiling of §1 rises from ~13/s to ~15/s. Widen the band to
flatten peaks, not to reduce total load.

**Tuning `early_refresh_seconds` spends a clock-skew budget.** `_is_fresh` compares the token's `exp` claim against
the pod's own `time.time()`, so the 300 s default doubles as the margin absorbing pod-to-PKS clock skew, and
lowering it to buy a longer effective token life tightens that budget by exactly the same amount — enough drift and
the broker starts handing out tokens PKS considers expired, which is the "clock problem" behind a `refresh_failures`
spike in §9.

---

## 3. What you configure

The broker takes a store, a cipher and a lock. The defaults are process-local and are right for a single process; for
a fleet, all three change together.

```python
import redis.asyncio

from knowledge.services.asyncio.broker import AsyncTokenBroker
from knowledge.services.cache.crypto import AesGcmCipher
from knowledge.services.cache.memory import AsyncInMemoryTokenStore, InMemoryTokenStore
from knowledge.services.cache.redis import AsyncRedisLock, AsyncRedisTokenStore
from knowledge.services.cache.tiered import AsyncTieredTokenStore

redis_client = redis.asyncio.Redis.from_url(settings.redis_url, decode_responses=False)  # binary client!

# Two keys per user, so size L1 for the users ONE pod serves - see foot-gun 2.
l1 = AsyncInMemoryTokenStore(InMemoryTokenStore(max_entries=2 * settings.users_per_pod))

broker = AsyncTokenBroker(
    settings.pks_instance,
    settings.tenant_api_key,
    store=AsyncTieredTokenStore(l1=l1, l2=AsyncRedisTokenStore(redis_client)),
    lock=AsyncRedisLock(redis_client),                          # a shared store needs a shared lock
    cipher=AesGcmCipher("2026-01", settings.token_cache_key),   # 32 bytes, from your secret store
    rate_limit=settings.sweep_logins_per_second,                # paces paced=True calls only
)
```

A request handler then does one thing:

```python
token = await broker.token_for(external_user_id)
things, _, _ = await knowledge_client.listing(THING_OBJECT, limit=10, auth_key=token)
```

One `AsyncWacomKnowledgeService` is built at startup and shared by the whole process. It is never logged in, never
rebound to a session; the per-method `auth_key=` override carries the identity. The shared store and cipher need the
optional extra:

```bash
pip install personal-knowledge-library[cache]
```

### Three foot-guns, in order of how much they cost

**1. A Redis store paired with the default process-local lock.** This is the expensive mistake.
`InProcessLock` / `AsyncInProcessLock` is exclusive *within one process only*, so every pod believes it holds the
lock for every user, every pod renews, and you get precisely the duplicate-document blow-up of §1 — the one the lock
exists to prevent. **If you pass a shared store, pass `RedisLock` / `AsyncRedisLock` too.**

The constructor logs a `warning` when it sees a shared store with one of the process-local lock classes — including
the one it defaults to when you pass no `lock=` at all. It is a warning rather than a `ValueError` because a lock
shared by some other means is legitimate; it will not stop you, and it is only as visible as your log pipeline makes
warnings at startup. **No counter will reveal the mistake either** — see §9 — so still assert it yourself at startup,
where it is one line:

```python
if store.shared and not isinstance(lock, AsyncRedisLock):
    raise RuntimeError("A shared token store needs a shared lock, not a process-local one.")
```

At the very least, log which lock class the broker was built with, so the answer is in the logs of every pod rather
than inferred from a dashboard during an incident.

**2. An undersized in-memory store — including as an L1 tier.** `InMemoryTokenStore` defaults to
`max_entries=10_000`, and each user consumes **two** keys (`…:a` for the access token, `…:r` for the refresh token).
The default therefore holds roughly **5,000 users** before it starts evicting oldest-first.

**The sizing rule is `max_entries ≥ 2 × distinct users served per pod`, and it applies to the L1 tier too.** It is
tempting to leave L1 at the default because Redis is behind it, and that works right up to the moment it matters: if
Redis goes away (§5) an undersized L1 thrashes, and the per-pod caching you were relying on turns back into
something close to a login per request. Behind a round-robin load balancer, "distinct users per pod" is your whole
population — 42,000 users means `max_entries=84_000`, not the default. Size it for the outage, not for the happy
path.

**3. A Redis client with `decode_responses=True`.** The store handles raw bytes, encrypted values included. Build the
client with `decode_responses=False`.

A shared store without a cipher is the one mistake the broker will not let you make: a shared store combined with the
default `NullCipher` raises `ValueError` in the constructor.

### Ownership and shutdown

**You own the Redis client.** No store and no lock in `knowledge.services.cache` exposes `close` or `aclose`, so
`AsyncTokenBroker.aclose()` closes only the aiohttp client it created itself, and `TokenBroker.close()` — whose
components, with the shipped classes, expose no `close` at all — releases nothing. Close the Redis client and your
shared service client yourself, at shutdown.

### Key naming

Keys are `pks:<session_id>:a`, `pks:<session_id>:r` and `pks:<session_id>:lk`, where `<session_id>` is the id
`TimedSession` computes from the issuer, the tenant id and the external user id. **External user ids never reach the
shared backend**, and the `pks:` namespace lets the broker share a Redis with other things.

---

## 4. Sizing

Take a PKS access token as **approximately 3 KB** — a working estimate, not a measured constant: a JWT's size
depends on its claims, so measure one from your own tenant before you size anything tightly. On that estimate,
42,000 users is `42,000 × 3 KB ≈ 130 MB` of access entries; the refresh entries are a pair of GUIDs each
(`$"{Guid.NewGuid()}-{Guid.NewGuid()}"` in the service) and round to nothing beside that. The ~130 MB is therefore
only as good as the 3 KB it comes from, and scales linearly with it. Budget it for the token cache in Redis, and
the same again per pod for an L1 tier sized to hold a pod's whole working set.

**Eviction is harmless, so `noeviction` is not required.** An evicted token is a miss, a miss is a login, and a login
produces a correct token. Nothing breaks; you only pay for it. Run the cache under whatever eviction policy the rest
of that Redis needs — `allkeys-lru` is fine. What to size for is *how much* eviction you can afford: at 42,000 users,
evicting the whole keyspace costs 42,000 logins.

---

## 5. When Redis goes away

This section matters more than any other in an incident.

**The store degrades cleanly.** `AsyncRedisTokenStore` raises `TokenStoreUnavailable` for every backend failure;
`AsyncTieredTokenStore` catches it, logs a warning and carries on with L1. You fall back to **per-pod caching** — not
to a failure, and not to a login per request. Each pod re-logs in each of its users once, then serves from memory.
With N pods you pay N× the ceiling of §1 until Redis comes back. This is why a tiered store is worth the extra class
over a bare `AsyncRedisTokenStore`.

**That fallback is only as good as L1's capacity**, and this is the moment foot-gun 2 cashes in. If `max_entries` is
below `2 × distinct users served per pod`, L1 evicts oldest-first under the full working set, most requests miss,
and you get close to a login per request anyway — precisely the outcome the tiered store exists to prevent, arriving
precisely when you least want it. Size L1 for this scenario.

**The lock does not degrade cleanly, and it cannot.** When the lock backend is unreachable, the broker's `_acquire`
returns `UNAVAILABLE`, which is deliberately *not* treated as contention: there is provably no holder whose write is
worth waiting for, so the caller renews immediately rather than stalling for `lock_wait_seconds`. The consequence is
that **concurrent callers for one user renew unsynchronised**, so an outage can produce parallel refresh chains for a
hot user. The alternative — blocking every caller on a holder that cannot exist — would be strictly worse, so this is
a chosen limitation, stated in `AsyncTokenBroker`'s class docstring.

**`rate_limit` bounds only `paced=True` work; interactive renewals during an outage are unbounded by the SDK.** The
limiter is taken in `_pace`, and only when the caller passed `paced=True`. Interactive calls do not wait for a
token — they bypass the limiter entirely, which is deliberate (a user's request is never held behind a token
bucket), but it means the SDK puts *nothing* between an interactive renewal and `/user/login`, outage or not.

So configure `rate_limit` for what it does do: keep your sweeps and batch jobs — which is where the volume is, and
where an outage would otherwise add a flood on top of an already-degraded login path — from making the incident
worse. For interactive renewals, the ceiling has to come from your own back-pressure layer, above the broker. If you
want the SDK's limiter to cover them too, you would have to pass `paced=True` on those calls as well, and accept
that a user's request can then wait on the bucket.

---

## 6. Key management

`AesGcmCipher` is AES-256-GCM. The associated data is the cache key, so a ciphertext copied from one user's key to
another's fails to decrypt instead of silently authenticating the wrong user.

- **Keys are 32 bytes.** Anything else is rejected at construction. Generate with a CSPRNG, keep it in your secret
  manager, never in the image.
- **Every ciphertext carries its key id**, in the `key_id + b":" + nonce + ciphertext` wire format. **A key id must
  not contain `:`** (and must be non-empty ASCII) — the constructor rejects one that does, because the separator is
  how the key id is parsed back out. Date-stamped ids such as `2026-01` work well.
- **Rotate by moving the active key into `retired_keys`:**

  ```python
  cipher = AesGcmCipher("2026-04", new_key, retired_keys={"2026-01": old_key})
  ```

  New writes use the active key; entries written with a retired key still decrypt. A key id cannot be both active and
  retired — that raises `ValueError`.
- **Dropping a retired key too early is not an outage.** An entry whose key id is unknown fails to decrypt, the
  broker logs a warning and treats it as a miss, and the miss becomes a login. Keep retired keys for longer than the
  longest TTL in the cache — 23 hours, from the refresh entries — and nothing is even noticed.

---

## 7. Interactive traffic versus sweeps

The cache flattens interactive traffic, because interactive traffic revisits the same users. **It cannot flatten a
sweep**: a job that walks every user touches each one once, so every single call is a cold miss by construction. A
sweep over 42,000 users is 42,000 logins however good your cache is.

Two things follow.

**Pace the sweep.** Pass `paced=True` to `token_for` and set `rate_limit=` on the constructor. The sweep's logins
then wait on the token bucket. Note what this is and is not: the limiter does not prioritise anything and there is
no shared queue to be ahead of or behind — interactive calls simply bypass it. The effect is that the sweep is
throttled while interactive traffic is not, which is the asymmetry you want from a batch job running beside live
requests.

**A read-only sweep should not use the broker at all.** In the PKS backend,
`GraphDataService/Common/MongoDb/Adapters/MongoDbBaseGraphAdapter.cs` contains

```csharp
if (userIsAdmin)
{
    filter |= Builders<VertexModel>.Filter.Empty;
}
```

in **both** `GetReadFilterAsync` and `GetDeleteFilterAsync`. `Filter.Empty` matches every vertex, so OR-ing it in
means a `TenantAdmin` token sees the whole tenant. A read-only sweep therefore needs **one** token, not 42,000.

**The caveat is not optional, and it is an easy, expensive mistake.** Entities created under an admin token get
`OwnerId = <admin>`. A sweep that *writes on behalf of users* — creating or updating entities that should belong to
them — must still use per-user tokens, or it silently re-owns the tenant's data to the admin account. Admin token for
reading; per-user tokens, paced, for writing. That is what the limiter is there for.

---

## 8. Anti-patterns

**Logging in per request.** `client.login(tenant_api_key, external_user_id)` in a request handler is the pattern the
broker exists to replace. It costs a round trip on every request and, because login *inserts* a refresh document, it
grows the service's refresh-token collection without bound. If you take nothing else from this document: let
authentication be bounded per user per token lifetime, instead of growing with your traffic.

**Sharing a *logged-in* client across users.** A client binds to one session at a time, so a shared, logged-in client
is racy: user A's request can be served under user B's token. Note the distinction — sharing a **stateless** client,
never logged in and driven entirely by `auth_key=`, is exactly right, and is what the broker is designed around. It
is the `login()` that must not be shared, not the client.

**A client per user per request.** The safe-looking alternative to the above, and wasteful: a fresh client per
request means a fresh connection pool and a fresh login every time. One process-wide client plus `auth_key=` gets you
both safety and reuse.

**Long lock waits.** `lock_wait_seconds` defaults to `0.5`, and raising it is tempting — a longer wait means more
callers pick up the winner's token instead of logging in. It is also, directly, a latency floor on every contended
renewal, and the thing it buys is *one login*, which is cheap. Keep it short. The same applies to `lock_ttl_seconds`
(default `5.0`): a renewal that outruns it no longer holds the lock it took, which the broker detects and handles by
leaving the lock to expire rather than freeing somebody else's.

---

## 9. What to measure

`broker.stats()` returns a `BrokerStats` with six counters. Export all six, and alert on the ratios rather than the
absolutes.

| Counter | Healthy | What a bad value means |
|---|---|---|
| `hits` | the overwhelming majority | — |
| `misses` | `misses / (hits + misses)` small and stable | Rising: cold pods cycling, an undersized store evicting, or the shared tier not being reached. Equal to your request count means the cache is not working at all. |
| `logins` | ≈ new users + restarts | Tracking `misses` means the refresh chain is not being used: entries are expiring past 23 h, or refreshes are failing (check `refresh_failures`). This is the counter that maps directly onto inserted PKS documents. |
| `refreshes` | the bulk of renewals; at most ~13/s at 42 k users, less if your users are not read continuously | Much lower than `logins` is the same symptom as above, seen from the other side. |
| `refresh_failures` | ~0 | Each one is a rejected refresh token followed by a login fallback. A steady trickle is normal (chains that idled out). A spike means the service is rejecting chains — an auth-side change, a clock problem, or cache entries outliving the service's copy. |
| `lock_contentions` | small; zero is also normal | Growing fast means renewals are slow, or `lock_ttl_seconds` is too long — every contention is a caller that waited `lock_wait_seconds`, so this is a latency signal. **A low or zero value proves nothing** (see below). |

**`lock_contentions` does not detect foot-gun 1, in either direction — do not alert on it.** It is tempting to read
a zero as "the shared lock is missing", and it is not: `InProcessLock` *is* exclusive within a process, so two
concurrent requests for the same user in one pod record a contention even when the lock is the wrong class; and with
a correct `RedisLock` zero is entirely plausible, because the jitter spreads renewals and two callers arriving at
one user's renewal edge at the same instant is rare. An alert on this counter false-positives on healthy fleets and
still misses the misconfiguration. Assert the lock class at startup instead (foot-gun 1). Treat a sustained zero as
weak corroborating evidence at most, and only once you have already confirmed the wiring some other way.

**The accounting quirk, so your dashboard is not confusing.** Every `token_for` call moves **exactly one** of `hits`
and `misses`, so their sum is the number of calls served and `hits / (hits + misses)` is the hit ratio. The one case
that looks like an exception is deliberate: a caller that loses the lock, waits, and then finds the winner's token in
the cache is **not** counted as a hit — it already counted a miss on the way in. Without that rule a single call
could move both counters and the ratio would stop meaning anything.

Also worth a graph: `logins + refreshes` against your user count. For a busy population it should sit at or below
the ceiling of §1, proportional to the population rather than to traffic. If it rises in step with your request rate
*while staying under the ceiling*, your users are simply read less often than once per 54 minutes — expected, not a
fault. If it rises in step with traffic *past* the ceiling, something is authenticating per request.

---

## 10. Deployment checklist

- [ ] One service client per process, never logged in, always called with `auth_key=`.
- [ ] One broker per process, built at startup, closed at shutdown.
- [ ] Shared store? Then a shared lock (`RedisLock` / `AsyncRedisLock`) **and** an `AesGcmCipher`.
- [ ] A startup assertion that a shared store is paired with `RedisLock` / `AsyncRedisLock`, or at least a log line
      naming the lock class. The constructor warns about the process-local default, but no counter will tell you,
      and a warning is easy to miss in a startup log.
- [ ] Tiered store (`l1=` in-memory, `l2=` Redis), so a Redis outage degrades to per-pod caching.
- [ ] **Every** in-memory store, L1 tier included, sized at `max_entries ≥ 2 × distinct users served per pod`
      (two keys per user). An undersized L1 thrashes during a Redis outage and gives you back a login per request.
- [ ] Redis client built with `decode_responses=False`, and closed by you.
- [ ] `rate_limit=` configured, and sweeps calling `token_for(..., paced=True)`; interactive renewals bounded by
      your own back-pressure layer, not by the SDK.
- [ ] 32-byte cipher key from a secret store; key id without `:`; retired keys kept ≥ 23 h after a rotation.
- [ ] Read-only sweeps using a `TenantAdmin` token instead of the broker; writes on behalf of users still per-user.
- [ ] All six `BrokerStats` counters exported. No alert on `lock_contentions`; it is not diagnostic.
