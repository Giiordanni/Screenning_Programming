import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import os

load_dotenv()

def db_connection():
    try:
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            connection = psycopg2.connect(database_url)
        else:
            connection = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_DATABASE'),
                sslmode=os.getenv('DB_SSL_MODE'),
                channel_binding=os.getenv('DB_CHANNEL_BINDING')
            )
        
        print("Conectado com sucesso ao banco de dados")
        return connection
    except Error as e:
        print(f"Erro na conexão com o banco: {e}")
        return None
    
    