import psycopg2
from psycopg2 import sql

    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                            password="Sebi3980", port="5432")
    cur = conn.cursor()

    conn.commit()
    