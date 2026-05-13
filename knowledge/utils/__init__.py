# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
""" "Utilities"""

# Note: ``wikidata`` is intentionally NOT re-exported here. The submodule is
# deprecated (see ``knowledge/utils/wikidata.py``) and re-exporting it would
# trigger its DeprecationWarning on every ``import knowledge`` — drowning out
# the signal for the few callers who actually use it. Explicit
# ``from knowledge.utils import wikidata`` still works and still warns.
__all__ = ["import_format", "graph", "wikipedia"]

from knowledge.utils import import_format
from knowledge.utils import graph
from knowledge.utils import wikipedia
