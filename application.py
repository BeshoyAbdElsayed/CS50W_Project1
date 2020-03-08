import os

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():

    name = request.form.get("name")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE name=:name AND password=:password", {"name":name, "password":password}).rowcount == 1:
        global session
        session["user"] = name
        return render_template("search.html", user=session["user"])
    
    return render_template("error.html", message="wrong user name or passwrd")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    password = request.form.get("password")
    if db.execute("SELECT name FROM users WHERE name=:name", {"name":name}).rowcount != 0:
        return render_template("error.html", message="user name is already exists try a different one")
    db.execute("INSERT INTO users(name, password) VALUES(:name, :password)", {"name":name, "password": password})
    db.commit()
    return render_template("success.html")


@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/search/result", methods=["POST"])
def result():
    search = request.form.get("search")
    search = f"%{search[1:-1]}%"
    search_by = request.form.get("search_by")    

    books = db.execute(f"SELECT * FROM books WHERE \"{search_by}\" LIKE '{search}'")
    return render_template("result.html", books=books, user=session["user"])


@app.route("/search/result/<string:isbn>")
def book(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn LIMIT 1", {"isbn":isbn}).fetchone()
    reviews = db.execute("SELECT user_name, rate, review FROM reviews WHERE book_isbn=:isbn", {"isbn":isbn})

    goodread_key = "svbY5pxTjsPoH9YeEY89w"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodread_key, "isbns": isbn})
    if res.status_code != 200:
        goodread_info = {"work_ratings_count":"Not found", "average_rating":"Not found"}
    else:
        goodread_info = res.json()["books"][0]

    return render_template("book.html", book=book, reviews=reviews, user=session["user"], goodread_info=goodread_info)

@app.route("/search/result/<string:isbn>/add_review", methods=["POST"])
def add_review(isbn):
    if db.execute("SELECT * FROM reviews WHERE user_name=:user AND book_isbn=:isbn", {"user":session["user"], "isbn":isbn}).rowcount == 1:
        return "You have already reviewed this book"

    rate = request.form.get("rate")
    review = request.form.get("review")
    
    db.execute("INSERT INTO reviews VALUES(:user, :isbn, :rate, :review)", {"user":session["user"], "isbn":isbn, "rate":rate, "review":review})
    db.commit()
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn LIMIT 1", {"isbn":isbn}).fetchone()
    reviews = db.execute("SELECT user_name, rate, review FROM reviews WHERE book_isbn=:isbn", {"isbn":isbn})
    return render_template("book.html", book=book, reviews=reviews, user=session["user"])

@app.route("/logout")
def logout():
    global session
    session["user"] = None
    return render_template("index.html")

@app.route("/api/<string:isbn>")
def api(isbn):
    if db.execute("SELECT isbn FROM books WHERE isbn=:isbn",{"isbn":isbn}).rowcount == 0:
        return "404 Error, book is Not found", 404
    book_info = db.execute("SELECT title, auther, isbn, year, avg, count FROM (SELECT title, auther, isbn, year, AVG(rate), COUNT(rate) FROM books LEFT JOIN reviews ON isbn=:isbn AND isbn=book_isbn GROUP BY isbn) AS a WHERE isbn=:isbn",{"isbn":isbn, "isbn":isbn}).fetchone()
    avg = book_info.avg
    if avg != None:
        avg = float(avg)
    return jsonify({
            "title":book_info.title,
            "auther":book_info.auther,
            "year":book_info.year,
            "isbn":book_info.isbn,
            "review_count":book_info.count,
            "average_score":avg
        })