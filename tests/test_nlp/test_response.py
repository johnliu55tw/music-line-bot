import unittest

from linebot.models import (
        CarouselColumn,
        URITemplateAction,
        CarouselTemplate,
        TemplateSendMessage,
        TextSendMessage)

from kkbox_line_bot.nlp import response


class ErrorResponseTestCase(unittest.TestCase):

    def test_init(self):
        obj = response.ErrorResponse(response_text='SomeErrorText')

        self.assertIsInstance(obj, response.ErrorResponse)
        self.assertEqual(obj.response_text, 'SomeErrorText')
        self.assertIsNone(obj.status_code)

    def test_init_with_status_code(self):
        obj = response.ErrorResponse(response_text='SomeErrorText', status_code=999)

        self.assertIsInstance(obj, response.ErrorResponse)
        self.assertEqual(obj.response_text, 'SomeErrorText')
        self.assertEqual(obj.status_code, 999)

    def test_as_line_messages(self):
        resp = response.ErrorResponse(response_text='SomeErrorText')

        msgs = resp.as_line_messages()

        self.assertIsInstance(msgs, list)

        self.assertIsInstance(msgs[0], TextSendMessage)
        self.assertEqual(msgs[0].text, 'SomeErrorText')

        self.assertIsInstance(msgs[1], TextSendMessage)
        self.assertEqual(msgs[1].text, 'DEBUG: status_code=None')


class NotImplementedResponseTestCase(unittest.TestCase):

    def test_init(self):
        obj = response.NotImplementedResponse(type='SomeTypeString')

        self.assertIsInstance(obj, response.NotImplementedResponse)

    def test_as_line_messages(self):
        resp = response.NotImplementedResponse(type='SomeTypeString')

        msgs = resp.as_line_messages()

        self.assertIsInstance(msgs, list)

        self.assertIsInstance(msgs[0], TextSendMessage)
        self.assertEqual(msgs[0].text,
                         'SomeTypeString這個功能還沒實作…請洽Line Bot的作者 :D')


class QuestionResponseTestCase(unittest.TestCase):

    def test_init(self):
        obj = response.QuestionResponse(response_text='TheQuestion')

        self.assertIsInstance(obj, response.QuestionResponse)

    def test_as_line_messages(self):
        resp = response.QuestionResponse(response_text='TheQuestion')

        msgs = resp.as_line_messages()

        self.assertIsInstance(msgs, list)
        self.assertEqual(len(msgs), 1)

        self.assertIsInstance(msgs[0], TextSendMessage)
        self.assertEqual(msgs[0].text, 'TheQuestion')


class KKBOXResponseTestCase(unittest.TestCase):

    def setUp(self):
        self.test_data_obj = [
                {'album': '葉惠美',
                 'albumId': 'Gp7hOlzjWop20h4mMz',
                 'artist': '周杰倫 (Jay Chou)',
                 'artistId': 'GtjT_E-Fw6HSCE7jgQ',
                 'id': 'PYki-YuSNHxJvvfWBT',
                 'photo': [
                     {'height': 160,
                      'url': 'https://i.kfs.io/album/tw/23212,0v1/fit/160x160.jpg',
                      'width': 160},
                     {'height': 500,
                      'url': 'https://i.kfs.io/album/tw/23212,0v1/fit/500x500.jpg',
                      'width': 500},
                     {'height': 1000,
                      'url': 'https://i.kfs.io/album/tw/23212,0v1/fit/1000x1000.jpg',
                      'width': 1000}],
                 'time': '269688',
                 'title': '晴天',
                 'url': 'https://event.kkbox.com/content/song/PYki-YuSNHxJvvfWBT'},
                {'album': '11月的蕭邦',
                 'albumId': '0oYr7A00u_GpDyirL3',
                 'artist': '周杰倫 (Jay Chou)',
                 'artistId': 'GtjT_E-Fw6HSCE7jgQ',
                 'id': 'Ksto1lw3fpSTS4Yt_2',
                 'photo': [
                     {'height': 160,
                      'url': 'https://i.kfs.io/album/tw/56062,1v3/fit/160x160.jpg',
                      'width': 160},
                     {'height': 500,
                      'url': 'https://i.kfs.io/album/tw/56062,1v3/fit/500x500.jpg',
                      'width': 500},
                     {'height': 1000,
                      'url': 'https://i.kfs.io/album/tw/56062,1v3/fit/1000x1000.jpg',
                      'width': 1000}],
                 'time': '294138',
                 'title': '一路向北',
                 'url': 'https://event.kkbox.com/content/song/Ksto1lw3fpSTS4Yt_2'}]

    def test_init(self):
        resp = response.KKBOXResponse(response_text='ResponseTextToUser',
                                      data_obj=self.test_data_obj)
        self.assertIsInstance(resp, response.KKBOXResponse)

    def test_init_empty_data_obj(self):
        resp = response.KKBOXResponse(response_text='ResponseTextToUser',
                                      data_obj=None)
        self.assertIsInstance(resp, response.KKBOXResponse)

    def test_get_carousel_columns(self):
        resp = response.KKBOXResponse(response_text='ResponseTextToUser',
                                      data_obj=self.test_data_obj)

        columns = resp._get_carousel_columns()

        self.assertEqual(len(columns), 2)
        self.assertIsInstance(columns[0], CarouselColumn)
        self.assertEqual(columns[0].text, self.test_data_obj[0]['artist'])
        self.assertEqual(columns[0].title, self.test_data_obj[0]['title'])
        self.assertEqual(columns[0].thumbnail_image_url,
                         self.test_data_obj[0]['photo'][1]['url'])
        self.assertEqual(columns[0].actions,
                         [URITemplateAction(label='Open in KKBOX',
                                            uri=self.test_data_obj[0]['url'])])

        self.assertIsInstance(columns[1], CarouselColumn)
        self.assertEqual(columns[1].text, self.test_data_obj[1]['artist'])
        self.assertEqual(columns[1].title, self.test_data_obj[1]['title'])
        self.assertEqual(columns[1].thumbnail_image_url,
                         self.test_data_obj[1]['photo'][1]['url'])
        self.assertEqual(columns[1].actions,
                         [URITemplateAction(label='Open in KKBOX',
                                            uri=self.test_data_obj[1]['url'])])

    def test_as_line_messages(self):
        resp = response.KKBOXResponse(response_text='ResponseTextToUser',
                                      data_obj=self.test_data_obj)

        msgs = resp.as_line_messages()

        self.assertIsInstance(msgs, list)

        self.assertIsInstance(msgs[0], TextSendMessage)
        self.assertEqual(msgs[0].text, 'ResponseTextToUser')

        self.assertIsInstance(msgs[1], TemplateSendMessage)
        self.assertEqual(msgs[1].alt_text, 'KKBOX Result')
        self.assertIsInstance(msgs[1].template, CarouselTemplate)
        self.assertEqual(msgs[1].template.columns,
                         resp._get_carousel_columns())

    def test_as_line_messages_empty_data_obj(self):
        resp = response.KKBOXResponse(response_text='NothingFoundInKKBOX',
                                      data_obj=None)

        msgs = resp.as_line_messages()

        self.assertIsInstance(msgs, list)
        self.assertEqual(len(msgs), 1)

        self.assertIsInstance(msgs[0], TextSendMessage)
        self.assertEqual(msgs[0].text, 'NothingFoundInKKBOX')


class WeatherResponseTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        resp = response.WeatherResponse(response_text='ResponseTextToUser',
                                        data_obj={'whatever': 'not important'})

        self.assertIsInstance(resp, response.WeatherResponse)

    def test_as_line_messages(self):
        resp = response.WeatherResponse(response_text='ResponseTextToUser',
                                        data_obj={'whatever': 'not important'})

        msgs = resp.as_line_messages()

        self.assertIsInstance(msgs, list)
        self.assertEqual(len(msgs), 1)

        self.assertIsInstance(msgs[0], TextSendMessage)
        self.assertEqual(msgs[0].text, 'ResponseTextToUser')
