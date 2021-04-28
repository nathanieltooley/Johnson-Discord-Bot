import discord
import asyncio
import enums.bot_enums as enums
import svc.utils as utils

from discord.ext import commands

from dialogue.dialogue_handler import DialogueHandler



class DialogueTree:
    def __init__(self, dialogue_nodes, start_node):
        self.dialogue_nodes = dialogue_nodes
        self.start_node = start_node

    @classmethod
    def from_json(cls, name):
        nodes = []

        json_file = DialogueHandler.get_json_dict(name)

        for k, v in json_file.items():
            # print(k, v)

            node = DialogueNode(k, v["dialogue"], v["options"])
            nodes.append(node)

        return DialogueTree(nodes, "start")

    async def start_tree(self, ctx, client):
        pointer = await self.perform_node(self.grab_node(self.start_node), ctx=ctx, client=client)

        while not (pointer is None):
            pointer = await self.perform_node(self.grab_node(pointer), ctx=ctx, client=client)

        await ctx.send("~fin~")

    async def perform_node(self, node, ctx, client):
        embed = self.create_dialogue_embed("*Epic Dialogue*", node.dialogue, node.options)

        await ctx.send(f"{ctx.author.mention}", embed=embed)

        if node.options is None:
            return None

        try:
            response = await client.wait_for("message", timeout=60.0,
                                       check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

        except asyncio.TimeoutError:
            await ctx.send("You have to respond")
            return None

        options_list = enumerate(node.options, 1)

        for i, option in options_list:
            if str(i) == response.content:
                return option["pointer"]

        return None

    def create_dialogue_embed(self, title, dialogue, options):
        embed = discord.Embed(
            title=title,
            description=dialogue,
            color=discord.Color.purple()
        )

        embed.set_thumbnail(url=enums.Enums.BOT_AVATAR_URL.value)

        if options is None:
            return embed

        options_list = enumerate(options, 1)

        for i, option in options_list:
            trigger = option["trigger"]
            embed.add_field(name=i, value=trigger)

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

    dialogues = DialogueHandler.get_json_files()

    def __init__(self, client):
        self.client = client

    @commands.command()
    @utils.Checks.rude_name_check()
    async def start_dialogue(self, ctx):

        DialogueHandler.get_json_files()

        embed = discord.Embed(title="Dialogue Start!",
                              description="What would you like to talk about?",
                              color=utils.Color.random_color())

        d_list = enumerate(self.dialogues, 1)

        for i, d in d_list:
            embed.add_field(name=i, value=d)

        await ctx.send(embed=embed)

        try:
            response = await self.client.wait_for("message", timeout=25.0,
                                                  check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        except asyncio.TimeoutError:
            await ctx.send("Oh, nevermind then. Guess i'll go play fortnite.")
            return

        final_answer = None

        # refresh
        d_list = enumerate(self.dialogues, 1)

        for i, d in d_list:
            if str(i) == response.content:
                final_answer = d

        if final_answer is None:
            await ctx.send("Could not process answer")
            return

        tree = DialogueTree.from_json(final_answer)

        await tree.start_tree(ctx=ctx, client=self.client)



        """try:
            msg = await self.client.wait_for("message", timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Ok, fuck you too")
        else:
            await ctx.send("Message received")"""


def setup(client):
    client.add_cog(Dialogue(client))

