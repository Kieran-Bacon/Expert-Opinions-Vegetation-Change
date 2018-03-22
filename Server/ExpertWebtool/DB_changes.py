import os, sqlite3, hashlib, uuid

ROOT = os.path.dirname(os.path.realpath(__file__))

database = sqlite3.connect(os.path.join(ROOT,"data","site.db"))
cursor = database.cursor()

try:
    cursor.execute("ALTER TABLE expertModels ADD COLUMN precision REAL")
    cursor.execute("ALTER TABLE expertModels ADD COLUMN accuracy REAL")
    cursor.execute("ALTER TABLE expertModels ADD COLUMN R2 REAL")
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN modelSpec TEXT")
except:
    pass

cursor.execute("UPDATE users SET modelSpec = 'KNN_regress'")

database.commit()

database.close()