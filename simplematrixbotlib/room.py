from typing import Optional

import markdown

from nio import MatrixRoom, AsyncClient


class Room:
    def __init__(self, room: MatrixRoom, client: AsyncClient) -> None:
        """@private"""
        self.room_id = room.room_id
        self.name = room.name
        self.summary = room.summary
        self.topic = room.topic
        self.room_version = room.room_version
        self.client = client
        self.nio_room = room

    def __repr__(self):
        return f"{self.room_id}: {self.name}"

    async def send_text(self, message_body: str, format_as_markdown: bool = False, reply_to_event_id: Optional[str] = None, room_id: Optional[str] = None):
        if not room_id:
            room_id = self.room_id

        content = {
            "msgtype": "m.text",
            "body": message_body
        }

        if format_as_markdown:
            content.update({
                "format": "org.matrix.custom.html",
                "formatted_body": markdown.markdown(message_body,
                                                    extensions=["sane_lists", "fenced_code", "nl2br"])
            })

        if reply_to_event_id:
            try:
                content["m.relates_to"]
            except KeyError:
                content["m.relates_to"] = {} # type: ignore
            content["m.relates_to"]["m.in_reply_to"] = { # type: ignore
                "event_id": reply_to_event_id
            }

        await self.client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content=content
        )

    async def join(self):
        await self.client.join(self.room_id)
