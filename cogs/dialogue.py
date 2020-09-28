import discord

from discord.ext import commands

import json


class DialogueTree:
    def __init__(self, dialogue_nodes, start_node):
        self.dialogue_nodes = dialogue_nodes
        self.start_node = start_node

    @classmethod
    def from_json(cls, path):
        nodes = []

        with open(path, "r", encoding="utf-8") as f:
            json_file = json.load(f)

        for k, v in json_file.items():
            # print(k, v)

            node = DialogueNode(k, v["dialogue"], v["options"])
            nodes.append(node)

        return DialogueTree(nodes, "start")

    def start_tree(self):
        pointer = self.perform_node(self.grab_node(self.start_node))

        while not (pointer is None):
            pointer = self.perform_node(self.grab_node(pointer))

    def perform_node(self, node):
        print(node.dialogue)
        # response = input()

        if node.options is None:
            print("~fin~")
            return None

        options_list = enumerate(node.options, 1)

        for i in range(0, len(node.options)):
            print(f"    {i + 1}. {node.options[i]['trigger']}")

        try:
            response = input()
            response = int(response)
        except:
            print("Please input a number.")

        for i, option in options_list:
            if i == response:
                return option["pointer"]

        """for option in node.options:
            trigger = option["trigger"]
            pointer = option["pointer"]

            print(trigger)"""

        """if self.match(response, trigger):
            return pointer"""

        # print("Could not figure out your answer.")
        return None

    def grab_node(self, node_id):
        for node in self.dialogue_nodes:
            if node.node_id == node_id:
                return node

        return None

    def match(self, x, y):
        if x.lower() == y.lower():
            return True
        else:
            return False


class DialogueNode:
    def __init__(self, node_id, dialogue, options):
        self.node_id = node_id
        self.dialogue = dialogue
        self.options = options

class Dialogue(commands.Cog):

    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(Dialogue(client))

