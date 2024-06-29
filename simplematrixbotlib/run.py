import logging

from asyncio import get_event_loop
from typing import Iterable, Optional

from nio import AsyncClient

from .callbacks import setup_callbacks
from .creds import Creds
from .config import Config
from .deps import Deps
from .handler import Handler

logger = logging.getLogger(__name__)
"""@private"""


async def run_async(creds: Creds, handlers: Iterable[Handler], deps: Optional[Deps] = None):
    client: AsyncClient = await creds.get_valid_client()

    setup_callbacks(client=client, handlers=handlers, deps=deps)

    try:
        logger.info("Ready")
        await client.sync_forever(timeout=30_000)
    finally:
        await client.close()


def run(creds: Creds, handlers: Iterable[Handler], config: Config = Config(), deps: Optional[Deps] = None):
    get_event_loop().run_until_complete(run_async(creds, handlers, deps))
