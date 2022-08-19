import datetime
import json
import logging
import uuid
import zoneinfo
from dataclasses import asdict
from typing import Any

import requests
from auth import OauthSecrets, auth_is_expire, get_auth_data, get_expiration_timestamp
from flask import Flask, redirect, request, url_for

import adschema
from utils import add_query_to_url

app = Flask(__name__)
logging.basicConfig()
logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def info() -> str:
    return 'conduit.app minimal oauth driver'


@app.route('/stats', methods=['POST'])
def stats() -> tuple[Any, int]:
    """Returns JSON with the table of data according to declared data schema"""
    body = request.get_json()
    auth_data = get_auth_data()

    if auth_is_expire(auth_data):
        # if auth need to refresh stop processing and return HTTP401
        return {}, 401

    date = datetime.date.fromisoformat(body['date'])
    tz = zoneinfo.ZoneInfo(body['tz'])
    native_id = body['native_id']  # Account internal id

    row = adschema.row
    row['date'] = date.isoformat()

    # returning data in JSON format
    return json.dumps([row]), 200


@app.route('/refresh', methods=['POST'])
def refresh() -> tuple[Any, int]:
    """Refresh Auth Data and return as JSON"""
    auth_data = get_auth_data()
    auth_data.expires_at = get_expiration_timestamp()

    return asdict(auth_data), 200


@app.route('/connect', methods=['GET'])
def connect() -> Any:
    """Starts OAuth connection procedure"""
    return_url = request.args['return_url']
    callback_url = request.args['callback_url']
    token = request.args['token']

    complete_url = add_query_to_url(
        url_for('oauth_callback'),
        {
            'sandbox_token': token,
            'sandbox_callback_url': callback_url,
            'return_url': return_url,
        },
    )

    # start oauth process that will return to complete url

    return redirect(complete_url)


@app.route('/oauth_callback', methods=['GET'])
async def oauth_callback() -> Any:
    """Finishes OAuth connection procedure. Sends result to sandbox API."""
    return_url = request.args['return_url']
    callback_url = request.args['sandbox_callback_url']
    token = request.args['sandbox_token']

    status = 0
    status_message = None

    # fetch token from the response
    credentials = OauthSecrets(
        access_token=uuid.uuid4().hex,
        refresh_token=uuid.uuid4().hex,
        expires_at=get_expiration_timestamp(),
    )
    # If there are any errors, set status to nonzero and status_message to description
    errors: list[str] = []

    if errors:
        status = 1
        status_message = ', '.join(errors)

    message = {
        'credentials': asdict(credentials),
        'status': status,
        'status_message': status_message,
    }

    # Send result of the try to sandbox API
    sandbox_status, sandbox_content, callback_data = await request_sandbox(callback_url, message, token)

    redirect_url = callback_data.get('redirect_url', return_url)

    if sandbox_status == 401:  # token expired
        # return to the server's UI
        return redirect(redirect_url)

    if sandbox_status == 200:
        # all is OK. return to the server's UI
        return redirect(redirect_url)

    # display an error to the user
    return f'{sandbox_content}<br><a href="{redirect_url}">Return</a>', sandbox_status


async def request_sandbox(url: str, data: dict[str, Any], token: str) -> tuple[int, str, dict[Any, Any]]:
    callback_data = {}

    try:
        r = requests.post(url, json=data, headers={'Authorization': f'Bearer {token}'})
        status_code = r.status_code
        callback_data = r.json()
        content = r.content

    except requests.RequestException as e:
        status_code = 500
        content = str(e)
        logger.error(content)

    return status_code, content, callback_data


if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run(debug=True, port=5001)
