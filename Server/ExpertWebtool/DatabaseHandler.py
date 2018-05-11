import uuid
from os import listdir
from os.path import abspath, exists, isfile, join
import sqlite3

if __name__ == "DatabaseHandler":
    import os
    import Helper
    ROOT = os.path.dirname(os.path.realpath(__file__))
else:
    from . import ROOT
    from . import Helper

class QueryError(Exception):
    """Exception when attempting the use a query incorrectly"""
    pass

class DatabaseHandler:

    _DatabaseLocation = join(ROOT,"data","site.db")
    _TableDefinitions = join(ROOT, "SQL", "tables") + "/"
    _QueryLocation = join(ROOT,"SQL", "queries") + "/"
    _SQLStore = {}

    @classmethod
    def build(cls, rebuild=False):
        """
        Ensure the construction of the database by checking the database location.
        Build the database from scratch if not found

        Params:
            rebuild - Toggle to rebuild the site if found
        """
        
        if exists(cls._DatabaseLocation) and not rebuild: return

        database = sqlite3.connect(join(ROOT,"data","site.db"))
        cursor = database.cursor()

        if exists(cls._DatabaseLocation) and rebuild:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                name = table[0]
                cursor.execute("DROP TABLE {}".format(name))

        for table in listdir(cls._TableDefinitions):
            with open(join(cls._TableDefinitions, table)) as filehandler:
                cursor.execute(filehandler.read())

        # Create admin account
        password = uuid.uuid4().hex
        hashed = Helper.hashPassword(password)
        cursor.execute("INSERT INTO users VALUES\
            ('admin','null',?,?,5,'','Admin','User','','/imgs/avatars/avatar-ninja.png', 'KNN_regress')", hashed)

        database.commit()
        database.close()

        print("Database has been constructed. Admin account :: admin - {}".format(password))

    @classmethod
    def load(cls, rebuild=False) -> None:
        """
        Load in sql query information into the static store.

        Returns:
            None
        """

        # Ensure that the database has been constructed
        cls.build(rebuild)
        
        for sqlFilename in listdir(cls._QueryLocation):

            SQLPath = join(cls._QueryLocation, sqlFilename)

            # Unrecognised item found
            if not isfile(SQLPath): 
                raise ValueError("Non sql file found in location:" + SQLPath)

            # Read in query content
            with open(SQLPath) as fileHandler:
                cls._SQLStore[sqlFilename] = fileHandler.read()

    def executeOne(queryTitle: str, queryVariables: list):
        """
        Returns the first row from the execution of the query
        """
        # Run the command
        rows = DatabaseHandler.execute(queryTitle, queryVariables)

        # Validate the response
        if len(rows) == 0: raise QueryError("No rows returned")

        return rows[0]

    def execute(queryTitle: str, queryVariables: list):
        """
        Locates and executes the query content that is stored under the query title.

        Params:
            queryTitle - The name of the query, the key to the _SQLStore
            queryVariables - Values that are to be entered into the query before execution

        Returns:
            sqlite3.Row - A collection of row objects from the database, Zero or more rows
        """
        return DatabaseHandler.execute_literal(DatabaseHandler._SQLStore[queryTitle], queryVariables)

    def execute_literal(queryContent: str, queryVariables: list):
        """
        Runs the query content provided against the query variables. Acts as a convience function
        such that one can write sql in place for speed.

        Params:
            queryContent - The SQL command to be run
            queryVariables - List of variables to dynamically change the sql command

        Returns:
            sqlite3.Row - A collection of row objects
        """

        # Open connection to the database
        database = sqlite3.connect(DatabaseHandler._DatabaseLocation)
        database.row_factory = sqlite3.Row
        cursor = database.cursor()

        # Execute the query command and retrieve response from the database
        cursor.execute(queryContent, queryVariables)
        response = cursor.fetchall()

        # Commit any changes made by the action and close connection
        database.commit()
        database.close()
        return response

    def executeID(queryTitle: str, queryVariables: list) -> int:
        """
        Executes SQL command and return the ID of the last row that was accessed or generated.
        Used to retrieve the Primary key of a new inserted row element

        Params:
            queryTitle - The name of the query, the key to the _SQLStore
            queryVariables - Values that are to be entered into the query before execution

        Returns:
            int - Row id of the last accessed row (the primary key for the row)
        """

        return DatabaseHandler.execute_literalID(DatabaseHandler._SQLStore[queryTitle], queryVariables)

    def execute_literalID(queryContent: str, queryVariables: list):
        """
        Executes SQL command and return the ID of the last row that was accessed or generated.
        Used to retrieve the Primary key of a new inserted row element

        Params:
            queryContent - The SQL command to be run
            queryVariables - Values that are to be entered into the query before execution

        Returns:
            int - Row id of the last accessed row (the primary key for the row)
        """

        # Open connection to the database
        database = sqlite3.connect(DatabaseHandler._DatabaseLocation)
        database.row_factory = sqlite3.Row
        cursor = database.cursor()

        # Execute the query command and retrieve response from the database
        cursor.execute(queryContent, queryVariables)
        rowID = cursor.lastrowid

        # Commit any changes made by the action and close connection
        database.commit()
        database.close()
        return rowID