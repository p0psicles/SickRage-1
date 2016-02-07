from requests.exceptions import (ConnectionError, Timeout, TooManyRedirects)
from _elementtree import ParseError


class AnidbException(Exception):
    """A Generic Anidb Exception"""


class AnidbAuthException(AnidbException):
    """A Generic Anidb Authentication Exception"""


class AnidbServerBusy(AnidbException):
    """A Generic Anidb Server Busy Exception"""


class AnidbMissingTokenException(AnidbException):
    """A Generic Anidb Missing Token Exception"""


class AnidbIOError(AnidbException, IOError):
    """A Generic Anidb IOError Exception"""


class AnidbConnectionException(AnidbIOError, ConnectionError):
    """A Generic Anidb Connection Exception, inherited from AnidbIOError and IOError"""


class AnidbTimeoutException(AnidbIOError, Timeout):
    """A Generic Anidb Timeout Exception, inherited from AnidbIOError and IOError"""


class AnidbUnavailableException(AnidbException):
    """A Generic Anidb Unavailable Exception,
    possibly raised when Anidb is reachable but is showing an unavailable response code.
    Possibly raised on in 500 series response codes"""


class AnidbResourceNotExistException(AnidbException):
    """A Generic Anidb Resource Not Exist Exception, possibly raised on 404"""


class AnidbTooManyRedirects(AnidbException, TooManyRedirects):
    """A Generic Anidb Too Many Redirects Exception"""


class AnidbInvalidQueryParams(AnidbException):
    """An Anidb exception when an invalid paramater has been provided
    For more info an the allowed query params refer to: http://tinyurl.com/zr5w92o"""
    
class AnidbParseError(AnidbException, ParseError):
    """A Generic Anidb XML parse exception"""
