import datetime
import json
from dataclasses import dataclass
from typing import Any, Optional

from flask import request


@dataclass
class OauthSecrets:
    access_token: str
    refresh_token: Optional[str] = None

    token_type: Optional[str] = None
    expires_at: Optional[float] = None

    extra: Optional[dict[str, Any]] = None


def get_auth_data() -> OauthSecrets:
    return OauthSecrets(**json.loads(request.headers['Authorization']))


def auth_is_expire(auth_data: OauthSecrets) -> bool:
    if expire_at := auth_data.expires_at:
        return expire_at < datetime.datetime.now().timestamp()

    return False


def get_expiration_timestamp() -> float:
    return (datetime.datetime.now() + datetime.timedelta(minutes=15)).timestamp()
