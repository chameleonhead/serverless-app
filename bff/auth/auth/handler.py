import base64
import datetime
import hashlib
import http.cookies
import json
import logging
import os
import urllib.parse

import boto3
import botocore
import botocore.exceptions
from jose import jwt

from .identity import Identity
from .storage import DataNotFoundException, Storage

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname:.4}] {name}: {message}",
    style="{",
)


def handler(event, context):
    path = event.get("rawPath")
    if path == "/auth/login":
        return handler_login(event, context)
    if path == "/auth/logout":
        return handler_logout(event, context)
    if path == "/auth/session":
        return handler_session(event, context)
    if path == "/auth/authorize":
        return handler_authorize(event, context)
    if path == "/auth/callback":
        return handler_callback(event, context)

    return {
        "statusCode": 404,
    }


def handler_login(event, context):
    body = event.get("body")
    if not body:
        return {"statusCode": 400}
    if event["isBase64Encoded"]:
        body = base64.b64decode(body).decode("utf-8")
    body = json.loads(body)

    s3_bucket = os.getenv("S3_BUCKET")
    s3 = boto3.client("s3")
    st = Storage(s3, s3_bucket)

    cognito_user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    cognito_user_pool_domain = os.getenv("COGNITO_USER_POOL_DOMAIN")
    api_client_secret_id = os.getenv("API_CLIENT_SECRET_ID")
    cognito_idp = boto3.client("cognito-idp")
    secretsmanager = boto3.client("secretsmanager")

    idp = Identity(
        cognito_idp,
        secretsmanager,
        cognito_user_pool_id,
        cognito_user_pool_domain,
        api_client_secret_id,
    )

    try:
        tokens = idp.login(body["username"], body["password"])
        claims = jwt.get_unverified_claims(tokens["id_token"])
        session_id = hashlib.sha256(
            tokens["refresh_token"].encode("utf-8"),
        ).hexdigest()
        logger.info(
            "User %s logged in (session id: %s)",
            claims["sub"],
            session_id,
        )
        st.save_tokens(session_id, tokens)
        set_cookie = f"session_id={session_id}"
        return {
            "statusCode": 200,
            "headers": set_security_headers(
                {
                    "Content-Type": "application/json",
                    "Set-Cookie": set_cookie,
                }
            ),
            "body": json.dumps(
                {
                    "session": {
                        "access_token": tokens["access_token"],
                        "id_token": tokens["id_token"],
                    },
                    "claims": claims,
                }
            ),
        }
    except botocore.exceptions.ClientError as e:
        logger.exception(e)
        return {
            "statusCode": 403,
            "headers": set_security_headers(
                {
                    "Content-Type": "application/json",
                }
            ),
            "body": json.dumps({"message": "Failed to login."}),
        }


def handler_logout(event, context):
    headers = event.get("headers", {})
    cookie = headers.get("cookie")
    sc = http.cookies.SimpleCookie(cookie)
    session_id = sc.get("session_id")
    if not session_id:
        return {"statusCode": 401}

    s3_bucket = os.getenv("S3_BUCKET")

    s3 = boto3.client("s3")
    st = Storage(s3, s3_bucket)

    try:
        tokens = st.get_tokens(session_id.value)
        st.delete_tokens(session_id.value)
    except DataNotFoundException:
        return {"statusCode": 401}

    claims = jwt.get_unverified_claims(tokens["id_token"])
    logger.info(
        "User %s logged out (session id: %s)",
        claims["sub"],
        session_id.value,
    )

    set_cookie = "session_id=deleted; expires=Thu, 01 Jan 1970 00:00:00 GMT"
    return {
        "statusCode": 200,
        "headers": set_security_headers(
            {
                "Set-Cookie": set_cookie,
            }
        ),
    }


def handler_authorize(event, context):
    query_params = event.get("queryStringParameters", {})
    idp = query_params.get("idp")
    if not idp:
        return {
            "statusCode": 400,
            "headers": set_security_headers({}),
            "body": "Bad Request",
        }

    s3_bucket = os.getenv("S3_BUCKET")
    cognito_user_pool_domain = os.getenv("COGNITO_USER_POOL_DOMAIN")
    api_client_secret_id = os.getenv("API_CLIENT_SECRET_ID")

    s3 = boto3.client("s3")
    secretsmanager = boto3.client("secretsmanager")

    secret_response = secretsmanager.get_secret_value(
        SecretId=api_client_secret_id,
    )

    secret_value = json.loads(secret_response["SecretString"])
    client_id = secret_value["client_id"]
    redirect_uri = secret_value["redirect_uri"]

    request_id = event.get("requestContext").get("requestId")
    redirect_url = query_params.get("redirect_url")

    st = Storage(s3, s3_bucket)
    st.save_state(request_id, {"redirect_url": redirect_url})
    query = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": base64.b64encode(
                json.dumps(
                    {
                        "request_id": request_id,
                    }
                ).encode()
            ).decode(),
            "identity_provider": idp,
            "scope": "openid profile",
        }
    )

    return {
        "statusCode": 302,
        "headers": set_security_headers(
            {
                "Location": f"https://{cognito_user_pool_domain}"
                + f"/oauth2/authorize?{query}"
            }
        ),
    }


def handler_callback(event, context):
    # Cognitoの認証コードをクエリパラメータから取得
    query_string_parameters = event.get("queryStringParameters", {})
    code = query_string_parameters.get("code")
    if not code:
        return {
            "statusCode": 400,
            "headers": set_security_headers({}),
            "body": "Bad Request",
        }

    s3_bucket = os.getenv("S3_BUCKET")
    s3 = boto3.client("s3")
    st = Storage(s3, s3_bucket)

    cognito_user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    cognito_user_pool_domain = os.getenv("COGNITO_USER_POOL_DOMAIN")
    api_client_secret_id = os.getenv("API_CLIENT_SECRET_ID")
    cognito_idp = boto3.client("cognito-idp")
    secretsmanager = boto3.client("secretsmanager")

    idp = Identity(
        cognito_idp,
        secretsmanager,
        cognito_user_pool_id,
        cognito_user_pool_domain,
        api_client_secret_id,
    )

    state = query_string_parameters.get("state")
    state = json.loads(base64.b64decode(state))
    request_id = state["request_id"]
    return_uri = st.get_state(request_id)["redirect_url"]

    tokens = idp.request_tokens_by_code(code)

    # トークンの取得に成功した場合
    claims = jwt.get_unverified_claims(tokens["id_token"])
    session_id = hashlib.sha256(
        tokens["refresh_token"].encode("utf-8"),
    ).hexdigest()
    logger.info(
        "User %s logged in (session id: %s)",
        claims["sub"],
        session_id,
    )
    st = Storage(s3, s3_bucket)
    st.save_tokens(session_id, tokens)
    set_cookie = f"session_id={session_id}"
    return {
        "statusCode": 302,
        "headers": set_security_headers(
            {
                "Set-Cookie": set_cookie,
                "Location": return_uri if return_uri else "/",
            }
        ),
    }


def handler_session(event, context):
    headers = event.get("headers", {})
    cookie = headers.get("cookie")
    sc = http.cookies.SimpleCookie(cookie)
    session_id = sc.get("session_id")
    if not session_id:
        return {"statusCode": 401}

    s3_bucket = os.getenv("S3_BUCKET")
    s3 = boto3.client("s3")
    st = Storage(s3, s3_bucket)

    cognito_user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    cognito_user_pool_domain = os.getenv("COGNITO_USER_POOL_DOMAIN")
    api_client_secret_id = os.getenv("API_CLIENT_SECRET_ID")
    cognito_idp = boto3.client("cognito-idp")
    secretsmanager = boto3.client("secretsmanager")

    idp = Identity(
        cognito_idp,
        secretsmanager,
        cognito_user_pool_id,
        cognito_user_pool_domain,
        api_client_secret_id,
    )

    try:
        tokens = st.get_tokens(session_id.value)
    except DataNotFoundException:
        return {"statusCode": 401}

    claims = jwt.get_unverified_claims(tokens["id_token"])

    if datetime.datetime.fromisoformat(
        tokens["expiration"],
    ) > datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(minutes=20):
        return {
            "statusCode": 200,
            "headers": set_security_headers(
                {
                    "Content-Type": "application/json",
                }
            ),
            "body": json.dumps(
                {
                    "session": {
                        "access_token": tokens["access_token"],
                        "id_token": tokens["id_token"],
                    },
                    "claims": claims,
                }
            ),
        }

    try:
        tokens = idp.refresh_tokens(
            claims["username"],
            tokens["refresh_token"],
        )

        claims = jwt.get_unverified_claims(tokens["id_token"])
        st.save_token(session_id.value, tokens)
        return {
            "statusCode": 200,
            "headers": set_security_headers(
                {
                    "Content-Type": "application/json",
                }
            ),
            "body": json.dumps(
                {
                    "session": {
                        "access_token": tokens["access_token"],
                        "id_token": tokens["id_token"],
                    },
                    "claims": claims,
                }
            ),
        }
    except Exception as e:
        print(e)
        return {"statusCode": 401}


def set_security_headers(headers):
    headers.update(
        {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": (
                "default-src *;"
                + "script-src * 'unsafe-inline';"
                + "connect-src * 'unsafe-inline';"
                + "img-src * data: blob: 'unsafe-inline';"
                + "frame-src *;"
                + "style-src * 'unsafe-inline';"
            ),
            "Strict-Transport-Security": (
                "max-age=63072000;" + "includeSubDomains;" + "preload"
            ),
        }
    )
    return headers
