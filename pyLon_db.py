import sqlite3


class Database:

    """ Creates a database instance - Simplifies database operations
        I wrote most of this so it can be reused in future projects. """

    def __init__(self, db_file: str):
        self.__db_file = db_file
        self.__db_conn = self.__connect_db()

    def __connect_db(self):

        """ Private Method: Opens the database file. """

        try:
            db_conn = sqlite3.connect(self.__db_file)
        except sqlite3.Error as error:  # unlikely but we need to handle this just in case
            print("[!] Database connection failed!")
            print("[!] ", error)
            return
        print("[*] Database connection success!")
        print("[*] SQLite version", sqlite3.version)
        return db_conn

    def __cursor(self, statement: str, fetch=False):

        """ Private Method: Open's and closes the cursor """

        cursor = self.__db_conn.cursor()
        cursor.execute(statement)
        if fetch:
            rows = cursor.fetchall()
            cursor.close()
            return rows
        cursor.close()

    def db_close(self):
        self.__db_conn.close()
        print("[*] Database closed cleanly.")

    def create_table(self, table_name: str, columns: dict):

        """ Create a table in the database """

        columns = "".join([f"{i} {columns[i]}," for i in columns]).rstrip(",")
        sql_statement = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
        try:
            self.__cursor(sql_statement)
            self.__db_conn.commit()
        except sqlite3.Error as error:
            print("[!] Creating table failed!")
            print("[!]", str(error).capitalize())
            return
        print(f"[*] Created table {table_name} successfully.")

    def insert_row(self, table: str, row_data: dict):

        """ Insert a row into defined table """

        columns = "".join([f"'{i}'," for i in row_data]).rstrip(",")
        keys = "".join([f"'{row_data[i]}'," for i in row_data]).rstrip(",")
        sql_statement = f"INSERT INTO {table} ({columns}) VALUES({keys});"
        try:
            self.__cursor(sql_statement)
            self.__db_conn.commit()
        except sqlite3.Error as error:
            print("[!] Couldn't add record")
            print("[!]", str(error).capitalize())
            return
        print("[*] Record added successfully.")

    def delete_rowid(self, table: str, rowid: str):

        """ Delete rowid from table """

        sql_statement = f"DELETE FROM {table} WHERE rowid = {rowid};"
        try:
            self.__cursor(sql_statement)
            self.__db_conn.commit()
            self.__cursor("VACUUM;")  # consolidate rowid's
            self.__db_conn.commit()
        except sqlite3.Error as error:
            print("[!] Couldn't delete record.")
            print("[!]", str(error).capitalize())
        print("[*] Record deleted successfully.")

    def select_rows(self, table: str, column: str, where_like: tuple = None, or_like: tuple = None):

        """ issues the following statement to the SQLite db items in brackets are optional

            SELECT column FROM table (WHERE key like '%search_string%')
                                        ( OR key like '%search_string%') """

        sql_statement = f"SELECT {column} FROM {table}"
        if where_like:  # if parameter passed execute this
            sql_statement += f" WHERE {where_like[0]} like '%{where_like[1]}%'"
        if where_like and or_like:  # must have a where like to have an or like
            sql_statement += f" OR {or_like[0]} like '%{or_like[1]}%'"
        sql_statement += ";"  # add the statement closer thingo
        try:
            rows = self.__cursor(sql_statement, fetch=True)
            return rows
        except sqlite3.Error as error:
            print("[!]", str(error).capitalize())
