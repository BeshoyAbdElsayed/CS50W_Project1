import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#check for environment variable 
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# setup database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# create tables
db.execute("CREATE TABLE books(isbn VARCHAR PRIMARY KEY, title VARCHAR NOT NULL, auther VARCHAR NOT NULL, year INTEGER NOT NULL);")

db.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, name VARCHAR UNIQUE NOT NULL, password VARCHAR NOT NULL);")

db.execute("CREATE TABLE reviews(user_id INTEGER REFERENCES users, book_isbn VARCHAR REFERENCES books,rate DECIMAL NOT NULL CHECK(rate<=5 AND rate>=0), review VARCHAR, PRIMARY KEY(user_id, book_ISBN));")

db.commit()