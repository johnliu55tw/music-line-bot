import unittest

from kkbox_line_bot.nlp import intent


class MusicIntentTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        music_intent = intent.PlayMusicIntent('SomeInputText',
                                              'SomeResponseText',
                                              {'param1_name': 'param1_value',
                                               'param2_name': 'param2_value'})
        self.assertIsInstance(music_intent, intent.PlayMusicIntent)
