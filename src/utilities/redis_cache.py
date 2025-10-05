from .logger import Logger
from .constants import ConstantsFetcher
from dotenv import load_dotenv
import asyncio
import redis 
import os 


load_dotenv()
logger = Logger.getLogger(__name__)


class RedisHandler:


    def __init__(self):
        self.redis = redis.asyncio.Redis(host='localhost', port=6379, db=0, 
                                        username=os.getenv('REDIS_USERNAME'),
                                        password=os.getenv('REDIS_PASSWORD'),
                                        decode_responses=True)
        

    
    def getRedis(self):
        return self.redis
