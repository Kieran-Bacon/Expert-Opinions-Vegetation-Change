from os import listdir
from os.path import abspath, isfile, join
import sqlite3

class QueryError(Exception):
	"""Exception when attempting the use a query incorrectly"""
	pass

class DatabaseHandler:

	_DatabaseLocation = abspath("./ExpertWebtool/data/site.db")
	_QueryLocation = abspath("./ExpertWebtool/queries/")
	_SQLStore = {}

	def load() -> None:
		"""
		Load in sql query information into the static store.

		Returns:
			None
		"""
		
		for sqlFilename in listdir(DatabaseHandler._QueryLocation):

			SQLPath = join(DatabaseHandler._QueryLocation, sqlFilename)

			# Unrecognised item found
			if not isfile(SQLPath): 
				raise ValueError("Non sql file found in location:" + SQLPath)

			# Read in query content
			with open(SQLPath) as fileHandler:
				DatabaseHandler._SQLStore[sqlFilename] = fileHandler.read()

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