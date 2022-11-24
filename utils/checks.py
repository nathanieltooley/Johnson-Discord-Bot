from discord.ext import commands
from enums import bot_enums

slur_list = ["nigger", 'nigga', 'negro', 'chink', 'niglet', 'nigtard', 'gook', 'kike',
                 'faggot', 'beaner']


def rude_name_check():
    def predicate(ctx):
        check_name = ""

        if ctx.author.nick is None:
            check_name = ctx.author.display_name
        else:
            check_name = ctx.author.nick

        for adl in slur_list:
            if adl in check_name:
                return False

        return True

    return commands.check(predicate)


def check_is_owner():
    def predicate(ctx):
        return ctx.author.id == bot_enums.OWNER_ID.value

    return commands.check(predicate)