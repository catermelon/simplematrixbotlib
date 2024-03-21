from typing import Iterable, get_type_hints, Optional
from logging import getLogger

from nio import AsyncClient, RoomMessageText

from .bot import Bot
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
            handler.original_callable_args[param] = EvalMe("Bot(self.client, self.prefix)")


def setup_callbacks(
        client: AsyncClient, handlers: Iterable[Handler], prefix: Optional[str] = None
) -> None:
    logger.debug(f"Setting up callbacks for handlers: {handlers}")
    room_message_text_callbacks = []
    for handler in handlers:
        bot_wrapper(handler)
        for listener in handler.listeners:
            match listener:
                case on_text:
                    message_wrapper(handler)
                    room_wrapper(handler)
        handler.eval_callback_args(client=client, prefix=prefix)
        for listener in handler.listeners:
            match listener:
                case on_text:
                    room_message_text_callbacks.append(handler.nio_callback)
                    break
    for callback in room_message_text_callbacks:
        client.add_event_callback(callback, RoomMessageText)
