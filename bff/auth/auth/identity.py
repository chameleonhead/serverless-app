import base64
import datetime
import hashlib
import hmac
import json
from typing import Any

import botocore.exceptions
import requests


def generate_secret_hash(client_id, client_secret, username):
    digest = hmac.digest(
        client_secret.encode("utf-8"),
        (username + client_id).encode("utf-8"),
        hashlib.sha256,
    )
    return base64.b64encode(digest).decode()


class LoginFailedException(Exception):
    pass


class TokenRefreshFailedException(Exception):
    pass


class Identity(object):

    def __init__(
        self,
        cognito_idp: Any,
        secretsmanager: Any,
        user_pool_id: str,
        user_pool_domain: str,
        secret_key_id: str,
    ):
        self.__cognito_idp = cognito_idp
        self.__secretsmanager = secretsmanager
        self.__user_pool_id = user_pool_id
        self.__user_pool_domain = user_pool_domain
        self.__secret_key_id = secret_key_id
        self.__client_id = None
        self.__client_secret = None
        self.__redirect_uri = None

    def __load_secret(self):
        secret_response = self.__secretsmanager.get_secret_value(
            SecretId=self.__secret_key_id,
        )

        secret_value = json.loads(secret_response["SecretString"])
        self.__client_id = secret_value["client_id"]
        self.__client_secret = secret_value["client_secret"]
        self.__redirect_uri = secret_value["redirect_uri"]

    def login(self, username: str, password: str):
        if not self.__client_id:
            self.__load_secret()

        try:
            response = self.__cognito_idp.admin_initiate_auth(
                UserPoolId=self.__user_pool_id,
                ClientId=self.__client_id,
                AuthFlow="ADMIN_USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": username,
                    "PASSWORD": password,
                    "SECRET_HASH": generate_secret_hash(
                        self.__client_id,
                        self.__client_secret,
                        username,
                    ),
                },
            )

            result = response["AuthenticationResult"]
            id_token = result["IdToken"]
            access_token = result["AccessToken"]
            refresh_token = result["RefreshToken"]
            expires_in = result["ExpiresIn"]
            return {
                "id_token": id_token,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiration": (
                    datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(seconds=expires_in)
                ).isoformat(),
            }
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] in ["NotAuthorizedException"]:
                raise LoginFailedException(e) from e
            raise e from e

    def request_tokens_by_code(self, code: str):
        if not self.__client_id:
            self.__load_secret()

        # Cognitoにトークンを要求
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.__client_id,
            "redirect_uri": self.__redirect_uri,
        }

        response = requests.post(
            f"https://{self.__user_pool_domain}/oauth2/token",
            data=body,
            headers=headers,
            auth=(str(self.__client_id), str(self.__client_secret)),
        )
        if response.status_code != 200:
            raise Exception()

        # トークンの取得に成功した場合
        result = response.json()
        id_token = result["id_token"]
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]
        expires_in = result["expires_in"]

        return {
            "id_token": id_token,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expiration": (
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(seconds=expires_in)
            ).isoformat(),
        }

    def refresh_tokens(self, username: str, refresh_token: str):
        if not self.__client_id:
            self.__load_secret()

        try:
            response = self.__cognito_idp.admin_initiate_auth(
                UserPoolId=self.__user_pool_id,
                ClientId=self.__client_id,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={
                    "REFRESH_TOKEN": refresh_token,
                    "SECRET_HASH": generate_secret_hash(
                        self.__client_id,
                        self.__client_secret,
                        username,
                    ),
                },
            )

            result = response["AuthenticationResult"]
            id_token = result["IdToken"]
            access_token = result["AccessToken"]
            refresh_token = result.get("RefreshToken", refresh_token)
            expires_in = result["ExpiresIn"]
            return {
                "id_token": id_token,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiration": (
                    datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(seconds=expires_in)
                ).isoformat(),
            }
        except botocore.exceptions.ClientError as e:
            raise TokenRefreshFailedException(e) from e
