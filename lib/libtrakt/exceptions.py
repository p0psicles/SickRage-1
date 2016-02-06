from requests.exceptions import (ConnectionError, Timeout, TooManyRedirects)


class TraktException(Exception):
    pass


class TraktAuthException(TraktException):
    pass


class TraktServerBusy(TraktException):
    pass


class TraktMissingTokenException(TraktException):
    pass


class TraktTimeoutException(TraktException, Timeout):
    pass


class TraktUnavailableException(TraktException):
    pass


class TraktResourceNotExistException(TraktException):
    pass


class TraktConnectionException(TraktException, ConnectionError):
    pass


class TraktTooManyRedirects(TraktException, TooManyRedirects):
    pass
 