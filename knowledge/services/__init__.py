# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom. All rights reserved.
from knowledge import __version__

USER_AGENT_STR: str = f"Personal Knowledge Library/{__version__}" \
                      "(+https://github.com/Wacom-Developer/personal-knowledge-library)"

__all__ = ['base', 'graph', 'ontology', 'tenant', 'users', 'USER_AGENT_STR']

from knowledge.services import base
from knowledge.services import graph
from knowledge.services import ontology
from knowledge.services import tenant
from knowledge.services import users
