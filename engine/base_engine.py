"""
base_engine.py

Classe base para todas as engines suportadas.
"""


class BaseEngine:

    NAME = "Unknown"

    def detect(self, game_path: str) -> bool:
        raise NotImplementedError

    def get_version(self, game_path: str) -> str:
        raise NotImplementedError

    def extract(self, game_path: str, output_path: str):
        raise NotImplementedError

    def parse(self, project_path: str):
        raise NotImplementedError

    def compile(self, project_path: str):
        raise NotImplementedError

    def apply_patch(self, game_path: str, project_path: str):
        raise NotImplementedError