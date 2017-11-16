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
cursor.execute("CREATE TABLE models (mid PRIMARY KEY, filepath TEXT)")
cursor.execute("CREATE TABLE questions (qid PRIMARY KEY, text TEXT)")
cursor.execute("CREATE TABLE labels (username TEXT, mid INT, qid INT, score INT)")

# Developer accounts
#	- Kieran's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "admin1").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES ('kb437', ?, ?, 'Kieran', 'Bacon', 'imgs/avatars/avatar-ninja.png')", (salt, hashedPassword))

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

# Commit the changes close the connection to the database
database.commit()
database.close()
