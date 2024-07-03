import logging

from asyncio import get_event_loop
from typing import List, Optional

from nio import AsyncClient, InviteMemberEvent

from .callbacks import setup_callbacks
from .creds import Creds
from .config import Config
from .deps import Deps
from .handler import Handler
from .listeners import on_membership_change
from .room import Room

logger = logging.getLogger(__name__)
"""@private"""


@on_membership_change
async def join_room_on_invite_handler(room: Room, event: InviteMemberEvent):
    if event.membership == 'invite':
        await room.join()


async def run_async(creds: Creds, handlers: List[Handler], config: Config, deps: Optional[Deps] = None):
    config.log()

    client: AsyncClient = await creds.get_valid_client() # type: ignore

    if config.join_room_on_invite_enabled:
        handlers.append(join_room_on_invite_handler)

    setup_callbacks(client=client, handlers=handlers, deps=deps)

    try:
        logger.info("Ready")
        await client.sync_forever(timeout=30_000)
    finally:
        await client.close()


def run(creds: Creds, handlers: List[Handler], config: Config = Config(), deps: Optional[Deps] = None):
    get_event_loop().run_until_complete(run_async(creds, handlers, config, deps))
