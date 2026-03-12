import os
import sanic
from sanic.exceptions import Unauthorized
from sanic.log import logger

import jwt
from jwt import PyJWKClient, InvalidSignatureError, ExpiredSignatureError

GROUPS_CLAIM = os.environ.get("GROUPS_CLAIM", "cognito:groups")


def get_signing_key(jwks_url: str):
    jwks_client = PyJWKClient(jwks_url)
    jwks_client.get_signing_keys()
    logger.info("Got signing keys")
    return jwks_client


def verify_token(request: sanic.Request, jwks_client: PyJWKClient) -> dict:
    try:
        token_header = request.headers["Authorization"]
    except KeyError:
        raise Unauthorized()

    token = token_header[7:]
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    try:
        token_decoded = jwt.decode(token, signing_key, algorithms=["RS256"])
    except InvalidSignatureError as e:
        logger.exception(e)
        raise Unauthorized()
    except ExpiredSignatureError as e:
        logger.exception(e)
        raise Unauthorized()

    return token_decoded


def get_groups_in_token(token: dict) -> list[str]:
    try:
        return token[GROUPS_CLAIM]
    except KeyError:
        return []
