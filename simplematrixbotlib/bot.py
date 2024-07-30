from typing import List

from nio import AsyncClient

from .room import Room


class Bot:
    nio_client: AsyncClient
    user_id: str


    def __init__(self, client: AsyncClient) -> None:
        """@private"""
        self.nio_client = client
        self.user_id = client.user_id


    def joined_rooms(self) -> List[Room]:
        rooms = []

        for matrix_room in self.nio_client.rooms.values():
            rooms.append(Room(matrix_room, self.nio_client))

        return rooms
