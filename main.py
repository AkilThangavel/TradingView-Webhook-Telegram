import time
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import config
from handler import *
import os
import json


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class TriggeredOrders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ordertype = db.Column(db.String(100), nullable=False)
    ticker = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(80), unique=True, nullable=False)
    orderprice = db.Column(db.String(100), nullable=False)
    orderdtime = db.Column(db.String(100), nullable=False)
    marketposition  = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<TriggeredOrders {self.Ticker}>'

@app.route('/')
def home():
    orderdetails = TriggeredOrders.query.all()
    return render_template('home.html', orderdetails=orderdetails)


@app.route('/onwebhooks', methods=['POST'])
def on_webhooks():
    config.var1 = True
    return json.dumps({'status':'OK'})

@app.route('/offwebhooks', methods=['POST'])
def off_webhooks():
    config.var1 = False
    return json.dumps({'status':'OK'})

@app.route('/sswebhooks', methods=['POST'])
def ss_webhooks():
    return ({'state': config.var1})


def get_timestamp():
    timestamp = time.strftime("%Y-%m-%d %X")
    return timestamp


@app.route("/webhook", methods=["POST"])
def webhook():    
    try:
        if request.method == "POST":
            data = request.get_json()
            key = data["passphrase"]
            if key == config.sec_key and config.var1 == True:
                print(get_timestamp(), "Alert Received & Sent!")
                # send_alert(data)
                # orderObject = TriggeredOrders(ordertype=data['strategy']['order_action'], ticker=data['ticker'],
                #        exchange=data['exchange'], orderprice=data['strategy']['order_price'], orderdtime = data['time'],
                #        marketposition=data['strategy']['market_position'])
                # db.session.add(orderObject)
                # db.session.commit()
                return "Sent alert", 200
            else:
                print("[X]", get_timestamp(), "Alert Received & Refused! (Wrong Key)")
                return "Refused alert", 400

    except Exception as e:
        print("[X]", get_timestamp(), "Error:\n>", e)
        return "Error", 400


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=80)
