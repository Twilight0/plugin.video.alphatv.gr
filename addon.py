# -*- coding: utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import sys
from tulip.compat import parse_qsl
from resources.lib import alphatv


params = dict(parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')
url = params.get('url')
title = params.get('title')
image = params.get('image')
query = params.get('query')


if action is None:
    alphatv.Indexer().root()

elif action == 'addBookmark':
    from tulip import bookmarks
    bookmarks.add(url)

elif action == 'deleteBookmark':
    from tulip import bookmarks
    bookmarks.delete(url)

elif action == 'recent':
    alphatv.Indexer().recent()

elif action == 'bookmarks':
    alphatv.Indexer().bookmarks()

elif action == 'index':
    alphatv.Indexer().index(url)

elif action == 'news':
    alphatv.Indexer().news(url)

elif action == 'episodes':
    alphatv.Indexer().episodes(url, title, image)

elif action == 'news_episodes':
    alphatv.Indexer().news_episodes(query)

elif action == 'play':
    alphatv.Indexer().play(url)

elif action == 'cache_clear':
    from tulip.cache import clear
    clear(withyes=False)

elif action == 'selector':
    alphatv.Indexer().selector()

elif action == 'back':
    from tulip.control import execute
    execute('Action(Back)')
