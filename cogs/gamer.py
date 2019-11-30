import svc.svc as svc
import discord


from discord.ext import commands, tasks

class Gamer(commands.Cog):
    
    def __init__(self, client):
        self.client = client

def setup(client):
    client.add_bot(Gamer(client))