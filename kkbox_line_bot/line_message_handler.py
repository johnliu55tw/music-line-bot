import logging


from kkbox_line_bot import app
from kkbox_line_bot.nlp import olami
from kkbox_line_bot.nlp import Error as NlpError
from kkbox_line_bot.nlp.intent import PlayMusicIntent
from kkbox_line_bot import kkbox
from kkbox_line_bot import transforms

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

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
        search_result = kkbox.search(app.config['KKBOX_ACCESS_TOKEN'],
                                     intent.parameters['keywords'],
                                     types=intent.parameters['type'],
                                     limit=10)
        messages = transforms.kkbox_search_to_line_messages(search_result)
        logger.debug('Line messages type: {}'.format(list(messages.keys())))

        try:
            line_bot_api.reply_message(event.reply_token,
                                       list(messages.values()))
        except Exception as e:
            logging.error('Line reply error. Detail: {}'.format(e.error))
    else:
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage('Unsupported intent: {}'.format(intent)))
