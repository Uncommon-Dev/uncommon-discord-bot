import asyncio
import discord
from discord.ext import commands
from discord_components import InteractionType

from libs.database import Database
from utils.utils import load_json, prepare_embed_dict, get_tracker_stats_components

config = load_json('config.json')
currency = config['tracker']['currency']
wait_time = config['tracker']['wait_time']
leaderboard_emojis = config['tracker']['leaderboard_emojis']


class trackerstats(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(
        aliases=['tst', 'tstats', 'trackerst'],
        usage='',
        description='Displays individual and server wide tracker stats'
    )
    #@commands.dm_only()
    async def trackerstats(self, ctx):

        e = load_json('storage/embeds/t_stats_embed.json')
        e['description'] = 'Showing user stats!'
        user_embed = discord.Embed().from_dict(prepare_embed_dict(e))
        e['description'] = 'Showing server stats!'
        server_embed = discord.Embed().from_dict(prepare_embed_dict(e))
        e['description'] = 'Top 5 leaderboard sorted by total profit!'
        leaderboard_embed = discord.Embed().from_dict(prepare_embed_dict(e))
        with Database() as db:
            user_stats = db.select_stats(ctx.author.id)
            if len(user_stats) == 0:
                return await ctx.send('ERROR: You do not have any stats to show!')
            user_stats = user_stats[0]
            if user_stats[5] > 0:
                user_embed.add_field(name='Information', value=f'```Total Items Bought: {user_stats[0]}\nTotal Tracked Entries: {user_stats[5]}\nAverage Amount Spent: {currency}{round(user_stats[6], 2)}```', inline=False)
                user_embed.add_field(name='Profit Calculator (All Time)', value=f'```\n\n- Buy: {currency}{user_stats[1]}\n- Fees: {currency}{user_stats[3]}\n+ Sell: {currency}{user_stats[2]}\n------------------\nProfit: {currency}{user_stats[4]}```', inline=False)

            server_stats = db.select_stats()
            if len(server_stats) == 0:
                return await ctx.send('ERROR: Something went wrong while retrieving server-wide stats!')
            server_stats = server_stats[0]
            if server_stats[5] > 0:
                server_embed.add_field(name='Information', value=f'```Total Items Bought: {server_stats[0]}\nTotal Tracked Entries: {server_stats[5]}\nAverage Amount Spent: {currency}{round(server_stats[6], 2)}```', inline=False)
                server_embed.add_field(name='Profit Calculator (All Time)', value=f'```\n\n- Buy: {currency}{server_stats[1]}\n- Fees: {currency}{server_stats[3]}\n+ Sell: {currency}{server_stats[2]}\n------------------\nProfit: {currency}{server_stats[4]}```', inline=False)

            leaderboard = db.select_leaderboard()
            for i in range(len(leaderboard)):
                row = leaderboard[i]
                try:
                    member = await ctx.guild.fetch_member(int(row[0]))
                    name = str(member)
                except:
                    name = row[0]
                leaderboard_embed.add_field(name=name, value=f'{leaderboard_emojis[i]}{currency}{row[1]}', inline=True)

        msg = await ctx.send(embed=user_embed, components=get_tracker_stats_components())
        while True:
            try:
                interaction = await self.client.wait_for(
                    "button_click",
                    check = lambda i: i.component.id in ["user", "server", "leaderboard"] and i.user.id == ctx.author.id and i.message.id == msg.id,
                    timeout=wait_time
                )

                if interaction.component.id == "user":
                    embed = user_embed
                elif interaction.component.id == "server":
                    embed = server_embed
                elif interaction.component.id == "leaderboard":
                    embed = leaderboard_embed

                await interaction.respond(type=InteractionType.UpdateMessage, embed=embed, components=get_tracker_stats_components())
            except asyncio.TimeoutError:
                await msg.edit(components=get_tracker_stats_components(True))
                break

def setup(client):
    client.add_cog(trackerstats(client))
