import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import DatabaseError
from dotenv import load_dotenv


load_dotenv()

class Database:
    def __init__(self):
        self.connection = None
    
        self.db_config = {
            "dbname": os.getenv("DATABASE_NAME"),
            "user": os.getenv("DATABASE_USER"),
            "password": os.getenv("DATABASE_PASSWORD"),
            "host": os.getenv("DATABASE_HOST"),
            "port": os.getenv("DATABASE_PORT"),
        }

    def connect(self):
        try:
            if not self.connection or self.connection.closed:
                self.connection = psycopg2.connect(**self.db_config)
            return self.connection
        except DatabaseError as e:
            print("Database connection error:", e)
            raise

    def execute_query(self, query, params=None):
        try:
            conn = self.connect()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
        except Exception as e:
            print("Error executing query:", e)
            raise

    def fetch_query(self, query, params=None):
        try:
            conn = self.connect()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print("Error fetching query:", e)
            raise

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
