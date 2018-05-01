class Intent(object):

    def __init__(self, input, response, parameters):
        self.input = input
        self.response = response
        self.parameters = parameters

    def __repr__(self):
        return ("<{} object: input: '{}', "
                "response: '{}', parameters: '{}'").format(
                        self.__class__.__name__,
                        self.input,
                        self.response,
                        self.parameters)


class PlayMusicIntent(Intent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
