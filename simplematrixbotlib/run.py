import logging

from asyncio import get_event_loop
from typing import Iterable, Union

from .creds import Creds
from .handler import Handler

logger = logging.getLogger(__name__)


async def run_coroutine(creds: Creds, handlers: Iterable[Handler], prefix: Union[str, None] = None):
    client = await creds.get_valid_client()

    for handler in handlers:
        if not hasattr(handler, "listeners"):
            await client.close()
            raise ValueError("Handler coroutines must have 1 or more listeners")

    await client.close()


def run(creds: Creds, handlers: Iterable[Handler], prefix: Union[str, None] = None):
    get_event_loop().run_until_complete(run_coroutine(creds, handlers, prefix))
