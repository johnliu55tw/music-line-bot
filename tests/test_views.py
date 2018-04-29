import unittest
from unittest import mock

from kkbox_line_bot import app


class IndexTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        rv = self.client.get('/')
        self.assertEqual(rv.data, 'This is the index page!'.encode('utf-8'))


class MessageTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    @mock.patch('kkbox_line_bot.views.webhook_handler')
    def test_unavailable_methods(self, m_webhook_handler):
        rv = self.client.get('/message')
        self.assertEqual(rv.status_code, 405)
        rv = self.client.patch('/message')
        self.assertEqual(rv.status_code, 405)
        rv = self.client.delete('/message')
        self.assertEqual(rv.status_code, 405)

    @mock.patch('kkbox_line_bot.views.webhook_handler')
    def test_post(self, m_webhook_handler):
        rv = self.client.post('/message',
                              headers={'X-Line-Signature': 'TestSignature'},
                              data='TheBodyData')
        self.assertEqual(rv.status_code, 200)
        m_webhook_handler.handle.assert_called_with('TheBodyData', 'TestSignature')
