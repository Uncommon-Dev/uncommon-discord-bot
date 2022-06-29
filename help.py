import discord
from discord.ext import commands
from datetime import datetime

from utils.utils import load_json, prepare_embed_dict


class help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(
        usage='',
        description='Displays all the commands for the bot'
    )
    async def help(self, ctx):

        # Read in embed
        help_embed = load_json('storage/embeds/help_embed.json')
        embed = discord.Embed().from_dict(prepare_embed_dict(help_embed))

        # Fill in commands
        for command in self.client.commands:
            if command.name == 'help':
                continue
            embed.add_field(name=f'**{ctx.prefix}{command.name} {command.usage}**', value=f'{command.description}', inline=False)

        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(help(client))
