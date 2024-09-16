import http.cookies
import json
import os
import sys
import unittest
import unittest.mock

import boto3
import moto

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import auth


class TestHandler(unittest.TestCase):
    def setup_cognito(self, cognito_idp, secretsmanager):
        user_pool = cognito_idp.create_user_pool(
            PoolName="dev-user-pool",
        )["UserPool"]
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
                }
            ),
        )
        return user_pool["Id"]

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
        user_pool_id = self.setup_cognito(cognito_idp, secretsmanager)

        with unittest.mock.patch.dict(
            os.environ,
            {
                "S3_BUCKET": "dev-s3-session-storage",
                "USER_POOL_ID": user_pool_id,
                "API_CLIENT_SECRET_ID": "dev/serverless-app/api-client",
            },
        ):
            result = auth.handler(
                {
                    "rawPath": "/auth/login",
                    "rawQueryString": "",
                    "headers": {
                        "host": "example.com",
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
    def test_handler_session(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="dev-s3-session-storage")
        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        user_pool_id = self.setup_cognito(cognito_idp, secretsmanager)

        with unittest.mock.patch.dict(
            os.environ,
            {
                "S3_BUCKET": "dev-s3-session-storage",
                "USER_POOL_ID": user_pool_id,
                "API_CLIENT_SECRET_ID": "dev/serverless-app/api-client",
            },
        ):
            login_result = auth.handler(
                {
                    "rawPath": "/auth/login",
                    "rawQueryString": "",
                    "headers": {
                        "host": "example.com",
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
                        "host": "example.com",
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
