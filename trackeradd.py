import asyncio
import discord
from discord.ext import commands

from libs.database import Database
from utils.utils import load_json, prepare_embed_dict
from utils.input_utils import is_valid_name, is_valid_quantity, is_valid_price

config = load_json('config.json')
wait_time = config['tracker']['wait_time']


class trackeradd(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(
        aliases=['ta', 'tadd', 'trackera'],
        usage='',
        description='Used to add an item to the profit tracker'
    )
    @commands.dm_only()
    async def trackeradd(self, ctx):

        try:
            ### BEGIN SUBMISSION FORM ###

            def message_check(m):
                return m.author.id == ctx.author.id and isinstance(m.channel, discord.DMChannel)

            # Name
            e = load_json('storage/embeds/t_name_embed.json')
            while True:
                msg = await ctx.author.send(embed=discord.Embed().from_dict(prepare_embed_dict(e)))
                response = await self.client.wait_for('message', check=message_check, timeout=wait_time)
                name = response.content

                if is_valid_name(name):
                    break

            # Quantity
            e = load_json('storage/embeds/t_quantity_embed.json')
            while True:
                msg = await ctx.author.send(embed=discord.Embed().from_dict(prepare_embed_dict(e)))
                response = await self.client.wait_for('message', check=message_check, timeout=wait_time)
                quantity = response.content

                if is_valid_quantity(quantity):
                    #quantity = int(quantity)
                    break

            # Price
            e = load_json('storage/embeds/t_price_embed.json')
            while True:
                msg = await ctx.author.send(embed=discord.Embed().from_dict(prepare_embed_dict(e)))
                response = await self.client.wait_for('message', check=message_check, timeout=wait_time)
                price = response.content

                if is_valid_price(price):
                    #price = float(price)
                    break

            # Finalize
            e = load_json('storage/embeds/t_finalize_embed.json')
            e['fields'].append({'name': '**Information**', 'value': f'```Name: {name}\nQuantity: {quantity}\nPrice (Per): ${price}\nPrice (Total): ${float(price)*int(quantity)}```', 'inline': False})
            e = discord.Embed().from_dict(prepare_embed_dict(e))
            while True:
                msg = await ctx.author.send(embed=e)
                response = await self.client.wait_for('message', check=message_check, timeout=wait_time)
                correct = response.content

                if correct == 'Y' or correct == 'YES':
                    break
                elif correct == 'N' or correct == 'NO':
                    return await ctx.author.send('Aborting... please use this command again to put in the correct details')

            ### END SUBMISSION FORM ###

            with Database() as db:
                db.insert_entry(ctx.author.id, name, quantity, price)

            await ctx.author.send('Successfully added your item to the profit tracker!')
        except asyncio.TimeoutError:
            e = load_json('storage/embeds/t_expired_embed.json')
            return await msg.edit(embed=discord.Embed().from_dict(prepare_embed_dict(e)))


def setup(client):
    client.add_cog(trackeradd(client))
