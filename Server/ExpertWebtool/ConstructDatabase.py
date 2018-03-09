import sqlite3, hashlib, uuid

database = sqlite3.connect("./data/site.db")
cursor = database.cursor()

# Drop previous tables if database already exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
	name = table[0]
	cursor.execute("DROP TABLE {}".format(name))

# Create tables in the database

cursor.execute("CREATE TABLE users (\
	username TEXT PRIMARY KEY,\
	email Text,\
	salt TEXT,\
	password TEXT,\
	permission INTEGER,\
	title TEXT,\
	firstname TEXT,\
	lastname TEXT,\
	organisation TEXT,\
	avatar TEXT)")
cursor.execute("CREATE TABLE expertModels (identifier TEXT PRIMARY KEY, username TEXT, qid INTEGER)")
cursor.execute("CREATE TABLE climateOutputs (cmoid INTEGER PRIMARY KEY, username TEXT)")
cursor.execute("CREATE TABLE questions (qid INTEGER PRIMARY KEY, text TEXT)")
cursor.execute("CREATE TABLE labels (username TEXT, qid INT, cmoid INT, isTrainedOn INT, score INT)")
cursor.execute("CREATE TABLE permissions (pid INTEGER PRIMARY KEY, uploading INTEGER, question INTEGER, invitation INTEGER)")

# Database contents creation

permissions = [[0],[1]]
for i in range(2):
	edit = []
	for pSet in permissions:
		edit.append(pSet + [0])
		edit.append(pSet + [1])
	permissions = edit

for i, combination in enumerate(permissions):
	cursor.execute("INSERT INTO permissions VALUES (?, ?, ?, ?)", [i] + combination)

# Developer accounts
#	- Kieran's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "admin1").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES ('bammins','kieran.bacon.working@gmail.com', ?, ?, 0,'Mr', 'Kieran', 'Bacon', 'University of Exeter', '/imgs/avatars/avatar-ninja.png')", (salt, hashedPassword))

#	- Ben's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "password").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES ('ben','example@exeter.ac.uk', ?, ?, 0,'Mr', 'Ben', 'Townsend', 'University of Exeter', '/imgs/avatars/avatar-professional-m.png')", (salt, hashedPassword))

#	- Paul's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "password").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES ('paul','example@exeter.ac.uk', ?, ?, 0,'Mr', 'Paul', 'Kim', 'University of Exeter', '/imgs/avatars/avatar-professional-f.png')", (salt, hashedPassword))

#	- Nick's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "password").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES ('nick','nh312@exeter.ac.uk', ?, ?, 0,'Mr', 'Nick', 'Higgins', 'University of Exeter', '/imgs/avatars/avatar-professional-f.png')", (salt, hashedPassword))

#       - Hugo's
salt = uuid.uuid4().hex
hashedPassword = hashlib.sha512((salt + "climate4life").encode("UTF-8")).hexdigest()
cursor.execute("INSERT INTO users VALUES ('hugo','F.H.Lambert@exeter.ac.uk', ?, ?, 0, 'Dr', 'Hugo', 'Lambert', 'University of Exeter', '/imgs/avatars/avatar-professional-m.png')", (salt, hashedPassword))

# Commit the changes close the connection to the database
database.commit()
database.close()
