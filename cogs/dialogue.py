import discord
import asyncio
import enums.bot_enums as enums

from pathlib import Path
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

    async def perform_node(self, node, ctx, client):
        embed = self.create_dialogue_embed("test", node.dialogue, node.options)

        await ctx.send(embed=embed)
        # response = input()

        if node.options is None:
            await ctx.send("~fin~")
            return None

        try:
            response = client.wait_for("message", timeout=25.0,
                                       check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

        except asyncio.TimeoutError:
            await ctx.send("You have to respond")
            return None

        options_list = enumerate(node.options, 1)

        for i, option in options_list:
            if i == response:
                return option["pointer"]

        return None

    def create_dialogue_embed(self, title, dialogue, options):
        embed = discord.Embed(
            title={title},
            description=dialogue,
            color=discord.Color.purple()
        )

        embed.set_thumbnail(enums.Enums.BOT_AVATAR_URL)

        if options is None:
            return embed

        options_list = enumerate(options, 1)

        for i, option in options_list:
            embed.add_field(name=i, value=options)

        return embed

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

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def test_response(self, ctx):
        # message = await ctx.send("Respond please, im lonely")

        path = Path("../dialogue/test.json")

        tree = DialogueTree.from_json(path.absolute())
        tree.start_tree()

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        """try:
            msg = await self.client.wait_for("message", timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Ok, fuck you too")
        else:
            await ctx.send("Message received")"""


def setup(client):
    client.add_cog(Dialogue(client))

