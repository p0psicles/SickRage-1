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


class Anime(object):
    """
    An anime. Identified by an `aid`
    """
    def __init__(self, aid):
        self.aid = aid
        self.title = {}
        self._type = None
        self._episodecount = None
        self.episodes = {}
        self.startdate = None
        self._enddate = None
        self._categories = []
        self._tags = []
        self.picture = None
        self.image_path = None
        self.url = "https://anidb.net/perl-bin/animedb.pl?show=anime&aid={0}".format(self.aid)
        self.ratings = {
            "permanent": {"count": None, "rating": None},
            "temporary": {"count": None, "rating": None},
            "review": {"count": None, "rating": None}
        }
