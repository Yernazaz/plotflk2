from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Tickers_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker_name = db.Column(db.String(10))
    ticker_company = db.Column(db.String(100))
    ticker_owner = db.Column(db.String(20))
    ticker_when = db.Column(db.String(10))
    ticker_price = db.Column(db.String(10))
    ticker_secform = db.Column(db.String(10))
