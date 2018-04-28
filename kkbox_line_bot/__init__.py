import os
import logging

from flask import Flask

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

import kkbox_line_bot.views
