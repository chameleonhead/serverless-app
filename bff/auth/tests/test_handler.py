import json
import os
import unittest
import unittest.mock

import auth
import boto3
import moto


class TestHandler(unittest.TestCase):
    @moto.mock_aws
    def test_handler_login(self):
        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        create_user_pool_response = cognito_idp.create_user_pool(
            PoolName="dev-user-pool"
        )
        user_pool = create_user_pool_response["UserPool"]
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
        create_user_pool_client_response = cognito_idp.create_user_pool_client(
            UserPoolId=user_pool["Id"],
            ClientName="dev-user-pool-client",
            GenerateSecret=True,
        )
        user_pool_client = create_user_pool_client_response["UserPoolClient"]
        secretsmanager.create_secret(
            Name="dev/serverless-app/api-client",
            SecretString=json.dumps(
                {
                    "client_id": user_pool_client["ClientId"],
                    "client_secret": user_pool_client["ClientSecret"],
                }
            ),
        )

        with unittest.mock.patch.dict(
            os.environ,
            {
                "USER_POOL_ID": user_pool["Id"],
                "API_CLIENT_SECRET_ID": "dev/serverless-app/api-client",
            },
        ):
            result = auth.handler(
                {
                    "rawPath": "/auth/auth/login",
                    "rawQueryString": "",
                    "headers": {
                        "host": "example.com",
                    },
                    "requestContext": {
                        "http": {
                            "method": "GET",
                            "path": "/auth/auth/login",
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
        self.assertEqual(
            {"message": "hello, world."},
            json.loads(result["body"]),
        )


if __name__ == "__main__":
    unittest.main()
