
import pg8000 as db
import time


class DatabaseManager:
    """
    Manages a database connection for plane objects.
    """

    def __init__(self, database: str, user: str, password: str, host: str = "localhost", port: str = "5432",
                 table_name: str = "planes") -> None:
        """
        Initialize a connection to the database, stop running if valid connection is not established.
        :param database: database name
        :param user: username
        :param password: password
        :param host: host name (default: localhost)
        :param port: port connection (default: 5432)
        :param table_name: table name (default: planes)
        """
        self.user_credentials = {
            "database": database,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self.user_table_name = table_name
        self._table_name = None
        self._conn = None
        self._credentials = None
        self.max_retries = 10
        self.retry_delay = 0.5

        if not self._set_conn():
            raise ValueError("Invalid credentials, connection not established exiting...")
        elif not self._set_table_name():
            raise ValueError("Invalid table name exiting...")
        else:
            print(f"Valid connection established")

    def __del__(self):
        pass

    @property
    def credentials(self):
        return self._credentials

    @property
    def table_name(self):
        return self._table_name

    def __execute_query(self, query, params=None, commit=False):
        """
        Helper method to execute a query.
        :param query: SQL query.
        :param params: Parameters to pass to the query. (Optional)
        :param commit: Commit transaction. (Optional)
        :return:
            list[] = The result of the query.
            True = if successful commit operation without return.
        """
        try:
            if not self.check_connection():
                raise ValueError("Connection not established exiting...")
            cursor = self._conn.cursor()
            cursor.execute(query, params)

            is_select_query = query.strip().lower().startswith("select")

            if is_select_query:
                result = cursor.fetchall()
                if not result:
                    print("No matching data found in the database")
                    cursor.close()
                    return None
            elif not is_select_query and "returning" in query.lower():
                result = cursor.fetchall()
            else:
                result = None
            if commit:
                self._conn.commit()

            cursor.close()
            return result if result else True

        except (db.DatabaseError, ConnectionError) as e:
            print(f"Error while executing query: {e}")
            if self.check_connection():
                if commit:
                    self._conn.rollback()
                    print("transaction rollback due to error")
                return self.__execute_query(query, params, commit)

    def __stop_connection(self):
        """
        Disconnects from the current connection and set credentials to None.
        For internal use only.
        """
        if self._conn:
            print("Disconnecting from database...")
            self._conn.close()
            self._conn = None
            self._credentials = None
            self._table_name = None
        else:
            print("No connection to database to disconnect...")

    def check_connection(self) -> bool:
        """
        Check if the connection to the database is still active.
        If connection is not active attempts to reconnect.
        :return: bool, True if connection is active, or successfully reconnected.
        """
        try:
            if self._conn is None:
                print("No connection established... Attempting to reconnect...")
                return self.reconnect()
            cursor = self._conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except (db.DatabaseError, AttributeError) as e:
            print(f"Error while connecting to database: {e}. Attempting to reconnect...")
            return self.reconnect()

    def reconnect(self) -> bool:
        """
        Attempts to reconnect to the database using the current credentials.
        Retries multiple times with delays.
        :return: bool, True if reconnection was successful.
        """
        try:
            retry_count = 0
            self.user_credentials = self._credentials
            while retry_count < self.max_retries:
                print(f"reconnect attempt {retry_count + 1} of {self.max_retries}")
                if self._set_conn():
                    return True
                else:
                    retry_count += 1
                    print(f"Re-connection failed. Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
            print("Failed to reconnect. after maximum retries.")
            return False
        finally:
            self.user_credentials = None

    def set_credentials(self):
        """
        Allow setting new credentials for a database connection
        If the new credentials are invalid or te table to connect is invalid
        object returns to original connection
        """
        self.user_credentials = {
            "database": input("Enter database name: "),
            "user": input("Enter username: "),
            "password": input("Enter password: "),
            "host": input("Enter database host (default: localhost): ") or "localhost",
            "port": input("Enter database port(default: 5432): ") or "5432",
        }
        self.user_table_name = input("Enter table name: ")

        self.display_credentials()
        confirmation = (input("Given current credentials, are you sure you want to attempt a new connection? (y/n): ")
                        .lower())
        if confirmation != "y":
            print("Credentials change cancelled keeping current credentials")
            return

        original_credentials = self.credentials
        original_table_name = self.table_name
        self.__stop_connection()

        if not self._set_conn():
            print("Invalid credentials, connection not established... Returning to original connection...")
            self.user_credentials = original_credentials
            self._set_conn()
        elif not self._set_table_name():
            print("Invalid table name, connection not established... Returning to original connection...")
            self.user_table_name = original_table_name
            self._set_table_name()

    def display_credentials(self):
        """
        Display the current connection credentials.
        """
        print("\nCurrent credentials:")
        for key, value in self._credentials.items():
            print(f"{key}: {value}")

    def _set_conn(self) -> bool:
        """"
        Method to establish a connection to the PostgreSQL database. For internal use only.
        Sets the user_credentials to the credentials attribute if successful.
        :return: bool, true if connection established
        """
        if self.user_credentials is None:
            print("Error in connection: New credentials are not set, established connection is maintained")
            self.display_credentials()
            return False
        elif self._conn is None:
            print("Attempting to establish new connection")
            try:
                self._conn = db.connect(
                    database=self.user_credentials["database"],
                    user=self.user_credentials["user"],
                    password=self.user_credentials["password"],
                    host=self.user_credentials["host"],
                    port=self.user_credentials["port"]
                )
            except db.DatabaseError as e:
                print(f"Error connecting to the database: {e}")
                return False
        print("Connection established")
        self._credentials = self.user_credentials
        self.user_credentials = None
        return True

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
        result = self.__execute_query(query, (self.user_table_name,))
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
        columns_data = self.__execute_query(query, (self.user_table_name,))
        if columns_data is False:
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

        print(f"Selected table structure valid in {self.user_table_name}")
        return True

    def _set_table_name(self) -> bool:
        """
        Check if a valid table exists in the database. For internal use.
        Sets the user_table_name to the table_name attribute if successful.
        :return: true if the table is valid.
        """
        if not self._check_table_exists():
            print("Table doesnt exists")
            return False
        elif not self._check_table_structure():
            print("Table structure invalid")
            return False
        else:
            self._table_name = self.user_table_name
            return True

    def load_plane(self, plane_id: int):
        """
        Load a plane´s data from the database.
        :return: A dictionary containing the plane data
        """
        query = f"SELECT * FROM {self.table_name} WHERE plane_id = %s"
        result = self.__execute_query(query, (plane_id,))
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
            result = self.__execute_query(query, (name, rows, columns), True)
            if result:
                print(f"Plane ID: '{result[0][0]}' inserted successfully")
                return result[0][0]
        else:
            query_n = f"""INSERT INTO {self.table_name} (plane_id, name, rows, cols) 
                              VALUES (%s, %s, %s, %s)
                              RETURNING plane_id;"""
            result_n = self.__execute_query(query_n, (plane_id, name, rows, columns), True)
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

        result = self.__execute_query(query, tuple(params), True)
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
        result = self.__execute_query(query, (plane_id,), True)
        if result:
            print(f"Plane ID: {plane_id} deleted")
            return True
        else:
            print(f"Plane ID: {plane_id} not found")
            return False
