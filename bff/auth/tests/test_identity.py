import json
import unittest

import boto3
import moto

import auth.identity


def setup_cognito(cognito_idp, secretsmanager):
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


class TestIdentity(unittest.TestCase):
    @moto.mock_aws
    def test_login(self):
        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        user_pool_id, user_pool_domain = setup_cognito(
            cognito_idp,
            secretsmanager,
        )

        sut = auth.identity.Identity(
            cognito_idp,
            secretsmanager,
            user_pool_id,
            user_pool_domain,
            "dev/serverless-app/api-client",
        )
        tokens = sut.login("admin@example.com", "P@ssw0rd")
        self.assertIsNotNone(tokens["id_token"])

    @moto.mock_aws
    def test_login_when_failed(self):
        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        user_pool_id, user_pool_domain = setup_cognito(
            cognito_idp,
            secretsmanager,
        )

        sut = auth.identity.Identity(
            cognito_idp,
            secretsmanager,
            user_pool_id,
            user_pool_domain,
            "dev/serverless-app/api-client",
        )
        with self.assertRaises(auth.identity.LoginFailedException):
            sut.login("admin@example.com", "invalid_password")

    @moto.mock_aws
    @unittest.mock.patch("requests.post")
    def test_request_tokens_by_code(self, mock_post):
        mock_response = unittest.mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "access_token",
            "id_token": "id_token",
            "refresh_token": "refresh_token",
            "expires_in": 100,
        }

        mock_post.return_value = mock_response

        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        user_pool_id, user_pool_domain = setup_cognito(
            cognito_idp,
            secretsmanager,
        )

        sut = auth.identity.Identity(
            cognito_idp,
            secretsmanager,
            user_pool_id,
            user_pool_domain,
            "dev/serverless-app/api-client",
        )
        tokens = sut.request_tokens_by_code("code")
        self.assertIsNotNone(tokens["id_token"])

    @moto.mock_aws
    def test_refresh_token(self):
        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        user_pool_id, user_pool_domain = setup_cognito(
            cognito_idp,
            secretsmanager,
        )

        sut = auth.identity.Identity(
            cognito_idp,
            secretsmanager,
            user_pool_id,
            user_pool_domain,
            "dev/serverless-app/api-client",
        )
        tokens = sut.login("admin@example.com", "P@ssw0rd")
        tokens_after = sut.refresh_tokens(
            "admin@example.com",
            tokens["refresh_token"],
        )
        self.assertEqual(
            tokens["refresh_token"],
            tokens_after["refresh_token"],
        )

    @moto.mock_aws
    def test_refresh_token_failed(self):
        cognito_idp = boto3.client("cognito-idp")
        secretsmanager = boto3.client("secretsmanager")
        user_pool_id, user_pool_domain = setup_cognito(
            cognito_idp,
            secretsmanager,
        )

        sut = auth.identity.Identity(
            cognito_idp,
            secretsmanager,
            user_pool_id,
            user_pool_domain,
            "dev/serverless-app/api-client",
        )
        tokens = sut.login("admin@example.com", "P@ssw0rd")
        cognito_idp.admin_user_global_sign_out(
            UserPoolId=user_pool_id,
            Username="admin@example.com",
        )
        with self.assertRaises(auth.identity.TokenRefreshFailedException):
            sut.refresh_tokens(
                "admin@example.com",
                tokens["refresh_token"],
            )
