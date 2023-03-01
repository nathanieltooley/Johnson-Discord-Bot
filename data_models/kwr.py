import json
import os
import random

from pathlib import Path
from typing import List

class KeywordResponse:

    config_file_path = Path(f"{os.getcwd()}/config/keyword_responses.json")

    def __init__(self, key_words, responses, weights) -> None:
        self.key_words = key_words
        self.responses = responses
        self.weights = weights

    @staticmethod
    def read_keyword_responses() -> List["KeywordResponse"]:

        with open(KeywordResponse.config_file_path, "r", encoding="utf-8") as config:
            keyword_dict = json.load(config)

            keywords = []
            for kw in keyword_dict:
               keywords.append(KeywordResponse(kw["key_words"], kw["responses"], kw["weights"]))

            return keywords 
        
    def choose_response(self):
        return random.choices(self.responses, weights=self.weights, k=1)[0]
    
    def message_trigger_response(self, check_message: str):
        for kw in self.key_words:
            if kw in check_message:
                return True
    