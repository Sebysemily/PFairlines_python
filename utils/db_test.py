import pg8000
from Planestb import PlaneTableManager
from Seatstb import SeatsTableManager
from Flightstb import FlightsTableManager
from utils.Reservationstb import ReservationsTableManager

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s [%(levelname)s] %(message)s"
)

'''
conn = pg8000.connect(host="localhost", user="postgres", password="1234", port="5432")
cur = conn.cursor()

cur.execute("""CREATE TABLE planes (
    plane_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rows INTEGER NOT NULL,
    cols VARCHAR[] NOT NULL
);
""")

cur.execute("""CREATE TABLE flights (
    flight_id SERIAL PRIMARY KEY,
    plane_id INTEGER NOT NULL,
    origin VARCHAR NOT NULL,
    destination VARCHAR NOT NULL,
    CONSTRAINT fk_plane FOREIGN KEY (plane_id) REFERENCES planes (plane_id) ON DELETE CASCADE
);

""")

cur.execute("""CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY, 
    name VARCHAR(255) NOT NULL 
);""")

cur.execute("""CREATE TABLE seats (
    seat_id VARCHAR(50) PRIMARY KEY, 
    flight_id INTEGER NOT NULL, 
    reservation_id INTEGER, 
    CONSTRAINT fk_flight FOREIGN KEY (flight_id) REFERENCES flights (flight_id) ON DELETE CASCADE,
    CONSTRAINT fk_reservation FOREIGN KEY (reservation_id) REFERENCES reservations (reservation_id) ON DELETE SET NULL
);
""")

conn.commit()
cur.close()
conn.close()

'''

flights_manager = FlightsTableManager(host="localhost", database="postgres", user="postgres", password="1234", port="5432",
                               table_name="flights")

seats_manager = SeatsTableManager(host="localhost", database="postgres", user="postgres", password="1234", port="5432",
                                  table_name="seats")
plane_manager = PlaneTableManager(host="localhost", database="postgres", user="postgres", password="1234", port="5432",
                               table_name="planes")
reservations_manager = ReservationsTableManager(host="localhost", database="postgres", user="postgres", password="1234",
                                                table_name="reservations")

new_plane = {
    "name": "Airbus A320",
    "rows": 20,
    "cols": ["A", "B", "C", "D", "E", "F"]
}


reservation_data = {"name": "John Doe"}

plane_id = plane_manager.insert_plane(new_plane)
flight_data = {
    "plane_id": plane_id,
    "origin": "Quito",
    "destination": "New York",
}

flight_id = flights_manager.insert_flight(seats_manager, plane_manager, flight_data)
print(f"Inserted flight with ID: {flight_id}")

flight = flights_manager.load_flight(flight_id)
print("Flight loaded:", flight)

update_data = {"origin": "GYE"}
update_success = flights_manager.update_flight(flight_id, update_data)
print(f"Flight updated: {update_success}")
seats_total = seats_manager.list_seats_for_flight(flight_id)

seats = seats_manager.list_available_seats_for_flight(flight_id)
print(f"Available seats: {seats}")


seat_ids = [f"{flight_id}-A1, {flight_id}-A2"]

reservation_id = 0
try:
    reservation_id = reservations_manager.insert_reservation(seats_manager, reservation_data, seat_ids)
    print(f"Inserted reservation with ID: {reservation_id}")
except ValueError as e:
    print(f"Error inserting reservation: {e}")

all_reservations = reservations_manager.list_all_reservations()
for reservation in all_reservations:
    print(reservation)

update_data = {"name": "Jane Doe"}

seats_in_reservation = reservations_manager.seats_in_reservation(reservation_id, seats_manager)
print("\nSeats in Reservation:")
for seat in seats_in_reservation:
    print(seat)
available_seats = seats_manager.list_available_seats_for_flight()
print(f"Available seats: {available_seats}")
delete_success = reservations_manager.delete_reservation(reservation_id)
print(f"\nReservation deleted: {delete_success}")
available_seats = seats_manager.list_available_seats_for_flight()
print(f"Available seats: {available_seats}")

print("\nReservations after deletion:")
all_reservations = reservations_manager.list_all_reservations()
for reservation in all_reservations:
    print(reservation)
