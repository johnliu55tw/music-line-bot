import unittest
import json

from linebot.models import CarouselColumn, TemplateSendMessage

from kkbox_line_bot import transforms

TRACK_OBJ_JSON_STRING = """
{"album": {"artist": {"id": "5aIlrhCxN9BcJ3RyUw",
    "images": [{"height": 160,
      "url": "https://i.kfs.io/artist/global/9420,0v7/fit/160x160.jpg",
      "width": 160},
     {"height": 300,
      "url": "https://i.kfs.io/artist/global/9420,0v7/fit/300x300.jpg",
      "width": 300}],
    "name": "Linkin Park",
    "url": "https://event.kkbox.com/content/artist/5aIlrhCxN9BcJ3RyUw"},
   "available_territories": ["TW", "HK", "SG", "MY", "JP"],
   "explicitness": true,
   "id": "Gngy2l1HPEfOCrWthG",
   "images": [{"height": 160,
     "url": "https://i.kfs.io/album/global/25695001,0v2/fit/160x160.jpg",
     "width": 160},
    {"height": 500,
     "url": "https://i.kfs.io/album/global/25695001,0v2/fit/500x500.jpg",
     "width": 500},
    {"height": 1000,
     "url": "https://i.kfs.io/album/global/25695001,0v2/fit/1000x1000.jpg",
     "width": 1000}],
   "name": "One More Light",
   "release_date": "2017-05-19",
   "url": "https://event.kkbox.com/content/album/Gngy2l1HPEfOCrWthG"},
  "available_territories": ["TW", "HK", "SG", "MY", "JP"],
  "duration": 216293,
  "explicitness": false,
  "id": "H-ZbmTlKCJ6qw-bCsW",
  "name": "Battle Symphony",
  "track_number": 4,
  "url": "https://event.kkbox.com/content/song/H-ZbmTlKCJ6qw-bCsW"}
"""

ALBUM_OBJ_JSON_STRING = """
{"artist": {"id": "5aIlrhCxN9BcJ3RyUw",
  "images": [{"height": 160,
    "url": "https://i.kfs.io/artist/global/9420,0v7/fit/160x160.jpg",
    "width": 160},
   {"height": 300,
    "url": "https://i.kfs.io/artist/global/9420,0v7/fit/300x300.jpg",
    "width": 300}],
  "name": "Linkin Park",
  "url": "https://event.kkbox.com/content/artist/5aIlrhCxN9BcJ3RyUw"},
 "available_territories": ["TW", "HK", "SG", "MY", "JP"],
 "explicitness": false,
 "id": "OqLKbqfVHgkGio9Tlj",
 "images": [{"height": 160,
   "url": "https://i.kfs.io/album/global/29803237,0v1/fit/160x160.jpg",
   "width": 160},
  {"height": 500,
   "url": "https://i.kfs.io/album/global/29803237,0v1/fit/500x500.jpg",
   "width": 500},
  {"height": 1000,
   "url": "https://i.kfs.io/album/global/29803237,0v1/fit/1000x1000.jpg",
   "width": 1000}],
 "name": "One More Light",
 "release_date": "2017-10-26",
 "url": "https://event.kkbox.com/content/album/OqLKbqfVHgkGio9Tlj"}
"""

PLAYLIST_OBJ_JSON_STRING = """
{"description": "2018-05",
 "id": "WoETD37ZlXeRCerB0q",
 "images": [{"height": 300,
   "url": "https://i.kfs.io/playlist/global/57048866v12/cropresize/300x300.jpg",
   "width": 300},
  {"height": 600,
   "url": "https://i.kfs.io/playlist/global/57048866v12/cropresize/600x600.jpg",
   "width": 600},
  {"height": 1000,
   "url": "https://i.kfs.io/playlist/global/57048866v12/cropresize/1000x1000.jpg",
   "width": 1000}],
 "owner": {"description": "",
  "id": "T-YMdq3gnf6AVbuqgt",
  "images": [{"height": 75,
    "url": "https://i.kfs.io/muser/global/noimg/cropresize/75x75.jpg",
    "width": 75},
   {"height": 180,
    "url": "https://i.kfs.io/muser/global/noimg/cropresize/180x180.jpg",
    "width": 180},
   {"height": 300,
    "url": "https://i.kfs.io/muser/global/noimg/cropresize/300x300.jpg",
    "width": 300}],
  "name": "KKBOX",
  "url": "https://www.kkbox.com/tw/profile/T-YMdq3gnf6AVbuqgt"},
 "title": "Linkin Park vs Jay-Z (聯合公園與傑斯) 歷年精選",
 "updated_at": "2018-05-01T00:21:06+00:00",
 "url": "https://event.kkbox.com/content/playlist/WoETD37ZlXeRCerB0q"}
"""

ARTIST_OBJ_JSON_STRING = """
{"id": "5aIlrhCxN9BcJ3RyUw",
 "images": [{"height": 160,
   "url": "https://i.kfs.io/artist/global/9420,0v7/fit/160x160.jpg",
   "width": 160},
  {"height": 300,
   "url": "https://i.kfs.io/artist/global/9420,0v7/fit/300x300.jpg",
   "width": 300}],
 "name": "Linkin Park",
 "url": "https://event.kkbox.com/content/artist/5aIlrhCxN9BcJ3RyUw"}
"""

TRACK_OBJ = json.loads(TRACK_OBJ_JSON_STRING)
ALBUM_OBJ = json.loads(ALBUM_OBJ_JSON_STRING)
PLAYLIST_OBJ = json.loads(PLAYLIST_OBJ_JSON_STRING)
ARTIST_OBJ = json.loads(ARTIST_OBJ_JSON_STRING)


class KKBOXToLineMessageTestCase(unittest.TestCase):

    def setUp(self):
        self.search_result = {
            'tracks': {'data': [TRACK_OBJ]},
            'albums': {'data': [ALBUM_OBJ]},
            'playlists': {'data': [PLAYLIST_OBJ]},
            'artists': {'data': [ARTIST_OBJ]},
            'other_key_1': {},
            'other_key_2': {}}

    def tearDown(self):
        pass

    def test_kkbox_search_to_line_messages(self):
        messages = transforms.kkbox_search_to_line_messages(
                {'tracks': {'data': [TRACK_OBJ]}})

        self.assertIsInstance(messages, dict)
        self.assertIsInstance(messages['tracks'], TemplateSendMessage)

    def test_kkbox_search_to_line_messages_multiple_results(self):
        messages = transforms.kkbox_search_to_line_messages(self.search_result)

        self.assertIsInstance(messages, dict)
        self.assertIsInstance(messages['tracks'], TemplateSendMessage)
        self.assertIsInstance(messages['albums'], TemplateSendMessage)
        self.assertIsInstance(messages['playlists'], TemplateSendMessage)
        self.assertIsInstance(messages['artists'], TemplateSendMessage)


class CreateCarouselTemplateMessage(unittest.TestCase):

    def setUp(self):
        pass

    def test_create_carousel_template_message(self):
        test_objs = [TRACK_OBJ] * 5

        line_msg = transforms.create_carousel_template_message(test_objs, 'tracks')

        self.assertIsInstance(line_msg, TemplateSendMessage)
        self.assertEqual(len(line_msg.template.columns), 5)

    def test_create_carousel_template_message_limiting(self):
        test_objs = [TRACK_OBJ] * 20

        line_msg = transforms.create_carousel_template_message(test_objs, 'tracks', limit=5)

        self.assertIsInstance(line_msg, TemplateSendMessage)
        self.assertEqual(len(line_msg.template.columns), 5)


class CreateColumnTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_column_track(self):
        result = transforms.create_column(TRACK_OBJ, data_type='tracks')

        self.assertIsInstance(result, CarouselColumn)

        self.assertEqual(result.thumbnail_image_url,
                         TRACK_OBJ['album']['images'][0]['url'])
        self.assertEqual(result.title,
                         TRACK_OBJ['name'])
        self.assertEqual(result.text,
                         TRACK_OBJ['album']['artist']['name'])

        self.assertEqual(len(result.actions), 1)
        self.assertEqual(result.actions[0].label, 'Open in KKBOX')
        self.assertEqual(result.actions[0].uri, TRACK_OBJ['url'])

    def test_create_column_album(self):
        result = transforms.create_column(ALBUM_OBJ, data_type='albums')

        self.assertIsInstance(result, CarouselColumn)

        self.assertEqual(result.thumbnail_image_url,
                         ALBUM_OBJ['images'][0]['url'])
        self.assertEqual(result.title,
                         ALBUM_OBJ['name'])
        self.assertEqual(result.text,
                         ALBUM_OBJ['artist']['name'])

        self.assertEqual(len(result.actions), 1)
        self.assertEqual(result.actions[0].label, 'Open in KKBOX')
        self.assertEqual(result.actions[0].uri, ALBUM_OBJ['url'])

    def test_create_column_playlist(self):
        result = transforms.create_column(PLAYLIST_OBJ, data_type='playlists')

        self.assertIsInstance(result, CarouselColumn)

        self.assertEqual(result.thumbnail_image_url,
                         PLAYLIST_OBJ['images'][0]['url'])
        self.assertEqual(result.title,
                         PLAYLIST_OBJ['title'])
        self.assertEqual(result.text,
                         PLAYLIST_OBJ['owner']['name'])

        self.assertEqual(len(result.actions), 1)
        self.assertEqual(result.actions[0].label, 'Open in KKBOX')
        self.assertEqual(result.actions[0].uri, PLAYLIST_OBJ['url'])

    def test_create_column_artist(self):
        result = transforms.create_column(ARTIST_OBJ, data_type='artists')

        self.assertIsInstance(result, CarouselColumn)

        self.assertEqual(result.thumbnail_image_url,
                         ARTIST_OBJ['images'][0]['url'])
        self.assertEqual(result.title,
                         ARTIST_OBJ['name'])
        self.assertEqual(result.text, 'Singer')

        self.assertEqual(len(result.actions), 1)
        self.assertEqual(result.actions[0].label, 'Open in KKBOX')
        self.assertEqual(result.actions[0].uri, ARTIST_OBJ['url'])

    def test_create_column_oversized_string(self):
        # Create new object from JSON string and modify it
        NEW_TRACK_OBJ = json.loads(TRACK_OBJ_JSON_STRING)
        # title for CarouselColumn
        NEW_TRACK_OBJ['name'] = 'a' * 41
        # text for CarouselColumn
        NEW_TRACK_OBJ['album']['artist']['name'] = 'b' * 61
        result = transforms.create_column(NEW_TRACK_OBJ, data_type='tracks')

        self.assertEqual(len(result.title), 40)
        self.assertEqual(len(result.text), 60)
