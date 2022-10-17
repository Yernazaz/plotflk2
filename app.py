import base64
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from flask import Flask, send_file, render_template, Response, request, url_for, redirect
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
from matplotlib import pyplot as plt
import os
from flask_sqlalchemy import SQLAlchemy
from flask_jsonpify import jsonpify
from sqlalchemy.sql import func


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def clear_weekends(date_lists):
    return [d for d in date_lists if d.isoweekday() < 6]


def to_date(s):
    d = datetime.strptime(s, '%b %d')
    dd = datetime.strptime(d.strftime(f'{datetime.now().year}-%m-%d'), '%Y-%m-%d')
    return dd


def parse_inside(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    screen = requests.get(url, headers=headers)
    table = pd.read_html(screen.text)[-1]
    table.columns = table.iloc[0]
    table = table[1:]
    return table


@app.route('/')
def show_table():
    table = parse_inside("https://finviz.com/insidertrading.ashx?or=-10&tv=100000&tc=2&o=-transactionvalue")
    tikcers = table.values.tolist()
    JSONP_data = jsonpify(tikcers)
    i = 0
    return render_template('tickers.html',len = len(tikcers),tikcers=tikcers,id=i)

@app.route('/<int:ticker_id>/ticker/', methods=('GET', 'POST'))
def ticker(ticker_id):
    table = parse_inside("https://finviz.com/insidertrading.ashx?or=-10&tv=100000&tc=2&o=-transactionvalue")
    ryh = table.iloc[[ticker_id]]
    d = datetime.today() - to_date(ryh.values[0][3]) + timedelta(days=4)
    start_date = to_date(ryh.values[0][3]) - timedelta(days=5)
    ticker = yf.Ticker(ryh.values[0][0]).history(start=start_date, end=datetime.now(), frequency='1dy')[
        ['Open', 'High', 'Low', 'Close']]
    data = pd.DataFrame(ticker)
    date_list = data.index
    data['date'] = date_list
    data.plot(x='date', y='Close',
              title=f'{ticker_id}) Ticker: {ryh.values[0][0]}, {ryh.values[0][4]}, Price:{ryh.values[0][5]}$')
    plt.axvline(pd.Timestamp(to_date(ryh.values[0][3])), color='r')
    secform = to_date(ryh.values[0][9].split()[0] + ' ' + ryh.values[0][9].split()[1])
    plt.axvline(pd.Timestamp(secform.date()), color='g')
    output = io.BytesIO()
    FigureCanvas(plt.gcf()).print_png(output)
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(output.getvalue()).decode('utf8')
    return render_template("index.html", image=pngImageB64String)


if __name__ == '__main__':
    app.run()
