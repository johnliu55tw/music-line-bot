import unittest
from unittest import mock
from os import urandom
from time import time
import json
import hmac
import hashlib
import base64

from kkbox_line_bot import app

from kkbox_line_bot import line_message_handler


def build_line_webhook_text_message_event(reply_token, user_id, msg_id, text, timestamp):
    return {'replyToken': reply_token,
            'type': 'message',
            'timestamp': timestamp,
            'source': {
                'type': 'user',
                'userId': user_id},
            'message': {
                'id': msg_id,
                'type': 'text',
                'text': text}}


def build_webhook_body(*event):
    return json.dumps({'events': list(event)})


def gen_signature(channel_secret, body):
    sig_bin = hmac.new(channel_secret, body.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(sig_bin).decode('utf-8')


class WebhookHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.reply_token = urandom(10).hex()
        self.user_id = urandom(6).hex()
        self.msg_id = urandom(10).hex()
        self.timestamp = int(time() * 1000)

    def tearDown(self):
        pass

    @mock.patch('kkbox_line_bot.line_message_handler.line_bot_api')
    @mock.patch('kkbox_line_bot.line_message_handler.transforms')
    @mock.patch('kkbox_line_bot.line_message_handler.olami')
    def test_intent_normal_processing_flow(self, m_olami, m_transforms, m_line_bot_api):
        m_olami_svc = m_olami.OlamiService.return_value
        text_msg_event = build_line_webhook_text_message_event(
                self.reply_token,
                self.user_id,
                self.msg_id,
                'TestWebhookMessage',
                self.timestamp)
        webhook_body = build_webhook_body(text_msg_event)
        webhook_signature = gen_signature(
                app.config['LINE_CHANNEL_SECRET'].encode('utf-8'),
                webhook_body)

        line_message_handler.webhook_handler.handle(body=webhook_body,
                                                    signature=webhook_signature)

        m_olami.OlamiService.assert_called_with(app.config['OLAMI_APP_KEY'],
                                                app.config['OLAMI_APP_SECRET'])
        m_olami_svc.assert_called_with('TestWebhookMessage')
        m_olami.intent_from_response.assert_called_with(m_olami_svc.return_value)

        m_transforms.intent_to_line_messages.assert_called_with(
                m_olami.intent_from_response.return_value)

        m_line_bot_api.reply_message.assert_called_with(
                self.reply_token,
                m_transforms.intent_to_line_messages.return_value)
