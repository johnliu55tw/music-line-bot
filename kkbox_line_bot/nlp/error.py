class Error(Exception):
    """Base error for NLP services"""


class NlpServiceError(Error):
    """Nlp service failed to process the reqeusts."""
