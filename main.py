import os
import logging

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import TemplateSendMessage, ButtonsTemplate, URITemplateAction

logging.basicConfig(format='%(name)s %(levelname)s %(message)s', level=logging.DEBUG)

app = Flask(__name__)


credentials = {'line_channel_access_token': None,
               'line_channel_secret': None}

for key in list(credentials.keys()):
    env_var = os.getenv(key.upper(), None)
    if not env_var:
        raise ValueError('{} env. variable is not set.'.format(key.upper()))
    else:
        credentials[key] = env_var

app.config['creds'] = credentials


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
                        label='Click to open KKBOX',
                        uri='kkbox://open'
                    )
                ]
            )
        )
        line_bot_api.reply_message(
                event.reply_token,
                buttons_template_message)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
