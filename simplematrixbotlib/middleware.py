from typing import Union, Callable

from .handler import Handler


def prefix(handler: Union[Handler, Callable], _prefix: Union[None, str] = None) -> Handler:
    handler = Handler(handler, middleware=prefix)
    if _prefix is not None:
        handler.prefix = _prefix
    return handler
