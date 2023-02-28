import aiomysql
from pymysql import connect
import asyncio
import os

#user = os.path.abspath(__file__).split('\\')[2]


class DBParameters:
    def __init__(self):
        self.Host = "localhost"
        self.Users = "root"
        self.Password = '5377'#4789' if user == 'пк' else '5377'
        self.DB_NAME = "taxi"
        self.loop = asyncio.new_event_loop()


db_config = DBParameters()


async def async_connect_to_my_sql():
    connection = await aiomysql.connect(
        host=db_config.Host,
        user=db_config.Users,
        db=db_config.DB_NAME,
        password=db_config.Password,
        loop=db_config.loop
    )
    cursor = await connection.cursor()
    return connection, cursor


def create_sync_con():
    con = connect(
        host=db_config.Host,
        user=db_config.Users,
        db=db_config.DB_NAME,
        password=db_config.Password
    )

    cur = con.cursor()
    return con, cur