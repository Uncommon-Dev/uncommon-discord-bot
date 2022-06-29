

def is_valid(value: str, type: str) -> bool:
    """
    Determines what the value is supposed to be and checks if it is valid
    """

    if type == 'name':
        return is_valid_name(value)
    elif type == 'quantity':
        return is_valid_quantity(value)
    elif type == 'buy_price' or type == 'sell_price' or type == 'fees':
        return is_valid_price(value)
    return False

def is_valid_name(name: str) -> bool:
    """
    Whether or not the provided name is valid
    """

    if len(name) > 255:
        return False
    return True

def is_valid_quantity(quantity: int) -> bool:
    """
    Whether or not the provided quantity is valid
    """

    try:
        quantity = int(quantity)
    except ValueError:
        return False
    if quantity < 0:
        return False
    return True

def is_valid_price(price: float) -> bool:
    """
    Whether or not the provided price is valid
    """

    try:
        price = round(float(price), 2)
    except ValueError:
        return False
    if price < 0:
        return False
    return True
