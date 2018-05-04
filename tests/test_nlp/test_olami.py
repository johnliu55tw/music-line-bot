import unittest
from unittest import mock
import json

from kkbox_line_bot.nlp import olami
from kkbox_line_bot.nlp import intent


class OlamiServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.app_key = '012345abcdef012345abcdef01234567'
        self.app_secret = '987654abcdef987654abcdef98765432'
        self.timestamp = 1525059761.962699

    def test_invalid_input_type(self):
        # Invalid input_type argument
        with self.assertRaisesRegex(ValueError, r'Invalid input_type.*'):
            olami.OlamiService(self.app_key, self.app_secret, input_type=2)

    def test_gen_sign(self):
        svc = olami.OlamiService(self.app_key, self.app_secret)
        sign = svc._gen_sign('seq', timestamp=1492099200.0)

        self.assertEqual(sign, '7d80ae313ae5e0358e725e40d1773214')

    @mock.patch('kkbox_line_bot.nlp.olami.time')
    def test_gen_sign_without_given_ts(self, m_time):
        m_time.time.return_value = self.timestamp

        svc = olami.OlamiService(self.app_key, self.app_secret)
        sign_no_given_ts = svc._gen_sign('seq')
        sign_given_ts = svc._gen_sign('seq', timestamp=self.timestamp)

        self.assertEqual(sign_no_given_ts, sign_given_ts)

    def test_gen_rq(self):
        svc = olami.OlamiService(self.app_key, self.app_secret)
        rq = svc._gen_rq('ThisIsTestText')
        self.assertEqual(rq,
                         {'data_type': 'stt',
                             'data': {
                                 'input_type': 1,
                                 'text': 'ThisIsTestText'}})

    def test_gen_rq_input_type(self):
        svc = olami.OlamiService(self.app_key, self.app_secret, input_type=0)
        rq = svc._gen_rq('ThisIsTestText')
        self.assertEqual(rq,
                         {'data_type': 'stt',
                             'data': {
                                 'input_type': 0,
                                 'text': 'ThisIsTestText'}})

    def test_gen_rq_as_text(self):
        svc = olami.OlamiService(self.app_key, self.app_secret)
        rq = svc._gen_rq('ThisIsTestText', as_text=True)
        self.assertEqual(rq,
                         json.dumps({'data_type': 'stt',
                                     'data': {
                                         'input_type': 1,
                                         'text': 'ThisIsTestText'}}))

    @mock.patch('kkbox_line_bot.nlp.olami.time')
    def test_gen_parameters(self, m_time):
        m_time.time.return_value = self.timestamp

        svc = olami.OlamiService(self.app_key, self.app_secret)
        params = svc._gen_parameters('TextForNli')
        self.assertEqual(params,
                         {'appkey': self.app_key,
                          'api': 'nli',
                          'timestamp': int(self.timestamp*1000),
                          'sign': svc._gen_sign('nli'),
                          'rq': svc._gen_rq('TextForNli', as_text=True)})

    @mock.patch('kkbox_line_bot.nlp.olami.time')
    def test_gen_parameters_with_cusid(self, m_time):
        m_time.time.return_value = self.timestamp

        svc = olami.OlamiService(self.app_key, self.app_secret, cusid='TheCusid')
        params = svc._gen_parameters('TextForNli')
        self.assertEqual(params,
                         {'appkey': self.app_key,
                          'api': 'nli',
                          'timestamp': int(self.timestamp*1000),
                          'sign': svc._gen_sign('nli'),
                          'cusid': 'TheCusid',
                          'rq': svc._gen_rq('TextForNli', as_text=True)})

    @mock.patch('kkbox_line_bot.nlp.olami.requests')
    @mock.patch('kkbox_line_bot.nlp.olami.time')
    def test_call(self, m_time, m_requests):
        m_time.time.return_value = self.timestamp
        m_requests.post.return_value.json.return_value = {'data': {'nli': 'NliResult'},
                                                          'status': 'ok'}

        svc = olami.OlamiService(self.app_key, self.app_secret)
        result = svc('TextForNli')

        self.assertEqual(result, 'NliResult')
        m_requests.post.assert_called_with(olami.OlamiService.BASE_URL,
                                           params=svc._gen_parameters('TextForNli'))

    @mock.patch('kkbox_line_bot.nlp.olami.requests')
    @mock.patch('kkbox_line_bot.nlp.olami.time')
    def test_call_nli_response_error(self, m_time, m_requests):
        m_time.time.return_value = self.timestamp
        m_requests.post.return_value.json.return_value = {'data': 'SomeData',
                                                          'status': 'error'}

        svc = olami.OlamiService(self.app_key, self.app_secret)
        with self.assertRaisesRegex(olami.NliStatusError, r"NLI responded status != 'ok':.*"):
            svc('TextForNli')


class IntentFromOlamiResponseTestCase(unittest.TestCase):

    def test_intent_from_response(self):
        olami_service_response = [
                        {'desc_obj': {'status': 0},
                         'semantic': [
                             {'app': 'music',
                              'customer': '5a97f2dfe4b02d92e8136091',
                              'input': '播放七里香',
                              'modifier': ['play_song'],
                              'slots': [{'name': 'content', 'value': '七里香'}]}],
                         'type': 'music'}]
        result_intent = olami.intent_from_response(olami_service_response)

        self.assertIsInstance(result_intent, intent.PlayMusicIntent)
        self.assertEqual(result_intent.input, '播放七里香')
        self.assertEqual(result_intent.response, '')
        self.assertEqual(result_intent.parameters,
                         {'type': 'track', 'keywords': ['七里香']})

    def test_intent_from_response_invalid(self):
        olami_service_response = [
                        {'desc_obj': {'status': 1},
                         'semantic': [
                             {'app': 'music',
                              'customer': '5a97f2dfe4b02d92e8136091',
                              'input': '播放七里香',
                              'modifier': ['play_song'],
                              'slots': [{'name': 'content', 'value': '七里香'}]}],
                         'type': 'music'}]
        with self.assertRaises(olami.InvalidIntent) as cm:
            olami.intent_from_response(olami_service_response)
        self.assertEqual(cm.exception.status, 1)
        self.assertEqual(cm.exception.response, 'Empty response!')

    def test_intent_from_response_invalid_status_1003(self):
        olami_service_response = [
                        {'desc_obj': {'status': 1003,
                                      'result': 'Result string of status 1003'},
                         'semantic': [
                             {'app': 'music',
                              'customer': '5a97f2dfe4b02d92e8136091',
                              'input': '播放七里香',
                              'modifier': ['play_song'],
                              'slots': [{'name': 'content', 'value': '七里香'}]}],
                         'type': 'music'}]
        with self.assertRaises(olami.InvalidIntent) as cm:
            olami.intent_from_response(olami_service_response)
        self.assertEqual(cm.exception.status, 1003)
        self.assertEqual(cm.exception.response, 'Result string of status 1003')
