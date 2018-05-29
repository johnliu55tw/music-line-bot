import unittest
from unittest import mock
import json

from kkbox_line_bot.nlp import olami, response
from kkbox_line_bot.nlp.error import NlpServiceError


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
    def test_make_request(self, m_time, m_requests):
        m_time.time.return_value = self.timestamp
        m_requests.post.return_value.status_code = 200
        m_requests.post.return_value.json.return_value = {'data': {'nli': 'NliResult'},
                                                          'status': 'ok'}

        svc = olami.OlamiService(self.app_key, self.app_secret)
        result = svc._make_request('TextForNli')

        self.assertEqual(result, 'NliResult')
        m_requests.post.assert_called_with(olami.OlamiService.BASE_URL,
                                           params=svc._gen_parameters('TextForNli'))

    @mock.patch('kkbox_line_bot.nlp.olami.requests')
    @mock.patch('kkbox_line_bot.nlp.olami.time')
    def test_make_request_http_status_error(self, m_time, m_requests):
        m_time.time.return_value = self.timestamp
        m_requests.post.return_value.status_code = 400
        m_requests.post.return_value.json.return_value = {'data': 'SomeData',
                                                          'status': 'whatever'}

        svc = olami.OlamiService(self.app_key, self.app_secret)
        with self.assertRaisesRegex(NlpServiceError, r"HTTP Response != 200:.*"):
            svc._make_request('TextForNli')

    @mock.patch('kkbox_line_bot.nlp.olami.requests')
    @mock.patch('kkbox_line_bot.nlp.olami.time')
    def test_make_request_nli_response_error(self, m_time, m_requests):
        m_time.time.return_value = self.timestamp
        m_requests.post.return_value.status_code = 200
        m_requests.post.return_value.json.return_value = {'data': 'SomeData',
                                                          'status': 'error'}

        svc = olami.OlamiService(self.app_key, self.app_secret)
        with self.assertRaisesRegex(NlpServiceError, r"NLI responded status != 'ok':.*"):
            svc._make_request('TextForNli')


class OlamiResponseFactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.olami_error_timeout_resp = [
                {'desc_obj': {'result': '我需要多一點時間來處理。', 'status': 3001},
                 'type': 'ds'}]

        self.olami_error_no_match_resp = [
                {'desc_obj': {'result': '對不起，你說的我還不懂，能換個說法嗎？', 'status': '1003'},
                 'type': 'ds'}]

        self.olami_question_resp = [
                {'desc_obj':
                    {'result': '主人，請問你想查哪裡的天氣呢？',
                     'type': 'weather',
                     'status': '0'},
                 'type': 'question'}]

        self.olami_kkbox_resp = [
            {'desc_obj': {'result': '馬上為你播放。', 'type': '', 'status': 0},
             'data_obj': [
                 {'artist': '周杰倫 (Jay Chou)',
                  'album': '周杰倫【天臺】電影原聲帶',
                  'photo': [
                      {'width': 160,
                       'url': 'https://i.kfs.io/album/tw/1517099,1v4/fit/160x160.jpg',
                       'height': 160},
                      {'width': 500,
                       'url': 'https://i.kfs.io/album/tw/1517099,1v4/fit/500x500.jpg',
                       'height': 500},
                      {'width': 1000,
                       'url': 'https://i.kfs.io/album/tw/1517099,1v4/fit/1000x1000.jpg',
                       'height': 1000}],
                  'albumId': 'CmPJwq4WAc3pyKUZUF',
                  'artistId': 'GtjT_E-Fw6HSCE7jgQ',
                  'id': 'HZ3bslJyEYKfkWmogJ',
                  'time': '81154',
                  'title': '錢難賺',
                  'url': 'https://event.kkbox.com/content/song/HZ3bslJyEYKfkWmogJ'},
                 {'artist': '周杰倫 (Jay Chou)',
                  'album': '十二新作',
                  'photo': [
                      {'width': 160,
                       'url': 'https://i.kfs.io/album/tw/525523,1v3/fit/160x160.jpg',
                       'height': 160},
                      {'width': 500,
                       'url': 'https://i.kfs.io/album/tw/525523,1v3/fit/500x500.jpg',
                       'height': 500},
                      {'width': 1000,
                       'url': 'https://i.kfs.io/album/tw/525523,1v3/fit/1000x1000.jpg',
                       'height': 1000}],
                  'albumId': '9YMqiF0HpTG8IZrErD',
                  'artistId': 'GtjT_E-Fw6HSCE7jgQ',
                  'id': 'GqU6TvAvHxj7MfaCBo',
                  'time': '242834',
                  'title': '大笨鐘',
                  'url': 'https://event.kkbox.com/content/song/GqU6TvAvHxj7MfaCBo'}],
             'type': 'kkbox'}]

        self.olami_kkbox_no_result_resp = [
                {'desc_obj': {'result': '很抱歉，沒有找到你要的結果。', 'type': '', 'status': 0},
                 'type': 'kkbox'}]

        self.not_implemented_resp = [
                {'desc_obj': {'result': 'This is a weird response that has not been implemented.',
                              'type': 'weird_stuff',
                              'status': '0'},
                 'type': 'some_weird_type'}]

        self.olami_weather_resp = [
                {'desc_obj':
                    {'result': '台北今天晴中雨，最高溫度30.4℃，最低溫度26.1℃，東北東風軟風。',
                     'status': 0},
                 'type': 'weather',
                 'data_obj': [
                     {'date': 0,
                      'weather_end': 0,
                      'pm25': 0,
                      'city': '台北',
                      'temperature_low': '26.1',
                      'weather_start': 0,
                      'temperature_high': '30.4',
                      'description': '2018年05月29日,晴中雨,東北東風軟風,最高溫度30.4℃,最低溫度26.1℃。',
                      'is_querying': 1,
                      'real_date': 1527523200000,
                      'wind': '東北東風軟風'},
                     {'date': 1,
                      'weather_end': 0,
                      'pm25': 0,
                      'city': '台北',
                      'temperature_low': '25.7',
                      'weather_start': 0,
                      'temperature_high': '28.5',
                      'description': '2018年05月30日,晴，少雲中雨,西南西風無風,最高溫度28.5℃,最低溫度25.7℃。',
                      'is_querying': 0,
                      'real_date': 1527609600000,
                      'wind': '西南西風無風'},
                     {'date': 2,
                      'weather_end': 0,
                      'pm25': 0,
                      'city': '台北',
                      'temperature_low': '24.6',
                      'weather_start': 0,
                      'temperature_high': '29.4',
                      'description': '2018年05月31日,多雲大雨,南南東風軟風,最高溫度29.4℃,最低溫度24.6℃。',
                      'is_querying': 0,
                      'real_date': 1527696000000,
                      'wind': '南南東風軟風'},
                     {'date': 3,
                      'weather_end': 0,
                      'pm25': 0,
                      'city': '台北',
                      'temperature_low': '24.7',
                      'weather_start': 0,
                      'temperature_high': '25.6',
                      'description': '2018年06月01日,多雲大雨,東北東風微風,最高溫度25.6℃,最低溫度24.7℃。',
                      'is_querying': 0,
                      'real_date': 1527782400000,
                      'wind': '東北東風微風'},
                     {'date': 4,
                      'weather_end': 0,
                      'pm25': 0,
                      'city': '台北',
                      'temperature_low': '24.5',
                      'weather_start': 0,
                      'temperature_high': '24.8',
                      'description': '2018年06月02日,陰，多雲大雨,北北東風微風,最高溫度24.8℃,最低溫度24.5℃。',
                      'is_querying': 0,
                      'real_date': 1527868800000,
                      'wind': '北北東風微風'}]}]

    def test_error_timeout_resp(self):
        nlp_resp = olami.response_factory(self.olami_error_timeout_resp)

        self.assertIsInstance(nlp_resp, response.ErrorResponse)
        self.assertEqual(nlp_resp.response_text,
                         self.olami_error_timeout_resp[0]['desc_obj']['result'])

    def test_error_no_match_resp(self):
        nlp_resp = olami.response_factory(self.olami_error_no_match_resp)

        self.assertIsInstance(nlp_resp, response.ErrorResponse)
        self.assertEqual(nlp_resp.response_text,
                         self.olami_error_no_match_resp[0]['desc_obj']['result'])

    def test_question_resp(self):
        nlp_resp = olami.response_factory(self.olami_question_resp)

        self.assertIsInstance(nlp_resp, response.QuestionResponse)
        self.assertEqual(nlp_resp.response_text,
                         self.olami_question_resp[0]['desc_obj']['result'])

    def test_kkbox_resp(self):
        nlp_resp = olami.response_factory(self.olami_kkbox_resp)

        self.assertIsInstance(nlp_resp, response.KKBOXResponse)

        self.assertEqual(nlp_resp.response_text, self.olami_kkbox_resp[0]['desc_obj']['result'])
        self.assertEqual(nlp_resp.data_obj, self.olami_kkbox_resp[0]['data_obj'])

    def test_kkbox_no_result_resp(self):
        nlp_resp = olami.response_factory(self.olami_kkbox_no_result_resp)

        self.assertIsInstance(nlp_resp, response.KKBOXResponse)

        self.assertEqual(nlp_resp.response_text,
                         self.olami_kkbox_no_result_resp[0]['desc_obj']['result'])
        self.assertEqual(nlp_resp.data_obj, None)

    def test_weather_resp(self):
        nlp_resp = olami.response_factory(self.olami_weather_resp)

        self.assertIsInstance(nlp_resp, response.WeatherResponse)

        self.assertEqual(nlp_resp.response_text, self.olami_weather_resp[0]['desc_obj']['result'])

    def test_not_implemented_resp(self):
        nlp_resp = olami.response_factory(self.not_implemented_resp)

        self.assertIsInstance(nlp_resp, response.NotImplementedResponse)
