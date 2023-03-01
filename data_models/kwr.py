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
        
    @staticmethod
    def message_check(message: str, kw):
        check_index = message.find(kw)
        pre_check_index = check_index - 1

        # Not Found
        if check_index < 0:
            return False

        before_space = message[pre_check_index].isspace()
        is_beginning = pre_check_index < 0
        nothing_after = False
        after_space = False

        # See if there is anything after the word
        try:
            after_space = message[check_index + len(kw)].isspace()
        except IndexError:
            nothing_after = True

        if (before_space or is_beginning) and (nothing_after or after_space):
            return True
        else:
            return False
        
    def choose_response(self):
        return random.choices(self.responses, weights=self.weights, k=1)[0]
    
    def message_trigger_response(self, check_message: str) -> bool:

        for kw in self.key_words:
            # seems like a waste but message_check may return false so we make sure to return true only here
            if KeywordResponse.message_check(check_message, kw):
                return True
            
        return False
    