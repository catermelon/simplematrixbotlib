"""@private"""

from typing import Iterable, get_type_hints, Optional
from logging import getLogger

from nio import AsyncClient, RoomMessageText, InviteMemberEvent

from .bot import Bot
from .deps import Deps
from .eval_me import EvalMe
from .handler import Handler
from .message import Message
from .room import Room

logger = getLogger(__name__)


def message_wrapper(handler: Handler):
    logger.debug(f"Wrapping {handler.callable} for Message")
    for param, param_class in get_type_hints(handler.callable).items():
        if param_class is Message:
            handler.original_callable_args[param] = EvalMe("Message(event)")


def room_wrapper(handler: Handler):
    logger.debug(f"Wrapping {handler.callable} for Room")
    for param, param_class in get_type_hints(handler.callable).items():
        if param_class is Room:
            handler.original_callable_args[param] = EvalMe("Room(room, self.client)")


def bot_wrapper(handler: Handler):
    logger.debug(f"Wrapping {handler.callable} for Bot")
    for param, param_class in get_type_hints(handler.callable).items():
        if param_class is Bot:
            handler.original_callable_args[param] = EvalMe("Bot(self.client)")


def membership_change_wrapper(handler: Handler):
    logger.debug(f"Wrapping {handler.callable} for Membership Change)")
    for param, param_class in get_type_hints(handler.callable).items():
        if param_class is InviteMemberEvent:
            handler.original_callable_args[param] = EvalMe("event")


def setup_callbacks(
        client: AsyncClient, handlers: Iterable[Handler], deps: Optional[Deps]
) -> None:
    logger.debug(f"Setting up callbacks for handlers: {handlers}")
    room_message_text_callbacks = []
    room_membership_change_callbacks = []
    for handler in handlers:
        bot_wrapper(handler)
        for listener in handler.listeners:
            match listener.__name__:
                case 'on_text':
                    message_wrapper(handler)
                    room_wrapper(handler)
                    break
                case 'on_membership_change':
                    membership_change_wrapper(handler)
                    room_wrapper(handler)
                    break
        handler.eval_callback_args(client=client, deps=deps)
        for listener in handler.listeners:
            match listener.__name__:
                case 'on_text':
                    room_message_text_callbacks.append(handler.nio_callback)
                    break
                case 'on_membership_change':
                    room_membership_change_callbacks.append(handler.nio_callback)
                    break
    for callback in room_message_text_callbacks:
        client.add_event_callback(callback, RoomMessageText)
    for callback in room_membership_change_callbacks:
        client.add_event_callback(callback, InviteMemberEvent) # type: ignore
