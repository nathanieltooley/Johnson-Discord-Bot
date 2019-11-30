import svc.svc as svc
import discord
import os

from discord.ext import commands, tasks

class Test(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Johnson is spittin straight cog!")
        
    # Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(client.latency * 1000)}ms")


def setup(client):
    client.add_cog(Test(client))