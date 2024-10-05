import json
import os
import unittest
import unittest.mock

import contacts


class TestHandler(unittest.TestCase):
    @unittest.skipIf(True, "Reason")
    def test_handler(self):
        with unittest.mock.patch.dict(
            os.environ,
            {
                "AWS_REGION": "ap-northeast-1",
                "DB_HOST": "localhost",
            },
        ):
            result = contacts.handler({}, None)
        self.assertEqual(
            json.dumps({"message": "hello, world."}),
            result["body"],
        )
