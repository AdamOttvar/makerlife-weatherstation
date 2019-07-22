import threading
import math
from time import sleep
from flask import Flask, request, render_template

app = Flask(__name__)

rainfall = 30.2
wind = 12.4

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    global rainfall

    if request.method == 'POST':
        rainfall = 0

    temp = round(23.6578443333, 1)
    return render_template('index.html', temp = temp, wind = wind, rainfall = rainfall)


if __name__ == '__main__':

    app.run(host='0.0.0.0')
