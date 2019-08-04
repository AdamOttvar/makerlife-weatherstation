import threading
import math
from time import sleep, localtime, strftime
from flask import Flask, request, render_template

logfile = "log.txt"

app = Flask(__name__)

rainfall = 30.2
wind = 12.4
temp_max = -999.9
temp_min = 999.9

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    global rainfall, wind, temp_max, temp_min

    temp = round(23.6578443333, 1)

    if request.method == 'POST':
        rainfall = 0
        temp_max = temp
        temp_min = temp

    temp_max = max(temp_max, temp)
    temp_min = min(temp_min, temp)
    return render_template('index.html', temp = temp, wind = wind, rainfall = rainfall, temp_max = temp_max, temp_min = temp_min)

def init_logging():
    with open(logfile, "w") as text_file:
        text_file.write("### Starting to log {} ###\n".format(strftime("%Y-%m-%d %H:%M:%S", localtime())))
        text_file.write("### {}, {}, {}, {} ###\n".format("Time", "Temp", "Wind", "Rain"))
    threading.Timer(30.0, log_values).start()

def log_values():
    global temp_max, temp_min
    temp = round(23.6578443333, 1)
    with open(logfile, "a") as text_file:
        text_file.write("{}, {}, {}, {}\n".format(strftime("%Y-%m-%d %H:%M:%S", localtime()), temp, wind, rainfall))
    # Call the log function every n:th second
    threading.Timer(30.0, log_values).start()

if __name__ == '__main__':

    # To start logging values
    #init_logging()

    app.run(host='0.0.0.0')
