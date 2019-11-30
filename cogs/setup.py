import svc.svc as svc
import discord
import os

from svc.mongo_setup import global_init
from discord.ext import commands, tasks

class Setup(commands.Cog):
    
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

    @commands.command(aliases=['helpme'])
    async def support(self, ctx):
        """Custom help message"""
        await ctx.send('--Made by Nathaniel--\n'
                    'Commands: \n'
                    '.ping: Pong!\n'
                    '.roll [number of sides]: Rolls a die, accepts a number; default is 6 \n'
                    '.rps [Player 1] [Player 2]: Shoot! There is a monetary reward for those who win\n'
                    ".viewgamerstats [id]: View a player's statistics.\n"
                    ".gamble [amount]: Gamble to your hearts content. It's Vegas baby!\n"
                    "I'm also a part-time Dad now as well!(as per Noah's request)\n"
                    "I'm also now controlled by the ADL\n"
                    "Source code available at https://github.com/applememes69420/Johnson-Discord-Bot")
        


def setup(client):
    client.add_cog(Setup(client))