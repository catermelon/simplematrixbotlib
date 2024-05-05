from typing import Optional

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

    async def send_text(self, message_body: str, reply_to_event_id: Optional[str] = None):
        content = {
            "msgtype": "m.text",
            "body": message_body
        }
        if reply_to_event_id:
            try:
                content["m.relates_to"]
            except KeyError:
                content["m.relates_to"] = {}
            content["m.relates_to"]["m.in_reply_to"] = {
                "event_id": reply_to_event_id
            }
        await self.client.room_send(
            room_id=self.room_id,
            message_type="m.room.message",
            content=content
        )
