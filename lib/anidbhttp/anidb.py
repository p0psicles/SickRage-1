# coding=utf-8
#
# URL: https://sickrage.github.io
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage. If not, see <http://www.gnu.org/licenses/>.

import time
import json
import requests
import certifi
import logging
from sickrage.helper.common import try_int
import xml.etree.ElementTree as ET

from anidbhttp.model import Anime
from anidbhttp.exceptions import (AnidbConnectionException, AnidbInvalidQueryParams, AnidbAuthException,
                                  AnidbUnavailableException, AnidbResourceNotExistException, AnidbException,
                                  AnidbTimeoutException, AnidbTooManyRedirects, AnidbParseError)
from multiprocessing.connection import Client


# from model import RecommendedShow  # Next step is to map all results to show objects, so it can use one template

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AnimeLists(object):
    """
    Class with the different request params.
    The anidb http api can be used by passing the following request param:
    * request=anime: add the parameter aid={integer} [required] to retrieve data for a specific anime
    * request=categorylist
    * request=randomrecommendation
    * request=hotanime
    """
    CATEGORIES = "categorylist"
    RANDOMRECOMMENDATION = "randomrecommendation"
    HOT = "hotanime"
    AIDSEARCH = "anime"


class AnidbApi(object):
    """A base class to use for recommended shows client API's"""
    def __init__(self, client='sickragehttp', clientversion='1', timeout=None, ssl_verify=None, **anidb_settings):  # pylint: disable=too-many-arguments
        headers = {
            'Content-Type': 'application/json',
        }

        self.session = requests.Session()
        self.client = client
        self.clientversion = clientversion
        self.ssl_verify = certifi.where() if ssl_verify else False
        self.timeout = timeout if timeout else None
        self.search_url = 'http://anisearch.outrance.pl?task=search&query=%s'
        self.api_url = 'http://api.anidb.net:9001/httpapi'
        self.headers = anidb_settings.get("headers", headers)
        self.anidb_settings = anidb_settings
        self.namespace = "{http://www.w3.org/XML/1998/namespace}"

    def _request(self, params, data=None, headers=None, url=None, method='GET', count=0):  # pylint: disable-msg=too-many-arguments,too-many-branches
        """function for performing the anidb http api request"""

        if headers is None:
            headers = self.headers

        base_params = {'client': self.client, 'clientver': self.clientversion, 'protover': '1'}

        params.update(base_params)

        data = json.dumps(data) if data else []

        try:
            resp = self.session.request(method, self.api_url, params=params, headers=headers, timeout=self.timeout,
                                        data=data, verify=self.ssl_verify)

            # convert response to json
            resp = ET.fromstring(resp.text)
        except AnidbTimeoutException:
            log.warning(u'Timeout connecting to Anidb. Try to increase timeout value in Anidb settings')
            raise AnidbTimeoutException(u'Timeout connecting to Anidb. Try to increase timeout value in Anidb settings')  # @UndefinedVariable
        except AnidbConnectionException:
            log.error(u'Could not connect to Anidb.')
            raise AnidbConnectionException()
        except AnidbTooManyRedirects:
            log.error(u'Too many redirections while connection to Anidb.')
            raise AnidbTooManyRedirects()
        except AnidbParseError:
            log.error(u'Could not parse the returned html.')
            raise AnidbParseError()
        except requests.RequestException as e:
            code = getattr(e.response, 'status_code', None)
            if code == 502:
                # Retry the request, cloudflare had a proxying issue
                log.debug(u'Retrying trakt api request: %s', path)
                return self.request(path, data, headers, url, method)
            elif code in (500, 501, 503, 504, 520, 521, 522):
                # http://docs.trakt.apiary.io/#introduction/status-codes
                log.debug(u"Anidb may have some issues and it's unavailable. Try again later please")
                raise AnidbUnavailableException(u"Anidb may have some issues and it\'s unavailable. Try again later please")
            elif code == 404:
                log.error(u'Anidb error (404) the resource does not exist: %s', url)
                raise AnidbResourceNotExistException(u'Anidb error (404) the resource does not exist: %s', url)
            else:
                log.error(u'Unknown Anidb request exception. Code error: %s', code)
                return {}

        # check and confirm anidbhttp call did not fail
        if not isinstance(resp, ET.Element):
            raise AnidbException("Not an XML")

        return resp

    def _parse(self, anime):
        new_anime = Anime(anime.get('id'))

        new_anime.title[anime.find('title').attrib["{0}lang".format(self.namespace)]] = anime.find('title').text
        new_anime.picture = anime.find('picture').text
        for vote_category in ['permanent', 'temporary', 'review']:
            if hasattr(anime.find('ratings').find(vote_category), 'tag'):
                new_anime.ratings[vote_category]['count'] = anime.find('ratings').find(vote_category).get('count')
                new_anime.ratings[vote_category]['votes'] = anime.find('ratings').find(vote_category).text
        new_anime.startdate = anime.find('startdate').text if hasattr(anime.find('startdate'), 'tag') else None
        new_anime.enddate = anime.find('enddate').text if hasattr(anime.find('enddate'), 'tag') else None
#         if "type" in anime.attrib:
#             t.type = anime.attrib["type"]
#         if "exact" in anime.attrib:
#             t.exact = True

        return new_anime

    def query(self, request, aid=None):
        """Get a list of anime shows using a request object.
        When a aid is provided only the show with the anidb aid (anime id) is returned.
        To search for a specific anime by aid pass the AnimeLists.AIDSEARCH paramater.
        :param anime_list: One of the categories from an AnimeLists object QUERY_CATEGORIES, QUERY_ANIME, QUERY_RANDOMRECOMMENDATION, QUERY_HOT
        :param aid: Filter the list of animes using this aid.
        """
        result = []

        if request in AnimeLists.AIDSEARCH and try_int(aid):
            params = {'request': request, 'aid': aid}
        elif request not in AnimeLists.AIDSEARCH:
            params = {'request': request}
        else:
            raise AnidbInvalidQueryParams()

        response = self._request(params, method='GET')

        for anime in response:
            result.append(self._parse(anime))

        return result
