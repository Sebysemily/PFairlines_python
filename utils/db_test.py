
from db import DatabaseManager
'''
conn = pg8000.connect(host="localhost", user="postgres", password="1234", port="5432")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS planes (
    plane_id SERIAL PRIMARY KEY,        
    name VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    cols TEXT[] NOT NULL
    );
""")
conn.commit()
cur.close()
conn.close()
'''

db_manager = DatabaseManager(host="localhost", database="postgres", user= "postgres", password="1234", port="5432",
                       table_name="planes")


db_manager.check_connection()
db_manager.reconnect()

plane_id = db_manager.insert_plane(rows=10, name="Plane A", columns=["A", "B", "C"])

# Test loading the inserted plane by ID
plane_data = db_manager.load_plane(plane_id)


# Test updating the plane

updated = db_manager.update_plane(plane_id, name="Updated Plane A", rows=15, columns=["D", "E", "F"])

print(plane_id, plane_data, updated)

