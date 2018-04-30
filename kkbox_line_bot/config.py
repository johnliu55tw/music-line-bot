import os


def getenv_raise(key):
    """Raise ValueError if the environment variable does not exist."""
    val = os.getenv(key, None)
    if val is None:
        raise ValueError('Environment variable "{}" does not exist.'.format(key))
    else:
        return val


def load_default():
    return {'LINE_CHANNEL_ACCESS_TOKEN': 'Line access token for testing',
            'LINE_CHANNEL_SECRET': 'Line channel secret fro testing',
            'OLAMI_APP_KEY': 'Olami service app key',
            'OLAMI_APP_SECRET': 'Olami app secret',
            'KKBOX_ACCESS_TOKEN': 'KKBOX access token'}


def load_production():
    return {'LINE_CHANNEL_ACCESS_TOKEN': getenv_raise('LINE_CHANNEL_ACCESS_TOKEN'),
            'LINE_CHANNEL_SECRET': getenv_raise('LINE_CHANNEL_SECRET'),
            'OLAMI_APP_KEY': getenv_raise('OLAMI_APP_KEY'),
            'OLAMI_APP_SECRET': getenv_raise('OLAMI_APP_SECRET'),
            'KKBOX_ACCESS_TOKEN': getenv_raise('KKBOX_ACCESS_TOKEN')}
