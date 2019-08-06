import os
import threading
import math
from time import sleep, localtime, strftime
from flask import Flask, request, render_template, flash, session
from passlib.hash import sha256_crypt

# dummy hash for 'admin' and 'password'
username_hash = '$5$rounds=535000$CWrew0XEF3Z2MHZV$5ly.8fTwUhxW48rrp70NVw.TIdV0X.jZVwGCErlsRq5'
password_hash = '$5$rounds=535000$pE43ViC/UiLBakSo$0HXlVz5HO3thZ1y3Jf8QDX7YE4GeVEW49Wae8z2m.SB'

logfile = "log.txt"

app = Flask(__name__)

rainfall = 30.2
wind = 12.4
temp_max = -999.9
temp_min = 999.9

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

    elif request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    
    else:
        flash('wrong password!')
    
    return index()

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        global temp_max, temp_min

        temp = round(23.6578443333, 1)

        temp_max = max(temp_max, temp)
        temp_min = min(temp_min, temp)
        return render_template('index.html', temp = temp, wind = wind, rainfall = rainfall, temp_max = temp_max, temp_min = temp_min)

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
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0')
