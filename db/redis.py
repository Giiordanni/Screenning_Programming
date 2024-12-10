import redis
import os
from dotenv import load_dotenv

load_dotenv()

def redis_client():
    connection = redis.StrictRedis.from_url(os.getenv("REDIS_CLIENT"), decode_responses=True)
    try:
        connection.ping()
        print("Conectado com sucesso ao Redis")
        return connection
    except redis.ConnectionError:
        print("Falha ao conectar ao Redis")
        return None