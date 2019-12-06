import discord
import svc.svc as svc

from discord.ext import commands, tasks

class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def update_vbucks(self, ctx, member: discord.Member, money: int):
        svc.update_vbucks(member, ctx.guild, money)
        await ctx.send(f"{member.mention}'s V-Buck amount has been updated to {money}")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def update_exp(self, ctx, member: discord.Member, exp: int):
        check = svc.update_exp(member, ctx.guild, exp)
        if check == None:
            await ctx.send(f"{member.mention}'s XP has been set to {exp}")
        else:
            await ctx.send(f"{member.mention}'s XP has been set to {exp} and their level has changed to {check}")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def spawn_item(self, ctx, member: discord.Member, ref_id):
        item, value = svc.give_item_to_user(member, ref_id, ctx.guild)
        await ctx.send(f"Given User Item: {item}, of Value: {value} V-Bucks")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def get_user_inventory(self, ctx, member: discord.Member = None):
        if member is None:
            item = svc.get_user_inventory(ctx.author, ctx.guild)
            name = ctx.author.nick
        else:
            item = svc.get_user_inventory(member, ctx.guild)
            if member.bot:
                name = member.name
            else:
                name = member.nick

        count = len(item)

        embed = discord.Embed(
            title=f"{name}'s Inventory",
            description=f"The inventory of {name}. Total Item Count {count}",
            color=discord.Colour.dark_purple()
        )

        if isinstance(item, list):
            item = enumerate(item, 1)
            for count, i in item:
                embed.add_field(name=f"{i.name}", value=f"{i.value} V-Bucks", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(item)
    

def setup(client):
    client.add_cog(Admin(client))