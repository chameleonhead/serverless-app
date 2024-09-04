import json
import unittest

import auth


class TestHandler(unittest.TestCase):
    def test_handler(self):
        result = auth.handler({}, None)
        self.assertEqual(
            json.dumps({"message": "hello, world."}),
            result["body"],
        )
