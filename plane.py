
class Plane:
    """Represents a plane"""
    def __init__(self, plane_id, name, rows=5, cols=("A", "B", "C", "D")):
        self.plane_id = plane_id
        self.name = name
        self.rows = rows
        self.cols = cols
        self.seats = {}

    def initialize_seats(self, day):
        for row in range(1, self.rows + 1):
            for columns in self.cols:
                seat = f"{columns}{row}"
                insert_seat(self.plane_id, seat, day)

    def load_seats(self, day):
        self.seats = {}
        query = """
        SELECT seat, reserved
        from seats
        WHERE plane_id = %s AND day = %s;
        """
        seat_data = execute_query(query, (self.plane_id, day))
        if seat_data:
            for seat, reserved in seat_data:
                self.seats[seat] = reserved

    def display_seats(self):
        print(f"\nSeating arrangement for {self.name}:")
        print("    "+" ".join(self.cols))
        for row in range(1, self.rows+1):
            row_display = []
            for column in self.cols:
                seat = f"{column}{row}"
                row_display.append("X" if self.seats.get(seat, False) else "*")
            print(f"Row {row:<2}: " + " ".join(row_display))

    def reserve_seat(self, seat, day):
        if seat not in self.seats:
            print(f"Seat {seat} does not exist in this plane. ")
            return False
        if self.seats[seat]:
            print(f"Seat {seat} is already reserved.")
            return False
        success = reserve_seat(self.plane_id, seat, day)
        if success:
            self.seats[seat] = True
            print(f"Seat {seat} has been successfully reserved.")
            return True
        else:
            print(f"Failed to reserve seat {seat}.")
            return False

    def get_available_seats(self, day):
        return get_available_seats(self.plane_id, day)