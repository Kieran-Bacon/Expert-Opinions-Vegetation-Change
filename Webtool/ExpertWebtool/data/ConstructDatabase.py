import sqlite3, hashlib, uuid

database = sqlite3.connect("./site.db")
cursor = database.cursor()

# Drop previous tables if database already exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
	name = table[0]
	cursor.execute("DROP TABLE {}".format(name))

# Create tables in the database

cursor.execute("CREATE TABLE users (id PRIMARY KEY, username TEXT, salt TEXT, password TEXT, firstname TEXT, lastname TEXT)")

# Developer accounts
#	- Kieran's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "admin1").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES (NULL, 'kb437', ?, ?, 'Kieran', 'Bacon')", (salt, hashedPassword))


# Commit the changes close the connection to the database
database.commit()
database.close()
