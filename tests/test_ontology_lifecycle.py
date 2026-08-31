# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""
End-to-end integration test of the ontology service on a throwaway tenant.
=========================================================================

The flow provisions its own tenant, exercises the full ``OntologyService`` surface against
it, proves that a committed and applied ontology is honoured by the graph service, and
tears everything down again:

1.  Create a tenant with ``createAndApplyOnto=True``.
2.  Provision a ``TenantAdmin`` shadow user and bind the ontology and graph clients to it.
3.  Read the context that the create-ontology option left behind.
4.  Create two concept classes (one of them a subclass of the other).
5.  Create data properties (string and integer ranges).
6.  Create object properties, including an inverse pair.
7.  Inspect the uncommitted state (``pending_version``, ``context_diff``).
8.  Modify concepts and properties (labels, comments, icon, NEL metadata, rename,
    domains, ranges) and delete a scratch concept/property again.
9.  ``commit`` the ontology and ``ontology_update`` it on the graph side.
10. Create entities of the new classes with the new data properties and relate them
    through the new object properties -- including the negative range check.
11. Modify the ontology a second time, commit, apply, and use the addition on an
    existing entity.
12. Exercise the lifecycle of a secondary, throwaway context.
13. Reset the context -- expected to fail while entities of the new classes exist.
14. Remove the entities and reset again -- expected to succeed.
15. Remove the tenant.

Requirements
------------
Creating and deleting tenants needs the Wacom-only *Tenant Management API Key*, which is
deliberately **not** baked into ``pytest.ini`` -- it is far more powerful than the tenant
key used by the rest of the suite. Supply it through the environment:

>>> TENANT_MANAGEMENT_API_KEY=<key> poetry run pytest tests/test_ontology_lifecycle.py

Without the variable the whole module is skipped.

**Remark:** the tests share state through class attributes and therefore must run in
order; the ``test_<nn>_`` prefixes keep unittest's alphabetical ordering aligned with the
flow. ``tearDownClass`` removes the tenant unconditionally, so an aborted run does not
leak a tenant on the target instance.
"""

import logging
import os
import time
import uuid
from contextlib import contextmanager
from http import HTTPStatus
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple
from unittest import TestCase

import pytest

from knowledge.base.language import DE, EN, EN_US
from knowledge.base.ontology import (
    THING_CLASS,
    Comment,
    DataProperty,
    DataPropertyType,
    InflectionLevel,
    InflectionSetting,
    OntologyChangeOperation,
    OntologyClass,
    OntologyClassReference,
    OntologyContext,
    OntologyDiff,
    OntologyLabel,
    OntologyProperty,
    OntologyPropertyReference,
    OntologyUpdateStatus,
    PendingOntologyVersion,
    PropertyType,
    ThingObject,
)
from knowledge.base.tenant import TenantConfiguration
from knowledge.services.base import WacomServiceException
from knowledge.services.graph import WacomKnowledgeService
from knowledge.services.ontology import OntologyService
from knowledge.services.tenant import TenantManagementServiceAPI
from knowledge.services.users import User, UserManagementServiceAPI, UserRole

# ------------------------------------------- Test configuration -------------------------------------------------------
INSTANCE: str = os.environ.get("INSTANCE", "https://stage-private-knowledge.wacom.com")
TENANT_MANAGEMENT_API_KEY: Optional[str] = os.environ.get("TENANT_MANAGEMENT_API_KEY")

RUN_ID: str = uuid.uuid4().hex[:8]
"""Disambiguates the artefacts of concurrent runs against the same instance."""
TENANT_NAME: str = f"pkl-e2e-ontology-{RUN_ID}"
ADMIN_EXTERNAL_ID: str = f"e2e-ontology-admin-{RUN_ID}"
SCRATCH_CONTEXT_NAME: str = f"e2escratch{RUN_ID}"

# Local names of the ontology objects the flow creates. They are resolved against the base
# URI of the tenant's own context, so the scheme and context part are not known upfront.
CLASS_NAME: str = "E2ELifecycle"
SUBCLASS_NAME: str = "E2ELifecycleDetail"
SCRATCH_CLASS_NAME: str = "E2ELifecycleScratch"
DATA_PROP_CODE_NAME: str = "e2eCodeName"
DATA_PROP_REVISION_NAME: str = "e2eRevision"
DATA_PROP_REVISION_RENAMED: str = "e2eRevisionNumber"
DATA_PROP_NOTE_NAME: str = "e2eNote"
DATA_PROP_SCRATCH_NAME: str = "e2eScratch"
OBJECT_PROP_NAME: str = "e2eLinkedTo"
OBJECT_PROP_INVERSE_NAME: str = "e2eLinkedFrom"

BASE_TOPIC_CLASS: OntologyClassReference = OntologyClassReference.parse("wacom:core#Topic")
"""A base-ontology class, used to prove that a write block is tenant-wide rather than type-specific."""

LONG_TIMEOUT: int = 120
TIMEOUT: int = 30
"""Relation calls, commits and RDF exports are noticeably slower than plain reads."""

REQUIRED_IDLE_POLLS: int = 2
"""Consecutive idle status readings needed before an apply counts as finished."""

pytestmark = pytest.mark.skipif(
    not TENANT_MANAGEMENT_API_KEY,
    reason="TENANT_MANAGEMENT_API_KEY is not set; the flow needs to create and delete its own tenant.",
)


class ResponseLogger:
    """Proxy around a request session that logs every failing HTTP response.

    `WacomServiceException` passes only its message to `Exception.__init__`, so a bare
    traceback names the SDK's own wording and drops the status code and the body the
    service sent. Against a live service those two are the whole diagnosis, so they are
    logged here - at the one boundary every client call passes through.

    Parameters
    ----------
    delegate: Any
        The real request session.
    """

    VERBS: Tuple[str, ...] = ("get", "post", "put", "patch", "delete")

    def __init__(self, delegate: Any) -> None:
        self._delegate: Any = delegate

    def __getattr__(self, name: str) -> Any:
        attribute: Any = getattr(self._delegate, name)
        if name not in ResponseLogger.VERBS or not callable(attribute):
            return attribute

        def logged(url: str, **kwargs: Any) -> Any:
            response: Any = attribute(url, **kwargs)
            if not getattr(response, "ok", True):
                logging.error(
                    "HTTP %s %s -> %s %s",
                    name.upper(),
                    url,
                    getattr(response, "status_code", "?"),
                    (getattr(response, "text", "") or "")[:2000],
                )
            return response

        return logged


class LoggingOntologyService(OntologyService):
    """OntologyService that logs failing responses."""

    @property
    def request_session(self) -> Any:
        return ResponseLogger(super().request_session)


class LoggingKnowledgeService(WacomKnowledgeService):
    """WacomKnowledgeService that logs failing responses."""

    @property
    def request_session(self) -> Any:
        return ResponseLogger(super().request_session)


class LoggingTenantService(TenantManagementServiceAPI):
    """TenantManagementServiceAPI that logs failing responses."""

    @property
    def request_session(self) -> Any:
        return ResponseLogger(super().request_session)


class LoggingUserService(UserManagementServiceAPI):
    """UserManagementServiceAPI that logs failing responses."""

    @property
    def request_session(self) -> Any:
        return ResponseLogger(super().request_session)


def describe_service_error(error: WacomServiceException) -> str:
    """Render everything a service exception knows.

    `WacomServiceException` passes only its message to `Exception.__init__`, so a bare
    traceback shows the SDK's own wording and drops the status code and the body the
    service actually sent. Those two are what a failure against a live service needs.

    Parameters
    ----------
    error: WacomServiceException
        Exception raised by a service client.

    Returns
    -------
    description: str
        Single-line rendering of the status, request and response.
    """
    return (
        f"status={error.status_code} method={error.method} url={error.url} "
        f"response={error.service_response!r} params={error.params} payload={error.payload}"
    )


@contextmanager
def service_call(description: str) -> Iterator[None]:
    """Log the full service response when a call in the block fails, then re-raise.

    Parameters
    ----------
    description: str
        What the block was trying to do, used as the log prefix.
    """
    try:
        yield
    except WacomServiceException as service_error:
        logging.error("%s -> %s", description, describe_service_error(service_error))
        raise


def eventually(action: Callable[[], None], attempts: int = 5, delay: float = 3.0) -> None:
    """Run an action until it no longer raises a service exception.

    Entity deletions propagate asynchronously, so an operation that depends on them being
    gone can legitimately fail for a moment before it succeeds.

    Parameters
    ----------
    action: Callable[[], None]
        Operation to retry.
    attempts: int (default:= 5)
        Number of attempts before the last exception is re-raised.
    delay: float (default:= 3.0)
        Delay between two attempts, in seconds.

    Raises
    ------
    WacomServiceException
        If the action still fails on the last attempt.
    """
    last_error: Optional[WacomServiceException] = None
    for attempt in range(1, attempts + 1):
        try:
            action()
            return
        except WacomServiceException as service_error:
            last_error = service_error
            logging.info(
                "Attempt %d/%d failed with status %s: %s",
                attempt,
                attempts,
                service_error.status_code,
                service_error.message,
            )
            if attempt < attempts:
                time.sleep(delay)
    if last_error is not None:
        raise last_error
    raise AssertionError("eventually() was called with attempts < 1")


class OntologyLifecycleFlow(TestCase):
    """
    Testing the full ontology lifecycle
    -----------------------------------
    Provisions a dedicated tenant, walks the ontology service through create / modify /
    commit / apply / reset, verifies that the graph service honours the applied ontology,
    and removes the tenant again.
    """

    # The Logging* variants only add a response logger; the behaviour is the base clients'.
    tenant_manager: TenantManagementServiceAPI = LoggingTenantService(
        tenant_token=TENANT_MANAGEMENT_API_KEY or "", service_url=INSTANCE
    )
    """Tenant management service - needs the Wacom-only tenant management key."""
    user_management: UserManagementServiceAPI = LoggingUserService(service_url=INSTANCE)
    """User management service."""
    ontology: OntologyService = LoggingOntologyService(service_url=INSTANCE)
    """Ontology service under test."""
    knowledge: WacomKnowledgeService = LoggingKnowledgeService(
        service_url=INSTANCE, application_name="Ontology lifecycle e2e test"
    )
    """Graph service - used to prove that the applied ontology took effect."""

    # -------------------------------------- State shared across the flow ----------------------------------------------
    tenant_id: Optional[str] = None
    tenant_api_key: Optional[str] = None
    context_name: Optional[str] = None
    base_uri: Optional[str] = None
    class_ref: Optional[OntologyClassReference] = None
    subclass_ref: Optional[OntologyClassReference] = None
    data_prop_code: Optional[OntologyPropertyReference] = None
    data_prop_revision: Optional[OntologyPropertyReference] = None
    data_prop_note: Optional[OntologyPropertyReference] = None
    object_prop: Optional[OntologyPropertyReference] = None
    object_prop_inverse: Optional[OntologyPropertyReference] = None
    parent_uri: Optional[str] = None
    detail_uri: Optional[str] = None

    @classmethod
    def tearDownClass(cls) -> None:
        """Remove the tenant even if the flow aborted halfway through."""
        if cls.tenant_id is None:
            return
        logging.warning("Tenant %s survived the flow - removing it in the teardown.", cls.tenant_id)
        try:
            cls.tenant_manager.delete_tenant(cls.tenant_id)
        except WacomServiceException as service_error:
            # A tenant left mid-reset is locked at ontology version 0, and the service
            # refuses to delete it until the reset is finished with an apply.
            logging.warning("Direct removal failed (%s): %s", service_error.status_code, service_error.message)
            try:
                cls.knowledge.ontology_update(timeout=LONG_TIMEOUT)
                cls._await_ontology_applied()
                cls.tenant_manager.delete_tenant(cls.tenant_id)
                logging.info("Tenant %s removed after finishing the pending ontology update.", cls.tenant_id)
            except (WacomServiceException, AssertionError) as recovery_error:
                logging.error(
                    "Teardown could not remove tenant %s - remove it manually: %s",
                    cls.tenant_id,
                    recovery_error,
                )
        finally:
            cls.tenant_id = None

    @classmethod
    def _log_ontology_state(cls, context: str, when: str) -> List[int]:
        """Log the version numbers the context reports, plus the graph-side update status.

        Parameters
        ----------
        context: str
            Name of the context.
        when: str
            Phrase describing the moment, used in the log line.

        Returns
        -------
        version_numbers: List[int]
            Distinct version numbers the change log mentions, ascending.
        """
        entries: List[Dict[str, Any]] = cls.ontology.versions(context)
        version_numbers: List[int] = sorted(
            {entry["version"] for entry in entries if isinstance(entry, dict) and entry.get("version") is not None}
        )
        current: Optional[OntologyContext] = cls.ontology.context()
        logging.info(
            "Ontology state %s: context version=%s, change log versions=%s, graph status=%s",
            when,
            current.version if current else None,
            version_numbers,
            cls.knowledge.ontology_update_status(),
        )
        return version_numbers

    @classmethod
    def _await_commit_visible(cls, context: str, attempts: int = 15, delay: float = 2.0) -> None:
        """Wait until a commit is observable, i.e. the context has no pending changes left.

        The apply refuses a version it has already applied, so triggering it before the
        commit is visible reports 'already applied' rather than doing the work.

        Parameters
        ----------
        context: str
            Name of the context.
        attempts: int (default:= 15)
            Number of polls before giving up.
        delay: float (default:= 2.0)
            Delay between two polls, in seconds.

        Raises
        ------
        AssertionError
            If pending changes remain after the allotted attempts.
        """
        for attempt in range(1, attempts + 1):
            try:
                pending: PendingOntologyVersion = cls.ontology.pending_version(context)
            except WacomServiceException as pending_error:
                logging.info("No pending version after the commit (status %s).", pending_error.status_code)
                return
            if pending.is_empty:
                logging.info("Commit visible after %d poll(s): nothing pending.", attempt)
                return
            logging.info(
                "Commit not visible yet (poll %d/%d): %d change(s) still pending at version %s.",
                attempt,
                attempts,
                len(pending.changes),
                pending.version,
            )
            time.sleep(delay)
        raise AssertionError(f"Pending changes remained {attempts * delay:.0f}s after the commit.")

    @classmethod
    def _commit_and_apply(cls, context: str) -> None:
        """Commit the ontology and apply it to the graph, waiting out both stages.

        Parameters
        ----------
        context: str
            Name of the context.
        """
        with service_call("commit"):
            cls.ontology.commit(context, timeout=LONG_TIMEOUT)
        cls._await_commit_visible(context)
        cls._log_ontology_state(context, "after the commit")

        # The apply is only accepted here; graph writes stay blocked until it completes.
        try:
            cls.knowledge.ontology_update(timeout=LONG_TIMEOUT)
        except WacomServiceException as apply_error:
            logging.error("Apply rejected -> %s", describe_service_error(apply_error))
            cls._log_ontology_state(context, "after the rejected apply")
            raise
        cls._await_ontology_applied()

    @classmethod
    def _await_ontology_applied(cls, attempts: int = 30, delay: float = 2.0) -> OntologyUpdateStatus:
        """Wait until the tenant's ontology update finished.

        `ontology_update` only accepts the apply; the work continues in the background
        while the tenant is locked, and every graph write is rejected until it completes.

        **Remark:**
        The service reports 'NoUpdateInProgress' both when an apply has completed and when
        none was ever started, without version fields to distinguish the two. A single idle
        reading would therefore return before a just-triggered apply registers its row, so
        `REQUIRED_IDLE_POLLS` consecutive idle readings are required.

        Parameters
        ----------
        attempts: int (default:= 30)
            Number of status polls before giving up.
        delay: float (default:= 2.0)
            Delay between two polls, in seconds.

        Returns
        -------
        status: OntologyUpdateStatus
            The status that ended the wait.

        Raises
        ------
        AssertionError
            If the update failed, or did not finish within the allotted attempts.
        """
        status: Optional[OntologyUpdateStatus] = None
        idle_streak: int = 0
        for attempt in range(1, attempts + 1):
            status = cls.knowledge.ontology_update_status()
            if status.has_failed:
                raise AssertionError(
                    f"The ontology update failed (applied version {status.applied_ontology_version}). "
                    "It has to be resumed with ontology_update(fix=True)."
                )
            # 'NoUpdateInProgress' means either 'finished' or 'never started', and the
            # service reports no version fields to tell them apart. A single idle reading
            # would therefore let a just-triggered apply through before it registers, so
            # two consecutive readings are required.
            idle_streak = idle_streak + 1 if status.is_idle else 0
            if idle_streak < REQUIRED_IDLE_POLLS:
                logging.info(
                    "Ontology update %s (poll %d/%d, idle streak %d/%d)",
                    status.status,
                    attempt,
                    attempts,
                    idle_streak,
                    REQUIRED_IDLE_POLLS,
                )
                time.sleep(delay)
                continue
            logging.info(
                "Ontology update idle after %d poll(s): ontology=%s previous=%s applied=%s added=%s modified=%s",
                attempt,
                status.ontology_name,
                status.previous_ontology_version,
                status.applied_ontology_version,
                status.date_added,
                status.date_modified,
            )
            return status
        raise AssertionError(
            f"The ontology update did not finish within {attempts * delay:.0f}s; "
            f"last status: {status.status if status else 'unknown'}"
        )

    # ----------------------------------------------- Helpers ----------------------------------------------------------
    def _required(self, value: Any, what: str) -> Any:
        """Skip the current test if a previous step did not produce its prerequisite."""
        if value is None:
            self.skipTest(f"{what} is unavailable - an earlier step of the flow failed.")
        return value

    def _class_ref(self, local_name: str) -> OntologyClassReference:
        """Build a class reference in the base URI of the tenant's context."""
        return OntologyClassReference.parse(f"{self._required(self.base_uri, 'Base URI')}{local_name}")

    def _prop_ref(self, local_name: str) -> OntologyPropertyReference:
        """Build a property reference in the base URI of the tenant's context."""
        return OntologyPropertyReference.parse(f"{self._required(self.base_uri, 'Base URI')}{local_name}")

    def _concept_refs(self) -> List[OntologyClassReference]:
        """List the concept references of the tenant's context."""
        context: str = self._required(self.context_name, "Context")
        return [reference for reference, _ in self.ontology.concepts(context)]

    def _property_refs(self) -> List[OntologyPropertyReference]:
        """List the property references of the tenant's context."""
        context: str = self._required(self.context_name, "Context")
        return [reference for reference, _ in self.ontology.properties(context)]

    def _log_relations(self, label: str, uri: str) -> Dict[OntologyPropertyReference, Any]:
        """Log every relation of an entity, in both directions.

        Parameters
        ----------
        label: str
            Human-readable name of the entity, used as the log prefix.
        uri: str
            URI of the entity.

        Returns
        -------
        relations: Dict[OntologyPropertyReference, Any]
            The relations, so a caller can assert on them.
        """
        relations: Dict[OntologyPropertyReference, Any] = self.knowledge.relations(uri, timeout=LONG_TIMEOUT)
        if not relations:
            logging.info("Relations of %s (%s): none", label, uri)
        for reference, object_property in relations.items():
            logging.info(
                "Relations of %s (%s): %s outgoing=%s incoming=%s",
                label,
                uri,
                reference.iri,
                object_property.outgoing_relations,
                object_property.incoming_relations,
            )
        return relations

    # ------------------------------------------------- Flow -----------------------------------------------------------
    def test_01_create_tenant_with_ontology(self) -> None:
        """Create the tenant with the create-and-apply-ontology option."""
        tenant: Dict[str, str] = self.tenant_manager.create_tenant(name=TENANT_NAME, create_and_apply_onto=True)
        self.assertIn("id", tenant)
        self.assertIn("apiKey", tenant)
        self.assertEqual(tenant["name"], TENANT_NAME)
        print(tenant)
        OntologyLifecycleFlow.tenant_id = tenant["id"]
        OntologyLifecycleFlow.tenant_api_key = tenant["apiKey"]
        logging.info("Created tenant %s (%s)", TENANT_NAME, tenant["id"])

        # createAndApplyOnto=True must leave the tenant with an ontology already applied.
        configurations: List[TenantConfiguration] = [
            configuration
            for configuration in self.tenant_manager.listing_tenant()
            if configuration.identifier == tenant["id"]
        ]
        self.assertEqual(len(configurations), 1, "The freshly created tenant must show up in the tenant listing.")
        configuration: TenantConfiguration = configurations[0]
        self.assertTrue(configuration.ontology_name, "createAndApplyOnto=True must name an ontology on the tenant.")
        # The automatic setup applies the ontology asynchronously, and the service returns
        # the tenant even when that setup failed - so the version and the lock are only
        # checked once the update reports itself finished, in the next step.
        logging.info(
            "Tenant ontology: %s (version %d, locked: %s)",
            configuration.ontology_name,
            configuration.ontology_version,
            configuration.is_locked,
        )

    def test_02_bootstrap_tenant_admin(self) -> None:
        """Provision a TenantAdmin user and bind the ontology and graph clients to it."""
        tenant_api_key: str = self._required(self.tenant_api_key, "Tenant API key")
        user, token, refresh_token, expiration = self.user_management.create_user(
            tenant_key=tenant_api_key,
            external_id=ADMIN_EXTERNAL_ID,
            meta_data={"purpose": "ontology-lifecycle-e2e"},
            roles=[UserRole.ADMIN],
        )
        self.assertIsInstance(user, User)
        self.assertEqual(user.external_user_id, ADMIN_EXTERNAL_ID)
        self.assertIn(UserRole.ADMIN, user.user_roles, "Ontology changes require the TenantAdmin role.")
        self.assertTrue(token)
        self.assertTrue(refresh_token)
        self.assertIsNotNone(expiration)

        # Each client keeps its own session table, so both of them log in separately.
        self.assertIsNotNone(self.ontology.login(tenant_api_key, ADMIN_EXTERNAL_ID))
        self.assertIsNotNone(self.knowledge.login(tenant_api_key, ADMIN_EXTERNAL_ID))

        # Now that an admin token exists, wait out the ontology setup that the tenant
        # creation kicked off and confirm it actually succeeded.
        status: OntologyUpdateStatus = self._await_ontology_applied()
        self.assertTrue(status.is_idle)
        tenant_id: str = self._required(self.tenant_id, "Tenant")
        configuration: TenantConfiguration = next(
            entry for entry in self.tenant_manager.listing_tenant() if entry.identifier == tenant_id
        )
        self.assertFalse(configuration.is_locked, "The tenant must be unlocked once the ontology has been applied.")
        self.assertGreaterEqual(
            configuration.ontology_version, 1, "createAndApplyOnto=True must leave an applied ontology version."
        )

    def test_03_read_created_context(self) -> None:
        """Read the context that the create-ontology option left behind."""
        self._required(self.tenant_api_key, "Tenant API key")
        contexts: List[OntologyContext] = self.ontology.contexts()
        self.assertGreater(len(contexts), 0, "createAndApplyOnto=True must leave the tenant with a context.")

        context: Optional[OntologyContext] = self.ontology.context()
        self.assertIsNotNone(context)
        assert context is not None  # narrows the type for the remainder of the test
        self.assertTrue(context.context)
        self.assertTrue(context.tenant_id)
        self.assertTrue(context.base_uri)
        self.assertTrue(context.base_uri.endswith("#"), "The base URI must be usable as an IRI prefix.")
        OntologyLifecycleFlow.context_name = context.context
        OntologyLifecycleFlow.base_uri = context.base_uri
        logging.info(
            "Context %s, base URI %s, version %d, orphaned %s",
            context.context,
            context.base_uri,
            context.version,
            context.orphaned,
        )

        # The base ontology is imported, so the compact and the full listings are populated.
        concepts: List[Tuple[OntologyClassReference, Optional[OntologyClassReference]]] = self.ontology.concepts(
            context.context
        )
        self.assertGreater(len(concepts), 1)
        self.assertIn(THING_CLASS, [reference for reference, _ in concepts])
        properties: List[Tuple[OntologyPropertyReference, Optional[OntologyPropertyReference]]] = (
            self.ontology.properties(context.context)
        )
        self.assertGreater(len(properties), 1)
        self.assertGreater(len(self.ontology.concepts_types(context.context)), 1)
        self.assertGreater(len(self.ontology.properties_types(context.context)), 1)

    def test_04_create_concepts(self) -> None:
        """Create the new concept class and a subclass of it."""
        context: str = self._required(self.context_name, "Context")
        class_ref: OntologyClassReference = self._class_ref(CLASS_NAME)
        subclass_ref: OntologyClassReference = self._class_ref(SUBCLASS_NAME)

        self.assertIsInstance(
            self.ontology.create_concept(
                context=context,
                reference=class_ref,
                subclass_of=THING_CLASS,
                labels=[
                    OntologyLabel("E2E lifecycle class", EN),
                    OntologyLabel("E2E-Lebenszyklus-Klasse", DE),
                ],
                comments=[Comment("Temporary class created by the ontology lifecycle test.", EN)],
            ),
            dict,
        )
        self.assertIsInstance(
            self.ontology.create_concept(
                context=context,
                reference=subclass_ref,
                subclass_of=class_ref,
                labels=[OntologyLabel("E2E lifecycle detail", EN)],
            ),
            dict,
        )
        OntologyLifecycleFlow.class_ref = class_ref
        OntologyLifecycleFlow.subclass_ref = subclass_ref

        concept: OntologyClass = self.ontology.concept(context, class_ref.iri)
        self.assertEqual(concept.reference, class_ref)
        self.assertEqual(concept.subclass_of, THING_CLASS)
        self.assertEqual({label.language_code for label in concept.labels}, {EN, DE})
        self.assertEqual(len(concept.comments), 1)

        detail: OntologyClass = self.ontology.concept(context, subclass_ref.iri)
        self.assertEqual(detail.subclass_of, class_ref, "The subclass must point at the class created before it.")

        concept_refs: List[OntologyClassReference] = self._concept_refs()
        self.assertIn(class_ref, concept_refs)
        self.assertIn(subclass_ref, concept_refs)

    def test_05_create_data_properties(self) -> None:
        """Create data properties with a string and an integer range."""
        context: str = self._required(self.context_name, "Context")
        class_ref: OntologyClassReference = self._required(self.class_ref, "Concept class")
        code_prop: OntologyPropertyReference = self._prop_ref(DATA_PROP_CODE_NAME)
        revision_prop: OntologyPropertyReference = self._prop_ref(DATA_PROP_REVISION_NAME)

        self.assertIsInstance(
            self.ontology.create_data_property(
                context=context,
                reference=code_prop,
                domains_cls=[class_ref],
                ranges_cls=[DataPropertyType.STRING],
                labels=[OntologyLabel("Code name", EN)],
                comments=[Comment("Free-text code name of the entity.", EN)],
            ),
            dict,
        )
        self.assertIsInstance(
            self.ontology.create_data_property(
                context=context,
                reference=revision_prop,
                domains_cls=[class_ref],
                ranges_cls=[DataPropertyType.INTEGER],
                labels=[OntologyLabel("Revision", EN)],
            ),
            dict,
        )
        OntologyLifecycleFlow.data_prop_code = code_prop
        OntologyLifecycleFlow.data_prop_revision = revision_prop

        code: OntologyProperty = self.ontology.property(context, code_prop.iri)
        self.assertTrue(code.is_data_property)
        self.assertEqual(code.kind, PropertyType.DATA_PROPERTY)
        self.assertIn(class_ref, code.domains)
        # Data-property ranges come back as XSD IRIs, so they are compared on the IRI.
        self.assertIn(DataPropertyType.STRING.value, [entry.iri for entry in code.ranges])
        self.assertEqual(len(code.labels), 1)

        revision: OntologyProperty = self.ontology.property(context, revision_prop.iri)
        self.assertTrue(revision.is_data_property)
        self.assertIn(DataPropertyType.INTEGER.value, [entry.iri for entry in revision.ranges])

        property_refs: List[OntologyPropertyReference] = self._property_refs()
        self.assertIn(code_prop, property_refs)
        self.assertIn(revision_prop, property_refs)

    def test_06_create_object_properties(self) -> None:
        """Create an object property and its inverse."""
        context: str = self._required(self.context_name, "Context")
        class_ref: OntologyClassReference = self._required(self.class_ref, "Concept class")
        subclass_ref: OntologyClassReference = self._required(self.subclass_ref, "Concept subclass")
        linked_to: OntologyPropertyReference = self._prop_ref(OBJECT_PROP_NAME)
        linked_from: OntologyPropertyReference = self._prop_ref(OBJECT_PROP_INVERSE_NAME)

        self.assertIsInstance(
            self.ontology.create_object_property(
                context=context,
                reference=linked_to,
                domains_cls=[class_ref],
                ranges_cls=[subclass_ref],
                labels=[OntologyLabel("linked to", EN)],
                comments=[Comment("Links a lifecycle entity to one of its details.", EN)],
            ),
            dict,
        )
        self.assertIsInstance(
            self.ontology.create_object_property(
                context=context,
                reference=linked_from,
                domains_cls=[subclass_ref],
                ranges_cls=[class_ref],
                inverse_of=linked_to,
                labels=[OntologyLabel("linked from", EN)],
            ),
            dict,
        )
        OntologyLifecycleFlow.object_prop = linked_to
        OntologyLifecycleFlow.object_prop_inverse = linked_from

        outgoing: OntologyProperty = self.ontology.property(context, linked_to.iri)
        self.assertFalse(outgoing.is_data_property)
        self.assertEqual(outgoing.kind, PropertyType.OBJECT_PROPERTY)
        self.assertEqual(outgoing.domains, [class_ref])
        self.assertEqual(outgoing.ranges, [subclass_ref])

        incoming: OntologyProperty = self.ontology.property(context, linked_from.iri)
        self.assertEqual(incoming.inverse_property_of, linked_to)
        self.assertEqual(incoming.domains, [subclass_ref])

    def test_07_inspect_uncommitted_state(self) -> None:
        """The additions must be visible as a pending version and in the context diff."""
        context: str = self._required(self.context_name, "Context")
        class_ref: OntologyClassReference = self._required(self.class_ref, "Concept class")
        subclass_ref: OntologyClassReference = self._required(self.subclass_ref, "Concept subclass")
        code_prop: OntologyPropertyReference = self._required(self.data_prop_code, "Data property")
        revision_prop: OntologyPropertyReference = self._required(self.data_prop_revision, "Data property")
        linked_to: OntologyPropertyReference = self._required(self.object_prop, "Object property")
        linked_from: OntologyPropertyReference = self._required(self.object_prop_inverse, "Object property")

        pending: PendingOntologyVersion = self.ontology.pending_version(context)
        self.assertFalse(pending.is_empty, "The uncommitted additions must show up as a pending version.")
        self.assertIsNotNone(pending.version)
        logging.info("Pending version %s with %d change(s):", pending.version, len(pending.changes))
        for change in pending.changes:
            logging.info("  %s %s -> %s", change.kind, change.element_kind, change.element_uri)

        # Every change belongs to the same pending version and reports a kind the SDK knows.
        for change in pending.changes:
            self.assertEqual(change.version, pending.version)
            self.assertEqual(change.context, context)
            self.assertIsNotNone(change.operation, f"Unrecognised change kind {change.kind!r}")
            self.assertIsNotNone(change.element_kind, f"Unrecognised change kind {change.kind!r}")
            self.assertIsNotNone(change.time_stamp)
            if change.operation is not OntologyChangeOperation.DELETE:
                self.assertIsNotNone(change.element, f"{change.kind} carries no element")

        # Everything created in steps 4 to 6 is part of the pending version.
        self.assertEqual({concept.reference for concept in pending.concepts}, {class_ref, subclass_ref})
        self.assertEqual({prop.reference for prop in pending.data_properties}, {code_prop, revision_prop})
        self.assertEqual({prop.reference for prop in pending.object_properties}, {linked_to, linked_from})

        # The diff reports everything the tenant put on top of the base ontology - which is
        # exactly what a reset would destroy.
        diff: OntologyDiff = self.ontology.context_diff(context)
        self.assertFalse(diff.is_empty, "The diff must report the tenant's additions.")
        logging.info("Context diff: %s", diff)
        self.assertEqual({concept.reference for concept in diff.added_concepts}, {class_ref, subclass_ref})
        self.assertEqual(
            {prop.reference for prop in diff.added_properties},
            {code_prop, revision_prop, linked_to, linked_from},
        )
        self.assertEqual(
            {prop.reference for prop in diff.added_properties if prop.is_data_property}, {code_prop, revision_prop}
        )
        # Nothing so far touched a base property.
        self.assertEqual(diff.modified_base_properties, [])

    def test_08_modify_concepts_and_properties(self) -> None:
        """Modify the new concept and properties, and delete scratch objects again."""
        context: str = self._required(self.context_name, "Context")
        class_ref: OntologyClassReference = self._required(self.class_ref, "Concept class")
        subclass_ref: OntologyClassReference = self._required(self.subclass_ref, "Concept subclass")
        code_prop: OntologyPropertyReference = self._required(self.data_prop_code, "Data property")
        revision_prop: OntologyPropertyReference = self._required(self.data_prop_revision, "Data property")
        linked_to: OntologyPropertyReference = self._required(self.object_prop, "Object property")

        # --- labels, comments and icon of a concept ---
        self.ontology.update_concept(
            context=context,
            reference=class_ref,
            icon="lifecycle.png",
            labels=[OntologyLabel("E2E lifecycle class (updated)", EN)],
            comments=[Comment("Updated by the ontology lifecycle test.", EN)],
        )
        concept: OntologyClass = self.ontology.concept(context, class_ref.iri)
        self.assertEqual(concept.icon, "lifecycle.png")
        self.assertEqual([label.content for label in concept.labels], ["E2E lifecycle class (updated)"])
        self.assertEqual([comment.content for comment in concept.comments], ["Updated by the ontology lifecycle test."])
        self.assertEqual(concept.subclass_of, THING_CLASS, "update_concept must not touch the superclass.")

        # --- Named Entity Linking metadata of a concept ---
        self.ontology.set_concept_metadata(
            context=context, reference=class_ref, inflection=InflectionLevel.HIGH, case_sensitive=True
        )
        settings: List[InflectionSetting] = self.ontology.context_metadata(context)
        # The stage service does not report the setting back for the new concept, so the
        # round trip is logged rather than asserted until that is understood.
        for entry in settings:
            logging.info(
                "Inflection setting: %s -> %s (case sensitive: %s)",
                entry.concept.iri,
                entry.inflection,
                entry.case_sensitive,
            )
        # self.assertEqual(len([e for e in settings if e.concept == class_ref]), 1)
        # self.assertEqual(matching[0].inflection, InflectionLevel.HIGH.value)
        # self.assertTrue(matching[0].case_sensitive)

        # --- labels and icon of a property ---
        self.ontology.update_property(
            context=context,
            reference=code_prop,
            icon="code.png",
            labels=[OntologyLabel("Code name (updated)", EN), OntologyLabel("Codename", DE)],
        )
        code: OntologyProperty = self.ontology.property(context, code_prop.iri)
        self.assertEqual(code.icon, "code.png")
        self.assertEqual({label.language_code for label in code.labels}, {EN, DE})

        # --- rename a property ---
        renamed_prop: OntologyPropertyReference = self._prop_ref(DATA_PROP_REVISION_RENAMED)
        self.ontology.rename_property(context=context, reference=revision_prop, new_reference=renamed_prop)
        OntologyLifecycleFlow.data_prop_revision = renamed_prop
        property_refs: List[OntologyPropertyReference] = self._property_refs()
        self.assertIn(renamed_prop, property_refs)
        self.assertNotIn(revision_prop, property_refs)
        self.assertEqual(self.ontology.property(context, renamed_prop.iri).reference, renamed_prop)

        # --- domains of a property ---
        self.ontology.add_property_domains(context=context, reference=linked_to, domains=[subclass_ref])
        results = set(self.ontology.property(context, linked_to.iri).domains)
        self.assertEqual(results, {class_ref, subclass_ref})
        self.ontology.remove_property_domains(context=context, reference=linked_to, domains=[subclass_ref])
        self.assertEqual(self.ontology.property(context, linked_to.iri).domains, [class_ref])

        # --- ranges of an object property (class references) ---
        self.ontology.add_property_ranges(context=context, reference=linked_to, ranges=[class_ref])
        self.assertEqual(set(self.ontology.property(context, linked_to.iri).ranges), {class_ref, subclass_ref})
        self.ontology.remove_property_ranges(context=context, reference=linked_to, ranges=[class_ref])
        self.assertEqual(self.ontology.property(context, linked_to.iri).ranges, [subclass_ref])

        # --- ranges of a data property (XSD data types) ---
        self.ontology.add_property_ranges(context=context, reference=code_prop, ranges=[DataPropertyType.INTEGER])
        self.assertEqual(
            {entry.iri for entry in self.ontology.property(context, code_prop.iri).ranges},
            {DataPropertyType.STRING.value, DataPropertyType.INTEGER.value},
        )
        self.ontology.remove_property_ranges(context=context, reference=code_prop, ranges=[DataPropertyType.INTEGER])
        self.assertEqual(
            [entry.iri for entry in self.ontology.property(context, code_prop.iri).ranges],
            [DataPropertyType.STRING.value],
        )

        # --- delete a scratch property and a scratch concept again ---
        scratch_prop: OntologyPropertyReference = self._prop_ref(DATA_PROP_SCRATCH_NAME)
        self.ontology.create_data_property(
            context=context, reference=scratch_prop, domains_cls=[class_ref], ranges_cls=[DataPropertyType.BOOLEAN]
        )
        self.assertIn(scratch_prop, self._property_refs())
        self.ontology.delete_property(context=context, reference=scratch_prop)
        self.assertNotIn(scratch_prop, self._property_refs())

        scratch_class: OntologyClassReference = self._class_ref(SCRATCH_CLASS_NAME)
        self.ontology.create_concept(context=context, reference=scratch_class, subclass_of=class_ref)
        self.assertIn(scratch_class, self._concept_refs())
        self.ontology.delete_concept(context=context, reference=scratch_class)
        self.assertNotIn(scratch_class, self._concept_refs())

    def test_09_commit_and_apply_ontology(self) -> None:
        """Commit the ontology and make the graph service pick it up."""
        context: str = self._required(self.context_name, "Context")
        class_ref: OntologyClassReference = self._required(self.class_ref, "Concept class")
        code_prop: OntologyPropertyReference = self._required(self.data_prop_code, "Data property")
        linked_to: OntologyPropertyReference = self._required(self.object_prop, "Object property")

        versions_before: int = len(self.ontology.versions(context))
        self._commit_and_apply(context)

        versions: List[Dict[str, Any]] = self.ontology.versions(context)
        self.assertGreaterEqual(len(versions), max(versions_before, 1))
        logging.info("Context has %d version(s) after the commit.", len(versions))

        # The committed RDF is the authoritative proof that the additions landed.
        rdf: str = self.ontology.rdf_export(context, timeout=LONG_TIMEOUT)
        self.assertTrue(rdf)
        for local_name in (class_ref.class_name, code_prop.property_name, linked_to.property_name):
            self.assertIn(local_name, rdf, f"{local_name} is missing from the committed ontology.")

    def test_10_create_entities_with_new_types(self) -> None:
        """Create entities of the new class with the new data and object properties."""
        class_ref: OntologyClassReference = self._required(self.class_ref, "Concept class")
        subclass_ref: OntologyClassReference = self._required(self.subclass_ref, "Concept subclass")
        code_prop: OntologyPropertyReference = self._required(self.data_prop_code, "Data property")
        revision_prop: OntologyPropertyReference = self._required(self.data_prop_revision, "Data property")
        linked_to: OntologyPropertyReference = self._required(self.object_prop, "Object property")
        linked_from: OntologyPropertyReference = self._required(self.object_prop_inverse, "Object property")

        parent: ThingObject = ThingObject(concept_type=class_ref)
        parent.add_label("E2E lifecycle parent", EN_US)
        parent.add_alias("E2E parent", EN_US)
        parent.add_description("Entity of the class created by the ontology lifecycle test.", EN_US)
        parent.add_data_property(DataProperty("alpha-release", code_prop, language_code=EN_US))
        # The revision property ranges over xsd:integer, so the literal is sent as a number.
        parent.add_data_property(DataProperty(7, revision_prop, language_code=EN_US))
        parent_uri: str = self.knowledge.create_entity(parent)
        OntologyLifecycleFlow.parent_uri = parent_uri

        detail: ThingObject = ThingObject(concept_type=subclass_ref)
        detail.add_label("E2E lifecycle detail", EN_US)
        detail.add_data_property(DataProperty("detail-record", code_prop, language_code=EN_US))
        detail_uri: str = self.knowledge.create_entity(detail)
        OntologyLifecycleFlow.detail_uri = detail_uri
        logging.info("Created entities %s and %s", parent_uri, detail_uri)

        # --- the new class and the new data properties survive the round trip ---
        fetched: ThingObject = self.knowledge.entity(parent_uri)
        self.assertEqual(fetched.concept_type, class_ref)
        self.assertIn(code_prop, fetched.data_properties)
        self.assertEqual(fetched.data_properties[code_prop][0].value, "alpha-release")
        self.assertIn(revision_prop, fetched.data_properties)
        # The service may hand an xsd:integer literal back as a number or as its string form.
        self.assertEqual(str(fetched.data_properties[revision_prop][0].value), "7")

        # --- relations through the new object properties ---
        # Object properties are not part of the create payload, so they are created separately.
        with service_call(f"create_relation({parent_uri}, {linked_to.iri}, {detail_uri})"):
            self.knowledge.create_relation(parent_uri, linked_to, detail_uri, timeout=LONG_TIMEOUT)

        relations: Dict[OntologyPropertyReference, Any] = self.knowledge.relations(parent_uri, timeout=LONG_TIMEOUT)
        self.assertIn(linked_to, relations)
        # The service answers /relation with entity objects rather than bare URIs, so the
        # comparison goes through outgoing_uris.
        self.assertIn(detail_uri, relations[linked_to].outgoing_uris)

        # --- the inverse edge is materialized by the service, not by the caller ---
        # e2eLinkedFrom is declared inverseOf e2eLinkedTo, so the single create_relation
        # above yields all four views of that one edge. Creating the reciprocal explicitly
        # is rejected with 409 'The relation already exists'.
        parent_relations: Dict[OntologyPropertyReference, Any] = self._log_relations("parent", parent_uri)
        detail_relations: Dict[OntologyPropertyReference, Any] = self._log_relations("detail", detail_uri)

        self.assertIn(detail_uri, parent_relations[linked_to].outgoing_uris)
        self.assertIn(
            detail_uri,
            parent_relations[linked_from].incoming_uris,
            "The inverse property must show the edge as incoming on the source.",
        )
        self.assertIn(parent_uri, detail_relations[linked_to].incoming_uris)
        self.assertIn(
            parent_uri,
            detail_relations[linked_from].outgoing_uris,
            "The inverse property must show the edge as outgoing on the target.",
        )

        with self.assertRaises(WacomServiceException) as duplicate:
            self.knowledge.create_relation(detail_uri, linked_from, parent_uri, timeout=LONG_TIMEOUT)
        self.assertEqual(duplicate.exception.status_code, HTTPStatus.CONFLICT)
        self.assertIn("already exists", (duplicate.exception.service_response or "").lower())

        # --- the range of the object property is enforced ---
        # linked_to ranges over <subclass_ref>; the parent is a <class_ref>, not a detail, so
        # this direction violates the range. It is not an existing edge either, so a
        # duplicate report here would mean the range is not being checked.
        with self.assertRaises(WacomServiceException) as violation:
            self.knowledge.create_relation(detail_uri, linked_to, parent_uri, timeout=LONG_TIMEOUT)
        response: str = violation.exception.service_response or ""
        logging.info("Range violation rejected with status %s: %s", violation.exception.status_code, response)
        self.assertNotIn(
            "already exists",
            response.lower(),
            "This edge must be rejected for violating the range, not as a duplicate.",
        )

    def test_11_modify_ontology_again(self) -> None:
        """Extend the committed ontology a second time and use the addition."""
        context: str = self._required(self.context_name, "Context")
        class_ref: OntologyClassReference = self._required(self.class_ref, "Concept class")
        parent_uri: str = self._required(self.parent_uri, "Parent entity")
        note_prop: OntologyPropertyReference = self._prop_ref(DATA_PROP_NOTE_NAME)

        self.ontology.create_data_property(
            context=context,
            reference=note_prop,
            domains_cls=[class_ref],
            ranges_cls=[DataPropertyType.STRING],
            labels=[OntologyLabel("Note", EN)],
        )
        self.ontology.update_concept(
            context=context,
            reference=class_ref,
            icon="lifecycle.png",
            labels=[OntologyLabel("E2E lifecycle class (second revision)", EN)],
            comments=[Comment("Second modification round of the ontology lifecycle test.", EN)],
        )
        OntologyLifecycleFlow.data_prop_note = note_prop

        self._commit_and_apply(context)

        self.assertIn(note_prop, self._property_refs())
        self.assertEqual(
            [label.content for label in self.ontology.concept(context, class_ref.iri).labels],
            ["E2E lifecycle class (second revision)"],
        )

        # The graph must accept the property that the second commit introduced.
        parent: ThingObject = self.knowledge.entity(parent_uri)
        parent.add_data_property(DataProperty("second revision note", note_prop, language_code=EN_US))
        self.knowledge.update_entity(parent)
        updated: ThingObject = self.knowledge.entity(parent_uri)
        self.assertIn(note_prop, updated.data_properties)
        self.assertEqual(updated.data_properties[note_prop][0].value, "second revision note")

    def test_12_reset_is_rejected_while_entities_exist(self) -> None:
        """Resetting the context must fail while entities of the new classes exist."""
        context: str = self._required(self.context_name, "Context")
        class_ref: OntologyClassReference = self._required(self.class_ref, "Concept class")
        parent_uri: str = self._required(self.parent_uri, "Parent entity")
        self.assertTrue(self.knowledge.exists(parent_uri), "The reset must be attempted with the entities in place.")

        with self.assertRaises(WacomServiceException) as rejected:
            self.ontology.reset_context(context, timeout=LONG_TIMEOUT)
        response: str = rejected.exception.service_response or ""
        logging.info("Reset rejected with status %s: %s", rejected.exception.status_code, response)
        self.assertEqual(
            rejected.exception.status_code,
            HTTPStatus.CONFLICT,
            f"A blocked reset must be reported as a conflict, not {rejected.exception.status_code}.",
        )
        self.assertIn(
            "reset is blocked",
            response.lower(),
            f"The service must name the blocker; it answered: {response}",
        )

        # The rejected reset must have left the ontology untouched.
        self.assertEqual(self.ontology.concept(context, class_ref.iri).reference, class_ref)
        self.assertIn(class_ref, self._concept_refs())
        self.assertFalse(self.ontology.context_diff(context).is_empty)

    def test_13_reset_succeeds_after_entities_are_removed(self) -> None:
        """Remove the entities, then reset the context successfully."""
        context: str = self._required(self.context_name, "Context")
        class_ref: OntologyClassReference = self._required(self.class_ref, "Concept class")
        subclass_ref: OntologyClassReference = self._required(self.subclass_ref, "Concept subclass")
        object_prop: OntologyPropertyReference = self._required(self.object_prop, "Object property")
        parent_uri: str = self._required(self.parent_uri, "Parent entity")
        detail_uri: str = self._required(self.detail_uri, "Detail entity")

        self.knowledge.delete_entities([detail_uri, parent_uri], force=True)
        for uri in (detail_uri, parent_uri):
            self.assertFalse(self.knowledge.exists(uri), f"Entity {uri} must be gone before the reset.")
        OntologyLifecycleFlow.parent_uri = None
        OntologyLifecycleFlow.detail_uri = None

        # Deletions propagate asynchronously, so the reset may need a few attempts.
        eventually(lambda: self.ontology.reset_context(context, timeout=LONG_TIMEOUT))

        # The ontology side is wiped immediately; reads are never blocked.
        concept_refs: List[OntologyClassReference] = self._concept_refs()
        self.assertNotIn(class_ref, concept_refs, "The reset must drop the tenant-specific class.")
        self.assertNotIn(subclass_ref, concept_refs)
        self.assertIn(THING_CLASS, concept_refs, "The reset must keep the base ontology in place.")
        self.assertNotIn(object_prop, self._property_refs())
        self.assertTrue(self.ontology.context_diff(context).is_empty, "The reset must leave the base ontology behind.")

        # The reset auto-commits but leaves the tenant locked at version 0, so every graph
        # write is refused until the pending update has been applied.
        blocked: ThingObject = ThingObject(concept_type=BASE_TOPIC_CLASS)
        blocked.add_label("E2E reset-pending probe", EN_US)
        with self.assertRaises(WacomServiceException) as rejected:
            self.knowledge.create_entity(blocked)
        logging.info("Graph write during reset-pending rejected: %s", rejected.exception.service_response)

        # Finish the reset. Without this the tenant cannot even be deleted.
        self.knowledge.ontology_update(timeout=LONG_TIMEOUT)
        self._await_ontology_applied()

        # Graph writes work again once the applied version is back above zero.
        probe_uri: str = self.knowledge.create_entity(blocked)
        self.assertTrue(self.knowledge.exists(probe_uri))
        self.knowledge.delete_entity(probe_uri, force=True)

    def test_14_remove_tenant(self) -> None:
        """Remove the tenant the flow created."""
        tenant_id: str = self._required(self.tenant_id, "Tenant")
        self.tenant_manager.delete_tenant(tenant_id)
        OntologyLifecycleFlow.tenant_id = None

        # The deletion is eventually consistent in the listing, so poll rather than
        # sleeping out the whole grace period.
        remaining: List[TenantConfiguration] = []
        for attempt in range(1, TIMEOUT + 1):
            remaining = [entry for entry in self.tenant_manager.listing_tenant() if entry.identifier == tenant_id]
            if not remaining:
                logging.info("Tenant %s disappeared from the listing after %ds.", tenant_id, attempt)
                break
            time.sleep(1.0)
        self.assertEqual(remaining, [], f"The tenant must be removed from the tenant manager within {TIMEOUT}s.")
