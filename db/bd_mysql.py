import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()


def db_connection():
    try:
        connection = mysql.connector.connect(
            host = os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE')
        )
        if connection.is_connected():
            print("Conectado com suceso ao banco de dados")
        return connection
    except Error as e:
            print(f"Error: {e}")
            return None
    
    