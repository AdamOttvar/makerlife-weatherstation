import os
import threading
import math
from time import sleep, localtime, strftime
from gpiozero import DigitalInputDevice
from w1thermsensor import W1ThermSensor
from flask import Flask, request, render_template, flash, session, redirect, url_for
from passlib.hash import sha256_crypt

app = Flask(__name__)

temp_max = -999.9
temp_min = 999.9
rainfall_glob = 0
wind_glob = 0
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

# dummy hash for 'admin' and 'password'
username_hash = '$5$rounds=535000$CWrew0XEF3Z2MHZV$5ly.8fTwUhxW48rrp70NVw.TIdV0X.jZVwGCErlsRq5'
password_hash = '$5$rounds=535000$pE43ViC/UiLBakSo$0HXlVz5HO3thZ1y3Jf8QDX7YE4GeVEW49Wae8z2m.SB'

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.method == 'POST' and 'resetBtn' in request.form:
        reset_values()
    
    elif request.method == 'POST' and 'updateBtn' in request.form:
        index()
    
    elif request.method == 'POST' and 'loginBtn' in request.form:
        username_correct = sha256_crypt.verify(request.form['username'], username_hash)
        password_correct = sha256_crypt.verify(request.form['password'], password_hash)
        if username_correct  and password_correct:
            session['logged_in'] = True
        else:
            print("Wrong credentials entered")
            flash('Fel användarnamn/lösenord')
    
    else:
        flash('wrong password!')
    
    return redirect(url_for('index'))

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        global temp_max, temp_min

        temp = round(sensor.get_temperature(), 1)

        temp_max = max(temp_max, temp)
        temp_min = min(temp_min, temp)
        return render_template('index.html', temp = temp, wind = wind_glob, rainfall = rainfall_glob, temp_max = temp_max, temp_min = temp_min)

def reset_values():
    global rainfall, temp_max, temp_min
    temp = round(23.6578443333, 1)
    rainfall = 0
    temp_max = temp
    temp_min = temp

def init_logging():
    with open(logfile, "w") as text_file:
        text_file.write("### Starting to log {} ###\n".format(strftime("%Y-%m-%d %H:%M:%S", localtime())))
        text_file.write("### {}, {}, {}, {} ###\n".format("Time", "Temp", "Wind", "Rain"))
    threading.Timer(10.0, log_values).start()

def log_values():
    temp = round(sensor.get_temperature(), 1)
    with open(logfile, "a") as text_file:
        text_file.write("{}, {}, {}, {}\n".format(strftime("%Y-%m-%d %H:%M:%S", localtime()), temp, wind_glob, rainfall_glob))
    # Call the log function every n:th second
    threading.Timer(600.0, log_values).start()

def wind():
    global wind_glob
    global wind_count
    wind_time = 5
    while True:
        circumference_cm = (2 * math.pi) * radius_cm
        rotations = wind_count / 2.0
        wind_count = 0

        dist_m = (circumference_cm * rotations) / CM_IN_A_M

        m_per_sec = dist_m / wind_time

        wind_glob = round(m_per_sec * ADJUSTMENT, 1)

        sleep(wind_time)
 
def spin():
    global wind_count
    wind_count = wind_count + 1
 
def rain():
    global rainfall_glob
    global bucket_count
    bucket_count = bucket_count + 1
    rainfall_glob = round(bucket_count * BUCKET_SIZE - BUCKET_SIZE, 1)


if __name__ == '__main__':
    windspeed = threading.Thread(name='wind', target=wind)
    raindata = threading.Thread(name='rain', target=rain)

    windspeed.start()
    raindata.start()

    wind_speed_sensor.when_activated = spin
    rain_sensor.when_activated = rain

    # To start logging values
    #init_logging()

    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0')
