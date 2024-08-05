from typing import Optional, Literal, Union
from collections.abc import Iterable
from uuid import uuid4

import asyncio
import markdown
import mimetypes
import os
import aiofiles.os

from nio import (MatrixRoom,
                 AsyncClient,
                 RoomSendResponse,
                 RoomSendError,
                 RoomLeaveResponse,
                 RoomLeaveError,
                 RoomForgetResponse,
                 RoomForgetError)


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

    async def send_text(self, message_body: str, format_as_markdown: bool = False, reply_to_event_id: Optional[str] = None, room_id: Optional[str] = None) -> Union[RoomSendResponse, RoomSendError]:
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

        return await self.client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content=content
        )

    async def send_media(self, filepath: str, filetype: Optional[Literal[str]] = None, room_id: Optional[str] = None) -> Union[RoomSendResponse, RoomSendError]:
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

        return await self.client.room_send(room_id, "m.room.message", content)

    async def send_reaction(self, event_id: str, key: str, room_id: Optional[str] = None) -> Union[RoomSendResponse, RoomSendError]:
        """
        Send a reaction to a message in a Matrix room.

        Returns the homeserver's response.

        Parameters
        ----------
        event_id : str
            The event id of the event you want to react to.

        key: str
            The content of the reaction. This is usually an emoji, but may technically be any text.

        room_id : str, optional
            The room id of the destination of the message.
        """
        if not room_id:
            room_id = self.room_id

        return await self.client.room_send(
            room_id=room_id,
            message_type="m.reaction",
            content={
                "m.relates_to": {
                    "event_id": event_id,
                    "key": key,
                    "rel_type": "m.annotation"
                }
            }
        )

    async def send_location_message(self, uri: str, location_description: Optional[str] = None, message: Optional[str] = None, room_id: Optional[str] = None) -> Union[RoomSendResponse, RoomSendError]:
        """
        Send a location message in a Matrix room.

        Returns the homeserver's response.

        Parameters
        ----------
        uri : str
            The geo URI scheme of the location.

        location_description : str, optional
            The description of the location, default uri

        message : str, optional
            The body of the message to be sent, default uri

        room_id : str, optional
            The room id of the destination of the message.
        """
        if not room_id:
            room_id = self.room_id

        content = {
            "msgtype": "m.location",
            "body": uri,
            "geo_uri": uri,
            "org.matrix.msc3488.location": {
                "uri": uri,
                "description": uri
            },
            "org.matrix.msc1767.text": uri,
        }

        if location_description:
            content["org.matrix.msc3488.location"]["description"] = location_description

        if message:
            content["body"] = message
            content["org.matrix.msc1767.text"] = message

        return await self.client.room_send(room_id, "m.room.message", content)

    async def start_poll(self, question: str, answers: Iterable, disclosed: bool = True, max_selections: int = 1, room_id: Optional[str] = None) -> Union[RoomSendResponse, RoomSendError]:
        """
        Start a poll in a Matrix room.

        Returns the homeserver's response.

        Parameters
        ----------
        question : str
            The content of the question to be sent.

        answers : Iterable
            The answers of the poll to be sent.

        disclosed : bool, optional
            Whether the poll is disclosed, default True

        max_selections : int, optional
            The maximum number of answers to be selected, default 1

        room_id : str, optional
            The room id of the destination of the poll.
        """
        if not room_id:
            room_id = self.room_id

        content = {
            "body": "",
            "org.matrix.msc3381.poll.start": {
                "question": {
                    "org.matrix.msc1767.text": question
                },
                "kind": "org.matrix.msc3381.poll.disclosed",
                "max_selections": max_selections,
                "answers": []
            }
        }

        if not disclosed:
            content["org.matrix.msc3381.poll.start"]["kind"] = "org.matrix.msc3381.poll.undisclosed"

        for answer in answers:
            content["org.matrix.msc3381.poll.start"]["answers"].append({
                "id": str(uuid4()),
                "org.matrix.msc1767.text": answer
            })

        return await self.client.room_send(room_id, "org.matrix.msc3381.poll.start", content)

    async def end_poll(self, event_id: str, room_id: Optional[str] = None):
        """
        End a poll in a Matrix room.

        Parameters
        ----------
        event_id : str
            The event id of the poll you want to end.

        room_id : str, optional
            The room id of the destination of the poll.
        """
        if not room_id:
            room_id = self.room_id

        await self.client.room_send(room_id, "org.matrix.msc3381.poll.end", {
            "body": "",
            "m.relates_to": {
                "rel_type": "m.reference",
                "event_id": event_id
            },
            "org.matrix.msc1767.text": "Ended poll"
        })

    async def ban(self, user_id: str, reason: Optional[str] = None, room_id: Optional[str] = None):
        """
        Ban a user in a Matrix room.

        Parameters
        ----------
        user_id : str
            The user id of the user that should be banned.

        reason : str, optional
            A reason for which the user is banned.

        room_id : str, optional
            The room id of the room that the user will be banned from.
        """
        if not room_id:
            room_id = self.room_id

        await self.client.room_ban(room_id, user_id, reason)

    async def unban(self, user_id: str, room_id: Optional[str] = None):
        """
        Unban a user in a Matrix room.

        Parameters
        ----------
        user_id : str
            The user id of the user that should be unbanned.

        room_id : str, optional
            The room id of the room that the user will be unbanned from.
        """
        if not room_id:
            room_id = self.room_id

        await self.client.room_unban(room_id, user_id)

    async def kick(self, user_id: str, reason: Optional[str] = None, room_id: Optional[str] = None):
        """
        Kick a user in a Matrix room.

        Parameters
        ----------
        user_id : str
            The user id of the user that should be kicked.

        reason : str, optional
            A reason for which the user is banned.

        room_id : str, optional
            The room id of the room that the user will be kicked from.
        """
        if not room_id:
            room_id = self.room_id

        await self.client.room_kick(room_id, user_id, reason)

    async def invite(self, user_id: str, room_id: Optional[str] = None):
        """
        Invite a user into a Matrix room.

        Parameters
        ----------
        user_id : str
            The user id of the user that should be invited.

        room_id : str, optional
            The room id of the room that the user will be invited to.
        """
        if not room_id:
            room_id = self.room_id

        await self.client.room_invite(room_id, user_id)

    async def redact(self, event_id: str, reason: Optional[str] = None, room_id: Optional[str] = None):
        """
        Redact an event in a Matrix room.

        Parameters
        ----------
        event_id : str
            The event id of the event you want to redact.

        reason : str, optional
            A reason for which the user is redacted.

        room_id : str, optional
            The room id of the room that the event will be redacted from.
        """
        if not room_id:
            room_id = self.room_id

        await self.client.room_redact(room_id, event_id, reason)

    async def edit(self, event_id: str, message_body: str, format_as_markdown: bool = False, room_id: Optional[str] = None):
        """
        Edit an event in a Matrix room.

        Parameters
        ----------
        event_id : str
            The event id of the event you want to edit.

        message_body : str
            The new content of the message to be sent.

        format_as_markdown : bool, optional
            Whether the new message should be markdown, default False.

        room_id : str, optional
            The room id of the destination of the message.
        """
        if not room_id:
            room_id = self.room_id

        content = {
            "msgtype": "m.text",
            "body": "* "+message_body,
            "m.relates_to": {
                "rel_type": "m.replace",
                "event_id": event_id
            },
            "m.new_content": {
                "msgtype": "m.text",
                "body": message_body
            }
        }

        if format_as_markdown:
            md = markdown.markdown(message_body,
                                   extensions=["sane_lists", "fenced_code", "nl2br"])

            content["body"] = "* "+message_body
            content["m.new_content"]["body"] = message_body

            content["m.new_content"].append({
                    "format": "org.matrix.custom.html",
                    "formatted_body": md
                })

        await self.client.room_send(room_id, "m.room.message", content)

    async def change_power_level(self, power_level: int, user_id: str, room_id: Optional[str] = None):
        """
        Change the power level of a user in a Matrix room.

        Parameters
        ----------
        power_level : int
            The power level.

        user_id : str
            The user id of the user who will be given a new power level.

        room_id : str, optional
            The room id of the room where the power level will be changed.
        """
        if not room_id:
            room_id = self.room_id

        response = await self.client.room_get_state(room_id)

        content = response.events[-1]["content"]
        content["users"][user_id] = power_level

        await self.client.room_put_state(room_id, "m.room.power_levels", content)

    async def leave(self, forget: bool = True, room_id: Optional[str] = None) -> Union[RoomLeaveResponse, RoomLeaveError] | Optional[tuple[Union[RoomLeaveResponse, RoomLeaveError], Union[RoomForgetResponse, RoomForgetError]]]:
        """
        Leave a Matrix room.

        Returns the homeserver's response.

        Parameters
        ----------
        forget : bool, optional
            Whether to forget the room, default True.

        room_id : str, optional
            The room id of the room to leave.
        """
        if not room_id:
            room_id = self.room_id

        leave_response = await self.client.room_leave(room_id)

        if forget:
            forget_response = await self.client.room_forget(room_id)
            return leave_response, forget_response

        return leave_response

    async def join(self):
        await self.client.join(self.room_id)
