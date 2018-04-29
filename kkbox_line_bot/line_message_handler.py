import logging

from kkbox_line_bot import app

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import TemplateSendMessage, ButtonsTemplate, URITemplateAction

logger = logging.getLogger(__name__)

line_bot_api = LineBotApi(app.config['LINE_CHANNEL_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(app.config['LINE_CHANNEL_SECRET'])


@webhook_handler.add(MessageEvent, message=TextMessage)
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
