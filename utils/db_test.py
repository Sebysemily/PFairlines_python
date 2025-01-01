import pg8000


conn = pg8000.connect(host="localhost", user="postgres",
                        password="1234", port="5432")
cur = conn.cursor()

cur.execute( """CREATE TABLE IF NOT EXISTS planes (
    plane_id SERIAL PRIMARY KEY,        
    name VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    cols TEXT[] NOT NULL
    );
""")

conn.commit()

cur.close()
conn.close()