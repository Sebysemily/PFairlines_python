from utils.TableManagerdb import TableManager


class SeatsTableManager(TableManager):
    """
    SeatsTableManager: subclass of TableManager
    To manage the seats database
    """
    expected_columns_and_types = {
        "seat_id": "character varying",
        "flight_id": "integer",
        "is_reserved": "boolean",
        "reservation_details": "character varying",
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
        return self.insert_record(data, returning_column)

    def load_seat(self, seat_id: str):
        """
        Alias for load_record specific to seats
        """
        return self.load_record(seat_id)

    def update_seat(self, seat_id: str, data: dict) -> bool:
        """
        alias for update_record specific to seats
        """
        return self.update_record(seat_id, data)

    def delete_seat(self, seat_id: str) -> bool:
        """
        alias for delete_record specific to seats
        """
        return self.delete_record(seat_id)

    def is_seat_available(self, seat_id: str) -> bool:
        """
        Checks if a seat is available.
        :param seat_id: The seat to check.
        :return: bool, true if available
        """
        query = f"SELECT is_reserved FROM {self.table_name} WHERE seat_id = %s"
        result = super()._execute_query(query, (seat_id,))
        if not result:
            raise ValueError(f"Seat ID '{seat_id}' not found.")
        return not result[0][0]

    def reserve_seat(self, seat_id: str, reservation_details: str) -> bool:
        """
        Reserve a seat.
        :param seat_id: The seat to reserve.
        :param reservation_details: The reservation details.
        :return: bool, true if reserved
        """
        seat_data = self.load_record(seat_id)
        if not seat_data:
            raise ValueError(f"Seat ID '{seat_id}' not found.")
        if seat_data["is_reserved"]:
            print(f"Seat ID '{seat_id}' is already reserved.")
            return False
        return self.update_seat(seat_id, {"is_reserved": True, "reservation_details": reservation_details})

    def cancel_reservation(self, seat_id: str) -> bool:
        """
        Cancel a reserved seat.
        :param seat_id: The seat to cancel.
        :return: bool, true if cancelled
        """
        seat_data = self.load_record(seat_id)
        if not seat_data:
            raise ValueError(f"Seat ID '{seat_id}' not found.")
        if not seat_data["is_reserved"]:
            print(f"Seat ID '{seat_id}' is not reserved.")
            return False
        return self.update_seat(seat_id, {"is_reserved": False, "reservation_details": None})

    def list_available_seats(self, flight_id: int) -> list[dict]:
        """
        List available seats for a flight.
        :param flight_id: The ID of the flight
        :return: A list containing the available seats
        """
        query = f"SELECT seat_id FROM {self._table_name} WHERE flight_id = %s AND is_reserved = FALSE"
        results = super()._execute_query(query, (flight_id,))
        if not results:
            print(f"No available seats for flight {flight_id}.")
            return []
        return [dict(zip(self._columns, row)) for row in results]



