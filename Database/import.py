import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#check for environment variable 
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# setup database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# open the file 
f = open("books.csv")
reader = csv.reader(f)
#insert values into the books table in the database 
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books(isbn, title, auther, year) VALUES(:isbn, :title, :auther, :year)", {"isbn":isbn, "title":title, "auther":author, "year":year})

db.commit()    