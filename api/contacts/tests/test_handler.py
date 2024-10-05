import json
import unittest

import contacts


class TestHandler(unittest.TestCase):
    def test_handler(self):
        result = contacts.handler({}, None)
        self.assertEqual(
            json.dumps({"message": "hello, world."}),
            result["body"],
        )
