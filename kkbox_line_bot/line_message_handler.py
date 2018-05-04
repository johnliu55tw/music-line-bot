import logging


from kkbox_line_bot import app
from kkbox_line_bot.nlp import olami
from kkbox_line_bot.nlp.error import NlpFailed
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
    except NlpFailed as e:
        msg = 'NLP service failed to deduce intent: {}'.format(repr(NlpFailed))
        logger.error(msg)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=e.response))
        return
    except Exception as e:
        logger.exception('Unexpected error')
        msg = 'Unexpected error: {}'.format(repr(e))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))
        return

    logger.debug('Got Intent: {}'.format(repr(intent)))
    try:
        reply_messages = transforms.intent_to_line_messages(intent)
    except transforms.UnsupportedIntent as e:
        reply_messages = TextSendMessage('Unsupported intent: {}'.format(e))
    except Exception as e:
        msg = 'Unable to transform intent to line messages: {}'.format(str(e))
        logger.error(msg)
        reply_messages = TextSendMessage(msg)
    finally:
        logger.info('Reply: {}'.format(reply_messages))
        line_bot_api.reply_message(event.reply_token, reply_messages)
