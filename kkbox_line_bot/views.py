import logging

from kkbox_line_bot import app
from flask import request, abort, jsonify

from kkbox_line_bot.line_message_handler import webhook_handler

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def index():
    return 'This is the index page!'


@app.route('/message', methods=['POST'])
def message():
    try:
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
    except Exception as e:
        msg = 'Invalid request: {}'.format(repr(e))
        abort(400, msg)

    try:
        webhook_handler.handle(body, signature)
    except Exception as e:
        msg = 'Line webhook handler error: {}'.format(repr(e))
        logger.exception(msg)
        abort(500, msg)

    return 'OK'


@app.errorhandler(400)
def bad_request_handler(e):
    return jsonify({'msg': e.description}), 400


@app.errorhandler(500)
def internal_error_handler(e):
    return jsonify({'msg': e.description}), 500
