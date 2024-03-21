import logging

from asyncio import get_event_loop
from typing import Iterable, Union

from .callbacks import setup_callbacks
from .creds import Creds
from .handler import Handler

logger = logging.getLogger(__name__)


async def run_coroutine(creds: Creds, handlers: Iterable[Handler], prefix: Union[str, None] = None):
    client = await creds.get_valid_client()

    setup_callbacks(client=client, handlers=handlers, prefix=prefix)

    try:
        logger.info("Ready")
        await client.sync_forever(timeout=30_000)
    finally:
        await client.close()


def run(creds: Creds, handlers: Iterable[Handler], prefix: Union[str, None] = None):
    get_event_loop().run_until_complete(run_coroutine(creds, handlers, prefix))
