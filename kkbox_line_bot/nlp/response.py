import reprlib

from linebot.models import (
        CarouselColumn,
        URITemplateAction,
        CarouselTemplate,
        TemplateSendMessage,
        TextSendMessage)


class ErrorResponse(object):

    def __init__(self, response_text, status_code=None):
        self.response_text = response_text
        self.status_code = status_code

    def __repr__(self):
        return '<ErrorResponse object: response_text = {}, status_code = {}>'.format(
                self.response_text,
                self.status_code)

    def as_line_messages(self):
        return [TextSendMessage(text=self.response_text),
                TextSendMessage(text='DEBUG: status_code={}'.format(self.status_code))]


class NotImplementedResponse(object):

    def __init__(self, type):
        self.type = type
        self.response_text = '{}這個功能還沒實作…請洽Line Bot的作者 :D'.format(self.type)

    def __repr__(self):
        return '<NotImplementedResponse object: type={}>'.format(self.type)

    def as_line_messages(self):
        return [TextSendMessage(text=self.response_text)]


class KKBOXResponse(object):

    def __init__(self, response_text, data_obj):
        self.response_text = response_text
        self.data_obj = data_obj

    def __repr__(self):
        return '<KKBOXResponse object: response_text = {}, data_obj = {}>'.format(
                self.response_text,
                reprlib.repr(self.data_obj))

    def as_line_messages(self):
        response_msg = TextSendMessage(text=self.response_text)
        template_msg = self._create_template_message() if self.data_obj else None
        return [response_msg, template_msg] if template_msg else [response_msg]

    def _create_template_message(self):
        return TemplateSendMessage(alt_text='KKBOX Result',
                                   template=CarouselTemplate(self._get_carousel_columns(),
                                                             image_aspect_ratio='square'))

    def _get_carousel_columns(self):
        return [CarouselColumn(thumbnail_image_url=kkbox_obj['photo'][1]['url'],
                               title=self.reduce_string_length(kkbox_obj['title'], 40),
                               text=self.reduce_string_length(kkbox_obj['artist'], 60),
                               actions=[URITemplateAction(label='Open in KKBOX',
                                                          uri=kkbox_obj['url'])])
                for kkbox_obj in self.data_obj]

    @staticmethod
    def reduce_string_length(s, size):
        return s[:size-1] + '…' if len(s) > size else s
