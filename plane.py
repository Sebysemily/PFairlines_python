from utils.db import DatabaseManager


class Plane:
    """
    Represents a plane object
    """
    def __init__(self, db_manager: DatabaseManager, plane_id: int = None, name: str = None, rows: int = None,
                 cols: list[str] = None):
        """
        Constructor, if None ID is provided, a new object is created.
        :param db_manager (DatabaseManager) A Database Manager instance
        :param plane_id (int, optional) The id of the plane, if None creates a new plane object in the table
        :param name (str, opt) The name of the plane (Required if plane_id is not provided or invalid)
        :param rows (int, opt) The number of rows in the plane (Required if plane_id is not provided or invalid)
        :param cols (list[str], opt) The list of column names in the plane
        (Required if plane_id is not provided or invalid)
        :
        """
        self.db_manager = db_manager
        self.plane_id = plane_id
        self.name = name
        self.rows = rows
        self.cols = cols
        if self.plane_id:
            if self._load_from_db() is None:
                print("Defaulting to inserting new plane")
                self._insert_to_db()
        else:
            self._insert_to_db()

    def _load_from_db(self) -> bool:
        """
        Loads the plane from the database with a given ID
        """
        data = self.db_manager.load_plane(self.plane_id)
        if data:
            self.name = data['name']
            self.rows = data['rows']
            self.cols = data['cols']
        else:
            return False
        return True

    def _insert_to_db(self):
        """
        Inserts a new plane to the database
        """
        try:
            self.plane_id = self.db_manager.insert_plane(self.rows, self.name, self.cols)
            if self.plane_id:
                print(f"New plane ID: , {self.plane_id} inserted successfully in table")
        except Exception as e:
            raise ValueError(f"Error: Failed to insert new plane with value {e}")

    
