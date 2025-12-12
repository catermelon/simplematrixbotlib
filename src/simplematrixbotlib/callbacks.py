import nio.events.room_events
import nio.events.to_device
from nio import InviteMemberEvent
from nio import MegolmEvent, KeyVerificationStart, KeyVerificationCancel, KeyVerificationKey, KeyVerificationMac, ToDeviceError, KeyVerificationEvent, LocalProtocolError

import logging

logger = logging.getLogger(__name__)


class Callbacks:
    """
    A class for handling callbacks.

    ...

    """

    def __init__(self, async_client, bot):
        self.async_client = async_client
        self.bot = bot

    async def setup_callbacks(self):
        """
        Add callbacks to async_client

        """
        if self.bot.config.join_on_invite:
            self.async_client.add_event_callback(self.invite_callback,
                                                 InviteMemberEvent)

        self.async_client.add_event_callback(self.decryption_failure,
                                             MegolmEvent)

        if self.bot.config.emoji_verify:
            self.async_client.add_to_device_callback(self.emoji_verification,
                                                     (KeyVerificationEvent, ))

        for event_listener in self.bot.listener._registry:
            if issubclass(event_listener[1],
                          nio.events.to_device.ToDeviceEvent):
                self.async_client.add_to_device_callback(
                    event_listener[0], event_listener[1])
            else:
                self.async_client.add_event_callback(event_listener[0],
                                                     event_listener[1])

    async def invite_callback(self, room, event, tries=1):
        """
        Callback for handling invites.

        Parameters
        ----------
        room : nio.rooms.MatrixRoom
        event : nio.events.room_events.InviteMemberEvent
        tries : int, optional
            Amount of times that this function has been called in a row for the same exact event.

        """
        if not event.membership == "invite":
            return

        try:
            await self.async_client.join(room.room_id)
            logger.info(f"Joined {room.room_id}")
        except Exception as e:
            logger.warning(f"Error joining {room.room_id}: {e}")
            tries += 1
            if not tries == 3:
                logger.debug("Trying again...")
                await self.invite_callback(room, event, tries)
            else:
                logger.error(f"Failed to join {room.room_id} after 3 tries")

    async def decryption_failure(self, room, event):
        """
        Callback for handling decryption errors.

        Parameters
        ----------
        room : nio.rooms.MatrixRoom
        event : nio.events.room_events.MegolmEvent

        """
        if not isinstance(event, MegolmEvent):
            return

        logger.warning(
            f"\nFailed to decrypt message: {event.event_id} from {event.sender} in {room.room_id}. "
            "If this error persists despite verification, reset the crypto session by deleting "
            f"{self.bot.config.store_path} and {self.bot.creds._session_stored_file}. "
            "You will have to verify any verified devices anew.\n")
        if self.bot.config._decrypt_failure_msg:
            await self.bot.api.send_text_message(
                room.room_id, "Failed to decrypt your message. "
                "Make sure encryption is enabled in my config and "
                "either enable sending messages to unverified devices or verify me if possible.",
                msgtype='m.notice')

