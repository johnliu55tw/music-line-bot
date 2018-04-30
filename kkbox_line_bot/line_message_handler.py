import logging
from pprint import pformat

from kkbox_line_bot import app
from kkbox_line_bot import olami

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import TemplateSendMessage, ButtonsTemplate, URITemplateAction

logger = logging.getLogger(__name__)

line_bot_api = LineBotApi(app.config['LINE_CHANNEL_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(app.config['LINE_CHANNEL_SECRET'])


@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    logger.debug('event: ' + str(event))
    olami_svc = olami.OlamiNliService(app.config['OLAMI_APP_KEY'],
                                      app.config['OLAMI_APP_SECRET'])
    try:
        nlp_result = olami_svc(event.message.text)
    except Exception as e:
        logger.exception('Olami service error')
        msg = 'Olami service error: {}'.format(repr(e))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))
    else:
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(pformat(nlp_result)))


# Test handler
# @webhook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    logger.debug('event: ' + str(event))
    logger.debug('event.reply_token: ' + event.reply_token)
    logger.debug('event.message.text: ' + event.message.text)
    if event.message.text == 'template':
        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='Menu',
                text='Please select',
                actions=[
                    URITemplateAction(
                        label='Open KKBOX',
                        uri='https://event.kkbox.com/content/song/GlcNVyRZylVNH8isik'
                    )
                ]
            )
        )
        logger.debug('template json obj: ' + str(buttons_template_message))
        line_bot_api.reply_message(
                event.reply_token,
                buttons_template_message)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
