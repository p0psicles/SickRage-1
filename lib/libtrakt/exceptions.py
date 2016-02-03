__all__ = ["traktException", "traktAuthException", "traktServerBusy", "traktMissingTokenException",
           "traktTimeoutException", "traktUnavailableException", "traktResourceNotExistException",
           "traktConnectionException"]


class traktException(Exception):
    pass


class traktAuthException(traktException):
    pass


class traktServerBusy(traktException):
    pass


class traktMissingTokenException(traktException):
    pass


class traktTimeoutException(traktException):
    pass


class traktUnavailableException(traktException):
    pass


class traktResourceNotExistException(traktException):
    pass


class traktConnectionException(traktException):
    pass
