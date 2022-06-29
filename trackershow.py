import asyncio
import discord
from discord.ext import commands
from discord_components import InteractionType

from libs.database import Database
from utils.utils import load_json, prepare_embed_dict, calculate_profit, get_tracker_show_components, get_tracker_edit_components
from utils.input_utils import is_valid

config = load_json('config.json')
currency = config['tracker']['currency']
wait_time = config['tracker']['wait_time']


class trackershow(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(
        aliases=['ts', 'tshow', 'trackers'],
        usage='<id>',
        description='Used to show, edit, or delete an entry on the profit tracker'
    )
    #@commands.dm_only()
    async def trackershow(self, ctx, id: int):

        with Database() as db:
            entry = db.select_entry(id)
            if len(entry) == 0:
                return await ctx.send(f'ERROR: The entry with the ID `{id}` could not be found')
            entry = entry[0]

            if int(entry[1]) != ctx.author.id:
                return await ctx.send('ERROR: This is not your entry to view!')

            # For editing entry
            params = {
                'id': entry[0],
                'name': entry[2],
                'quantity': entry[3],
                'buy_price': entry[4],
                'sell_price': entry[5],
                'fees': entry[6]
            }

            # For displaying entry
            info_field_value = f'```\nName: {entry[2]}\nQuantity: {entry[3]}\nAdded On: {entry[7]}```'
            calc_field_value = f'```\n\n- Buy: {currency}{entry[3]*entry[4]}\n- Fees: {currency}{entry[6]}\n+ Sell: {currency}{entry[5]}\n------------------\nProfit: {currency}{calculate_profit(entry[4], entry[3], entry[5], entry[6])}```'

            e = load_json('storage/embeds/t_show_embed.json')
            e['title'] = e['title'].replace('Entry', 'Entry #' + str(id))
            e['fields'] = [
                {'name': 'Information', 'value': info_field_value, 'inline': False},
                {'name': 'Sale Calculator', 'value': calc_field_value, 'inline': False}
            ]
            entry_embed = discord.Embed().from_dict(prepare_embed_dict(e))

            msg = await ctx.send(embed=entry_embed, components=get_tracker_show_components())
            while True:
                try:
                    interaction = await self.client.wait_for(
                        "button_click",
                        check = lambda i: i.component.id in ["edit", "delete"] and i.user.id == ctx.author.id and i.message.id == msg.id,
                        timeout=wait_time
                    )

                    if interaction.component.id == 'edit':
                        e = load_json('storage/embeds/t_edit_embed.json')

                        await interaction.respond(type=InteractionType.UpdateMessage, embed=discord.Embed().from_dict(prepare_embed_dict(e)), components=get_tracker_edit_components())
                        interaction = await self.client.wait_for(
                            "select_option",
                            check = lambda i: i.component[0].value in ['name', 'quantity', 'buy_price', 'sell_price', 'fees'] and i.user.id == ctx.author.id and i.message.id == msg.id,
                            timeout=wait_time
                        )

                        e['description'] = 'Please type the desired value for this edit below'
                        await interaction.respond(type=InteractionType.UpdateMessage, embed=discord.Embed().from_dict(prepare_embed_dict(e)), components=[])

                        response = await self.client.wait_for('message', check = lambda m: m.channel.id == ctx.channel.id and m.author.id == ctx.author.id, timeout = wait_time)

                        if isinstance(response.channel, discord.DMChannel) == False:
                            # Work around for discord-componenets library tampering with await response.delete()
                            resp_msg = await response.channel.fetch_message(response.id)
                            await resp_msg.delete()

                        if is_valid(response.content, interaction.component[0].value):
                            params[interaction.component[0].value] = response.content
                            db.update_entry(**params)
                            info_field_value = f'```\nName: {params["name"]}\nQuantity: {params["quantity"]}\nAdded On: {entry[7]}```'
                            calc_field_value = f'```\n\n- Buy: {currency}{int(params["quantity"])*float(params["buy_price"])}\n- Fees: {currency}{params["fees"]}\n+ Sell: {currency}{params["sell_price"]}\n------------------\nProfit: {currency}{calculate_profit(params["buy_price"], params["quantity"], params["sell_price"], params["fees"])}```'
                            e['fields'] = [
                                {'name': 'Information', 'value': info_field_value, 'inline': False},
                                {'name': 'Sale Calculator', 'value': calc_field_value, 'inline': False}
                            ]
                            entry_embed = discord.Embed().from_dict(prepare_embed_dict(e))

                    elif interaction.component.id == 'delete':
                        db.delete_entry(id)
                        e['description'] = '**DELETED ENTRY**'
                        e['fields'] = [
                            {'name': 'Information', 'value': '~~' + info_field_value + '~~', 'inline': False},
                            {'name': 'Sale Calculator', 'value': '~~' + calc_field_value + '~~', 'inline': False}
                        ]
                        await interaction.respond(type=InteractionType.UpdateMessage, embed=discord.Embed().from_dict(prepare_embed_dict(e)), components=get_tracker_show_components(True))
                        break

                    await msg.edit(embed=entry_embed, components=get_tracker_show_components())
                except asyncio.TimeoutError:
                    await msg.edit(embed=entry_embed, components=get_tracker_show_components(True))
                    break

def setup(client):
    client.add_cog(trackershow(client))
