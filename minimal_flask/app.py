from functools import wraps
from flask import Flask, request, abort, jsonify, render_template, redirect
from werkzeug.exceptions import HTTPException
import requests
import logging

app = Flask(__name__)
logging.basicConfig()
logger = logging.getLogger(__name__)


def get_account(**kwargs):
    return {
               "name": "Platform Account",
               "native_id": "12345678",
           }, 200


def auth_required(func):
    @wraps(func)
    def test_auth(*args, **kwargs):
        authorization_token = request.headers.get("Authorization-Token")
        authorization_login = request.headers.get("Authorization-Login")
        authorization_password = request.headers.get("Authorization-Password")
        if not (authorization_token or (authorization_login and authorization_password)):
            abort(403)
        account, status_code = get_account(authorization_token=authorization_token,
                                           authorization_login=authorization_login,
                                           authorization_password=authorization_password)

        return func(account, *args, **kwargs)

    return test_auth


@app.route('/', methods=["GET"])
@app.route('/info', methods=["GET"])
def info():
    return {
        "name": "flask_driver",
        "auth_type": ["token", "login"]
    }


@app.route("/accounts", methods=["POST"])
@auth_required
def accounts(account):
    response = {
        "name": account['name'],
        "native_id": account['native_id'],
        "accounts": [
            {
                "name": "Account 1",
                "native_id": "1234"
            },
            {
                "name": "Account 2",
                "native_id": "1235"
            },
        ]
    }
    return response, 200


@app.route("/check", methods=["POST"])
@auth_required
def check(account):
    body = request.get_json()
    if account['native_id'] != body['native_id']:
        abort(400, {"error": "Bad native_id"})
    return "", 200


@app.route("/stats", methods=["POST"])
@auth_required
def stats(account):
    body = request.get_json()
    login = request.headers.get("Authorization-Login")
    if account['native_id'] != body['native_id']:
        abort(400, {"error": "Bad native_id"})
    if not 'date' in body:
        abort(400, {"error": "Date not found"})

    return jsonify({
        "native_id": account['native_id'],
        "login": login,
        "data": [
            {"stat1": "data1", "date": body['date'], "tz": body['tz']},
            {"stat2": "data2", "date": body['date'], "tz": body['tz']}
        ]}), 200


@app.route("/connect", methods=["GET"])
def connect():
    context = {"driver_name": "Flask Driver"}
    context.update(request.args)
    return render_template("connect_button.html", **context)


@app.route("/test_connect", methods=["POST"])
async def test_connect():
    authorization_token = request.args.get("token")
    authorization_login = request.args.get("login")
    authorization_password = request.args.get("password")
    sessionToken = request.form.get("sessionToken")
    redirect_url = request.form.get("redirect_url")
    login = request.form.get("login")
    _status = None
    status_message = None
    try:
        account, status_code = get_account(authorization_token=authorization_token,
                                           authorization_login=authorization_login,
                                           authorization_password=authorization_password)
        if status_code == 200:
            _status = 0
    except HTTPException as e:
        status_message = e.detail
        _status = 2
    except Exception as e:
        status_message = e.detail
        _status = 1
    message = {
        "sessionToken": sessionToken,
        "credentials": {"native_id": account['native_id'], "login": login, "password": request.form.get("password")},
        "status": _status,
        "status_message": status_message
    }
    sandbox_status, sandbox_content = await request_sandbox(request.form.get("webhook_url"), message)

    if sandbox_status in [200]:
        return redirect(redirect_url)
    else:
        params = {"sandbox_status": sandbox_status, "sandbox_content": sandbox_content}
        req = requests.models.PreparedRequest()
        req.prepare_url(redirect_url, params)
        return redirect(req.url)
    message['sandbox_status_code'] = sandbox_status
    return message


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
