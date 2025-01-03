from utils.db import DatabaseManager


class SeatsDatabaseManager(DatabaseManager):
    """
    SeatsDatabaseManager: subclass of DatabaseManager
    To manage the seats database
    """
    def __init__(self,  database: str, user: str, password: str, host: str = "localhost", port: str = "5432",
                 table_name: str = "seats") -> None:
        super().__init__(database, user, password, host, port)
        self.user_table_name = table_name
        if self.is_table_valid():
            self.table_name = self.user_table_name
            print("Valid table, connection established")
        else:
            raise ValueError("Invalid table name exiting...")