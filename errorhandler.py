import discord
from discord.ext import commands

from utils.utils import load_json

config = load_json('config.json')


class error_handler(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.command != None and ctx.command.has_error_handler(): # If command already has a handler, disregard error here
            return

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Proper Usage: {ctx.prefix}{ctx.command.qualified_name} {ctx.command.usage}")
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.message.delete()
            await ctx.send(f'ERROR: {ctx.author.mention}, this command must be done in private messages with the bot', delete_after=5)
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send('ERROR: This command must done within the server')
        elif isinstance(error, commands.MissingAnyRole):
            await ctx.send('ERROR: You do not have any of the required roles to execute this command')
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.CheckFailure)  or isinstance(error, commands.CheckAnyFailure):
            await ctx.send('ERROR: You do not have the required permissions to execute this command')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('ERROR: This command has been disabled')

        elif isinstance(error, commands.CommandInvokeError):
            exception = error.original
            if isinstance(exception, discord.Forbidden):
                await ctx.send('ERROR: This bot user needs higher permissions in order to complete this command')
            print(exception)
        else:
            #await ctx.send('ERROR: ' + str(error))
            print(error)
            print(type(error))

def setup(client):
    client.add_cog(error_handler(client))
