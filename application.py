import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

user = None

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("name")
    password = request.form.get("password")
    if db.execute("SELECT * FROM users WHERE name=:name AND password=:password", {"name":name, "password":password}).rowcount == 1:
        global user
        user = name
        return render_template("search.html", user=user)
    
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
    return render_template("result.html", books=books, user=user)


@app.route("/search/result/<string:isbn>")
def book(isbn):
    return "TODO"