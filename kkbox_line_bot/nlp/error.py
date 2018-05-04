class Error(Exception):
    """Base error for NLP services"""


class NlpFailed(Error):
    """NLP service failed to process the query."""
    def __init__(self, status_code, response, reason=None):
        self.status_code = status_code
        self.response = response
        self.reason = reason
