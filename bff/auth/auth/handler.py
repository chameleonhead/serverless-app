import base64
import datetime
import hashlib
import hmac
import http.cookies
import json
import logging
import os
import urllib.parse

import boto3
import botocore
import botocore.exceptions
import requests
from jose import jwt

from .storage import DataNotFoundException, Storage

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname:.4}] {name}: {message}",
    style="{",
)


def generate_secret_hash(client_id, client_secret, username):
    digest = hmac.digest(
        client_secret.encode("utf-8"),
        (username + client_id).encode("utf-8"),
        hashlib.sha256,
    )
    return base64.b64encode(digest).decode()


def handler(event, context):
    path = event.get("rawPath")
    if path == "/auth/login":
        return handler_login(event, context)
    if path == "/auth/logout":
        return handler_logout(event, context)
    if path == "/auth/authorize":
        return handler_authorize(event, context)
    if path == "/auth/callback":
        return handler_callback(event, context)
    if path == "/auth/session":
        return handler_session(event, context)

    return {
        "statusCode": 404,
    }


def handler_login(event, context):
    body = event.get("body")
    if not body:
        return {"statusCode": 400}
    if event["isBase64Encoded"]:
        body = base64.b64decode(body).decode("utf-8")

    s3_bucket = os.getenv("S3_BUCKET")
    cognito_user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    api_client_secret_id = os.getenv("API_CLIENT_SECRET_ID")

    s3 = boto3.client("s3")
    cognito_idp = boto3.client("cognito-idp")
    secretsmanager = boto3.client("secretsmanager")

    secret_response = secretsmanager.get_secret_value(
        SecretId=api_client_secret_id,
    )

    secret_value = json.loads(secret_response["SecretString"])
    client_id = secret_value["client_id"]
    client_secret = secret_value["client_secret"]

    body = json.loads(body)
    try:
        response = cognito_idp.admin_initiate_auth(
            UserPoolId=cognito_user_pool_id,
            ClientId=client_id,
            AuthFlow="ADMIN_USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": body["username"],
                "PASSWORD": body["password"],
                "SECRET_HASH": generate_secret_hash(
                    client_id,
                    client_secret,
                    body["username"],
                ),
            },
        )

        result = response["AuthenticationResult"]
        id_token = result["IdToken"]
        access_token = result["AccessToken"]
        refresh_token = result["RefreshToken"]
        expires_in = result["ExpiresIn"]
        claims = jwt.get_unverified_claims(id_token)
        session_id = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
        logger.info(
            "User %s logged in (session id: %s)",
            claims["sub"],
            session_id,
        )
        st = Storage(s3, s3_bucket)
        st.save_tokens(
            session_id,
            {
                "id_token": id_token,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiration": (
                    datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(seconds=expires_in)
                ).isoformat(),
            },
        )
        set_cookie = f"session_id={session_id}"
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Set-Cookie": set_cookie,
            },
            "body": json.dumps(
                {
                    "session": {
                        "access_token": access_token,
                        "id_token": id_token,
                    },
                    "claims": claims,
                }
            ),
        }
    except botocore.exceptions.ClientError as e:
        logger.exception(e)
        return {
            "statusCode": 403,
            "headers": {
                "Content-Type": "application/json",
            },
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
        st.delete_tokens(session_id.value)
    except DataNotFoundException:
        return {"statusCode": 401}

    set_cookie = "session_id=deleted; expires=Thu, 01 Jan 1970 00:00:00 GMT"
    return {
        "statusCode": 200,
        "headers": {
            "Set-Cookie": set_cookie,
        },
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
        "headers": {
            "Location": f"https://{cognito_user_pool_domain}/"
            + f"oauth2/authorize?{query}"
        },
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
    cognito_user_pool_domain = os.getenv("COGNITO_USER_POOL_DOMAIN")
    api_client_secret_id = os.getenv("API_CLIENT_SECRET_ID")

    s3 = boto3.client("s3")
    state = query_string_parameters.get("state")
    state = json.loads(base64.b64decode(state))
    request_id = state["request_id"]
    st = Storage(s3, s3_bucket)
    return_uri = st.get_state(request_id)["redirect_url"]

    secretsmanager = boto3.client("secretsmanager")

    secret_response = secretsmanager.get_secret_value(
        SecretId=api_client_secret_id,
    )

    secret_value = json.loads(secret_response["SecretString"])
    client_id = secret_value["client_id"]
    client_secret = secret_value["client_secret"]
    redirect_uri = secret_value["redirect_uri"]

    # Cognitoにトークンを要求
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
    }

    response = requests.post(
        f"https://{cognito_user_pool_domain}/oauth2/token",
        data=body,
        headers=headers,
        auth=(client_id, client_secret),
    )
    if response.status_code == 200:
        # トークンの取得に成功した場合
        result = response.json()
        id_token = result["id_token"]
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]
        expires_in = result["expires_in"]
        claims = jwt.get_unverified_claims(id_token)
        session_id = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
        logger.info(
            "User %s logged in (session id: %s)",
            claims["sub"],
            session_id,
        )
        st = Storage(s3, s3_bucket)
        st.save_tokens(
            session_id,
            {
                "id_token": id_token,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiration": (
                    datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(seconds=expires_in)
                ).isoformat(),
            },
        )
        set_cookie = f"session_id={session_id}"
        return {
            "statusCode": 302,
            "headers": {
                "Set-Cookie": set_cookie,
                "Location": return_uri if return_uri else "/",
            },
        }
    else:
        # トークンの取得に失敗した場合
        return {
            "statusCode": response.status_code,
            "body": response.text,
        }


def handler_session(event, context):
    headers = event.get("headers", {})
    cookie = headers.get("cookie")
    sc = http.cookies.SimpleCookie(cookie)
    session_id = sc.get("session_id")
    if not session_id:
        return {"statusCode": 401}

    s3_bucket = os.getenv("S3_BUCKET")
    user_pool_id = os.getenv("USER_POOL_ID")
    api_client_secret_id = os.getenv("API_CLIENT_SECRET_ID")

    s3 = boto3.client("s3")
    cognito_idp = boto3.client("cognito-idp")
    secretsmanager = boto3.client("secretsmanager")
    st = Storage(s3, s3_bucket)

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
            "headers": {
                "Content-Type": "application/json",
            },
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

    secret_response = secretsmanager.get_secret_value(
        SecretId=api_client_secret_id,
    )
    secret_value = json.loads(secret_response["SecretString"])
    client_id = secret_value["client_id"]
    client_secret = secret_value["client_secret"]

    try:
        response = cognito_idp.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": tokens["refresh_token"],
                "SECRET_HASH": generate_secret_hash(
                    client_id,
                    client_secret,
                    claims["username"],
                ),
            },
        )

        result = response["AuthenticationResult"]
        id_token = result["IdToken"]
        access_token = result["AccessToken"]
        refresh_token = result.get("RefreshToken", tokens["refresh_token"])
        expires_in = result["ExpiresIn"]
        claims = jwt.get_unverified_claims(id_token)
        st.save_token(
            session_id.value,
            {
                "id_token": id_token,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiration": (
                    datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(seconds=expires_in)
                ).isoformat(),
            },
        )
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps(
                {
                    "session": {
                        "access_token": access_token,
                        "id_token": id_token,
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
