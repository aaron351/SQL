import os

from flask import Flask, session, flash, redirect, render_template, request, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp

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
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            flash("Usuario vacio")
            return render_template("login.html")

        elif not request.form.get("password"):
            flash("Contraseña vacia")
            return render_template("login.html")    
        

        rows=db.execute("SELECT * FROM users WHERE username=:username", {"username":request.form.get("username")})
        rows=rows.fetchone()
        print(rows)
        #check contraseña
        if rows == None or not check_password_hash(rows[2], request.form.get("password")):
            print('error: contraseña incorrecta o usuario no registrado')
            return render_template("error.html")
       
        print(rows[1])
        session["user_id"] = rows[0]
        return render_template("index.html")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        if not request.form.get("username"):
            flash("username vacio")
            return render_template("register.html")

        elif not request.form.get("password"):
            flash("password vacio")
            return render_template("register.html")

        elif not request.form.get("password") == request.form.get("confirmation"):
            flash("No coincide")
            return render_template("register.html")

        username = request.form.get("username")
        paswordhash = generate_password_hash(request.form.get("password"))
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        print(rows)
        if rows:
            flash("El usuario ya existe")
            return render_template("register.html")
        else:
            row2 = db.execute("INSERT INTO users (username, hashs) VALUES(:username, :password)", {"username": username, "password": paswordhash})
            db.commit()
            flash("Usuario registrado")
            return render_template("login.html")
    return render_template("register.html")