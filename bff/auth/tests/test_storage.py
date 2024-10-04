import unittest

import boto3
import moto

import auth.storage


class TestStorage(unittest.TestCase):
    @moto.mock_aws
    def test_save_tokens(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        sut = auth.storage.Storage(s3, "test-bucket")
        sut.save_tokens("request-id", {"tokens": "tokens"})
        ret = sut.get_tokens("request-id")
        self.assertEqual({"tokens": "tokens"}, ret)

    @moto.mock_aws
    def test_delete_tokens(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        sut = auth.storage.Storage(s3, "test-bucket")
        sut.save_tokens("request-id", {"tokens": "tokens"})
        sut.delete_tokens("request-id")
        with self.assertRaises(auth.storage.DataNotFoundException):
            sut.get_tokens("request-id")
        with self.assertRaises(auth.storage.DataNotFoundException):
            sut.delete_tokens("request-id")

    @moto.mock_aws
    def test_save_state(self):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        sut = auth.storage.Storage(s3, "test-bucket")
        sut.save_state("request-id", {"redirect_url": "/"})
        ret = sut.get_state("request-id")
        self.assertEqual({"redirect_url": "/"}, ret)
