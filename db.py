from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from models import initialize_schema

class DatabaseConnection:
  def __init__(self, conn_string):
    # test connection
    print("\nconnection string: ", conn_string)
    self.engine = self.__create_engine(conn_string)

    # Initialize schema if db tables don't already exist.
    self.__create_schema()
    self.__test_connection()

  def __create_engine(self, conn_string):
    print("\ncreating engine...")
    return create_engine(conn_string)

  def __create_schema(self):
    print("\ncreating schema...")
    metadata = initialize_schema() # TODO: define and use this function
    metadata.create_all(self.engine)

  def __test_connection(self):
    print("\ntesting connection...")
    try:
      with self.engine.connect() as con:
        res = con.execute('SELECT VERSION();')
        for row in res:
          print(row)
        con.close()
    except SQLAlchemyError as err:
      print("error", err.__cause__)

  def query(self, sql):
    print(f"running query {sql} ...")
    try:
      with self.engine.connect() as con:
        res = con.execute(text(sql))
        result_objects = []
        for row in res:
          print(f"Row: {row}")
          result_objects.append(dict(row._mapping))
      con.close()
      return result_objects
    except SQLAlchemyError as err:
      print("error", err.__cause__)
