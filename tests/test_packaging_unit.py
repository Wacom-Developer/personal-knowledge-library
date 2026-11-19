# -*- coding: utf-8 -*-
# Copyright © 2026-present Wacom. All rights reserved.
"""Packaging tests — what the build backend actually puts in the distribution.

These read the artifacts already in ``dist/`` rather than invoking a builder, so they run
offline in well under a second. They skip when ``dist/`` is empty, which keeps the unit
suite green for anyone who has not built.

Build first with::

    uv build
"""

import os
import re
import tarfile
import zipfile
from email.message import Message
from email.parser import BytesParser
from pathlib import Path
from typing import List

import pytest
from packaging.specifiers import SpecifierSet

REPO_ROOT: Path = Path(__file__).resolve().parent.parent
DIST: Path = REPO_ROOT / "dist"

#: Directories that must never reach PyPI. The source tree holds ~12 MB of them, and a
#: build backend left on its defaults would ship the lot.
SDIST_FORBIDDEN_TOP_LEVEL: frozenset = frozenset({"assets", "tests", "docs", "samples", "scrapping", "pkl-cache"})

#: Everything the 5.1.1 sdist contained at top level, built with poetry-core, plus
#: ``.gitignore``: hatchling force-includes the VCS ignore file in every sdist and ignores
#: an ``exclude`` for it. It is a public, secret-free file, so it is the one accepted
#: difference from the poetry-core baseline.
SDIST_EXPECTED_TOP_LEVEL: frozenset = frozenset(
    {"knowledge", "README.md", "LICENSE", "pyproject.toml", "PKG-INFO", ".gitignore"}
)

#: Extras a consumer can install: ``pip install personal-knowledge-library[cache]``.
EXPECTED_EXTRAS: frozenset = frozenset({"dev", "cache"})

EXPECTED_PYTHON_RANGE: SpecifierSet = SpecifierSet(">=3.10,<4.0")


def _sole_artifact(pattern: str) -> Path:
    """Return the one artifact matching ``pattern``.

    Skips locally when nothing has been built, so the unit suite stays green for anyone who
    has not run ``uv build``. Under CI it fails instead: this is the gate that stands between
    a mis-pinned sdist and PyPI, and a gate that can pass by skipping is not a gate.
    """
    hits: List[Path] = sorted(DIST.glob(pattern))
    if not hits:
        if os.environ.get("CI"):
            pytest.fail(f"no {pattern} in dist/ — the distribution must be built before it is verified")
        pytest.skip(f"no {pattern} in dist/ — run `uv build` first")
    assert len(hits) == 1, f"expected exactly one {pattern} in dist/, found {[h.name for h in hits]}"
    return hits[0]


@pytest.fixture(scope="module")
def wheel_names() -> List[str]:
    """Every member path inside the built wheel."""
    with zipfile.ZipFile(_sole_artifact("*.whl")) as archive:
        return sorted(archive.namelist())


@pytest.fixture(scope="module")
def sdist_names() -> List[str]:
    """Every member path inside the built sdist, with the version prefix directory stripped."""
    with tarfile.open(_sole_artifact("*.tar.gz")) as archive:
        return sorted(name.split("/", 1)[1] for name in archive.getnames() if "/" in name)


@pytest.fixture(scope="module")
def wheel_metadata() -> Message:
    """The wheel's ``.dist-info/METADATA``, parsed."""
    with zipfile.ZipFile(_sole_artifact("*.whl")) as archive:
        metadata_name = next(n for n in archive.namelist() if n.endswith(".dist-info/METADATA"))
        with archive.open(metadata_name) as handle:
            return BytesParser().parse(handle)


def _source_modules() -> frozenset:
    """Every importable module in the source tree, as it would appear inside a wheel."""
    return frozenset(
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "knowledge").rglob("*.py")
        if "__pycache__" not in path.parts
    )


def test_wheel_contains_every_source_module(wheel_names: List[str]) -> None:
    """The wheel ships every module in knowledge/, and the backend swap loses none."""
    packaged = frozenset(name for name in wheel_names if name.startswith("knowledge/"))

    assert packaged == _source_modules()


def test_wheel_ships_nothing_but_the_package_and_its_metadata(wheel_names: List[str]) -> None:
    """Nothing outside knowledge/ and .dist-info/ rides along in the wheel."""
    strays = [name for name in wheel_names if not name.startswith("knowledge/") and ".dist-info/" not in name]

    assert strays == []


def test_sdist_excludes_the_development_tree(sdist_names: List[str]) -> None:
    """assets/, tests/, docs/ and samples/ do not get published."""
    top_level = {name.split("/", 1)[0] for name in sdist_names}

    assert top_level & SDIST_FORBIDDEN_TOP_LEVEL == set()


def test_sdist_contents_match_the_poetry_core_baseline(sdist_names: List[str]) -> None:
    """The sdist carries exactly what 5.1.1 carried: the package plus four metadata files."""
    top_level = {name.split("/", 1)[0] for name in sdist_names}

    assert top_level == SDIST_EXPECTED_TOP_LEVEL


def test_sdist_contains_every_source_module(sdist_names: List[str]) -> None:
    """A consumer building from source gets the whole package."""
    packaged = frozenset(name for name in sdist_names if name.startswith("knowledge/") and name.endswith(".py"))

    assert packaged == _source_modules()


def test_wheel_metadata_declares_both_extras(wheel_metadata: Message) -> None:
    """`pip install personal-knowledge-library[cache]` still resolves from the built metadata."""
    assert frozenset(wheel_metadata.get_all("Provides-Extra") or []) == EXPECTED_EXTRAS


def test_wheel_declares_the_supported_python_range(wheel_metadata: Message) -> None:
    """Requires-Python survives the backend swap; compared parsed, since backends reorder clauses."""
    assert SpecifierSet(wheel_metadata["Requires-Python"]) == EXPECTED_PYTHON_RANGE


def test_lock_resolves_for_every_supported_python() -> None:
    """uv.lock covers the whole requires-python range, not just the interpreter that wrote it.

    CI runs the matrix down to 3.10 while the lock is usually generated on a newer
    interpreter, so a lock pinned narrower than the project would fail only in CI.
    """
    lock = REPO_ROOT / "uv.lock"
    assert lock.exists(), "uv.lock is missing — run `uv lock`"

    # Read the first top-level requires-python; it precedes every [[package]] table.
    # Parsed by regex rather than tomllib, which does not exist on Python 3.10.
    declared = re.search(r'^requires-python = "([^"]+)"', lock.read_text(encoding="utf-8"), re.MULTILINE)

    assert declared is not None, "uv.lock declares no requires-python"
    assert SpecifierSet(declared.group(1)) == EXPECTED_PYTHON_RANGE


def test_lock_contains_the_project_itself() -> None:
    """The lock describes this package, so `uv sync` installs it rather than only its dependencies."""
    assert 'name = "personal-knowledge-library"' in (REPO_ROOT / "uv.lock").read_text(encoding="utf-8")


def _declared_version(text: str) -> str:
    """The first ``version = "..."`` following the project's own package entry."""
    after_project = text.split('name = "personal-knowledge-library"', 1)[-1]
    match = re.search(r'^version = "([^"]+)"', after_project, re.MULTILINE)
    assert match is not None, "uv.lock has no version for the project"
    return match.group(1)


def test_lock_is_in_step_with_pyproject() -> None:
    """A stale lock must fail here, not in a release.

    ``uv sync --frozen`` does not check this — it skips the up-to-dateness check entirely —
    so a lock left behind by a version bump or a dependency change ships silently. This is
    the guard that caught exactly that.
    """
    pyproject_version = re.search(
        r'^version = "([^"]+)"', (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.MULTILINE
    )
    assert pyproject_version is not None

    assert _declared_version((REPO_ROOT / "uv.lock").read_text(encoding="utf-8")) == pyproject_version.group(1)


def test_lock_does_not_carry_retired_dev_tools() -> None:
    """tox left the dev extra; a lock still pinning it means the lock was never regenerated."""
    assert '\nname = "tox"\n' not in (REPO_ROOT / "uv.lock").read_text(encoding="utf-8")
