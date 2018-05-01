import unittest

from kkbox_line_bot.nlp.intent import Intent


class IntentTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_from_olami_result(self):
        olami_service_response = [
                {'desc_obj': {'status': 0},
                 'semantic': [
                     {'app': 'music',
                      'customer': '5a97f2dfe4b02d92e8136091',
                      'input': '播放七里香',
                      'modifier': ['play_song'],
                      'slots': [{'name': 'content', 'value': '七里香'}]}],
                 'type': 'music'}]

        intent = Intent.from_olami_result(olami_service_response[0])

        self.assertEqual(intent.input, '播放七里香')
        self.assertEqual(intent.response, '')
        self.assertEqual(intent.action, 'play_song')
        self.assertEqual(intent.parameters, {'content': '七里香'})
