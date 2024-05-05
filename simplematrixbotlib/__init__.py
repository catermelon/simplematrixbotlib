"""
.. include:: ../README.md
.. include:: ../SECURITY.md
.. include:: ../CONTRIBUTING.md
.. include:: ../CONDUCT.md
"""

__version__ = "3.0.0-dev"

from .bot import Bot
from .creds import Creds
from .defaults import DATA_PATH
from .deps import Deps
from .listeners import on_text
from .message import Message
from .room import Room
from .run import run
