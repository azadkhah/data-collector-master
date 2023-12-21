from threading import Thread

import flask
from flask import send_file

from tor_list_uploader import t_up

app = flask.Flask(__name__)
app.config["DEBUG"] = True

thread1 = Thread(target=t_up, )
thread1.start()

@app.route('/torbulkexitlist', methods=['GET'])
def torbulkexitlist():
    return send_file("torbulkexitlist.txt")

@app.route('/exit-addresses', methods=['GET'])
def home():
    return send_file("exit-addresses.txt")

app.run(host="0.0.0.0")
