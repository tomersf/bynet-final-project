from db import AttendanceDB
from Logger import Logger
from env import env_config
from flask import Flask, jsonify
from flask_cors import CORS
from colorama import init
init()


app = Flask(__name__)
CORS(app, origins="*")

attendance_db = AttendanceDB()
if attendance_db.connect():
    if attendance_db.load_participants():
        Logger.SUCCESS('Loaded participants to DB!')
    else:
        Logger.ERROR('Unable to load participants to DB!')
else:
    Logger.ERROR('Unable to connect to DB!')


@app.route("/attendees")
def attendess():
    attendees = attendance_db.get_all_attendees()
    return jsonify(attendees)


@app.route("/attendance")
def attendance():
    attendance = attendance_db.get_attendance()
    return jsonify(attendance)


if __name__ == '__main__':
    app.run(host=env_config['WEB_HOST'], port=env_config['WEB_PORT'])
