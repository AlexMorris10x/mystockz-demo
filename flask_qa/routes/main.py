import requests
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user, login_required

from flask_qa.extensions import db
from flask_qa.models import Stocks, User


main = Blueprint("main", __name__)


def lookup(symbol):
    try:
        api_key = "pk_fa13b2b328ff43bb9a268b23e4c28eba"

        response = requests.get(
            f"https://cloud-sse.iexapis.com/stable/stock/{(symbol)}/quote?token={api_key}"
        )
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        quote = response.json()

    except (KeyError, TypeError, ValueError):
        return None

    return {
        "name": quote["companyName"],
        "price": float(quote["latestPrice"]),
        "symbol": quote["symbol"],
    }


@main.route("/")
def index():
    userStocks = (
        db.session.query(
            Stocks.share,
            Stocks.price,
            db.func.sum(Stocks.shares).label("shares"))
        .filter(Stocks.name == 'username')
        .order_by(Stocks.share)
        .group_by(Stocks.share, Stocks.price,)
        # .group_by(Stocks.share)
        .all()
    )
    # cash = Stocks.query.filter_by(name='username').last()
    descending = Stocks.query.order_by(Stocks.id.desc())
    cash = descending.first()

    flash("You currnetly have")
    flash("$")
    flash(str(round(cash.cash, 2)))
    flash("in your digital wallet.")

    currentCash = db.session.query(Stocks).filter(
        Stocks.name == 'username').all()

    totalStocks = (
        db.session.query(Stocks.shares, Stocks.price, db.func.sum(
            Stocks.shares * Stocks.price).label("totalStocks"))
        .filter(Stocks.name == 'username').all()
    )

    return render_template(
        "home.html",
        userStocks=userStocks,
        currentCash=currentCash,
        totalStocks=totalStocks,
    )


@main.route("/quote", methods=["GET", "POST"])
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        flash(quote["name"])
        flash("is currently priced at")
        flash(quote["price"])
        flash("usd")
    return render_template("quote.html")


@main.route("/buy", methods=["GET", "POST"])
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = float(request.form.get("shares"))
        quote = lookup(symbol)
        share = quote["name"]
        price = float(quote["price"])
        time = datetime.datetime.utcnow()
        currentCash = 0
        # name = current_user.name

        sum = price * shares

        # currentUser = User.query.filter(User.id == current_user.id).all()
        currentUser = Stocks.query.filter(Stocks.name == 'username').all()

        for cash in currentUser:
            currentCash = cash.cash

        if (currentCash - sum) > 0:
            newCash = currentCash - sum
            newStocks = Stocks(
                name='username', share=share, shares=shares, price=price, time=time, cash=newCash
            )

            db.session.add(newStocks)
            db.session.commit()
            descending = Stocks.query.order_by(Stocks.id.desc())
            cash = descending.first()

            flash("You currnetly have")
            flash("$")
            flash(str(round(cash.cash, 2)))
            flash("in your digital wallet.")

            # update = User.query.filter_by(id=current_user.id).first()
            # update.cash = newCash
            # db.session.commit()
        else:
            flash("Not enough funds")
    return render_template("buy.html")


@main.route("/sell", methods=["GET", "POST"])
def sell():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        negShares = float(request.form.get("shares")) * -1

        # name = current_user.name
        quote = lookup(symbol)
        share = quote["name"]
        price = float(quote["price"])
        time = datetime.datetime.utcnow()
        sum = price * negShares

        currentUser = Stocks.query.filter(Stocks.name == 'username').all()
        for cash in currentUser:
            currentCash = cash.cash

        stockLookup = Stocks.query.filter(Stocks.name == 'username').all()
        totalStocks = 0
        for stocks in stockLookup:
            totalStocks += stocks.shares

        if (totalStocks + negShares) >= 0:
            newCash = currentCash - sum
            newStocks = Stocks(
                name='username', share=share, shares=negShares, price=price, cash=newCash, time=time
            )

            db.session.add(newStocks)
            db.session.commit()
            descending = Stocks.query.order_by(Stocks.id.desc())
            cash = descending.first()

            flash("You currnetly have")
            flash("$")
            flash(str(round(cash.cash, 2)))
            flash("in your digital wallet.")

            # update = User.query.filter_by(name='username').first()
            # update.cash = newCash
            # db.session.commit()
        else:
            flash("Not enough shares")
    return render_template("sell.html")


@main.route("/history", methods=["GET", "POST"])
def history():
    userStocks = (
        db.session.query(Stocks.share, Stocks.shares, Stocks.time)
        .filter(Stocks.name == 'username').all()
    )
    return render_template("history.html", userStocks=userStocks)
