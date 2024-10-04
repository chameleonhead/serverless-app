import json

import botocore.exceptions


class DataNotFoundException(Exception):
    pass


class Storage(object):
    def __init__(self, s3, bucket: str):
        self.__s3 = s3
        self.__bucket = bucket

    def save_tokens(self, session_id: str, data: dict):
        self.__s3.put_object(
            Bucket=self.__bucket,
            Key=f"sessions/{session_id}/tokens.json",
            Body=json.dumps(data).encode(),
        )

    def get_tokens(self, session_id: str) -> dict:
        try:
            res = self.__s3.get_object(
                Bucket=self.__bucket,
                Key=f"sessions/{session_id}/tokens.json",
            )
            return json.loads(res["Body"].read())
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] in ["404", "NoSuchKey"]:
                raise DataNotFoundException()
            raise Exception(e) from e

    def delete_tokens(self, session_id: str):
        try:
            self.__s3.head_object(
                Bucket=self.__bucket,
                Key=f"sessions/{session_id}/tokens.json",
            )
            self.__s3.delete_object(
                Bucket=self.__bucket,
                Key=f"sessions/{session_id}/tokens.json",
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] in ["404", "NoSuchKey"]:
                raise DataNotFoundException()
            raise Exception(e) from e

    def save_state(self, request_id: str, data: dict):
        self.__s3.put_object(
            Bucket=self.__bucket,
            Key=f"oauth2/{request_id}/state.json",
            Body=json.dumps(data).encode(),
        )

    def get_state(self, request_id: str) -> dict:
        try:
            res = self.__s3.get_object(
                Bucket=self.__bucket,
                Key=f"oauth2/{request_id}/state.json",
            )
            return json.loads(res["Body"].read())
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] in ["404", "NoSuchKey"]:
                raise DataNotFoundException()
            raise Exception(e) from e
