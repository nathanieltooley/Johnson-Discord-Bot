import json
import os

from pathlib import Path


class DialogueHandler:
    @staticmethod
    def get_json_dict(node_map_name):
        path = Path(f"{os.getcwd()}/dialogue/{node_map_name}.json")

        with open(path.absolute(), "r", encoding="utf-8") as f:
            json_dict = json.load(f)
            return json_dict

    @staticmethod
    def get_json_files():
        folder = Path(f"{os.getcwd()}/dialogue/")

        all_files = os.listdir(folder)

        filtered = []

        for file in all_files:
            if file.endswith(".json"):
                i = file.index(".")
                filtered.append(file[0:i])

        return filtered
