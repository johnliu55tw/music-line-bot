from itertools import islice
from functools import singledispatch

from linebot.models import (
        TemplateSendMessage,
        CarouselTemplate,
        CarouselColumn,
        URITemplateAction,
        TextSendMessage)

from kkbox_line_bot.nlp.intent import PlayMusicIntent
from kkbox_line_bot import kkbox
from kkbox_line_bot import app


class Error(Exception):
    """Base error"""


class UnsupportedIntent(Error):
    """Intent is not supported"""


@singledispatch
def intent_to_line_messages(intent):
    raise UnsupportedIntent(intent.__class__.__name__)


@intent_to_line_messages.register(PlayMusicIntent)
def _(intent):
    spaced_keywords = ' '.join(intent.parameters['keywords'])
    try:
        search_result = kkbox.search(app.config['KKBOX_ACCESS_TOKEN'],
                                     spaced_keywords,
                                     types=intent.parameters['type'],
                                     limit=10)
    except kkbox.EmptySearchResult:
        return TextSendMessage('KKBOX上找不到您要的資訊耶…要不要試試別的說法呢?')
    else:
        return list(kkbox_search_to_line_messages(search_result).values())


def kkbox_search_to_line_messages(search_result):
    data_types = ('tracks', 'albums', 'artists', 'playlists')
    messages = dict()

    for key in search_result:
        if key not in data_types:
            continue
        else:
            messages[key] = create_carousel_template_message(search_result[key]['data'],
                                                             data_type=key,
                                                             limit=10)
    return messages


def create_carousel_template_message(objs, data_type, limit=10):
    columns = [create_column(obj, data_type) for obj in islice(objs, limit)]
    carousel_template = CarouselTemplate(columns, image_aspect_ratio='square')
    return TemplateSendMessage(alt_text='KKBOX result list', template=carousel_template)


def create_column(obj, data_type):
    def reduce_string_length(s, size):
        return s[:size-1] + '…' if len(s) > size else s

    if data_type == 'tracks':
        image_url = obj['album']['images'][0]['url']
        title = obj['name']
        text = obj['album']['artist']['name']
        actions = [URITemplateAction(label='Open in KKBOX', uri=obj['url'])]

    elif data_type == 'albums':
        image_url = obj['images'][0]['url']
        title = obj['name']
        text = obj['artist']['name']
        actions = [URITemplateAction(label='Open in KKBOX', uri=obj['url'])]

    elif data_type == 'artists':
        image_url = obj['images'][0]['url']
        title = obj['name']
        text = 'Singer'
        actions = [URITemplateAction(label='Open in KKBOX', uri=obj['url'])]

    elif data_type == 'playlists':
        image_url = obj['images'][0]['url']
        title = obj['title']
        text = obj['owner']['name']
        actions = [URITemplateAction(label='Open in KKBOX', uri=obj['url'])]
    # The length of title and text is limited by the Line Message API
    return CarouselColumn(thumbnail_image_url=image_url,
                          title=reduce_string_length(title, 40),
                          text=reduce_string_length(text, 60),
                          actions=actions)
