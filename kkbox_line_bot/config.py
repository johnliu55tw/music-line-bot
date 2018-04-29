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
            'LINE_CHANNEL_SECRET': 'Line channel secret fro testing'}


def load_production():
    return {'LINE_CHANNEL_ACCESS_TOKEN': getenv_raise('LINE_CHANNEL_ACCESS_TOKEN'),
            'LINE_CHANNEL_SECRET': getenv_raise('LINE_CHANNEL_SECRET')}
