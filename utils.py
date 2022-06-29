import json
from datetime import datetime
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption, InteractionType

def load_json(file_name: str) -> dict:
    """
    Load the given json into a dict and returns it
    """

    try:
        with open(file_name, encoding='utf-8') as file:
            data = json.load(file)
        return data
    except json.decoder.JSONDecodeError:
        print('ERROR: There was an error loading the following file: ' + file_name)

def shave_dict(data: dict) -> dict:
    """
    Remove empty k,v pairs from dict
    """

    new_dict = {}
    for key in data:
        value = data[key]

        if isinstance(value, dict):
            value = shave_dict(value)
            if len(value) != 0:
                new_dict[key] = value
        elif isinstance(value, list):
            if len(value) != 0:
                new_dict[key] = value
        elif isinstance(value, str):
            if value != "":
                new_dict[key] = value
        elif isinstance(value, int) or isinstance(value, float):
            if value != 0:
                new_dict[key] = value
    return new_dict

def prepare_embed_dict(data: dict) -> dict:
    """
    Removes empty fields, cleans up empty values, returns dict ready for conversion
    """

    new_dict = {'fields': []}
    if 'fields' in data:
        for field in data['fields']:
            if field['name'] == '' or field['value'] == '':
                continue
            new_dict['fields'].append({
                "name": field['name'],
                "value": field['value'],
                "inline": field['inline']
            })
        del data['fields']
    for key in data:
        new_dict[key] = data[key]
    new_dict['timestamp'] = str(datetime.utcnow())
    return shave_dict(new_dict)

def calculate_profit(buy_price: float, quantity: int, sell_price: float, fees: float) -> float:
    """
    Returns rounded float representing approx profit made
    """

    profit = float(sell_price) - (float(buy_price)*int(quantity)+float(fees))
    return round(profit, 2)

def get_tracker_list_components(index: int, length: int, disabled: bool=False) -> list:
    """
    Gets the components used on the tracker list
    """

    return [
        [
            Button(
                label = "Prev",
                id = "prev",
                style = ButtonStyle.blue,
                disabled=disabled
            ),
            Button(
                label = f"Page {index+1}/{length}",
                id = "page",
                style = ButtonStyle.grey,
                disabled=True
            ),
            Button(
                label = "Next",
                id = "next",
                style = ButtonStyle.blue,
                disabled=disabled
            )
        ]
    ]

def get_tracker_show_components(disabled: bool=False) -> list:
    """
    Gets the components used on the tracker show cmd
    """

    return [
        [
            Button(
                emoji = "✏️",
                id = "edit",
                style = ButtonStyle.blue,
                disabled=disabled
            ),
            Button(
                emoji = "🗑️",
                id = "delete",
                style = ButtonStyle.red,
                disabled=disabled
            )
        ]
    ]

def get_tracker_edit_components(disabled: bool=False) -> list:
    """
    Gets the components used on the tracker show cmd
    """

    return [
        [
            Select(
                placeholder='Placeholder',
                id='edit_select',
                options=[
                    SelectOption(label='Name', value='name'),
                    SelectOption(label='Quantity', value='quantity'),
                    SelectOption(label='Buy Price (Per)', value='buy_price'),
                    SelectOption(label='Sell Price', value='sell_price'),
                    SelectOption(label='Fees', value='fees')
                ],
                min_values=1,
                max_values=1
            )
        ]
    ]

def get_tracker_stats_components(disabled: bool=False) -> list:
    """
    Gets the components used on the tracker stats cmd
    """

    return [
        [
            Button(
                emoji = "👤",
                id = "user",
                style = ButtonStyle.gray,
                disabled=disabled
            ),
            Button(
                emoji = "👥",
                id = "server",
                style = ButtonStyle.gray,
                disabled=disabled
            ),
            Button(
                emoji = "🏆",
                id = "leaderboard",
                style = ButtonStyle.gray,
                disabled=disabled
            )
        ]
    ]
