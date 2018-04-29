from flask import Flask
from kkbox_line_bot import config

app = Flask(__name__)

if app.env == 'production':
    app.config.update(config.load_production())
else:
    app.config.update(config.load_default())

import kkbox_line_bot.views
