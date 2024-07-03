from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass
from logging import getLogger


logger = getLogger(__name__)


@dataclass
class Config:
    data_path: str = "./bot_data/"
    join_room_on_invite_enabled: bool = True

    @staticmethod
    def load_toml(file_path: str) -> Config:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
        return Config(**data.get("tool").get("simplematrixbotlib"))

    def log(self):
        for attr, default_value in Config().__dict__.items():
            value = self.__dict__.get(attr)
            if value != default_value:
                logger.info(f"Changed from default: {attr} ({value})")
