from utils.TableManager import TableManager


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