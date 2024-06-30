"""
.. include:: ../README.md
.. include:: ../SECURITY.md
.. include:: ../CONTRIBUTING.md
.. include:: ../CONDUCT.md
"""

__version__ = "3.0.0-dev"

from .bot import Bot
from .creds import Creds
from .config import Config
from .deps import Deps
from .listeners import on_text, on_membership_change
from .message import Message
from .room import Room
from .run import run
