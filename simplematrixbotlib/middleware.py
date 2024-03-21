from typing import Union, Callable, Optional

from .handler import Handler


def prefix(handler: Union[Handler, Callable], _prefix: Optional[str] = None) -> Handler:
    handler = Handler(handler, middleware=prefix)
    if _prefix is not None:
        handler.prefix = _prefix
    return handler
