from dataclasses import dataclass


@dataclass
class Config:
    data_path = "./bot_data/"
    join_room_on_invite_enabled = True
