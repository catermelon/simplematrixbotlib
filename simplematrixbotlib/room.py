from typing import Optional, Literal

import asyncio
import markdown
import mimetypes
import os
import aiofiles.os

from nio import MatrixRoom, AsyncClient


async def ffprobe(path: str, entries: str):
    process = await asyncio.create_subprocess_exec("ffprobe.exe" if os.name == "nt" else "ffprobe",
                                                   "-i",
                                                   path,
                                                   "-show_entries",
                                                   entries,
                                                   "-v",
                                                   "quiet",
                                                   "-of",
                                                   "csv=p=0",
                                                   stdout=asyncio.subprocess.PIPE)
    stdout = await process.stdout.read()
    return stdout.decode().strip()


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

    async def send_media(self, filepath: str, filetype: Optional[Literal[str]] = None, room_id: Optional[str] = None):
        if not room_id:
            room_id = self.room_id

        mime_type = mimetypes.guess_type(filepath)[0]

        if not filetype:
            filetype = "file"
            if mime_type and mime_type.split("/")[0] in ("video", "audio", "image"):
                filetype = mime_type.split("/")[0]

        basename = os.path.basename(filepath)

        file_stat = await aiofiles.os.stat(filepath)
        async with aiofiles.open(filepath, "r+b") as file:
            resp, _ = await self.client.upload(
                file,
                content_type=mime_type,
                filename=basename,
                filesize=file_stat.st_size
            )

        content = {
            "body": basename,
            "info": {
                "size": file_stat.st_size,
                "mimetype": mime_type,
            },
            "msgtype": "m."+filetype,
            "url": resp.content_uri
        }

        if filetype in ("video", "audio"):
            content["info"]["duration"] = int(float(await ffprobe(filepath, "format=duration") * 1000))
        if filetype in ("image", "video"):
            (width, height) = await ffprobe(filepath, "stream=width,height").split(",")
            content["info"].append({"w": width, "h": height})

        await self.client.room_send(room_id, "m.room.message", content)

    async def join(self):
        await self.client.join(self.room_id)
