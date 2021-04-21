import asyncio

import svc.utils as svc
import discord
import os
import random

from discord.ext import commands, tasks


class Gamble(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    @commands.command()
    async def roll(self, ctx, sides=6):
        await ctx.send(f'{ctx.message.author.nick} rolled a {random.randrange(1, sides)}')

    # might be reworked, probably won't
    # could possibly use enums or something
    @commands.command()
    @commands.cooldown(1, 15, discord.ext.commands.BucketType.member)
    async def rps(self, ctx, member1: discord.member.Member, member2: discord.member.Member):
        rps_member1 = svc.Games.pickrps()
        rps_member2 = svc.Games.pickrps()
        rpstotal = rps_member1 + ' ' + rps_member2
        
        rpsdict = {
            "rock scissors": member1,
            "paper rock": member1,
            "scissors paper": member1,
            "scissors rock": member2,
            "rock paper": member2,
            "paper scissors": member2
        }

        await ctx.send(f'{member1.mention} got {rps_member1}, and {member2.mention} got {rps_member2}')

        if rps_member1 != rps_member2:
            winner = rpsdict[rpstotal]
            loser = None

            if winner == member1:  # find the loser using the winner
                loser = member2
            else:
                loser = member1

            winner_user = svc.Mongo.create_user(winner, ctx.guild)  # Create the user if there isn't one
            loser_user = svc.Mongo.create_user(loser, ctx.guild)

            winner_user = svc.Mongo.get_user(winner, ctx.guild)
            loser_user = svc.Mongo.get_user(loser, ctx.guild)

            vbuck_reward = int(loser_user.vbucks * (random.randrange(1, 10) / 100))  # Get between 0% and 10% of the loser's vbucks

            vbuck_limit = 1500
            if vbuck_reward > vbuck_limit:
                vbuck_reward = vbuck_limit

            svc.Mongo.income(winner, ctx.guild, vbuck_reward)
            svc.Mongo.income(loser, ctx.guild, (-vbuck_reward))
            
            await ctx.send(f"{winner.mention} won and got {vbuck_reward} from {loser.mention}")
        else:
            await ctx.send('Its a tie!')

    @commands.command()
    @commands.cooldown(1, 30, discord.ext.commands.BucketType.member)
    async def gamble(self, ctx, amount: int):
        user = svc.Mongo.get_user(ctx.author, ctx.guild)

        rand_selection = random.random()
        if (.1 <= rand_selection <= .7) and (amount < user.vbucks):
            new_amount = amount * ((random.randrange(1, 20)) / 10)
            int(new_amount)
            svc.Mongo.income(ctx.author, ctx.guild, new_amount)
            print_vbucks = new_amount + user.vbucks
            await ctx.send(f"You gained {new_amount}. You now have {print_vbucks}.")
        elif (rand_selection >= .7) and (amount < user.vbucks):
            new_amount = (-amount)
            svc.Mongo.income(ctx.author, ctx.guild, new_amount)
            print_vbucks = user.vbucks - amount
            await ctx.send(f"You lost {amount}. You have {print_vbucks} left.")
        else:
            await ctx.send("You can't gamble for more than you own, I can't program loans. Not yet at least.")

    @commands.command()
    @commands.cooldown(1, 10, discord.ext.commands.BucketType.member)
    async def blackjack(self, ctx, amount: int):
        user = svc.Mongo.get_user(ctx.author, ctx.guild)

        if amount > user.vbucks:
            await ctx.send("You don't have that kind of money")
            return

        dealer_cards = []
        player_cards = []

        dealer_color = discord.Color.red()
        player_color = discord.Color.blue()

        reward = int(amount * (1 + random.random()))

        # Dealer Starting Cards
        self.draw_cards(dealer_cards, 1)

        await ctx.send(ctx.author.mention, embed=svc.Games.create_card_view(self.client.user, dealer_cards, dealer_color))

        """
        # Dealer Natural
        if self.has_natural(dealer_cards):
            ctx.send(f"{ctx.author.mention} You Lost! You lose {amount}!")
            svc.Mongo.income(ctx.author, ctx.guild, -amount)
            return
        """

        self.draw_cards(player_cards, 2)

        await ctx.send(ctx.author.mention, embed=svc.Games.create_card_view(ctx.author, player_cards, player_color))

        # Player Natural
        if self.has_natural(player_cards):
            ctx.send(f"{ctx.author.mention} You Win! You gain {reward}")
            svc.Mongo.income(ctx.author, ctx.guild, reward)
            return

        # player's turn
        while True:
            await ctx.send(ctx.author.mention, embed=svc.Games.send_blackjack_option(ctx.author))

            try:
                response = await self.client.wait_for("message", timeout=90.0,
                                             check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            except asyncio.TimeoutError:
                await ctx.send("You failed to respond. Game was forfeited")
                return
            else:
                if response.content == "1":
                    # Hit

                    self.draw_cards(player_cards, 1)

                    await ctx.send(ctx.author.mention, embed=svc.Games.create_card_view(ctx.author, player_cards, player_color))

                    if self.busted(player_cards):
                        await ctx.send(f"{ctx.author.mention} You Busted! You lose {amount}!")
                        svc.Mongo.income(ctx.author, ctx.guild, -amount)
                        return

                elif response.content == "2":
                    break
                else:
                    await ctx.send("Invalid Option. Trying again")
                    continue

        # Dealer's turn
        while True:
            has_ace = False
            dealer_value = 0

            for card in dealer_cards:
                if (card[0] == 1):
                    has_ace = True

                dealer_value += min(card[0], 10)

            if has_ace:
                dealer_value_with_ace = dealer_value + 9
            else:
                dealer_value_with_ace = dealer_value

            if dealer_value < 17 and dealer_value_with_ace < 17:
                self.draw_cards(dealer_cards, 1)

                await ctx.send(ctx.author.mention,
                               embed=svc.Games.create_card_view(self.client.user, dealer_cards, dealer_color))

                if self.busted(dealer_cards):
                    await ctx.send(f"Dealer Busted, {ctx.author.mention} You Win! You gain {reward}")
                    svc.Mongo.income(ctx.author, ctx.guild, reward)
                    return

                continue

            break

        dealer_min = 0
        dealer_max = 0

        for card in dealer_cards:
            dealer_min += min(card[0], 10)

            if card[0] == 1:
                dealer_max += 10
            else:
                dealer_max += min(card[0], 10)

        player_min = 0
        player_max = 0

        for card in player_cards:
            player_min += min(card[0], 10)
            if card[0] == 1:
                player_max += 10
            else:
                player_max += min(card[0], 10)


        dealer_compare_value = 0
        player_compare_value = 0

        if player_max > 21:
            player_compare_value = player_min
        else:
            player_compare_value = player_max

        if dealer_max > 21:
            dealer_compare_value = dealer_min
        else:
            dealer_compare_value = dealer_max

        if dealer_compare_value > player_compare_value:
            await ctx.send(f"{ctx.author.mention} You Lost! You lose {amount}!")
            svc.Mongo.income(ctx.author, ctx.guild, -amount)
            return
        elif player_compare_value > dealer_compare_value:
            await ctx.send(f"{ctx.author.mention} You Win! You gain {reward}")
            svc.Mongo.income(ctx.author, ctx.guild, reward)
            return
        elif player_compare_value == dealer_compare_value:
            await ctx.send(f"Tie! No one wins.")
            return
        else:
            await ctx.send(f"Error")
            return

    @staticmethod
    def has_natural(cards):
        has_ace = False
        has_ten = False

        for card in cards:
            if card[0] == 1:
                has_ace = True
            elif card[0] >= 10:
                has_ten = True

        if has_ace and has_ten:
            return True

        return False

    @staticmethod
    def draw_cards(cards, amount):
        for i in range(amount):
            rand_card = None
            rand_suit = None

            while True:
                rand_card = random.randint(1, 13)
                rand_suit = random.randint(1, 4)

                # no dupes
                if (rand_card, rand_suit) in cards:
                    continue

                break

            cards.append((rand_card, rand_suit))

    @staticmethod
    def busted(cards):
        value = 0

        for card in cards:
            value += min(card[0], 10)

        if (value > 21):
            return True

        return False


def setup(client):
    client.add_cog(Gamble(client))
