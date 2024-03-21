from __future__ import annotations

from typing import Awaitable, Callable, Optional, Union

from nio import Event, MatrixRoom, AsyncClient

from .eval_me import EvalMe
# noinspection PyUnresolvedReferences
from .bot import Bot
# noinspection PyUnresolvedReferences
from .message import Message
# noinspection PyUnresolvedReferences
from .room import Room


class Handler:
    nio_callback: Optional[Callable[[MatrixRoom, Event], Optional[Awaitable[None]]]]
    callable: Callable
    callable_args: dict
    original_callable_args: dict
    listeners: list[Callable]
    prefix: Optional[str]
    client: Optional[AsyncClient]

    def __init__(self,
                 handler: Union[Handler, Callable],
                 listener: Optional[Callable] = None,
                 middleware: Optional[Callable] = None) -> None:

        if isinstance(handler, Handler):
            self.nio_callback = handler.nio_callback
            self.callable = handler.callable
            self.callable_args = handler.callable_args
            self.original_callable_args = handler.original_callable_args
            self.listeners = handler.listeners
            self.middleware = handler.middleware
            self.prefix = None
        else:
            self.nio_callback = None
            self.callable = handler
            self.callable_args = {}
            self.original_callable_args = {}
            self.listeners = []
            self.middleware = []

        if listener is not None:
            self.listeners.append(listener)

        if middleware is not None:
            self.middleware.append(middleware)

    def eval_callback_args(self,
                           client: Optional[AsyncClient] = None,
                           prefix: Optional[str] = None):
        if client is not None:
            self.client = client
        else:
            # noinspection PyUnusedLocal
            client = self.client

        if prefix is not None:
            self.prefix = prefix
        else:
            # noinspection PyUnusedLocal
            prefix = self.prefix

        async def callback(room: MatrixRoom, event: Event) -> None:
            for param, arg in self.original_callable_args.items():
                if isinstance(arg, EvalMe):
                    self.callable_args[param] = eval(arg.to_eval)
            await self.callable(**self.callable_args)

        self.nio_callback = callback
