import sqlite3

from typing import List


class SQLiteDataBaseController:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.connection = None

    def create_connection(self) -> sqlite3.Connection:
        self.connection = sqlite3.connect(self.db_file)
        return self.connection

    def get_cursor(self) -> sqlite3.Cursor:
        connection = self.create_connection()
        return connection.cursor()

    def commit_and_close(self):
        self.connection.commit()
        self.connection.close()

    def select_all(self, table: str) -> List:
        cursor = self.get_cursor()
        cursor.execute(f'SELECT * FROM {table};')
        data = cursor.fetchall()
        self.commit_and_close()
        return data

    def select_distinct(self, field: str, table: str):
        cursor = self.get_cursor()
        cursor.execute(f'SELECT DISTINCT {field} FROM {table};')
        data = cursor.fetchall()
        self.commit_and_close()
        return data

    def select_col_by_equal_cond(
            self,
            field: str,
            table: str,
            eq_field: str,
            eq_value: str,
    ):
        cursor = self.get_cursor()
        cursor.execute(
            f'SELECT {field} FROM {table} WHERE {eq_field}="{eq_value}";')
        data = cursor.fetchall()
        self.commit_and_close()
        return data

    def write(self, table: str, data) -> int:
        cursor = self.get_cursor()
        result = cursor.executemany(
            f'INSERT INTO {table} VALUES (?, ?);',
            data
        )
        self.commit_and_close()
        return result.rowcount
