import click
from flask.cli import with_appcontext

from .extensions import db
# from .models import User, Stocks
from .models import Stocks

@click.command(name="create_tables")
@with_appcontext
def create_tables():
    db.create_all()
    newStocks = Stocks(
        name='username', share='Apple, Inc.', shares=1, price=284, time='2019-12-23 21:17:42.938156', cash=9716
    )
    db.session.add(newStocks)
    db.session.commit()