import unittest
import json
import hello


class TestHandler(unittest.TestCase):
    def test_handler(self):
        result = hello.handler({}, None)
        self.assertEqual(json.dumps({"message": "hello, world."}), result["body"])
