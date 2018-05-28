import time
import json
import logging
from hashlib import md5

from .error import NlpServiceError
from . import response

import requests


logger = logging.getLogger(__name__)


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
        return response_factory(self._make_request(text))

    def _make_request(self, text):
        resp = requests.post(self.BASE_URL,
                             params=self._gen_parameters(text))
        # HTTP Response code != 200: Service Error!
        if resp.status_code != 200:
            raise NlpServiceError('HTTP Response != 200: {}'.format(resp.status_code))

        resp_json = resp.json()
        # The outermost status value
        if resp_json['status'] != 'ok':
            raise NlpServiceError(
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


def response_factory(olami_resp):
    """Simple factory function creates a response.*Response class from OLAMI response."""
    first_match = olami_resp[0]

    if first_match['type'] == 'ds':
        return response.ErrorResponse(response_text=first_match['desc_obj']['result'],
                                      status_code=first_match['desc_obj']['status'])

    elif first_match['type'] == 'kkbox':
        return response.KKBOXResponse(response_text=first_match['desc_obj']['result'],
                                      data_obj=first_match['data_obj'])

    else:
        return response.NotImplementedResponse(type=first_match['type'])
