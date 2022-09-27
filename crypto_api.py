"""Crypto API."""

from typing import Dict, List, Set
from config import *
from db import DatabaseConnection

import datetime
import logging
import requests
import schedule

# API Documentation - https://www.coingecko.com/en/api#explore-api

# If filename throws error try using os package like filename=os.path.join(mydir, myfile)
# as this can happen on certain OS
logging.basicConfig(filename='storage/logs/app.log', encoding='utf-8', level=logging.DEBUG)

conn_string = f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
db = DatabaseConnection(conn_string)

def get_coins(db_coins: Set) -> List[Dict]:
    """This function will get the top 10 coins at the current time, sorted by market cap in desc order."""
    response = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false')
    response = response.json()

    print(f"DB Coins: ", db_coins)

    # Create coins in DB.
    for coin in response:
        if coin['id'] not in db_coins:
            print("Adding coin to db for first time: ", coin['id'])
            db.query(f"INSERT INTO crypto (id, symbol, name, current_price) VALUES ('{coin['id']}', '{coin['symbol']}', '{coin['name']}', {coin['current_price']});")
            db_coins.add(coin['id'])
        else:
            print("Coin exists in db, making trade and updating price: ", coin['id'], coin['current_price'])
            db.query(f"UPDATE crypto SET current_price = {coin['current_price']} WHERE id = '{coin['id']}';")

    return response

def get_top_coins(top_n_coins: int, db_coins: Set) -> List[Dict]:
    """This function will get the top N coins by market cap"""
    return get_coins(db_coins)[:top_n_coins]

# utilize this function when submitting an order
def submit_order(coin_id: str, quantity: int, bid: float):
    """
    Mock function to submit an order to an exchange. 
    
    Assume order went through successfully and the return value is the price the order was filled at.
    """
    return bid

# NOTE: Mismatch on commented return value (List[Tuple]) and typed return value (List[Dict])
def get_coin_price_history(coin_id: str, position_objects: Dict, position_set: Set) -> List[Dict]:
    print(f"Getting coin price history of {coin_id}")
    response = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=9&interval=daily")
    response = response.json()['prices']
    cnt = len(response)
    total = sum([p[1] for p in response])
    avg, curr = total/cnt, response[-1][1] # TODO: find average price
    
    print(f"10D Avg: {avg}, Current Price: {curr}")
    if curr <= avg:
        print(f"Make a bid for {coin_id}")
        _ = submit_order(coin_id, 1, curr) # This would be the bid.

        if coin_id not in position_set:
            print(f"Adding position to DB for first time: {coin_id}")
            logging.info(f"Adding position to DB for first time: {coin_id}")
            
            # Create new position.
            db.query(f"INSERT INTO position (crypto, quantity, average_price) VALUES ('{coin_id}', 1, {curr});")
            
            position_objects[coin_id] = {
                'crypto': coin_id,
                'quantity': 1,
                'average_price': curr
            }
            print(f"New position in DB: {position_objects[coin_id]}")
        else:
            position = position_objects[coin_id]
            print(f"\n\n\nNEW AVG = (({position['quantity']}*{position['average_price']})+{curr}) / {position['quantity']}+1")
            new_summ, new_quantity = position['quantity']*position['average_price']+curr, position['quantity']+1
            new_avg = new_summ / new_quantity
            print("Position exists in DB, updating position: ", coin_id, curr)
            logging.info(f"Position exists in DB, updating position: {coin_id}, {curr}")
            db.query(f"UPDATE position SET average_price = {new_avg}, quantity = {new_quantity} WHERE crypto = '{coin_id}';")
            position_objects[coin_id]['average_price'] = new_avg
            position_objects[coin_id]['quantity'] = position['quantity']+1

        # Since bid == curr price, no need to return here vs end of function.
        # return {'coin_id': coin_id, 'ten_day_avg': avg, 'bid': bid}

    # NOTE: refer to comment above func for mismatch on this vs typing in
    # return value.
    # Returns a list of tuples
    # Item 0 -> Unix Timestamp
    # Item 1 -> price
    print(f"No bid for {coin_id}")
    return {'coin_id': coin_id, 'ten_day_avg': avg, 'current_price': curr}

def main() -> None:
    logging.info(f"Running our program: {datetime.datetime.now()}")

    # Get all coins in DB and check for top coins of the day - if one of these
    # doesn't exist in DB, add it.
    db_crypto = set([dbc['id'] for dbc in db.query("SELECT id FROM crypto;")])
    
    # NOTE: Ask for user input on number of coins (out of scope?).
    top_coins = get_top_coins(3, db_crypto)
    top_coin_names = [(c['id'], c['name']) for c in top_coins]
    print(f"The top coins for today are: {top_coin_names}")

    positions_result = db.query("SELECT * FROM position;")
    positions_set = set([dbp['crypto'] for dbp in positions_result])

    # Allow for constant lookup time by crypto name when
    position_objects = {}
    for pos in positions_result:
        positions_set.add(pos['crypto'])
        position_objects[pos['crypto']] = pos

    print(f"\nExisting positions: {positions_result}")
    print(f"\nExisting coins: {db_crypto}")

    for coin in top_coin_names:
        get_coin_price_history(coin[0], position_objects, positions_set)

    print(f"Final positions after bidding: {position_objects}")
    logging.info(position_objects)

# This should be a DAG in Airflow such as @hourly 0 * * * *:
# PythonOperator (get coins) > SQLOperator (update coins) > SQLOperator (select positions)
# >> PythonOperator (get 10 day history on each coin) >> SQLOperator (update positions)
# schedule.every().hour.at(":41").do(main)

# # Extra ETL notes - to backfill create DAG with a previous
# # start_date, possibly an end_date, and a schedule_interval.

# while True:
#     schedule.run_pending()   

main()