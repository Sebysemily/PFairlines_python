
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

print("Checking connection...")
db_manager.check_connection()
# Test table existence
print("Checking if table exists...")
db_manager._check_table_exists()
# Test table structure
print("Checking table structure...")
db_manager._check_table_structure()
print("Inserting a plane...")
plane_id = db_manager.insert_plane(rows=10, name="Plane A", columns=["A", "B", "C"])
if plane_id:
    print(f"Plane inserted with ID: {plane_id}")
else:
    print("Failed to insert plane.")

# Test loading the inserted plane by ID
print("Loading the plane by ID...")
plane_data = db_manager.load_plane(plane_id)
if plane_data:
    print(f"Loaded plane data: {100}")
else:
    print("Failed to load plane.")

# Test updating the plane
print("Updating the plane...")
updated = db_manager.update_plane(plane_id, name="Updated Plane A", rows=15, columns=["D", "E", "F"])
if updated:
    print("Plane updated successfully.")
else:
    print("Failed to update plane.")

# Test deleting the plane
print("Deleting the plane...")
deleted = db_manager.delete_plane(plane_id)
if deleted:
    print("Plane deleted successfully.")
else:
    print("Failed to delete plane.")


