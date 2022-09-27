from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.sql import func

import datetime

def initialize_schema():
  metadata_obj = MetaData()

  crypto = Table('crypto', metadata_obj,
    Column('id', String(50), primary_key=True, nullable=False),
    Column('symbol', String(10), nullable=False),
    Column('name', String(50), nullable=False),
    Column('last_updated', DateTime(timezone=True), onupdate=datetime.datetime.utcnow),
    Column('current_price', Float, nullable=False),
  )

  # Historical values of daily averages of a crypto
  prices = Table('prices', metadata_obj,
    Column('id', String(50), primary_key=True, nullable=False),
    Column('crypto', ForeignKey('crypto.id'), nullable=False),
    Column('date', DateTime(timezone=True), server_default=func.now()),
    Column('price', Float, nullable=False),
  )

  # datetime.utcfromtimestamp(ts) pass timestamp ts and convert to datetime
  # to insert into db...

  # # Historical trades per portfolio
  # trade = Table('trade', metadata_obj,
  #   Column('id', Integer, primary_key=True),
  #   Column('crypto', ForeignKey('crypto.id'), nullable=False),
  #   Column('date', DateTime(timezone=True), server_default=func.now()),
  #   Column('price', Float, nullable=False),
  # )

  # Number of shares and average price per share, update avg price on trades
  postion = Table('position', metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('crypto', ForeignKey('crypto.id'), nullable=False),
    Column('quantity', Float, nullable=False),
    Column('average_price', Float, nullable=False),    
  )

  # # Balance has one to one relationship with portfolio and is current acct balance
  # balance = Table('balance', metadata_obj,
  #   Column('id', Integer, primary_key=True),
  #   Column('total', Float, nullable=False),
  #   # (out of scope?)
  #   # Column('trade_profit_loss', Float, ForeignKey, nullable=False)
  # )

  # # Every user has a portfolio (out of scope?)
  # portfolio = Table('portfolio', metadata_obj,
  #   Column('id', Integer, primary_key=True),
  #   Column('owner', String(50), nullable=False),
  # )
  return metadata_obj