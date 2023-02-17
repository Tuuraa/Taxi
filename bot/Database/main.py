import os

import aiomysql
from pymysql import connect
import asyncio
import os

class DBParameters:
    def __init__(self):
        self.Host = "localhost"
        self.Users = "root"
        self.Password = '4789'
        self.loop = asyncio.get_event_loop()


