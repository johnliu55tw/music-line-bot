import unittest
from unittest import mock

from kkbox_line_bot import kkbox


class KKBOXTestCase(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://api.kkbox.com/v1.1/'
        self.token = 'A_KKBOX_ACCESS_TOKEN'

    def tearDown(self):
        pass

    @mock.patch('kkbox_line_bot.kkbox.requests')
    def test_search(self, m_requests):
        m_requests.get.return_value.status_code = 200
        m_requests.get.return_value.json.return_value = {'SomeJsonKey': 'SomeValue'}

        result = kkbox.search(self.token, 'This is the keyword')

        self.assertEqual(result, {'SomeJsonKey': 'SomeValue'})
        m_requests.get.assert_called_with(self.base_url + 'search',
                                          headers={'Authorization': 'Bearer ' + self.token},
                                          params={'q': 'This is the keyword',
                                                  'territory': 'TW',
                                                  'type': None,
                                                  'limit': None,
                                                  'offset': None})

    @mock.patch('kkbox_line_bot.kkbox.requests')
    def test_search_optional_args(self, m_requests):
        m_requests.get.return_value.status_code = 200
        m_requests.get.return_value.json.return_value = {'SomeJsonKey': 'SomeValue'}

        result = kkbox.search(token=self.token, keyword='This is the keyword',
                              territory='HK',
                              types=['artist', 'track', 'playlist', 'album'],
                              limit=9,
                              offset=12)

        self.assertEqual(result, {'SomeJsonKey': 'SomeValue'})
        m_requests.get.assert_called_with(self.base_url + 'search',
                                          headers={'Authorization': 'Bearer ' + self.token},
                                          params={'q': 'This is the keyword',
                                                  'territory': 'HK',
                                                  'type': 'artist,track,playlist,album',
                                                  'limit': 9,
                                                  'offset': 12})

    def test_search_invalid_arguments(self):
        with self.assertRaisesRegex(ValueError, r"Invalid type: 'some_type'."):
            kkbox.search(self.token, self.base_url + 'search',
                         types=['some_type'])

    @mock.patch('kkbox_line_bot.kkbox.requests')
    def test_search_response_error(self, m_requests):
        m_requests.get.return_value.status_code = 403
        m_requests.get.return_value.json.return_value = {'SomeJsonKey': 'SomeValue'}

        with self.assertRaises(kkbox.Error):
            kkbox.search(self.token, 'This is the keyword')
