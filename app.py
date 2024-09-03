"""
app.py - PostgreSQL DB 'employee' table data manager.
"""

import random
import logging

import pandas as pd
import psycopg2
from faker import Faker

log = logging.getLogger(__name__)

def generate_data(how_many):
    """Employee fake data generator.
    """
    fake = Faker()
    for _ in range(how_many):
        person = (
            fake.first_name(),
            random.randint(18, 100),
            fake.job()
        )
        yield person

def create_db_table(conn, tablename):
    """Create a table.
    """
    try:
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {tablename} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                age INT CHECK (age >= 0 AND age <= 100) NOT NULL,
                department VARCHAR(50) NOT NULL
            );
        """)
        conn.commit()
        cur.close()
        #log.info("Table %s created successfully", tablename)
        return
    except psycopg2.errors.SyntaxError as e:
        log.error("Error creating table %s: %s", tablename, e)
    except psycopg2.DatabaseError as e:
        log.error("Database error: %s", e)
    except AttributeError as e:
        log.error("Database connection error: %s", e)
    except Exception as e:
        log.error("Error: %s", e)
    conn.rollback()

def insert_data_into_table(conn, tablename):
    """Insert data into the table.
    """
    try:
        cur = conn.cursor()

        cur.executemany(f"""
            INSERT INTO {tablename} (name, age, department) 
            VALUES (%s, %s, %s)
        """, generate_data(10))
        conn.commit()
        cur.close()
        #log.info("Data inserted into table %s successfully", tablename)
    except Exception as e:
        log.error("Data inserting error: %s", e)
        conn.rollback()

def read_data_from_db(conn, tablename):
    """Read data from table.
    """
    try:
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM {tablename}')

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        dataframe = pd.DataFrame(rows, columns=columns)
        cur.close()
        #log.info("Data read from table %s successfully", tablename)
        return dataframe
    except psycopg2.Error as e:
        log.error("Error reading data from table %s: %s", tablename, e)
        return None
    except Exception as e:
        log.error("Error: %s", e)
        return None

def print_dataframe(dataframe):
    """Print dataframe.
    """
    try:
        for _, row in dataframe.iterrows():
            print(
                f"ID: {row['id']}, "
                f"Name: {row['name']}, "
                f"Age: {row['age']}, "
                f"Department: {row['department']}"
            )
    except KeyError as e:
        log.error("Error printing dataframe: missing column %s", e)
    except Exception as e:
        log.error("Error: %s", e)

def connect_to_db():
    """Connect to the PostgreSQL database.
    """
    conn = None
    # DB data
    db_name = 'postgres'
    db_user = 'postgres'
    db_password = 'mysecretpassword'
    db_host = 'db'
    db_port = '5432'
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        #log.info("Connected to database %s successfully", db_name)
    except psycopg2.OperationalError:
        log.error("Connection to server at %s:%s failed", db_host, db_port)
    except Exception as e:
        log.error("Error: %s", e)
    return conn


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    connect = connect_to_db()
    if connect is not None:
        create_db_table(connect, 'employees')
        insert_data_into_table(connect, 'employees')
        df = read_data_from_db(connect, 'employees')
        print_dataframe(df)
    else:
        log.info("Exited")
