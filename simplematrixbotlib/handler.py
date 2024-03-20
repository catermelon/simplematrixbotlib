from __future__ import annotations

from typing import Union, Callable


class Handler:
    callable: Callable
    listeners: list[Callable]
    prefix: Union[None, str]

    def __init__(self,
                 handler: Union[Handler, Callable],
                 listener: Union[None, Callable] = None,
                 middleware: Union[None, Callable] = None) -> None:

        if isinstance(handler, Handler):
            self.callable = handler.callable
            self.listeners = handler.listeners
            self.middleware = handler.middleware
            self.prefix = None
        else:
            self.callable = handler
            self.listeners = []
            self.middleware = []

        if listener is not None:
            self.listeners.append(listener)

        if middleware is not None:
            self.middleware.append(middleware)
