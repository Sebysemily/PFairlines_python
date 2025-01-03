from utils.Planestb import PlaneTableManager
from utils.Seatstb import SeatsTableManager
from utils.TableManagerdb import TableManager


class FlightsTableManager(TableManager):
    """
    flights table manager: subclass of TableManager
    To manage the flights database
    """
    expected_columns_and_types = {
        "flight_id": "integer",
        "plane_id": "integer",
        "origin": "character varying",
        "destination": "character varying",
    }
    primary_key_column = "flight_id"

    def __init__(self, database: str, user: str, password: str, host: str = "localhost", port: str = "5432",
                 table_name: str = "flights"):
        """
        Initialize the FlightsTableManager
        """
        super().__init__(database, user, password, host, port, table_name)

    def insert_flight(self, data: dict, returning_column: str = None):
        """
        Alias for insert_record specific to flights.
        """
        return self.insert_record(data, returning_column)

    def load_flight(self, flight_id: int):
        """
        Alias for load_record specific to flights.
        """
        return self.load_record(flight_id)

    def update_flight(self, flight_id: int, data: dict) -> bool:
        """
        Alias for update_record specific to flights.
        """
        return self.update_record(flight_id, data)

    def delete_flight(self, flight_id: int) -> bool:
        """
        Alias for delete_record specific to flights.
        """
        return self.delete_record(flight_id)

    def create_seats_for_flight(self, flight_id: int, seats_table_manager: SeatsTableManager,
                                plane_manager: PlaneTableManager):
        """
        Generate seats for a flight based on the associated plane and store them in the seats table.
        :param flight_id: The ID of the flight.
        :param seats_table_manager: An instance of SeatsTableManager.
        :param plane_manager: an instance of PlaneTableManager.
        """
        flight_data = self.load_flight(flight_id)
        if not flight_data:
            raise ValueError(f"Flight ID: '{flight_id}' was not found.")

        plane_id = flight_data["plane_id"]

        seat_identifiers = plane_manager.generate_seats_identifiers(plane_id)

        seats = [
            {
                "seat_id": f"{flight_id}-{seat_id}",
                "flight_id": flight_id,
                "is_reserved": False,
                "reservation_details": ""
            }
            for seat_id in seat_identifiers
        ]

        for seat in seats:
            seats_table_manager.insert_seat(seat)

        print(f"Seats for flight '{flight_id}' created successfully.")
