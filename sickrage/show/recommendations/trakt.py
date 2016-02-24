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

import sickbeard
from sickbeard.logger import (Logger as logger, DEBUG, WARNING)

from libtrakt.trakt import TraktApi
from libtrakt.exceptions import traktAuthException, traktException

from sickrage.show.Show import Show
from sickrage.helper.exceptions import ex
from sickrage.helper.exceptions import MultipleShowObjectsException
from .recommended import RecommendedShow


class TraktPopular(object):
    """This class retrieves a speficed recommended show list from Trakt
    The list of returned shows is mapped to a RecommendedShow object"""

    def fetch_and_refresh_token(self, trakt_api, path):
        try:
            library_shows = trakt_api.request(path) or []
        except traktAuthException:
            logger.log(u"Refreshing Trakt token", DEBUG)
            (access_token, refresh_token) = trakt_api.get_token(sickbeard.TRAKT_REFRESH_TOKEN)
            if access_token:
                sickbeard.TRAKT_ACCESS_TOKEN = access_token
                sickbeard.TRAKT_REFRESH_TOKEN = refresh_token
                library_shows = trakt_api.request(path) or []

        return library_shows

    def fetch_popular_shows(self, page_url=None, trakt_list=None):  # pylint: disable=too-many-nested-blocks,too-many-branches
        """
        Get a list of popular shows from different Trakt lists based on a provided trakt_list
        :param page_url: the page url opened to the base api url, for retreiving a specific list
        :param trakt_list: a description of the trakt list
        :return: A list of RecommendedShow objects, an empty list of none returned
        :throw: ``Exception`` if an Exception is thrown not handled by the libtrats exceptions
        """
        trending_shows = []

        # Create a trakt settings dict
        trakt_settings = {"trakt_api_secret": sickbeard.TRAKT_API_SECRET, "trakt_api_key": sickbeard.TRAKT_API_KEY,
                          "trakt_access_token": sickbeard.TRAKT_ACCESS_TOKEN, "trakt_api_url": sickbeard.TRAKT_API_URL,
                          "trakt_auth_url": sickbeard.TRAKT_OAUTH_URL}

        trakt_api = TraktApi(sickbeard.SSL_VERIFY, sickbeard.TRAKT_TIMEOUT, **trakt_settings)

        try:  # pylint: disable=too-many-nested-blocks
            not_liked_show = ""
            if sickbeard.TRAKT_ACCESS_TOKEN != '':
                library_shows = self.fetch_and_refresh_token(trakt_api, "sync/collection/shows?extended=full")

                if sickbeard.TRAKT_BLACKLIST_NAME is not None and sickbeard.TRAKT_BLACKLIST_NAME:
                    not_liked_show = trakt_api.request("users/" + sickbeard.TRAKT_USERNAME + "/lists/" +
                                                       sickbeard.TRAKT_BLACKLIST_NAME + "/items") or []
                else:
                    logger.log(u"Trakt blacklist name is empty", DEBUG)

            if trakt_list not in ["recommended", "newshow", "newseason"]:
                limit_show = "?limit=" + str(100 + len(not_liked_show)) + "&"
            else:
                limit_show = "?"

            shows = self.fetch_and_refresh_token(trakt_api, page_url + limit_show + "extended=full,images") or []

            if sickbeard.TRAKT_ACCESS_TOKEN != '':
                library_shows = self.fetch_and_refresh_token(trakt_api, "sync/collection/shows?extended=full") or []

            for show in shows:
                try:
                    if 'show' not in show:
                        show['show'] = show

                    if not Show.find(sickbeard.showList, [int(show['show']['ids']['tvdb'])]):
                        if sickbeard.TRAKT_ACCESS_TOKEN != '':
                            if show['show']['ids']['tvdb'] not in (lshow['show']['ids']['tvdb']
                                                                   for lshow in library_shows):
                                if not_liked_show:
                                    if show['show']['ids']['tvdb'] not in (show['show']['ids']['tvdb']
                                                                           for show in not_liked_show if show['type'] == 'show'):
                                        trending_shows += [show]
                                else:
                                    trending_shows += [show]
                        else:
                            if not_liked_show:
                                if show['show']['ids']['tvdb'] not in (show['show']['ids']['tvdb']
                                                                       for show in not_liked_show if show['type'] == 'show'):
                                    trending_shows += [show]
                            else:
                                trending_shows += [show]

                except MultipleShowObjectsException:
                    continue

            blacklist = sickbeard.TRAKT_BLACKLIST_NAME not in ''

        except traktException as e:
            logger.log(u"Could not connect to Trakt service: %s" % ex(e), WARNING)

        return (blacklist, trending_shows)
