import threading
import math
from time import sleep
from gpiozero import DigitalInputDevice
from w1thermsensor import W1ThermSensor
from flask import Flask, request

app = Flask(__name__)

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

        wind = m_per_sec * ADJUSTMENT

        sleep(wind_time)
 

def spin():
    global wind_count
    wind_count = wind_count + 1
 
def rain():
    global rainfall 
    global bucket_count
    bucket_count = bucket_count + 1
    rainfall = (bucket_count * BUCKET_SIZE - BUCKET_SIZE)

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    global rainfall

    if request.method == 'POST':
        rainfall = 12

    temp = sensor.get_temperature()
    return '''
            <html>
                <head>
                    <title>Väder Lilla Havedal</title>
                </head>
                <body>
                    <h1>Temperaturen: ''' + str(temp) + ''' grader</h1>
                    <h1>Det blåser: ''' + str(wind) + ''' m/s</h1>
                    <h1>Det har regnat: ''' + str(rainfall) + ''' mm</h1>
                    <form action="/" method="post">
                        <button name="resetBtn" type="submit">Återställ</button>
                    </form>
                </body>
            </html>'''


if __name__ == '__main__':
    windspeed = threading.Thread(name='wind', target=wind)
    raindata = threading.Thread(name='rain', target=rain)

    windspeed.start()
    raindata.start()

    wind_speed_sensor.when_activated = spin
    rain_sensor.when_activated = rain

    app.run(host='0.0.0.0')
