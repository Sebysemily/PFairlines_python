
from Planesdb import PlaneTableManager
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

db_manager = PlaneTableManager(host="localhost", database="postgres", user="postgres", password="1234", port="5432",
                               table_name="planes")


db_manager.check_connection()
db_manager.reconnect()

new_plane = {
    "name": "Airbus A320",
    "rows": 20,
    "cols": ["A", "B", "C", "D", "E", "F"]
}
new_plane_id = db_manager.insert_plane(new_plane)
print(f"Inserted Plane ID: {new_plane_id}")

# Load a plane
plane_data = db_manager.load_plane(new_plane_id)
print("Loaded Plane Data:", plane_data)

# Update a plane
db_manager.update_plane(new_plane_id, {"name": "Airbus A320 Updated", "rows": 30})

plane_data = db_manager.load_plane(new_plane_id)

print("Updated Plane Data:", plane_data)
# Delete a plane
db_manager.delete_plane(new_plane_id)

