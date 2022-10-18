from models.ticker_models import Tickers_info, db
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import base64
import requests
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
from matplotlib import pyplot as plt
from flask import render_template, redirect


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


def insert_into_db(data):
    ticker_check = Tickers_info.query.filter_by(ticker_name=data[0], ticker_company=data[1], ticker_when=data[3],
                                                ticker_price=data[5], ticker_secform=data[9]).first()
    if ticker_check:
        pass
    else:
        ticker_info = Tickers_info(ticker_name=data[0], ticker_company=data[1], ticker_owner=data[2],
                                   ticker_when=data[3],
                                   ticker_price=data[5], ticker_secform=data[9])
        db.session.add(ticker_info)
        db.session.commit()


def show_table():
    table = parse_inside("https://finviz.com/insidertrading.ashx?or=-10&tv=100000&tc=2&o=-transactionvalue")
    tikcers = table.values.tolist()
    for i in range(0, len(tikcers)):
        insert_into_db(tikcers[i])
    return render_template('tickers.html', len=len(tikcers), tikcers=tikcers)


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


def ticker_list(ticker_id):
    table = parse_inside("https://finviz.com/insidertrading.ashx?or=-10&tv=100000&tc=2&o=-transactionvalue")
    tikcers = table.values.tolist()
    for i in range(0, len(tikcers)):
        insert_into_db(tikcers[i])
    ryh = table.iloc[[ticker_id]]
    ticker_info = [ryh.values[0][0], ryh.values[0][1], ryh.values[0][2], ryh.values[0][3], ryh.values[0][5]]

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
    return render_template('tickers_list.html', len=len(tikcers), tikcers=tikcers, ticker_info=ticker_info,
                           image=pngImageB64String)


def re():
    return redirect("/0/ticker_list/")
