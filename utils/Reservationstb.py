from utils.TableManagerdb import TableManager
from utils.Seatstb import SeatsTableManager


class ReservationsTableManager(TableManager):
    """
    ReservationsTableManager :subclass of TableManager
    To manage the reservations database
    """
    expected_columns_and_types = {
        "reservation_id": "integer",
        "name": "character varying",
    }
    primary_key_column = "reservation_id"

    def __init__(self, database: str, user: str, password: str, host: str = "localhost", port: str = "5432",
                 table_name: str = "reservations"):
        """
        Initialize the ReservationsTableManager
        """
        super().__init__(database, user, password, host, port, table_name)

    def insert_reservation(self, seats_table_manager: SeatsTableManager, reservation_data: dict, seat_ids: list[str]):
        """
        Alias for insert_record specific to reservation
        :param seats_table_manager: SeatsTableManager
        :param reservation_data: dict
        :param seat_ids: list[str]
        :return: the reservation_id
        """
        available_seats = []
        already_reserved = []
        invalid_seats = []
        for seat_id in seat_ids:
            try:
                seat_data = seats_table_manager.load_seats(seat_id)
                if seat_data[0]["reservation_id"] not in (None, 0):
                    already_reserved.append(seat_id)
                else:
                    available_seats.append(seat_id)
            except ValueError as e:
                print(e)
                invalid_seats.append(seat_id)

        print("\nSeat Reservation Summary:")
        print(f"Available seats: {available_seats}")
        if already_reserved:
            print(f"Already reserved seats: {already_reserved}")
        if invalid_seats:
            print(f"Invalid seats: {invalid_seats}")
        if not available_seats:
            raise ValueError("No available seats")
        confirm = input("\nDo you want to proceed with the reservation [y/n]")
        if confirm != "y":
            print("Reservation creation aborted.")
            return None
        try:
            reservation_id = super().insert_record(reservation_data)
            print(f"Reservation created with ID: {reservation_id}")
        except ValueError as e:
            print(f"Error creating reservation: {e}")
            return None

        for seat_id in available_seats:
            try:
                seats_table_manager.update_seat(seat_id, {"reservation_id": reservation_id})
                print(f"Seat ID '{seat_id}' successfully reserved.")
            except ValueError as e:
                print(f"Error reserving seat ID '{seat_id}': {e}")

        return reservation_id

    def load_reservation(self, reservation_id: int):
        """
        Alias for load_record specific to reservations
        """
        return super().load_record(reservation_id)

    def update_reservation(self, reservation_id: int, data: dict) -> bool:
        """
        alias for update_record specific to reservations
        """
        return self.update_record(reservation_id, data)

    def delete_reservation(self, reservation_id: int) -> bool:
        """
        alias for delete_record specific to reservations
        """
        return super().delete_record(reservation_id)

    def _reserve_seat(self, seats_table_manager: SeatsTableManager, reservation_id: int, seat_id: str) -> bool:
        """
        Reserve a seat.
        :param seats_table_manager: An instance of SeatsTableManager.
        :param reservation_id: The seat to reserve.
        :param seat_id: The reservation details.
        :return: bool, true if reserved
        """
        seat_data = seats_table_manager.load_seats(seat_id)
        if seat_data[0]["reservation_id"] not in (None, 0):
            print(f"Seat ID '{seat_id}' is already reserved.")
            return False

        return seats_table_manager.update_seat(seat_id, {"reservation_id": reservation_id})

    def _cancel_seat_reservation(self, seat_id: str, seats_table_manager: SeatsTableManager) -> bool:
        """
        Cancel a reserved seat.
        :param seat_id: The seat to cancel.
        :param seats_table_manager: An instance of SeatsTableManager.
        :return: bool, true if cancelled
        """
        seat_data = seats_table_manager.load_seats(seat_id)

        if seat_data[0]["reservation_id"] in (None, 0):
            print(f"Seat ID '{seat_id}' is not reserved.")
            return False

        return seats_table_manager.update_seat(seat_id, {"reservation_id": None})

    def seats_in_reservation(self, reservation_id: int, seats_table_manager: SeatsTableManager) -> list[dict]:
        """
        Gives all seats associated with a specific reservation.
        :param reservation_id: The reservation ID.
        :param seats_table_manager: An instance of SeatsTableManager.
        :return: A list of seats associated with the reservation.
        """
        return [
            seat for seat in seats_table_manager.load_seats(reservation_id, "reservation_id")
            if seat["reservation_id"] not in (None, 0)
        ]

    def list_all_reservations(self) -> list[dict]:
        """
        list all reservations in the database.
        :return: A list of reservations.
        """
        try:
            return self.load_all_records()
        except Exception as e:
            print(f"Error listing all reservations: {e}")
            return []
