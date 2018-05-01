import logging
from itertools import islice
from pprint import pformat


from kkbox_line_bot import app
from kkbox_line_bot.nlp import olami
from kkbox_line_bot.nlp import Error as NlpError
from kkbox_line_bot.nlp.intent import PlayMusicIntent

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import TemplateSendMessage, CarouselTemplate, CarouselColumn, URITemplateAction

import requests

logger = logging.getLogger(__name__)

line_bot_api = LineBotApi(app.config['LINE_CHANNEL_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(app.config['LINE_CHANNEL_SECRET'])


@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    logger.debug('event: ' + str(event))
    olami_svc = olami.OlamiService(app.config['OLAMI_APP_KEY'],
                                   app.config['OLAMI_APP_SECRET'])
    try:
        intent = olami.intent_from_response(olami_svc(event.message.text))
    except NlpError as e:
        msg = 'NLP service error: {}'.format(repr(e))
        logger.error(msg)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))
        return
    except Exception as e:
        logger.exception('Unexpected error')
        msg = 'Unexpected error: {}'.format(repr(e))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))
        return

    logger.debug('Got Intent: {}'.format(repr(intent)))

    if isinstance(intent, PlayMusicIntent):
        line_bot_api.reply_message(
                event.reply_token,
                create_tracks_carousel(
                    search_tracks(app.config['KKBOX_ACCESS_TOKEN'],
                                  intent.parameters['type'],
                                  intent.parameters['keywords'])))
    else:
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(pformat(intent)))


def search_tracks(token, search_type, keyword, limit=10):
    resp = requests.get('https://api.kkbox.com/v1.1/search',
                        headers={'Authorization': 'Bearer ' + token},
                        params={'territory': 'TW',
                                'type': [search_type],
                                'limit': limit,
                                'q': keyword})
    resp.raise_for_status()
    return resp.json()['tracks']['data']


def create_tracks_carousel(tracks, limit=10):
    columns = list()
    for track in islice(tracks, limit):
        artist_name = track['album']['artist']['name']
        track_name = track['name']
        image_url = track['album']['images'][0]['url']
        event_url = track['url']

        column = CarouselColumn(thumbnail_image_url=image_url,
                                title=track_name,
                                text=artist_name,
                                actions=[URITemplateAction(label='Open in KKBOX',
                                                           uri=event_url)])

        columns.append(column)

    return TemplateSendMessage(alt_text='Tracks list',
                               template=CarouselTemplate(columns))
