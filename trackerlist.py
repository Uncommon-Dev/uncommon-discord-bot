import asyncio
import discord
from discord.ext import commands
from discord_components import InteractionType

from libs.database import Database
from utils.utils import load_json, prepare_embed_dict, get_tracker_list_components

config = load_json('config.json')
currency = config['tracker']['currency']
wait_time = config['tracker']['wait_time']


class trackerlist(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(
        aliases=['tl', 'tlist', 'trackerl'],
        usage='',
        description='Displays your tracked entries/flips'
    )
    #@commands.dm_only()
    async def trackerlist(self, ctx):

        index = 0
        embeds = []
        e = load_json('storage/embeds/t_list_embed.json')
        with Database() as db:
            embed = discord.Embed().from_dict(prepare_embed_dict(e))
            for entry in db.select_entries(ctx.author.id):
                if index % 5 == 0 and index != 0:
                    embeds.append(embed)
                    embed = discord.Embed().from_dict(prepare_embed_dict(e))
                embed.add_field(name='**Entry #' + str(index+1) + '**', value=f'```ID: {entry[0]}\nName: {entry[2]}\nAdded On: {entry[7]}```', inline=False)
                index += 1
            embeds.append(embed)
            index = 0

        msg = await ctx.send(embed=embeds[index], components=get_tracker_list_components(index, len(embeds)))
        while True:
            try:
                interaction = await self.client.wait_for(
                    "button_click",
                    check = lambda i: i.component.id in ["prev", "next"] and i.user.id == ctx.author.id and i.message.id == msg.id,
                    timeout=wait_time
                )

                if interaction.component.id == "prev":
                    index -= 1
                elif interaction.component.id == "next":
                    index += 1

                if index == len(embeds):
                    index = 0
                elif index < 0:
                    index = len(embeds) - 1

                await interaction.respond(type=InteractionType.UpdateMessage, embed=embeds[index], components=get_tracker_list_components(index, len(embeds)))
            except asyncio.TimeoutError:
                await msg.edit(components=get_tracker_list_components(index, len(embeds), True))
                break

def setup(client):
    client.add_cog(trackerlist(client))
