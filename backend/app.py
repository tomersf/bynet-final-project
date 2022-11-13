from db import AttendanceDB
from Logger import Logger
from env import env_config
from flask import Flask, jsonify
from flask_cors import CORS
from colorama import init
import json
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
    result = attendance_db.get_all_attendees()
    if result is False:
        return jsonify(result=[])
    else:
        return jsonify(result=json.dumps(result))


@app.route("/attendance")
def attendance():
    result = attendance_db.get_attendance()
    if result is False:
        return jsonify(result=[])
    else:
        print(result)
        return jsonify(result=json.dumps(result))

@app.route("/reload-data")
def reload_data():
    is_data_reloaded = attendance_db.reload_data()
    if is_data_reloaded:
        return jsonify(result=True)
    else:
        return jsonify(result=False)




if __name__ == '__main__':
    app.run(host=env_config['WEB_HOST'], port=env_config['WEB_PORT'])
