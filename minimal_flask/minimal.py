import json
import logging
import datetime

import requests
import zoneinfo
from flask import Flask, request, render_template, redirect


app = Flask(__name__, static_url_path="/static/", static_folder="static")
logging.basicConfig()
logger = logging.getLogger(__name__)


# @app.after_request
# def add_header(response):
#     response.cache_control.max_age = 1
#     return response

@app.route('/', methods=["GET"])
def info():
    return "cndt.app driver"


@app.route("/stats", methods=["POST"])
def stats():
    body = request.get_json()
    auth_data = get_auth_data(request)

    if auth_is_expire(auth_data):
        # if auth need to refresh stop processing and return HTTP401
        return {}, 401

    date = body['date']
    tz = zoneinfo.ZoneInfo(body['tz'])

    # requesting external data
    with open('adschema.json') as f:
        lines = f.read()
    # returning data in JSON format
    return lines, 200


@app.route("/refresh", methods=["POST"])
def refresh():
    """Refresh Auth Data and return as JSON"""
    auth_data = get_auth_data(request)
    auth_data['expire_at'] = get_expiration_timestamp()

    return auth_data, 200


@app.route("/connect", methods=["GET"])
def connect():
    context = get_context()
    context.update(request.args)
    return render_template("connect_button.html", **context)


@app.route("/test_connect", methods=["POST"])
async def test_connect():
    login = request.form.get("login")
    password = request.form.get("password")

    token = request.form.get("token")
    callback_url = request.form.get("callback_url")

    _status = 0
    status_message = None

    # verify that the credentials are correct
    errors = []
    if login == 'failed_login':
        errors.append('Login are incorrect')

    if password == '123':
        errors.append('Password to simple')

    if errors:
        context = get_context() | {'errors': errors}
        context.update(request.form)

        return render_template("connect_button.html", **context)

    # for refresh endpoint example
    expire_at = get_expiration_timestamp()

    message = {
        "credentials": {"login": login, "password": password, "expire_at": expire_at},
        "status": _status,
        "status_message": status_message
    }

    sandbox_status, sandbox_content, callback_data = await request_sandbox(callback_url, message, token)

    redirect_url = callback_data.get('redirect_url', request.form.get('return_url'))

    if sandbox_status in [200]:
        # return to the server's UI
        return redirect(redirect_url)

    # display an error to the user
    return f'{sandbox_content}<br><a href="{redirect_url}">Return</a>', sandbox_status


def get_context():
    return {"driver_name": "Minimalistic Example"}


def get_auth_data(request):
    return json.loads(request.headers.get("Authorization"))


def auth_is_expire(auth_data):
    if expire_at := auth_data.get('expire_at'):
        return expire_at < datetime.datetime.now().timestamp()

    return False


def get_expiration_timestamp():
    return (datetime.datetime.now() + datetime.timedelta(minutes=15)).timestamp()


async def request_sandbox2(url, data):
    r = requests.post(url, json=data)
    return r.status_code, r.content


async def request_sandbox(url, data, token):
    callback_data = {}
    try:
        r = requests.post(url, json=data, headers={'Authorization': f'Bearer {token}'})
        status_code = r.status_code
        callback_data = r.json()
        content = r.content
    except Exception as e:
        status_code = 500
        content = e.__str__()
        logger.error(content)
    return status_code, content, callback_data


if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run(debug=True)
