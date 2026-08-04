import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def create_db():
    passwords = ["", "postgres", "admin", "password"]
    conn = None
    for pwd in passwords:
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password=pwd,
                host="localhost",
                port="5432"
            )
            print(f"Connected with password: '{pwd}'")
            break
        except Exception as e:
            pass

    if not conn:
        print("Failed to connect to PostgreSQL")
        sys.exit(1)

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE DATABASE nextroute;")
        print("Database 'nextroute' created successfully")
    except psycopg2.errors.DuplicateDatabase:
        print("Database 'nextroute' already exists")
    except Exception as e:
        print(f"Error creating db: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_db()
