"""@private"""

from types import MappingProxyType
from typing import Union, Callable

from nio import RoomMessageText

from .handler import Handler


def on_text(handler: Union[Handler, Callable]) -> Handler:
    return Handler(handler, listener=on_text)


LISTENER_EVENT_MAPPING = MappingProxyType({
    on_text: RoomMessageText
})
