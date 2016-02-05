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

# import requests
# from anidbhttp import anidbquery
# from anidbhttp.query import QUERY_HOT
# from sickrage.helper.common import try_int
# 
# from recommended import RecommendedShow
# 
# class AnidbPopular(object):
#     def __init__(self):
#         self.cache_subfolder = __name__.split('.')[-1] if '.' in __name__ else __name__
#         self.session = requests.Session()
# 
#     def fetch_latest_hot_shows(self):
#         """Get popular show information from IMDB"""
# 
#         shows = []
#         result = []
# 
#         shows = anidbquery.query(QUERY_HOT)
#         for show in shows:
#             try:
#                 recommended_show = RecommendedShow(show.id, show.titles['x-jat'][0], 1, show.tvdbid, cache_subfolder=self.cache_subfolder,
#                      rating=str(show.ratings['temporary']['rating']), votes=str(try_int(show.ratings['temporary']['count'],0)), image_href=show.url)
# 
#                 # Check cache or get and save image
#                 recommended_show.cache_image("http://img7.anidb.net/pics/anime/{0}".format(show.image_path))
# 
#                 result.append(recommended_show)
#             except:
#                 pass
# 
#         return result
# 
# anidb_popular = AnidbPopular()
