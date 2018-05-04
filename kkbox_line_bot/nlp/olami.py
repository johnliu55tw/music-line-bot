import time
import json
import logging
from hashlib import md5

from .error import Error, NlpFailed
from .intent import PlayMusicIntent

import requests


logger = logging.getLogger(__name__)


class NliStatusError(Error):
    """The NLI result status is not 'ok'"""


def intent_from_response(resp):
    def get_status(match_result):
        return match_result['desc_obj']['status']

    def get_response(match_result, default=''):
        return match_result['desc_obj'].get('result', default)

    def get_input(match_result):
        return match_result['semantic'][0]['input']

    def get_parameters(match_result):
        first_semantic = match_result['semantic'][0]
        first_modifier = first_semantic['modifier'][0]
        slots = first_semantic['slots']
        slots_dict = {slot['name']: slot['value'] for slot in slots}

        if 'album_or_singer_album' in slots_dict or\
           'album' in slots_dict or\
           'name_or_album' in slots_dict or\
           first_modifier == 'play_album':
            return {'type': 'album', 'keywords': list(slots_dict.values())}

        elif 'singer' in slots_dict:
            return {'type': 'artist', 'keywords': list(slots_dict.values())}

        elif first_modifier == 'play_theme':
            return {'type': 'playlist', 'keywords': list(slots_dict.values())}

        elif first_modifier == 'play_song':
            return {'type': 'track', 'keywords': list(slots_dict.values())}
        else:
            raise ValueError('Unable to get parameters from {}'.format(match_result))

    first_match = resp[0]
    if get_status(first_match) == 0:
        return PlayMusicIntent(get_input(first_match),
                               get_response(first_match),
                               get_parameters(first_match))
    else:
        raise NlpFailed(get_status(first_match),
                        get_response(first_match, default='Empty response!'))


class OlamiService(object):
    BASE_URL = 'https://tw.olami.ai/cloudservice/api'

    def __init__(self, app_key, app_secret, cusid=None, input_type=1, nli_config=None):
        self.app_key = app_key
        self.app_secret = app_secret
        self.cusid = cusid
        if input_type not in (0, 1):
            raise ValueError('Invalid input_type: {}'.format(input_type))
        self.input_type = input_type
        # TO BE Implemented
        if nli_config is not None:
            raise NotImplementedError('nli_config has not finished yet')
        self.nli_config = nli_config

    def __call__(self, text):
        resp = requests.post(self.BASE_URL,
                             params=self._gen_parameters(text))
        resp.raise_for_status()

        resp_json = resp.json()
        if resp_json['status'] != 'ok':
            raise NliStatusError(
                    "NLI responded status != 'ok': {}".format(resp_json['status']))
        else:
            return resp_json['data']['nli']

    def _gen_sign(self, api_parameter, timestamp=None):
        timestamp_ms = int(timestamp*1000) if timestamp else int(time.time()*1000)

        data = self.app_secret + 'api=' + api_parameter + 'appkey=' + self.app_key +\
            'timestamp=' + str(timestamp_ms) + self.app_secret

        return md5(data.encode('ascii')).hexdigest()

    def _gen_rq(self, text, as_text=False):
        obj = {'data_type': 'stt',
               'data': {
                   'input_type': self.input_type,
                   'text': text}}

        return obj if not as_text else json.dumps(obj)

    def _gen_parameters(self, text, timestamp=None):
        ts = timestamp if timestamp else time.time()
        ts_ms = int(ts*1000)
        params = {'appkey': self.app_key,
                  'api': 'nli',
                  'timestamp': ts_ms,
                  'sign': self._gen_sign('nli', timestamp=ts),
                  'rq': self._gen_rq(text, as_text=True)}
        if self.cusid is not None:
            params.update(cusid=self.cusid)

        return params
