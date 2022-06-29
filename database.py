import mysql.connector
from mysql.connector import Error

from utils.utils import load_json

config = load_json('config.json')

INSERT_ENTRY = 'INSERT INTO entries (discord_id, name, quantity, buy_price, sell_price, fees) VALUES (%s, %s, %s, %s, %s, %s)'
SELECT_ENTRY = 'SELECT * FROM entries WHERE id = %s'
SELECT_ENTRIES = 'SELECT * FROM entries WHERE discord_id = %s LIMIT %s'
SELECT_ENTRY_STATS_USER = 'SELECT SUM(quantity), SUM(quantity*buy_price), SUM(sell_price), SUM(fees), SUM(sell_price-buy_price*quantity-fees), COUNT(ID), AVG(quantity*buy_price) FROM entries WHERE discord_id = %s'
SELECT_ENTRY_STATS_SERVER = 'SELECT SUM(quantity), SUM(quantity*buy_price), SUM(sell_price), SUM(fees), SUM(sell_price-buy_price*quantity-fees), COUNT(ID), AVG(quantity*buy_price) FROM entries'
SELECT_ENTRY_LEADERBOARD = 'SELECT discord_id, total_profit FROM ( SELECT discord_id, SUM(sell_price-buy_price*quantity-fees) AS total_profit FROM entries GROUP BY discord_id ) A ORDER BY total_profit DESC'
DELETE_ENTRY = 'DELETE FROM entries WHERE id = %s LIMIT 1'
UPDATE_ENTRY = 'UPDATE entries SET name=%s, quantity=%s, buy_price=%s, sell_price=%s, fees=%s WHERE id = %s'


class Database():

    def __init__(self):
        try:
            self.connection = mysql.connector.connect(**config['sql'])
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(e)
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        self.commit()

    def executemany(self, sql, params=None):
        self.cursor.executemany(sql, params or ())

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()

    def insert_entry(self, discord_id: int, name: str, quantity: int, buy_price: float, sell_price: float=0, fees: float=0):
        """
        Creates a new entry in the database for the item with the given information
        """

        self.execute(INSERT_ENTRY, (discord_id, name, quantity, buy_price, sell_price, fees,))

    def select_entry(self, id: int):
        """
        Select a single entry by ID
        """

        return self.query(SELECT_ENTRY, (id,))

    def select_entries(self, discord_id: int, limit: int=9999):
        """
        Select all the entries for a given user
        """

        return self.query(SELECT_ENTRIES, (discord_id, limit,))

    def delete_entry(self, id: int):
        """
        Delete the entry with the given id
        """

        self.execute(DELETE_ENTRY, (id,))

    def update_entry(self, id: int, name: str, quantity: int, buy_price: float, sell_price: float, fees: float):
        """
        Update an existing entry
        """

        self.execute(UPDATE_ENTRY, (name, quantity, buy_price, sell_price, fees, id))

    def select_stats(self, discord_id: int=-1):
        """
        Retrieve the stats (total quantity, total amount spent, total amount made, total fees paid, total profit made, # of entries, avg amount spent)
        """

        if discord_id == -1:
            return self.query(SELECT_ENTRY_STATS_SERVER)
        return self.query(SELECT_ENTRY_STATS_USER, (discord_id,))

    def select_leaderboard(self):
        """
        Get the top 5 user's by profit
        """

        return self.query(SELECT_ENTRY_LEADERBOARD)
