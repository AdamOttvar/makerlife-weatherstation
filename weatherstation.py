import threading
import math
from time import sleep, localtime, strftime
from gpiozero import DigitalInputDevice
from w1thermsensor import W1ThermSensor
from flask import Flask, request, render_template

app = Flask(__name__)

temp_max = -999.9
temp_min = 999.9
rainfall = 0
wind = 0
wind_count = 0
bucket_count = 0
radius_cm = 9.0
interval = 5
ADJUSTMENT = 1.18
CM_IN_A_KM = 100000.0
CM_IN_A_M = 100.0
SECS_IN_AN_HOUR = 3600
BUCKET_SIZE = 0.2794

sensor = W1ThermSensor()
wind_speed_sensor = DigitalInputDevice(17, pull_up=True)
rain_sensor = DigitalInputDevice(27, pull_up=True)

logfile = "log.txt"

def init_logging():
    with open(logfile, "w") as text_file:
        text_file.write("### Starting to log {} ###\n".format(strftime("%Y-%m-%d %H:%M:%S", localtime())))
        text_file.write("### {}, {}, {}, {} ###\n".format("Time", "Temp", "Wind", "Rain"))
    threading.Timer(10.0, log_values).start()

def log_values():
    global temp_max, temp_min
    temp = round(sensor.get_temperature(), 1)
    with open(logfile, "a") as text_file:
        text_file.write("{}, {}, {}, {}\n".format(strftime("%Y-%m-%d %H:%M:%S", localtime()), temp, wind, rainfall))
    # Call the log function every n:th second
    threading.Timer(600.0, log_values).start()

def wind():
    global wind
    global wind_count
    wind_time = 5
    while True:
        circumference_cm = (2 * math.pi) * radius_cm
        rotations = wind_count / 2.0
        wind_count = 0

        dist_m = (circumference_cm * rotations) / CM_IN_A_M

        m_per_sec = dist_m / wind_time

        wind = round(m_per_sec * ADJUSTMENT, 1)

        sleep(wind_time)
 

def spin():
    global wind_count
    wind_count = wind_count + 1
 
def rain():
    global rainfall 
    global bucket_count
    bucket_count = bucket_count + 1
    rainfall = round(bucket_count * BUCKET_SIZE - BUCKET_SIZE, 1)

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    global rainfall
    global wind

    temp = round(sensor.get_temperature(), 1)

    if request.method == 'POST':
        rainfall = 0
        temp_max = temp
        temp_min = temp

    temp_max = max(temp_max, temp)
    temp_min = min(temp_min, temp)
    return render_template('index.html', temp = temp, wind = wind, rainfall = rainfall, temp_max = temp_max, temp_min = temp_min)


if __name__ == '__main__':
    windspeed = threading.Thread(name='wind', target=wind)
    raindata = threading.Thread(name='rain', target=rain)

    windspeed.start()
    raindata.start()

    wind_speed_sensor.when_activated = spin
    rain_sensor.when_activated = rain

    # To start logging values
    #init_logging()

    app.run(host='0.0.0.0')
