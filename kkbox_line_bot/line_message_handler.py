import logging
from itertools import islice


from kkbox_line_bot import app
from kkbox_line_bot.nlp import olami
from kkbox_line_bot.nlp import Error as NlpError
from kkbox_line_bot.nlp.intent import PlayMusicIntent
from kkbox_line_bot import kkbox

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import TemplateSendMessage, CarouselTemplate, CarouselColumn, URITemplateAction

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
        result_obj = kkbox.search(app.config['KKBOX_ACCESS_TOKEN'],
                                  intent.parameters['keywords'],
                                  types=intent.parameters['type'],
                                  limit=10)
        result_data = result_obj[intent.parameters['type']+'s']
        carousels = create_carousel(result_data, intent.parameters['type'])
        try:
            line_bot_api.reply_message(event.reply_token, carousels)
        except Exception as e:
            logging.error('Line reply error. Detail: {}'.format(e.error))
    else:
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage('Unsupported intent: {}'.format(intent)))


def create_carousel(objs, content_type, limit=10):
    columns = [create_column(obj, content_type) for obj in islice(objs, limit)]
    return TemplateSendMessage(alt_text='KKBOX result list',
                               template=CarouselTemplate(columns,
                                                         image_aspect_ratio='square'))


def create_column(obj, content_type):
    def reduce_string_length(s, size):
        return s[:size-1] + '…' if len(s) > size else s

    if content_type == 'track':
        image_url = obj['album']['images'][0]['url']
        title = obj['name']
        text = obj['album']['artist']['name']
        actions = [URITemplateAction(label='Open in KKBOX', uri=obj['url'])]

    elif content_type == 'album':
        image_url = obj['images'][0]['url']
        title = obj['name']
        text = obj['artist']['name']
        actions = [URITemplateAction(label='Open in KKBOX', uri=obj['url'])]

    elif content_type == 'artist':
        image_url = obj['images'][0]['url']
        title = obj['name']
        text = 'Singer'
        actions = [URITemplateAction(label='Open in KKBOX', uri=obj['url'])]
    elif content_type == 'playlist':
        image_url = obj['images'][0]['url']
        title = obj['title']
        text = obj['owner']['name']
        actions = [URITemplateAction(label='Open in KKBOX', uri=obj['url'])]
    # The length of title and text is limited by the Line Message API
    return CarouselColumn(thumbnail_image_url=image_url,
                          title=reduce_string_length(title, 40),
                          text=reduce_string_length(text, 60),
                          actions=actions)
