from typing import Optional

from nio import AsyncClient


class Bot:
    nio_client: AsyncClient
    prefix: Optional[str]
    user_id: str

    def __init__(self, client: AsyncClient, prefix: Optional[str] = None) -> None:
        self.nio_client = client
        self.prefix = prefix
        self.user_id = client.user_id
