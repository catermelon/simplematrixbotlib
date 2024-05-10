from nio import AsyncClient


class Bot:
    nio_client: AsyncClient
    user_id: str

    def __init__(self, client: AsyncClient) -> None:
        """@private"""
        self.nio_client = client
        self.user_id = client.user_id
