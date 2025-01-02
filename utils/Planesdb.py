from utils.db import DatabaseManager


class PlaneDatabaseManager(DatabaseManager):
    """
    PlaneDatabaseManager: subclass of DatabaseManager
    To manage the planes database
    """
    def __init__(self,  database: str, user: str, password: str, host: str = "localhost", port: str = "5432",
                 table_name: str = "planes") -> None:
        super().__init__(database, user, password, host, port)
        self.user_table_name = table_name
        if self.is_table_valid():
            self.table_name = self.user_table_name
            print("Valid table, connection established")
        else:
            raise ValueError("Invalid table name exiting...")

    @property
    def table_name(self) -> str:
        return self._table_name

    @table_name.setter
    def table_name(self, value):
        self._table_name = value

    def display_table_name(self) -> None:
        print(f"Current table Name: {self._table_name}")

    def _set_new_table_name(self) -> None:
        self.user_table_name = input("Enter new table name: ")
        super().display_credentials()
        self.display_table_name()
        confirmation = ((input("Given current credentials do you wish to proceed? with the change (y/n): ")).
                        lower().strip())
        
        if confirmation != "y":
            print("Table name change canceled, keeping current name...")
            return
        
        if not self.is_table_valid():
            print("Invalid table name, connection not established... Returning to original table")
            return
    
        self.table_name = self.user_table_name
        print("Table name changed!")
        return

    def _check_table_exists(self) -> bool:
        """
        Check if a table exists in the database. For internal use only.
        :return: bool, true if table exists.
        """
        query = """
               SELECT EXISTS(
               SELECT 1 
               FROM information_schema.tables 
               WHERE table_name = %s
               );
                """
        result = super()._execute_query(query, (self.user_table_name,))
        if result and result[0]:
            return True
        return False

    def _check_table_structure(self) -> bool:
        """
        Check if the table has a correct table structure For internal use.
        :return: bool, true if the table structure is valid.
        """

        query = """
               SELECT column_name, data_type 
               FROM information_schema.columns 
               WHERE table_name = %s
               """
        columns_data = super()._execute_query(query, (self.user_table_name,))

        if columns_data is None:
            print(f"Error no data returned for table columns in {self.user_table_name}")
            return False

        if not all(len(column_data) == 2 for column_data in columns_data):
            print(f"Unexpected data structure for table columns: {columns_data} in {self.user_table_name}")
            return False

        expected_columns_and_types = {
            "plane_id": "integer",
            "name": "character varying",
            "rows": "integer",
            "cols": "ARRAY",
        }

        actual_column_names = set(column for column, _ in columns_data)
        expected_columns_names = set(expected_columns_and_types.keys())
        missing_column_names = expected_columns_names - actual_column_names
        extra_column_names = actual_column_names - expected_columns_names
        if missing_column_names:
            print(f"Missing columns: {', '.join(missing_column_names)} in {self.user_table_name}")
            return False
        if extra_column_names:
            print(f"Extra columns: {', '.join(extra_column_names)} in {self.user_table_name}")
            return False

        for column, actual_type in columns_data:
            expected_type = expected_columns_and_types.get(column)
            if expected_type and expected_type != actual_type:
                print(f"Column '{column}' has an invalid data type: expected "f"'{expected_type}',"
                      f" found '{actual_type}'")
                return False
        return True

    def is_table_valid(self, table_name: str = None) -> bool:
        """
        Check if a valid table exists in the database. For internal use.
        Sets the user_table_name to the table_name attribute if successful.
        :return: true if the table is valid.
        """
        if table_name:
            self.user_table_name = table_name
        if not self._check_table_exists():
            print("Table doesnt exists")
            return False
        elif not self._check_table_structure():
            print("Table structure invalid")
            return False
        else:
            print(f"Table structure from table '{self.user_table_name}' is valid")
            return True

    def load_plane(self, plane_id: int):
        """
        Load a plane´s data from the database.
        :return: A dictionary containing the plane data
        """
        query = f"SELECT * FROM {self.table_name} WHERE plane_id = %s"
        result = super()._execute_query(query, (plane_id,))
        if result is None:
            print(f"Plane ID: '{plane_id}' not found")
            return None
        plane_data = {
            "plane_id": result[0][0],
            "name": result[0][1],
            "rows": result[0][2],
            "columns": result[0][3],
        }
        return plane_data

    def insert_plane(self, rows: int, name: str, columns: list[str], plane_id: int = None):
        """
        Insert a plane into the database.
        :param name: The name of the plane
        :param rows: The number of rows in the plane
        :param columns: The number of columns in the plane.
        :param plane_id: The ID of the plane (Optional for not auto-incrementing plane_ids)
        :return: The plane ID.
        """
        if not name:
            print("Error: Plane name cannot be empty")
            return None
        if rows <= 0:
            print("Error: Rows must be greater than 0")
            return None
        if not columns:
            print("Error: Columns cannot be empty")
            return None

        if plane_id is None:
            query = f"""INSERT INTO {self.table_name} (name, rows, cols) 
                            VALUES (%s, %s, %s)
                            RETURNING plane_id;"""
            result = super()._execute_query(query, (name, rows, columns), True)
            if result:
                print(f"Plane ID: '{result[0][0]}' inserted successfully")
                return result[0][0]
        else:
            query_n = f"""INSERT INTO {self.table_name} (plane_id, name, rows, cols) 
                              VALUES (%s, %s, %s, %s)
                              RETURNING plane_id;"""
            result_n = super()._execute_query(query_n, (plane_id, name, rows, columns), True)
            if result_n:
                print(f"Plane ID: '{result_n[0][0]}' inserted successfully")
                return result_n[0][0]
        return None

    def update_plane(self, plane_id: int, name: str = None, rows: int = None, columns: list[str] = None) -> bool:
        """
        Update a plane from the database.
        :param plane_id: The ID of the plane
        :param name: Name of the plane
        :param rows: The number of rows in the plane
        :param columns: The number of columns in the plane.
        :return: bool, true if update was successful
        """
        updates = []
        params = []
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if rows is not None:
            updates.append("rows = %s")
            params.append(rows)
        if columns is not None:
            updates.append("cols = %s")
            params.append(columns)
        if not updates:
            print("No updates provided")
            return False

        query = f"""
                 UPDATE {self.table_name} 
                 SET {', '.join(updates)}
                 WHERE plane_id = %s
                 """
        params.append(plane_id)

        result = super()._execute_query(query, tuple(params), True)
        if result is None:
            print(f"Plane ID: '{plane_id}' not found")
        else:
            print(f"Plane ID: '{plane_id}' updated successfully")
        return result

    def delete_plane(self, plane_id: int) -> bool:
        """
        Delete a plane from the database.
        :param plane_id: The ID of the plane
        :return: bool, True if delete was successful
        """
        query = f"DELETE FROM {self.table_name} WHERE plane_id = %s"
        result = super()._execute_query(query, (plane_id,), True)
        if result:
            print(f"Plane ID: {plane_id} deleted")
            return True
        else:
            print(f"Plane ID: {plane_id} not found")
            return False
