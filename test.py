import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


search = "\"A Little\""
search = f"%{search[1:-1]}%"
print(search)
search_by = "title"    

books = db.execute(f"SELECT * FROM books WHERE \"{search_by}\" LIKE '{search}'")
for book in books:
    print(book)