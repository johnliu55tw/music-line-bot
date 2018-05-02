import requests

BASE_URL = 'https://api.kkbox.com/v1.1/'
VALID_SEARCH_TYPES = ('album', 'track', 'artist', 'playlist')


class Error(Exception):
    """Base Error"""


def search(token, keyword,
           territory='TW', types=None, limit=None, offset=None):

    if types is not None:
        types = [types] if not isinstance(types, (list, tuple)) else types
        if not all(t in VALID_SEARCH_TYPES for t in types):
            invalid_types = (t for t in types if t not in VALID_SEARCH_TYPES)
            raise ValueError("Invalid type: '{}'.".format(', '.join(invalid_types)))
        else:
            types = ','.join(types)

    resp = requests.get(BASE_URL+'search',
                        headers={'Authorization': 'Bearer ' + token},
                        params={'q': keyword,
                                'territory': territory,
                                'type': types,
                                'limit': limit,
                                'offset': offset})

    if resp.status_code != 200:
        raise Error(resp.json())
    else:
        return resp.json()
