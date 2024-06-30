"""@private"""

from __future__ import annotations

from typing import Awaitable, Callable, Optional, Union

from nio import Event, MatrixRoom, AsyncClient, InviteMemberEvent

from .deps import Deps
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
    client: Optional[AsyncClient]

    def __init__(self,
                 handler: Union[Handler, Callable],
                 listener: Optional[Callable] = None) -> None:

        if isinstance(handler, Handler):
            self.nio_callback = handler.nio_callback
            self.callable = handler.callable
            self.callable_args = handler.callable_args
            self.original_callable_args = handler.original_callable_args
            self.listeners = handler.listeners
            self.deps = None
        else:
            self.nio_callback = None
            self.callable = handler
            self.callable_args = {}
            self.original_callable_args = {}
            self.listeners = []

        if listener is not None:
            self.listeners.append(listener)

    def eval_callback_args(self,
                           client: Optional[AsyncClient] = None,
                           deps: Optional[Deps] = None):
        if client is not None:
            self.client = client
        else:
            # noinspection PyUnusedLocal
            client = self.client

        async def callback(room: MatrixRoom, event: Event) -> None:
            for param, arg in self.original_callable_args.items():
                if isinstance(arg, EvalMe):
                    self.callable_args[param] = eval(arg.to_eval)
                if isinstance(arg, Deps):
                    self.callable_args[param] = self.deps

            await self.callable(**self.callable_args)

        self.nio_callback = callback
