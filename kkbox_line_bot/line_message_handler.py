import logging


from kkbox_line_bot import app
from kkbox_line_bot.nlp import olami
from kkbox_line_bot.nlp.error import NlpServiceError

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
        resp = olami_svc(event.message.text)
        reply = resp.as_line_messages()
    except NlpServiceError as e:
        err_msg = 'NLP service is currently unavailable: {}'.format(repr(e))
        logger.error(err_msg)
        reply = TextSendMessage(text=err_msg)
    except Exception as e:
        err_msg = 'Unexpected error: {}'.format(repr(e))
        logger.exception(err_msg)
        reply = TextSendMessage(text=err_msg)
    finally:
        logger.info('Reply: {}'.format(reply))
        line_bot_api.reply_message(event.reply_token, reply)
