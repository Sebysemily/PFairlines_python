from utils.TableManagerdb import TableManager


class SeatsTableManager(TableManager):
    """
    SeatsTableManager: subclass of TableManager
    To manage the seats database
    """
    expected_columns_and_types = {
        "seat_id": "character varying",
        "flight_id": "integer",
        "reservation_id": "integer",
    }
    primary_key_column = "seat_id"

    def __init__(self, database: str, user: str, password: str, host: str = "localhost", port: str = "5432",
                 table_name: str = "seats"):
        """
        Initialize the SeatsTableManager
        """
        super().__init__(database, user, password, host, port, table_name)

    def insert_seat(self, data: dict, returning_column: str = None):
        """
        Alias for insert_record specific to seats
        """
        return super().insert_record(data, returning_column)

    def load_seats(self, seat_id, column_to_search=None):
        """
        Alias for load_record specific to seats
        """
        return super().load_record(seat_id, column_to_search)

    def update_seat(self, seat_id: str, data: dict) -> bool:
        """
        alias for update_record specific to seats
        """
        return super().update_record(seat_id, data)

    def delete_seat(self, seat_id: str) -> bool:
        """
        alias for delete_record specific to seats
        """
        return super().delete_record(seat_id)

    def is_seat_available(self, seat_id: str):
        """
        Checks if a seat is available.
        :param seat_id: The seat to check.
        :return: bool, true if available
        """
        seat_data = self.load_seats(seat_id)
        return seat_data[0][0] in (None, "", 0)

    def list_available_seats_for_flight(self, flight_id: int) -> list[dict]:
        """
        List available seats for a flight.
        :param flight_id: The ID of the flight
        :return: A list containing the available seats
        """
        seats_data = self.load_seats(flight_id, "flight_id")
        seat_list = [
            {"seat_id": seat["seat_id"], "reservation_id": seat["reservation_id"]}
            for seat in seats_data
        ]
        available_seats = [
            seat for seat in seat_list if seat["reservation_id"] in (None, "", 0)
        ]

        return available_seats

    def list_seats_for_flight(self, flight_id: int) :
        """
        List seats for a flight.
        :param flight_id: The ID of the flight
        :return: A list containing the available seats or None if empty
        """
        seats_for_flight = self.load_seats(flight_id, "flight_id")
        return seats_for_flight
