
from Planestb import PlaneTableManager
from Seatstb import SeatsTableManager
from Flightstb import FlightsTableManager
'''
conn = pg8000.connect(host="localhost", user="postgres", password="1234", port="5432")
cur = conn.cursor()
cur.execute("""CREATE TABLE flights (
    flight_id SERIAL PRIMARY KEY,
    plane_id INTEGER NOT NULL,
    origin VARCHAR NOT NULL,
    destination VARCHAR NOT NULL
);

""")
conn.commit()
cur.close()
conn.close()
'''

new_plane = {
    "name": "Airbus A320",
    "rows": 20,
    "cols": ["A", "B", "C", "D", "E", "F"]
}
flights_manager = FlightsTableManager(host="localhost", database="postgres", user="postgres", password="1234", port="5432",
                               table_name="flights")


flights_manager.check_connection()
flights_manager.reconnect()
plane_manager = PlaneTableManager(host="localhost", database="postgres", user="postgres", password="1234", port="5432",
                               table_name="planes")
plane_id = plane_manager.insert_plane(new_plane)
flight_data = {
    "plane_id": plane_id,
    "origin": "Quito",
    "destination": "New York",
}
flight_id = flights_manager.insert_flight(flight_data, returning_column="flight_id")
print(f"Inserted flight with ID: {flight_id}")

flight = flights_manager.load_flight(flight_id)
print("Flight loaded:", flight)

update_data = {"origin": "GYE"}
update_success = flights_manager.update_flight(flight_id, update_data)
print(f"Flight updated: {update_success}")

seats_manager = SeatsTableManager(host="localhost", database="postgres", user="postgres", password="1234", port="5432",
                                table_name="seats")
flights_manager.create_seats_for_flight(flight_id, seats_manager, plane_manager)
seats = seats_manager.list_available_seats(flight_id)

print(f"Available seats: {seats}")