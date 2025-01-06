import pg8000 as db
import time


class DatabaseManager:
    """
    Parent class for database management
    """

    _shared_conn = None

    def __init__(self, database: str, user: str, password: str, host: str = "localhost", port: str = "5432",
                 ) -> None:
        """
        Initialize a connection to the database, stop running if valid connection is not established.
        :param database: database name
        :param user: username
        :param password: password
        :param host: host name (default: localhost)
        :param port: port connection (default: 5432)
        """
        self.user_credentials = {
            "database": database,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self._table_name = None
        self._credentials = None
        self.max_retries = 10
        self.retry_delay = 0.5

        if not self._set_conn():
            raise ValueError("Invalid credentials, connection not established exiting...")
        else:
            return

    def __del__(self):
        pass

    @property
    def credentials(self):
        return self._credentials

    def _execute_query(self, query, params=None, commit=False):
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
            cursor = DatabaseManager._shared_conn.cursor()
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
                DatabaseManager._shared_conn.commit()

            cursor.close()
            return result if result else True

        except (db.DatabaseError, ConnectionError) as e:
            print(f"Error while executing query: {e}")
            if self.check_connection():
                if commit:
                    DatabaseManager._shared_conn.rollback()
                    print("transaction rollback due to error")

    def __stop_connection(self):
        """
        Disconnects from the current connection and set credentials to None.
        For internal use only.
        """
        if DatabaseManager._shared_conn:
            print("Disconnecting from database...")
            DatabaseManager._shared_conn.close()
            DatabaseManager._shared_conn = None
            self._credentials = None
        else:
            print("No connection to database to disconnect...")

    def check_connection(self) -> bool:
        """
        Check if the connection to the database is still active.
        If connection is not active attempts to reconnect.
        :return: bool, True if connection is active, or successfully reconnected.
        """
        try:
            if DatabaseManager._shared_conn is None:
                print("No connection established... Attempting to reconnect...")
                return self.reconnect()
            cursor = DatabaseManager._shared_conn.cursor()
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

    def set_new_credentials(self):
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

        self.display_credentials()
        confirmation = (input("Given current credentials, are you sure you want to attempt a new connection? (y/n): ")
                        .lower())
        if confirmation != "y":
            print("Credentials change cancelled keeping current credentials")
            return

        original_credentials = self.credentials
        self.__stop_connection()

        if not self._set_conn():
            print("Invalid credentials, connection not established... Returning to original connection...")
            self.user_credentials = original_credentials
            self._set_conn()

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
        elif DatabaseManager._shared_conn is None:
            print("Attempting to establish new connection")
            try:
                DatabaseManager._shared_conn = db.connect(
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
