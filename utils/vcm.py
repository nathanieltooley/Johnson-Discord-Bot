import discord

from discord.ext import commands
from enums import bot_enums

def _is_member_in_vc(voice_client, member: discord.Member):
    for vc_member in voice_client.channel.members:
        if vc_member.id == member.id:
            return True

    return False

async def connect_to_member(client: commands.Bot, member: discord.Member):
    voice_state: discord.VoiceState = member.voice

    # My bot can only have one voice_client
    if voice_state is None:
        return None

    if len(client.voice_clients) == 0:
        return await voice_state.channel.connect()
    else:
        # move the voice client to the correct channel
        voice_client = client.voice_clients[0]

        # if we are already connected with the right member, just return the vc
        if _is_member_in_vc(voice_client, member):
            return voice_client

        await voice_client.move_to(voice_state.channel)
        return voice_client

async def get_current_vc(client: commands.Bot):
    if client.voice_clients is None or len(client.voice_clients) == 0:
        return None

    return client.voice_clients[0]

async def disconnect(client: commands.Bot):
    if len(client.voice_clients) != 0:
        await client.voice_clients[0].disconnect()
        return bot_enums.ReturnTypes.RETURN_TYPE_SUCCESSFUL_DISCONNECT
    else:
        return None