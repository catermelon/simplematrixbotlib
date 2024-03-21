from __future__ import annotations

import json
import os
from asyncio import get_event_loop
from logging import getLogger
from typing import Optional

from nio import AsyncClient, LoginError, SyncError

from .defaults import DATA_PATH

logger = getLogger(__name__)

creds_path = os.path.join(DATA_PATH, "creds.json")


def format_homeserver_url(homeserver: str) -> str:
    # noinspection HttpUrlsUsage
    if homeserver.startswith("http://") or homeserver.startswith("https://"):
        return homeserver
    else:
        return "https://" + homeserver


def get_stored_access_token() -> Optional[str]:
    os.makedirs(DATA_PATH, exist_ok=True)
    if os.path.exists(creds_path):
        with open(creds_path, "r") as f:
            data = json.load(f)
            try:
                return data["access_token"]
            except KeyError:
                return None
    return None


def store_access_token(access_token: str) -> None:
    logger.debug(
        f"Storing access token: {access_token[:7]}...{access_token[-3:]} to {creds_path}"
    )

    os.makedirs(DATA_PATH, exist_ok=True)

    data = {}
    if os.path.exists(creds_path):
        with open(creds_path, "r") as f:
            data = json.load(f)

    data["access_token"] = access_token
    with open(creds_path, "w") as f:
        json.dump(data, f)


class Creds:
    homeserver: str
    user: str
    access_token: str
    regenerate_if_invalid: bool

    def __init__(self, homeserver: str, user: str, access_token: str):
        self.homeserver = format_homeserver_url(homeserver)
        self.user = user
        self.access_token = access_token

    async def get_valid_client(self) -> Optional[AsyncClient]:
        client = AsyncClient(homeserver=self.homeserver, user=self.user, store_path=f"{DATA_PATH}/store")
        client.access_token = self.access_token
        resp = await client.sync(timeout=10)
        if isinstance(resp, SyncError):
            return None
        store_access_token(self.access_token)
        logger.debug("Successfully confirmed valid access token")
        return client

    @classmethod
    def from_args(cls, homeserver: str, user: str, password: str, regenerate_if_invalid: bool = True) -> Creds:
        homeserver = format_homeserver_url(homeserver)

        if user.startswith('@'):
            username = user.split('@')[1].split(':')[0]
        else:
            username = user

        access_token_is_valid = False
        access_token = get_stored_access_token()
        if access_token:
            creds = cls(homeserver, username, access_token)
            client: Optional[AsyncClient] = get_event_loop().run_until_complete(
                creds.get_valid_client()
            )
            if client:
                get_event_loop().run_until_complete(
                    client.close()
                )
                return creds
        else:
            access_token_is_valid = False

        client = AsyncClient(homeserver=homeserver, user=username)

        if (not access_token) \
                or (regenerate_if_invalid and not access_token_is_valid):

            resp = get_event_loop().run_until_complete(
                client.login(password, device_name="simplematrixbotlib")
            )

            if isinstance(resp, LoginError):
                raise RuntimeError(resp.message)

            access_token = client.access_token

            logger.debug("Successfully generated access token from username and password")

        get_event_loop().run_until_complete(
            client.close()
        )

        return cls(
            homeserver=homeserver,
            user=username,
            access_token=access_token
        )

    @classmethod
    def from_env(cls, homeserver, user, password, regenerate_if_invalid: bool = True):
        try:
            os.environ[homeserver]
        except KeyError:
            raise RuntimeError(f"Environment variable '{homeserver}' not set")
        try:
            os.environ[user]
        except KeyError:
            raise RuntimeError(f"Environment variable '{user}' not set")
        try:
            os.environ[password]
        except KeyError:
            raise RuntimeError(f"Environment variable '{password}' not set")
        return cls.from_args(
            homeserver=os.environ[homeserver],
            user=os.environ[user],
            password=os.environ[password],
            regenerate_if_invalid=regenerate_if_invalid
        )
