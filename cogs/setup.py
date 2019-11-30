import svc.svc as svc
import discord
import os

from svc.mongo_setup import global_init
from discord.ext import commands, tasks

class Test(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        global_init()
        print("Johnson is spittin straight cog!")
        
    # Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.client.latency * 1000)}ms")

    @commands.command()
    async def shutdown(self, ctx):
        if ctx.message.author.id == 139374003365216256: #replace OWNERID with your user id
            print("Shutdown")
        try:
            await self.client.logout()
        except:
            print("EnvironmentError")
            self.client.clear()
        else:
            await ctx.send("You do not own this bot!")


def setup(client):
    client.add_cog(Test(client))