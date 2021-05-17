import os
import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session , url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    users_rows = db.execute("SELECT * FROM users WHERE id = ? ", session["user_id"])
    shares_rows = db.execute("SELECT * FROM transactions WHERE id = ? ", session["user_id"])
    #print(shares_rows)

    shares = dict()

    for item in shares_rows:
        if item['symbol'] not in shares:
            shares[item['symbol']] = item['number']
        else:
            shares[item['symbol']] += item['number']

    stock_price = dict()
    #print(shares)
    total = 0
    for key , value in shares.items():
        stock_price[key] = [ usd(lookup(key)['price']) , usd(lookup(key)['price']*value) , lookup(key)['name'] ]
        total += lookup(key)['price']*value

    return render_template("home.html" , cash = usd(users_rows[0]["cash"]) , rows=shares , price = stock_price , TOTAL = usd(total+users_rows[0]["cash"]) )

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("must provide symbol of stock" , 404)
        shares = float(request.form.get("shares"))
        if not shares and shares<=0:
            return apology("must provide number of shares" , 404)


        price = shares* ( lookup(symbol)["price"] )
        rows= db.execute("SELECT * FROM users WHERE id=?",session["user_id"])
        balance = rows[0]["cash"]
        if balance < price:
            return apology("Your balance is insufficient for this purchase" , 404)

        balance = balance - price
        db.execute("UPDATE users SET cash = ? WHERE id= ?" ,balance , session["user_id"])
        db.execute("INSERT INTO transactions (id , symbol , number , time) VALUES (? , ? , ? , ? ) " , session["user_id"] , symbol , shares , datetime.datetime.now()  )

        users_rows = db.execute("SELECT * FROM users WHERE id = ? ", session["user_id"])
        shares_rows = db.execute("SELECT * FROM transactions WHERE id = ? ", session["user_id"])
        #print(shares_rows)

        shares = dict()

        for item in shares_rows:
            if item['symbol'] not in shares:
                shares[item['symbol']] = item['number']
            else:
                shares[item['symbol']] += item['number']

        stock_price = dict()
        #print(shares)
        total = 0
        for key , value in shares.items():
            stock_price[key] = [ usd(lookup(key)['price']) , usd(lookup(key)['price']*value) , lookup(key)['name'] ]
            total += lookup(key)['price']*value

        return render_template("home.html" , cash = usd(users_rows[0]["cash"]) , rows=shares , price = stock_price , TOTAL = usd(total+users_rows[0]["cash"]) )


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute("SELECT * FROM transactions WHERE id=? ", session["user_id"])
    names = dict()

    #print(rows)
    for row in rows:
        names[row['symbol']] = lookup(row['symbol'])['name']


    return render_template("history.html" , rows=rows , names=names)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        # print(rows)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    if request.method == "POST":
        response = lookup(request.form.get("symbol"))
        return render_template("quoted.html" , response=response)
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method=="POST":
        #print(request.form.get)
        username = request.form.get("username")
        if username is None:
            return apology("No username provided" , 404)
        #print(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username")))
        if len(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))) > 0 :
            return apology("Username Already Registered" , 404)
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password or not confirmation  or password != confirmation :
            return apology("Password Not Matched/Entered", 404)
        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username , hash) VALUES ( ? , ? )", username , password_hash)

        return redirect(url_for("login"))
    if request.method=="GET":
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method=="GET":

        shares_rows = db.execute("SELECT * FROM transactions WHERE id = ? ", session["user_id"])
        shares = dict()

        for item in shares_rows:
            if item['symbol'] not in shares:
                shares[item['symbol']] = item['number']
            else:
                shares[item['symbol']] += item['number']

        return render_template("sell.html" , rows=shares)
    else:
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("must provide symbol of stock" , 404)
        shares = float(request.form.get("shares"))
        if not shares and shares<=0:
            return apology("must provide number of shares" , 404)

        rows = db.execute("SELECT * FROM transactions WHERE id=? and symbol=? " , session["user_id"] , symbol )
        number = 0
        for row in rows:
            number += row["number"]

        if number<shares:
            return apology("not that much shares to sell" , 404)

        db.execute("INSERT INTO transactions (id , symbol , number , time) VALUES (? , ? , ? , ?) ", session["user_id"] , symbol , -1*shares , datetime.datetime.now() )

        cash = db.execute("SELECT cash FROM users WHERE id=?" , session["user_id"])


        #print(cash)
        balance = cash[0]["cash"] + (shares * (lookup(symbol)['price']) )

        db.execute("UPDATE users SET cash = ? WHERE id= ?" ,balance , session["user_id"])

        return redirect(url_for('index'))


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
