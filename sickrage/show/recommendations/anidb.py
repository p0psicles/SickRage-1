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

import requests
from sickbeard import logger
from sickrage.helper.exceptions import ex

from sickrage.helper.common import try_int
from adba.aniDBtvDBmaper import TvDBMap
from anidbhttp.anidb import AnidbApi, AnimeLists
from anidbhttp.exceptions import AnidbException
from .recommended import RecommendedShow


class AnidbPopular(object):  # pylint: disable=too-few-public-methods
    def __init__(self):
        """This class retrieves a speficed recommended show list from Trakt
        The list of returned shows is mapped to a RecommendedShow object"""
        self.cache_subfolder = __name__.split('.')[-1] if '.' in __name__ else __name__
        self.session = requests.Session()
        self.recommender = "Anidb Popular"
        self.default_img_src = ''

    def _create_recommended_show(self, show_obj):
        """creates the RecommendedShow object from the returned showobj"""
        try:
            tvdb_id = TvDBMap().get_tvdb_for_anidb(show_obj.get('id')) if show_obj.get('id') else None
        except Exception:
            tvdb_id = None
            logger.log("Couldn't map aid [{0}] to tvdbid ".format(self.id), logger.WARNING)
            return

        rec_show = RecommendedShow(self,
                                   show_obj.get('id'), show_obj.findall('title')[0].text,
                                   1,  # indexer
                                   tvdb_id,
                                   rating=str(float(show_obj.find('ratings').find('permanent').text) * 10),
                                   votes=str(try_int(show_obj.find('ratings').find('permanent').get('count'), 0)),
                                   image_href='https://anidb.net/perl-bin/animedb.pl?show=anime&aid={0}'.format(show_obj.get('id')))

        # Check cache or get and save image
        rec_show.cache_image("http://img7.anidb.net/pics/anime/{0}".format(show_obj.find('picture').text))

        return rec_show

    def fetch_popular_shows(self):
        """Get popular show information from IMDB"""
        shows = []
        result = []

        try:
            shows = AnidbApi().query(AnimeLists.HOT)
        except AnidbException, e:
            logger.log(u"Could not connect to Anidb service: %s" % ex(e), logger.WARNING)

        for show in shows:
            try:
                result.append(self._create_recommended_show(show))
            except Exception, e:
                logger.log(u"Could not parse Anidb show, with exception: %s" % ex(e), logger.WARNING)

        return result

anidb_popular = AnidbPopular()
