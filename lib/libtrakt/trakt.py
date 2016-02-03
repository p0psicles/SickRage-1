import time
import json
import requests
import certifi
import logging
from libtrakt.exceptions import *

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class RecommendedShow(object):
    '''A base class for a recommended show'''
    def __init__(self):
        self.show_name = None
        self.show_id = None
        self.rating = None
        self.votes = None
        self.title = None
        self.image_href = None
        self.image_src = None


class RecommendedShowsApi(object):
    '''A base class to use for recommended shows client API's'''
    def __init__(self, headers={}, timeout=None, api_url=None, auth_url=None, ssl_verify=None):
        self.session = requests.Session()
        self.ssl_verify = certifi.where() if ssl_verify else False
        self.timeout = timeout if timeout else None
        self.auth_url = auth_url
        self.api_url = api_url
        self.headers = headers

    def _get_token(self, path, data, headers, count=0):
        headers['Content-Type'] = 'application/json'

        resp = self._request(path, data=data, headers=headers, url=self.auth_url, method='POST', count=count)

        return resp

    def _request(self, path, data=None, headers=None, url=None, method='GET', count=0):  # pylint: disable-msg=too-many-arguments
        if url is None:
            url = self.api_url

        count = count + 1

        if headers is None:
            headers = self.headers

        data = json.dumps(data) if data else []

        try:
            resp = self.session.request(method, url + path, headers=headers, timeout=self.timeout,
                                        data=data, verify=self.ssl_verify)

            # check for http errors and raise if any are present
            resp.raise_for_status()

            # convert response to json
            resp = resp.json()
        except requests.RequestException as e:
            raise e

        return resp


class TraktAPI(RecommendedShowsApi):
    '''Trakt specific client api class'''
    def __init__(self, ssl_verify=True, timeout=30, **trakt_settings):
        headers = {
            'Content-Type': 'application/json',
            'trakt-api-version': '2',
            'trakt-api-key': trakt_settings['trakt_api_key']
        }

        self.trakt_api_secret = trakt_settings['trakt_api_secret']
        self.trakt_api_key = trakt_settings['trakt_api_key']
        self.trakt_access_token = trakt_settings['trakt_access_token']

        super(TraktAPI).__init__(headers, timeout=timeout, api_url=trakt_settings['trakt_api_url'],
                                 auth_url=trakt_settings['trakt_auth_url'], ssl_verify=ssl_verify)

    def _get_token(self, refresh_token=None, trakt_pin=None, refresh=False, count=0):
        '''function or refreshing a trakt token'''
        if count > 3:
            self.trakt_access_token = ''
            return False
        elif count > 0:
            time.sleep(2)

        data = {
            'client_id': self.trakt_api_key,
            'client_secret': self.trakt_api_secret,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'
        }

        if refresh and refresh_token:
            data['grant_type'] = 'refresh_token'
            data['refresh_token'] = refresh_token
        else:
            data['grant_type'] = 'authorization_code'
            if trakt_pin is not None:
                data['code'] = trakt_pin

        headers = {
            'Content-Type': 'application/json'
        }

        resp = self._get_token('oauth/token', data=data, headers=headers, url=self.auth_url, method='POST', count=count)

        if 'access_token' in resp:
            access_token = resp['access_token']
            if 'refresh_token' in resp:
                refresh_token = resp['refresh_token']
            return (access_token, refresh_token)
        return False

    def validate_account(self):
        '''function for validation of trakt account'''
        resp = self.trakt_request('users/settings')

        if 'account' in resp:
            return True
        return False

    def trakt_request(self, path, data=None, headers=None, url=None, method='GET', count=0):  # pylint: disable-msg=too-many-arguments,too-many-branches
        '''function for performing the trakt request'''
        if self.trakt_access_token == '' and count >= 2:
            raise traktMissingTokenException(u'You must get a Trakt TOKEN. Check your Trakt settings')

        if self.trakt_access_token != '':
            headers['Authorization'] = 'Bearer ' + self.trakt_access_token

        try:
            resp = self._request(url + path, headers=headers, data=data)

            # convert response to json
            resp = resp.json()
        except requests.RequestException as e:
            code = getattr(e.response, 'status_code', None)
            if not code:
                if 'timed out' in e:
                    log.warning(u'Timeout connecting to Trakt. Try to increase timeout value in Trakt settings')
                    traktTimeoutException(u'Timeout connecting to Trakt. Try to increase timeout value in Trakt settings')  # @UndefinedVariable
                # This is pretty much a fatal error if there is no status_code
                # It means there basically was no response at all
                else:
                    log.debug(u'Could not connect to Trakt. Error: %s', e)
                    traktException(u'Could not connect to Trakt. Error: {0}'.format(e))  # @UndefinedVariable
            elif code == 502:
                # Retry the request, cloudflare had a proxying issue
                log.debug(u'Retrying trakt api request: %s', path)
                return self._request(path, data, headers, url, method)
            elif code == 401:
                if self._get_token(refresh=True, count=count):
                    return self.trakt_request(path, data, headers, url, method)
                else:
                    # Need to refresh the token
                    log.warning(u'Unauthorized. Please check your Trakt settings')
                    traktAuthException(u'Unauthorized. Please check your Trakt settings')
            elif code in (500, 501, 503, 504, 520, 521, 522):
                # http://docs.trakt.apiary.io/#introduction/status-codes
                log.debug(u'Trakt may have some issues and it\'s unavailable. Try again later please')
                traktUnavailableException(u'Trakt may have some issues and it\'s unavailable. Try again later please')
            elif code == 404:
                log.error(u'Trakt error (404) the resource does not exist: %s', url + path)
                traktResourceNotExistException(u'Trakt error (404) the resource does not exist: %s', url + path)
            else:
                log.error(u'Could not connect to Trakt. Code error: %s', code)
                traktConnectionException(u'Could not connect to Trakt. Code error: %s', code)
            return {}

        # check and confirm trakt call did not fail
        if isinstance(resp, dict) and resp.get('status', False) == 'failure':
            if 'message' in resp:
                raise traktException(resp['message'])
            if 'error' in resp:
                raise traktException(resp['error'])
            else:
                raise traktException('Unknown Error')

        return resp
