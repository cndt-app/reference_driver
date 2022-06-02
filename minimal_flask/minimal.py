from functools import wraps
from flask import Flask, request, abort, jsonify, render_template, redirect
from werkzeug.exceptions import HTTPException
import requests
import logging
import zoneinfo
app = Flask(__name__)
logging.basicConfig()
logger = logging.getLogger(__name__)

@app.after_request
def add_header(response):
    response.cache_control.max_age = 1
    return response

@app.route("/stats", methods=["POST"])
def stats():
    body = request.get_json()
    login = request.headers.get("Authorization-Login")
    password = request.headers.get("Authorization-Password")
    date = body['date']
    tz = zoneinfo.ZoneInfo(body['tz'])

    #requesting external data
    with open('adschema.json') as f:
        lines = f.read()
    #returning data in JSON format
    return lines, 200


@app.route("/connect", methods=["GET"])
def connect():
    context = {"driver_name": "Minimalistic Example"}
    context.update(request.args)
    return render_template("connect_button.html", **context)


@app.route("/test_connect", methods=["POST"])
async def test_connect():
    token = request.form.get("token")
    login = request.form.get("login")
    password = request.form.get("password")
    sessionToken = request.form.get("sessionToken")
    webhook_url= request.form.get("webhook_url")
    redirect_url = request.form.get("redirect_url")
    account="NA"

    _status = 0
    status_message = None
    # verify that the credentials are correct

    message = {
        "sessionToken": sessionToken,
        "credentials": {"native_id": account, "login": login, "password": password},
        "status": _status,
        "status_message": status_message
    }

    sandbox_status, sandbox_content = await request_sandbox(webhook_url,message)

    if sandbox_status in [200]:
        #return to the server's UI
        return redirect(redirect_url)
    #display an error to the user
    return f"{sandbox_content}<br><a href='{redirect_url}'>Return</a>", sandbox_status

async def request_sandbox2(url, data):
    r = requests.post(url, json=data)
    return r.status_code, r.content

async def request_sandbox(url, data):
    status_code = None
    try:
        r = requests.post(url, json=data)
        status_code = r.status_code
        content = r.content
    except Exception as e:
        status_code = 500
        content = e.__str__()
        logger.error(content)
    return status_code, content

if __name__ == '__main__':
    app.run()
