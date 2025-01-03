from utils.db import DatabaseManager


class TableManager(DatabaseManager):
    expected_columns_and_types = {}
    primary_key_column: str = "id"
    """
    TableManager: Parent class of table manager classes.
    """

    def __init__(self, database: str, user: str, password: str, host: str = "localhost", port: str = "5432",
                 table_name: str = "default") -> None:
        super().__init__(database, user, password, host, port)
        self.user_table_name = table_name
        self._table_name = None
        self._columns = None
        if self.is_table_name_valid():
            self.table_name = self.user_table_name
            self.get_columns_to_cache()
            print("Valid table, connection established")
        else:
            raise ValueError("Invalid table name exiting...")

    @property
    def table_name(self) -> str:
        return self._table_name

    @table_name.setter
    def table_name(self, value):
        self._table_name = value

    def get_columns_to_cache(self):
        """
        Fetch column names of the current table, and sets them in cache.
        :return: bool, true if column names were cached.
        """
        query = f"""
        SELECT column_name
        FROM information_schema.columns 
        WHERE table_name = %s
        """
        result = super()._execute_query(query, (self.table_name,))
        if not result:
            raise ValueError(f"Error: No columns found for table {self.table_name}.")
        self._columns = [row[0] for row in result]

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

        if not self.is_table_name_valid():
            print("Invalid table name, connection not established... Returning to original table")
            return

        self.table_name = self.user_table_name
        self.user_table_name = None
        print("Table name changed!")
        return self.get_columns_to_cache()

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

    def __validate_new_table_structure(self) -> bool:
        """
        Validate the new table structure against the expected structure from the user_table_name.
        :return: bool, true if the new table structure matches the expected structure.
        """
        query = f"""
                           SELECT column_name, data_type
                           FROM information_schema.columns 
                           WHERE table_name = %s
                           """
        actual_columns = super()._execute_query(query, (self.user_table_name,))
        if not actual_columns:
            raise ValueError(f"Error: No columns found for table {self.user_table_name}.")
        actual_columns_and_types = {column: dtype for column, dtype in actual_columns}

        expected_columns = set(self.expected_columns_and_types.keys())
        actual_columns = set(actual_columns_and_types.keys())

        missing_columns = expected_columns - actual_columns
        extra_columns = actual_columns - expected_columns
        if missing_columns:
            raise ValueError(f"Missing columns: {', '.join(missing_columns)} in {self.user_table_name}")
        if extra_columns:
            raise ValueError(f"Extra columns: {', '.join(extra_columns)} in {self.user_table_name}")

        for column, actual_type in actual_columns_and_types.items():
            expected_type = self.expected_columns_and_types.get(column)
            if expected_type and expected_type != actual_type:
                raise ValueError(
                    f"Error: Column '{column}' in table '{self.user_table_name}' has type '{actual_type}', "
                    f"but expected '{expected_type}'."
                )
        print("Table structure check passed!")
        return True

    def __validate_column_type(self, value, column_type: str) -> bool:
        """
        Validate the type of value against a column type.
        :param value: The value to validate.
        :param column_type: The database column type.
        :return: bool, True if the value matches the column type.
        """
        type_mapping = {
            "integer": int,
            "character varying": str,
            "boolean": bool,
            "real": float,
            "double precision": float,
            "array": list,
        }
        expected_type = type_mapping.get(column_type.lower())
        return isinstance(value, expected_type)

    def __validate_data(self, data: dict, is_update: bool) -> bool:
        """
        Validate provided data against expected data structure.
        :param data: a dictionary of column names and values to validate.
        :param is_update: bool to indicate if it is for an update operation.
        :return: bool, true if data is valid.
        """
        data_keys = set(data.keys())
        expected_columns = set(self.expected_columns_and_types.keys())
        include_primary_key = self.primary_key_column in data
        if is_update:
            unexpected_columns = data_keys - expected_columns
            if unexpected_columns:
                raise ValueError(
                    f"Error: Unexpected columns: {', '.join(unexpected_columns)} in data provided for update.")
        elif include_primary_key:
            pk_value = data[self.primary_key_column]
            expected_type = self.expected_columns_and_types.get(self.primary_key_column)
            if not self.__validate_column_type(pk_value, expected_type):
                raise TypeError(
                    f"Error: Primary key '{self.primary_key_column}' expects a value of type '{expected_type}', "
                    f"but got '{type(pk_value).__name__}' with value '{pk_value}'."
                )
        else:
            required_columns = expected_columns - {self.primary_key_column}
            missing_data_columns = required_columns - data_keys
            extra_data_columns = data_keys - required_columns

            if missing_data_columns:
                raise ValueError(f"Error: Missing required data columns: {', '.join(missing_data_columns)}")
            if extra_data_columns:
                raise ValueError(f"Error: Unexpected data columns: {', '.join(extra_data_columns)}")

        for column, value in data.items():
            expected_type = self.expected_columns_and_types.get(column)
            if expected_type:
                if not self.__validate_column_type(value, expected_type):
                    raise TypeError(
                        f"Error: Column '{column}' expects a value of type '{expected_type}', "
                        f"but got '{type(value).__name__}'."
                    )
        print("Data structure check passed!")
        return True

    def _check_table_structure(self, data: dict = None, is_update: bool = False) -> bool:
        """
        Check if a table has a correct table structure For internal use.
        :param data: a dictionary of column names and values to validate (optional).
        :return: bool, true if the table structure is valid.
        """
        if data is None:
            return self.__validate_new_table_structure()

        if data:
            return self.__validate_data(data, is_update)
        return False

    def is_table_name_valid(self, table_name: str = None) -> bool:
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

    def load_record(self, primary_key) -> dict | None:
        """
        Load a record from the database.
        :param primary_key: the primary key of the record.
        :return: A dictionary containing the record data.
        """
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key_column} = %s"
        result = super()._execute_query(query, (primary_key,))
        if not result:
            print(f"Error: Record with '{self.primary_key_column}': '{primary_key}' not found")
            return None
        return dict(zip(self._columns, result[0]))

    def insert_record(self, data: dict, returning_column: str = None):
        """
        Insert a record in the database after validating its structure.
        :param data: A dictionary of column names and values to insert.
        :param returning_column: The column to return after insertion (defaults to ID if none provided).
        :return: The returning column else None
        """
        returning_column = returning_column or self.primary_key_column

        include_primary_key = self.primary_key_column in data

        self._check_table_structure(data)

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        returning_clause = f"RETURNING {returning_column}" if returning_column else ""
        query = f"""
                 INSERT INTO {self.table_name} 
                 ({columns}) VALUES ({placeholders})
                 {returning_clause};
                 """
        result = super()._execute_query(query, tuple(data.values()), True)
        if returning_column and result:
            print(f"Record inserted successfully with ID: {result[0][0]}")
            return result[0][0]
        print("Record inserted successfully")
        return None

    def update_record(self, primary_key, data: dict) -> bool:
        """
        Update a record in the database.
        :param primary_key: the primary key of the record.
        :param data: A dictionary of column names and values to update.
        :return: bool, true if update was successful
        """
        if not data:
            print("No updates provided")
            return False

        self._check_table_structure(data, True)

        updates = ', '.join([f"{col} = %s" for col in data.keys()])
        query = f"""
                    UPDATE {self.table_name} 
                    SET {updates}
                    WHERE {self.primary_key_column} = %s
                    """
        params = list(data.values()) + [primary_key]
        result = super()._execute_query(query, tuple(params), True)

        if result:
            print(f"Record with '{self.primary_key_column}': '{primary_key}' updated successfully")
            return True
        print("Failed to update record with '{self.primary_key_column}': '{primary_key}'")
        return False

    def delete_record(self, primary_key) -> bool:
        """
        Delete a record from the database.
        :param primary_key: the primary key of the record.
        :return: bool, True if delete was successful
        """
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key_column} = %s"
        result = super()._execute_query(query, (primary_key,), True)
        if result:
            print(f"Record with {self.primary_key_column}: '{primary_key}' deleted successfully")
            return True
        else:
            print(f"Failed to delete record with: {self.primary_key_column}: '{primary_key}' not found")
            return False
