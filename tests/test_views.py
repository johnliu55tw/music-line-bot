import unittest

from kkbox_line_bot import app


class ViewsTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        rv = self.client.get('/')
        self.assertEqual(rv.data, 'This is the index page!'.encode('utf-8'))
