import base64
import http.cookies
import json
import os
import unittest
import unittest.mock
import urllib.parse

import boto3
import moto

import auth
import auth.handler


class TestHandler(unittest.TestCase):
    def setup_cognito(self, cognito_idp, secretsmanager):
        user_pool = cognito_idp.create_user_pool(
            PoolName="dev-user-pool",
        )["UserPool"]
        user_pool_domain = cognito_idp.create_user_pool_domain(
            UserPoolId=user_pool["Id"],
            Domain=user_pool["Id"],
        )
        cognito_idp.admin_create_user(
            UserPoolId=user_pool["Id"],
            Username="admin@example.com",
            UserAttributes=[
                {"Name": "email", "Value": "user@example.com"},
                {"Name": "email_verified", "Value": "true"},
            ],
        )
        cognito_idp.admin_set_user_password(
            UserPoolId=user_pool["Id"],
            Username="admin@example.com",
            Password="P@ssw0rd",
            Permanent=True,
        )
        user_pool_client = cognito_idp.create_user_pool_client(
            UserPoolId=user_pool["Id"],
            ClientName="dev-user-pool-client",
            GenerateSecret=True,
        )["UserPoolClient"]
        secretsmanager.create_secret(
            Name="dev/serverless-app/api-client",
            SecretString=json.dumps(
                {
                    "client_id": user_pool_client["ClientId"],
                    "client_secret": user_pool_client["ClientSecret"],
                    "redirect_uri": "https://example.com/auth/callback",
                }
            ),
        )
        return user_pool["Id"], user_pool_domain["CloudFrontDomain"]

    @moto.mock_aws
    @unittest.mock.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ap-northeast-1"},
    )
    def test_handler_login(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="dev-s3-session-storage")
        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        user_pool_id, user_pool_domain = self.setup_cognito(
            cognito_idp,
            secretsmanager,
        )

        with unittest.mock.patch.dict(
            os.environ,
            {
                "S3_BUCKET": "dev-s3-session-storage",
                "COGNITO_USER_POOL_ID": user_pool_id,
                "COGNITO_USER_POOL_DOMAIN": user_pool_domain,
                "API_CLIENT_SECRET_ID": "dev/serverless-app/api-client",
            },
        ):
            result = auth.handler(
                {
                    "rawPath": "/auth/login",
                    "rawQueryString": "",
                    "headers": {
                        "host": "lambda-url.com",
                    },
                    "requestContext": {
                        "http": {
                            "method": "POST",
                            "path": "/auth/login",
                        },
                        "requestId": "be4172b1-0ea4-4121-88db-08960adb054f",
                        "timeEpoch": 1725703735416,
                    },
                    "body": json.dumps(
                        {
                            "username": "admin@example.com",
                            "password": "P@ssw0rd",
                        }
                    ),
                    "isBase64Encoded": False,
                },
                None,
            )
        self.assertEqual(200, result["statusCode"])
        res_body = json.loads(result["body"])
        self.assertIsNotNone(res_body["session"]["id_token"])
        self.assertIsNotNone(res_body["session"]["access_token"])

    @moto.mock_aws
    @unittest.mock.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ap-northeast-1"},
    )
    def test_handler_login_with_idp(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="dev-s3-session-storage")
        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        user_pool_id, user_pool_domain = self.setup_cognito(
            cognito_idp,
            secretsmanager,
        )

        secret_response = secretsmanager.get_secret_value(
            SecretId="dev/serverless-app/api-client",
        )
        secret_value = json.loads(secret_response["SecretString"])
        client_id = secret_value["client_id"]

        with unittest.mock.patch.dict(
            os.environ,
            {
                "S3_BUCKET": "dev-s3-session-storage",
                "COGNITO_USER_POOL_ID": user_pool_id,
                "COGNITO_USER_POOL_DOMAIN": user_pool_domain,
                "API_CLIENT_SECRET_ID": "dev/serverless-app/api-client",
            },
        ):
            result = auth.handler(
                {
                    "rawPath": "/auth/login",
                    "rawQueryString": "?idp=COGNITO",
                    "queryStringParameters": {"idp": "COGNITO"},
                    "headers": {
                        "host": "lambda-url.com",
                    },
                    "requestContext": {
                        "http": {
                            "method": "GET",
                            "path": "/auth/login",
                        },
                        "requestId": "be4172b1-0ea4-4121-88db-08960adb054f",
                        "timeEpoch": 1725703735416,
                    },
                },
                None,
            )
        self.assertEqual(302, result["statusCode"])
        location = result["headers"]["Location"]
        state = base64.b64encode(
            json.dumps(
                {
                    "request_id": "be4172b1-0ea4-4121-88db-08960adb054f",
                }
            ).encode()
        ).decode()
        self.assertEqual(
            f"https://{user_pool_domain}/oauth2/authorize?"
            + "response_type=code&"
            + f"client_id={client_id}&"
            + "redirect_uri=https%3A%2F%2Fexample.com%2Fauth%2Fcallback&"
            + f"state={urllib.parse.quote(state)}&"
            + "identity_provider=COGNITO&"
            + "scope=openid+profile",
            location,
        )

    @moto.mock_aws
    @unittest.mock.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ap-northeast-1"},
    )
    @unittest.mock.patch("requests.post")
    def test_handler_callback(self, mock_post):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="dev-s3-session-storage")
        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        user_pool_id, user_pool_domain = self.setup_cognito(
            cognito_idp,
            secretsmanager,
        )

        secret_response = secretsmanager.get_secret_value(
            SecretId="dev/serverless-app/api-client",
        )

        secret_value = json.loads(secret_response["SecretString"])
        client_id = secret_value["client_id"]
        client_secret = secret_value["client_secret"]

        s3.put_object(
            Bucket="dev-s3-session-storage",
            Key="oauth2/be4172b1-0ea4-4121-88db-08960adb054f/state.json",
            Body=json.dumps(
                {
                    "redirect_url": "https://example.com",
                }
            ).encode("utf-8"),
        )

        response = cognito_idp.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow="ADMIN_USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": "admin@example.com",
                "PASSWORD": "P@ssw0rd",
                "SECRET_HASH": auth.generate_secret_hash(
                    client_id,
                    client_secret,
                    "admin@example.com",
                ),
            },
        )

        result = response["AuthenticationResult"]
        id_token = result["IdToken"]
        access_token = result["AccessToken"]
        refresh_token = result["RefreshToken"]
        expires_in = result["ExpiresIn"]

        mock_response = unittest.mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": access_token,
            "id_token": id_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
        }

        mock_post.return_value = mock_response
        state = base64.b64encode(
            json.dumps(
                {
                    "request_id": "be4172b1-0ea4-4121-88db-08960adb054f",
                }
            ).encode()
        ).decode()

        with unittest.mock.patch.dict(
            os.environ,
            {
                "S3_BUCKET": "dev-s3-session-storage",
                "COGNITO_USER_POOL_ID": user_pool_id,
                "COGNITO_USER_POOL_DOMAIN": user_pool_domain,
                "API_CLIENT_SECRET_ID": "dev/serverless-app/api-client",
            },
        ):
            result = auth.handler(
                {
                    "rawPath": "/auth/callback",
                    "rawQueryString": f"?code=valid_code&state={state}",
                    "queryStringParameters": {
                        "code": "valid_code",
                        "state": state,
                    },
                    "headers": {
                        "host": "lambda-url.com",
                    },
                    "requestContext": {
                        "http": {
                            "method": "GET",
                            "path": "/auth/callback",
                        },
                        "requestId": "be4172b1-0ea4-4121-88db-08960adb054f",
                        "timeEpoch": 1725703735416,
                    },
                },
                None,
            )
        self.assertEqual(302, result["statusCode"])
        location = result["headers"]["Location"]
        self.assertEqual(
            "https://example.com",
            location,
        )

    @moto.mock_aws
    @unittest.mock.patch.dict(
        os.environ,
        {"AWS_DEFAULT_REGION": "ap-northeast-1"},
    )
    def test_handler_session(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="dev-s3-session-storage")
        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        user_pool_id, user_pool_domain = self.setup_cognito(
            cognito_idp,
            secretsmanager,
        )

        with unittest.mock.patch.dict(
            os.environ,
            {
                "S3_BUCKET": "dev-s3-session-storage",
                "COGNITO_USER_POOL_ID": user_pool_id,
                "COGNITO_USER_POOL_DOMAIN": user_pool_domain,
                "API_CLIENT_SECRET_ID": "dev/serverless-app/api-client",
            },
        ):
            login_result = auth.handler(
                {
                    "rawPath": "/auth/login",
                    "rawQueryString": "",
                    "headers": {
                        "host": "lambda-url.com",
                    },
                    "requestContext": {
                        "http": {
                            "method": "POST",
                            "path": "/auth/login",
                        },
                        "requestId": "be4172b1-0ea4-4121-88db-08960adb054f",
                        "timeEpoch": 1725703735416,
                    },
                    "body": json.dumps(
                        {
                            "username": "admin@example.com",
                            "password": "P@ssw0rd",
                        }
                    ),
                    "isBase64Encoded": False,
                },
                None,
            )
            cookies = http.cookies.SimpleCookie(
                login_result["headers"]["Set-Cookie"],
            )
            result = auth.handler(
                {
                    "rawPath": "/auth/session",
                    "rawQueryString": "",
                    "headers": {
                        "host": "lambda-url.com",
                        "cookie": cookies.output(header="", sep=";").strip(),
                    },
                    "requestContext": {
                        "http": {
                            "method": "GET",
                            "path": "/auth/session",
                        },
                        "requestId": "be4172b1-0ea4-4121-88db-08960adb054f",
                        "timeEpoch": 1725703735416,
                    },
                    "isBase64Encoded": False,
                },
                None,
            )
        self.assertEqual(200, result["statusCode"])
        res_body = json.loads(result["body"])
        self.assertIsNotNone(res_body["session"]["id_token"])
        self.assertIsNotNone(res_body["session"]["access_token"])


if __name__ == "__main__":
    unittest.main()
