from typing import Dict, Any, Optional


class Deps:
    def __init__(self, **kwargs):
        """@private"""
        self._dependencies: Dict[str, Any] = {}

        for key, arg in kwargs.items():
            self._dependencies[key] = arg

    def get(self, key: str) -> Optional[Any]:
        return self._dependencies.get(key, None)
