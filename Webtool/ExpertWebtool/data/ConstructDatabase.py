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

cursor.execute("CREATE TABLE users (username TEXT PRIMARY KEY, salt TEXT, password TEXT, firstname TEXT, lastname TEXT, avatar TEXT)")
cursor.execute("CREATE TABLE models (mid INTEGER PRIMARY KEY, username TEXT)")
cursor.execute("CREATE TABLE questions (qid INTEGER PRIMARY KEY, text TEXT)")
cursor.execute("CREATE TABLE labels (username TEXT, mid INT, qid INT, score INT)")

# Database contents creation

# Developer accounts
#	- Kieran's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "admin1").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES ('bammins', ?, ?, 'Kieran', 'Bacon', 'imgs/avatars/avatar-ninja.png')", (salt, hashedPassword))

#	- Ben's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "password").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES ('ben', ?, ?, 'Ben', 'Townsend', 'imgs/avatars/avatar-professional-m.png')", (salt, hashedPassword))

#	- Paul's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "password").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES ('paul', ?, ?, 'Paul', 'Kim', 'imgs/avatars/avatar-professional-f.png')", (salt, hashedPassword))

#	- Nick's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "password").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES ('nick', ?, ?, 'Nick', 'Higgins', 'imgs/avatars/avatar-professional-f.png')", (salt, hashedPassword))

# models

cursor.execute("INSERT INTO models VALUES (1, 'bammins')")
cursor.execute("INSERT INTO models VALUES (2, 'bammins')")

# questions

cursor.execute("INSERT INTO questions VALUES (1, 'Does this model reflect the true nature of evergreen plants?')")
cursor.execute("INSERT INTO questions VALUES (2, 'Does this model illustrate sea current well?')")

# lables

cursor.execute("INSERT INTO labels VALUES ('bammins', 1, 2, 69)")
cursor.execute("INSERT INTO labels VALUES ('bammins', 2, 1, 83)")

# Commit the changes close the connection to the database
database.commit()
database.close()
