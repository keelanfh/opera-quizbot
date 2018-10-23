import json
import unittest

from django.test import Client


class IncomingTextMessageTest(unittest.TestCase):
    """Test an incoming text message."""

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        body = {"object": "page", "entry": [{"id": "2007846762763519", "time": 1510077859680, "messaging":
            [{"sender": {"id": "1360874744034438"},
              "recipient": {"id": "2007846762763519"},
              "timestamp": 1510077858550,
              "message": {"mid": "mid.$cAAd4023jHCZlyOzK9lfl6eCtlLp7",
                          "seq": 200932, "text": "Testing äscii"}}]}]}

        response = self.client.post('/webhook', data=json.dumps(body),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)


class IncomingThumbsUpMessageTest(unittest.TestCase):
    """Test an incoming thumbs-up message."""

    def setUp(self):
        self.client = Client()

    def test_details(self):
        body = {"object": "page", "entry": [{"id": "700740276789359", "time": 1510310603147, "messaging": [
            {"sender": {"id": "1360874744034438"}, "recipient": {"id": "700740276789359"}, "timestamp": 1510310602633,
             "message": {"mid": "mid.$cAAInouOq6LZl1swviVfpYbm8QZDA", "seq": 201820, "sticker_id": 369239263222822,
                         "attachments": [{"type": "image", "payload": {
                             "url": "https:\/\/scontent.xx.fbcdn.net\/v\/t39.1997-6\/851557_369239266556155_759568595_n.png?_nc_ad=z-m&_nc_cid=0&oh=9058fb52f628d0a6ab92f85ea310db0a&oe=5A9DAADC",
                             "sticker_id": 369239263222822}}]}}]}]}

        headers = {"X-Hub-Signature": "sha1=0dba7e22dd04f2757fc10ca42e390aca872f6066"}

        response = self.client.post('/webhook', data=json.dumps(body),
                                    content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)


class IncomingStickerMessageTest(unittest.TestCase):
    """Test an incoming sticker."""

    def setUp(self):
        self.client = Client()

    def test_details(self):
        body = {"object": "page", "entry":
            [{"id": "7007402˚76789359", "time": 1510310857131, "messaging": [
                {"sender": {"id": "1360874744034438"},
                 "recipient": {"id": "700740276789359"},
                 "timestamp": 1510310856616,
                 "message": {"mid": "mid.$cAAInouOq6LZl1tAPqFfpYrHKxxTx",
                             "seq": 201823, "sticker_id": 144885035685763,
                             "attachments": [{"type": "image", "payload": {
                                 "url": "https:\/\/scontent.xx.fbcdn.net\/v\/t39.1997-6\/p100x100\/851539_272698496237749_786804483_n.png?_nc_ad=z-m&_nc_cid=0&oh=37129cedb1081f6fb8e60dd5cacce1b6&oe=5A67CCCB",
                                 "sticker_id": 144885035685763}}]}}]}]}

        headers = {"X-Hub-Signature": "sha1=3cf43a7933d8d5423823dbc831c971c465d68987"}

        response = self.client.post('/webhook', data=json.dumps(body),
                                    content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)


class IncomingNoMessageTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        body = {
            "entry": [
                {
                    "time": 1511967492,
                    "id": "0",
                    "changed_fields": [
                        "locale"
                    ],
                    "uid": "0"
                }
            ],
            "object": "user"
        }
        headers = {"X-Hub-Signature": "sha1=a7d25de5ccd1a98a4c2473e6d7ecf4c80df06d5b"}
        response = self.client.post('/webhook', data=json.dumps(body),
                                    content_type='application/json', headers=headers)

        self.assertEqual(response.status_code, 200)
