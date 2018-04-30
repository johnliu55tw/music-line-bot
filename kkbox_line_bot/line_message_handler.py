import logging
from itertools import islice
from pprint import pformat


from kkbox_line_bot import app
from kkbox_line_bot import olami

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
    olami_svc = olami.OlamiNliService(app.config['OLAMI_APP_KEY'],
                                      app.config['OLAMI_APP_SECRET'])
    try:
        intent = olami.Intent.from_olami_result(olami_svc(event.message.text))
    except Exception as e:
        logger.exception('Olami service error')
        msg = 'Olami service error: {}'.format(repr(e))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))
        return

    logger.debug('Intent: {}'.format(repr(intent)))

    if intent.action == 'play_song' and 'content' in intent.parameters:
        line_bot_api.reply_message(
                event.reply_token,
                create_tracks_carousel(
                    search_tracks(app.config['KKBOX_ACCESS_TOKEN'],
                                  intent.parameters['content'])))
    else:
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(pformat(intent)))


def search_tracks(token, keyword, limit=10):
    resp = requests.get('https://api.kkbox.com/v1.1/search',
                        headers={'Authorization': 'Bearer ' + token},
                        params={'territory': 'TW',
                                'type': ['track'],
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
