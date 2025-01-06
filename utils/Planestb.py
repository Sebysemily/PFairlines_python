from utils.TableManagerdb import TableManager


class PlaneTableManager(TableManager):
    """
    PlaneTableManager: subclass of TableManager to manage the planes table
    """
    expected_columns_and_types = {
        "plane_id": "integer",
        "name": "character varying",
        "rows": "integer",
        "cols": "ARRAY",
    }

    primary_key_column = "plane_id"

    def __init__(self, database: str, user: str, password: str, host: str = "localhost", port: str = "5432",
                 table_name: str = "planes"):
        """
        Initialize the PlaneTableManager
        """
        super().__init__(database, user, password, host, port, table_name)

    def insert_plane(self, data: dict, returning_column: str = None):
        """
        Alias for insert_record specific to planes.
        """
        return self.insert_record(data, returning_column)

    def load_plane(self, plane_id: int):
        """
        Alias for load_record specific to planes.
        """
        return self.load_record(plane_id)

    def update_plane(self, plane_id: int, data: dict) -> bool:
        """
        Alias for update_record specific to planes.
        """
        return self.update_record(plane_id, data)

    def delete_plane(self, plane_id: int) -> bool:
        """
        Alias for delete_record specific to planes.
        """
        return self.delete_record(plane_id)

    def generate_seats_identifiers(self, plane_id: int) -> list:
        """
        Generate seats identifiers for a plane.
        :param plane_id: primary key of the plane
        :return:  list of seats identifiers
        """
        plane_data = self.load_plane(plane_id)
        if not plane_data:
            raise ValueError(f"Plane ID: '{plane_id}' not found")
        rows = plane_data["rows"]
        cols = plane_data["cols"]

        seats_identifiers = []
        for row in range(1, rows + 1):
            for col in cols:
                seats_identifiers.append(f"{row}{col}")
        return seats_identifiers
