import os
import discord
from discord.ext import commands
from discord_components import DiscordComponents

from utils.utils import load_json

config = load_json('config.json')
config_general = config['general']

client = commands.Bot(command_prefix = config_general['prefix'], help_command=None)

@client.event
async def on_ready():
	DiscordComponents(client)
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(config_general['token'])
