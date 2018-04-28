import logging

from kkbox_line_bot import app
from flask import request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import TemplateSendMessage, ButtonsTemplate, URITemplateAction

line_bot_api = LineBotApi(app.config['creds']['line_channel_access_token'])
handler = WebhookHandler(app.config['creds']['line_channel_secret'])


@app.route('/', methods=['GET'])
def index():
    return 'This is the index page!'


@app.route('/message', methods=['POST'])
def message():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    logging.debug('Request body: ' + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    logging.debug('event: ' + str(event))
    logging.debug('event.reply_token: ' + event.reply_token)
    logging.debug('event.message.text: ' + event.message.text)
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
        logging.debug('template json obj: ' + str(buttons_template_message))
        line_bot_api.reply_message(
                event.reply_token,
                buttons_template_message)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
