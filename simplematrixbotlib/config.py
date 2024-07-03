from __future__ import annotations

import logging
import json
import tomllib
from dataclasses import dataclass
from logging import getLogger


logger = getLogger(__name__)

class InvalidConfig(ValueError):
    pass


@dataclass
class Config:
    data_path: str = "./bot_data/"
    join_room_on_invite_enabled: bool = True

    @staticmethod
    def _from_dict(data: dict) -> Config:
        values: dict = {}

        if data.get("tool.simplematrixbotlib"):
            values = data.get("tool.simplematrixbotlib") #type: ignore

        elif data.get("tool"):
            tool_values = data.get("tool", {})
            if tool_values.get("simplematrixbotlib"):
                values = tool_values.get("simplematrixbotlib")

        else:
            raise InvalidConfig("Config values must be within tool.simplematrixbotlib")

        return Config(**values)

    @staticmethod
    def load_toml(file_path: str) -> Config:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
        return Config._from_dict(data)

    @staticmethod
    def load_json(file_path: str) -> Config:
        with open(file_path, "r") as f:
            data = json.load(f)
        return Config._from_dict(data)

    def log(self):
        for attr, default_value in Config().__dict__.items():
            value = self.__dict__.get(attr)
            if value != default_value:
                logger.info(f"Changed from default: {attr} ({value})")
