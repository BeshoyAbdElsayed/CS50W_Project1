import os

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

import requests
isbn = '034553283X'
if db.execute("SELECT isbn FROM books WHERE isbn=:isbn",{"isbn":isbn}).rowcount == 0:
    print("404 Error, book is Not found")
book_info = db.execute("SELECT title, auther, isbn, year, avg, count FROM (SELECT title, auther, isbn, year, AVG(rate), COUNT(rate) FROM books LEFT JOIN reviews ON isbn=:isbn AND isbn=book_isbn GROUP BY isbn) AS a WHERE isbn=:isbn",{"isbn":isbn, "isbn":isbn}).fetchone()
avg = book_info.avg
if avg != None:
    avg = float(avg)
print({
        "title":book_info.title,
        "auther":book_info.auther,
        "year":book_info.year,
        "isbn":book_info.isbn,
        "review_count":book_info.count,
        "average_score":avg
    }) 