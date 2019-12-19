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


import json, re
from time import sleep
from tulip.compat import urljoin, iteritems, parse_qs, urlparse, range
from tulip import bookmarks, directory, client, cache, user_agents, control, youtube, workers


class Indexer:

    def __init__(self):

        self.list = []; self.data = []

        self.basegr_link = 'https://www.alphatv.gr'
        self.basecy_link = 'https://www.alphacyprus.com.cy'

        self.xhr_show_list = ''.join([self.basegr_link, '/ajax/Isobar.AlphaTv.Components.Shows.Show.list'])
        self.seriesgr_link = '?'.join([self.xhr_show_list, 'Key=0&Page=1&PageSize=50&ShowType=1'])
        self.showsgr_link = '?'.join([self.xhr_show_list, 'Key=0&Page=1&PageSize=50&ShowType=0'])

        self.views_ajax = ''.join([self.basecy_link, '/views/ajax'])
        self.ajax_post_index = '&'.join(
            [
                'view_name=alpha_shows_category_view', 'view_display_id=page_3', 'view_args=',
                'view_path=shows', 'view_base_path=shows', 'page={page}', 'pager_element=0'
            ]
        )
        self.ajax_post_episodes = '&'.join(
            [
                'view_name=webtv', 'view_display_id=block_3', 'view_args={view_args}',
                'view_path={view_path}/webtv', 'view_base_path=shows/%/%/webtv', 'page={page}', 'pager_element=0'
            ]
        )

        self.webtvcy_link = ''.join([self.basecy_link, '/shows'])

        self.episodeslist_gr = ''.join([self.basegr_link, '/ajax/Isobar.AlphaTv.Components.Shows.Show.episodeslist'])
        self.episodeslist_gr_query = '?'.join([self.episodeslist_gr, 'Key={year}&Page=1&PageSize={pages}&ShowId={show_id}'])

        self.player_link = ''.join([self.basegr_link, '/ajax/Isobar.AlphaTv.Components.PopUpVideo.PopUpVideo.PlayMedia'])
        self.player_query = '/?'.join([self.player_link, 'vid={video_id}&showId={show_id}&year={year}'])

        self.newsgr_link = ''.join([self.basegr_link, '/news'])
        self.newsgr_link_ajax = ''.join([self.newsgr_link, '/?pg={page}&$component=NewsSection[0]&articleCategory={category}'])
        # self.newscy_link = ''.join([self.basecy_link, '/shows/informative/kentrikodeltio/webtv'])
        self.newscy_link = ''.join([self.basecy_link, '/shows/informative/kentrikodeltio/webtv'])

        self.live_link_gr = ''.join([self.basegr_link, '/live/'])
        self.live_link_cy = ''.join([self.basecy_link, '/page/live'])

        self.yt_id_gr = 'UCYKe1v03QBPyApJID8CPjPA'
        self.yt_id_cy = 'UCxO8Xtg_dmOxubozdzLw3AA'
        self.yt_key = 'AIzaSyBOS4uSyd27OU0XV2KSdN3vT2UG_v0g9sI'

    def root(self):

        if control.setting('region') == 'CY':
            formatter = control.lang(32005)
        else:
            formatter = control.lang(32004)

        self.list = [
            {
                'title': control.lang(32003).format(formatter),
                'action': 'selector',
                'icon': 'selector.png',
                'isFolder': 'False',
                'isPlayable': 'False'
            }
            ,
            {
                'title': control.lang(32001),
                'action': 'play',
                'icon': 'live.png',
                'url': self.live_link_cy if control.setting('region') == 'CY' else self.live_link_gr,
                'isFolder': 'False'
            }
            ,
            {
                'title': control.lang(32010),
                'action': 'recent',
                'icon': 'recent.png'
            }
            ,
            {
                'title': control.lang(32008),
                'action': 'index',
                'icon': 'shows.png',
                'url': 'shows'
            }
            ,
            {
                'title': control.lang(32002),
                'action': 'index',
                'icon': 'series.png',
                'url': 'series'
            }
            ,
            {
                'title': control.lang(32011),
                'action': 'episodes' if control.setting('region') == 'CY' else 'news',
                'icon': 'news.png',
                'url': self.newscy_link if control.setting('region') == 'CY' else self.newsgr_link
            }
            ,
            {
                'title': control.lang(32009),
                'action': 'bookmarks',
                'icon': 'bookmarks.png'
            }
        ]

        webtv = {
            'title': control.lang(32012),
            'action': 'index',
            'icon': 'shows.png',
            'url': 'webtv'
        }

        if control.setting('region') == 'CY':

            del self.list[3:5]
            self.list.insert(3, webtv)

        for item in self.list:

            cache_clear = {'title': 32022, 'query': {'action': 'cache_clear'}}
            item.update({'cm': [cache_clear]})

        directory.add(self.list, content='videos')

    @staticmethod
    def selector():

        choices = [control.lang(32004), control.lang(32005)]

        choice = control.selectDialog(choices, control.lang(32007))

        if choice == 0:
            control.setSetting('region', 'GR')
        elif choice == 1:
            control.setSetting('region', 'CY')

        if choice != -1:

            control.sleep(200)
            control.refresh()

    def recent(self):

        if control.setting('region') == 'CY':
            url = self.yt_id_cy
        else:
            url = self.yt_id_gr

        self.list = cache.get(youtube.youtube(key=self.yt_key).videos, 2, url)

        if self.list is None:
            return

        for i in self.list:
            i.update({'action': 'play', 'isFolder': 'False'})

        directory.add(self.list)

    def bookmarks(self):

        self.list = bookmarks.get()

        if not self.list:

            na = [{'title': 'N/A', 'action': None}]
            directory.add(na)

            return

        for i in self.list:

            bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
            bookmark['delbookmark'] = i['url']
            i.update({'cm': [{'title': 32502, 'query': {'action': 'deleteBookmark', 'url': json.dumps(bookmark)}}]})

        control.sortmethods('title')

        directory.add(self.list, content='videos')

    def index_gr(self, url):

        html = client.request(url)

        items = [i for i in re.findall(r'(<a.+?/a>)', html, re.S) if 'BLOCK_SERIES' not in i]

        for item in items:

            url = client.parseDOM(item, 'a', ret='href')[0]
            title = client.replaceHTMLCodes(client.parseDOM(item, 'h3')[0]).replace(u'ᵒ', u' μοίρες')
            image = client.parseDOM(item, 'div', attrs={'class': 'tvShowImg'}, ret='style')[0]
            image = re.search(r'\([\'"](.+?)[\'"]\)', image).group(1)

            data = {'title': title, 'image': image, 'url': url}

            if 'alpha-news' in url:

                data.update({'action': 'news'})

            self.list.append(data)

        return self.list

    def index_cy(self, url):

        html = client.request(url)

        try:
            pages = client.parseDOM(html, 'li', attrs={'class': 'pager__item pager__item--last'})[0]
            pages = int(re.search(r'(\d{1,3})$', client.parseDOM(pages, 'a', ret='href')[0], re.M).group(1))
        except Exception:
            pages = 0

        if pages:

            threads = []

            for i in list(range(0, pages + 1)):
                threads.append(workers.Thread(self.thread, i, self.views_ajax, self.ajax_post_index.format(page=str(i)), False))
                self.data.append('')
            [i.start() for i in threads]
            [i.join() for i in threads]

            htmls = '\n'.join([json.loads(i)[2]['data'] for i in self.data])

            items = client.parseDOM(htmls, 'li', attrs={'class': 'views-row views-row-.+?'})

        else:

            items = client.parseDOM(html, 'li', attrs={'class': 'views-row views-row-.+?'})

        filters = ['box-office', 'ellinikes-tenies', 'block-series']
        items = [i for i in items if not any([f for f in filters if f in i])]

        for item in items:

            title_field = client.parseDOM(item, 'div', attrs={'class': 'views-field-title'})[0]
            title = client.replaceHTMLCodes(client.parseDOM(title_field, 'a')[0]).replace(u'ᵒ', u' μοίρες')
            url = client.parseDOM(title_field, 'a', ret='href')[0]
            url = urljoin(self.basecy_link, url + '/webtv')
            image = client.parseDOM(item, 'img', ret='src')[0]

            data = {'title': title, 'image': image, 'url': url}

            self.list.append(data)

        return self.list

    def index(self, url):

        if self.basecy_link in url:
            self.list = cache.get(self.index_cy, 24, url)
        elif self.basegr_link in url:
            self.list = cache.get(self.index_gr, 24, url)
        elif url == 'shows':
            self.list = cache.get(self.index_gr, 24, self.showsgr_link)
        elif url == 'series':
            self.list = cache.get(self.index_gr, 24, self.seriesgr_link)
        elif url == 'webtv':
            self.list = cache.get(self.index_cy, 24, self.webtvcy_link)

        if not self.list:
            return

        for i in self.list:
            if 'action' not in i:
                i.update({'action': 'episodes'})

        for i in self.list:
            bookmark = dict((k, v) for k, v in iteritems(i) if not k == 'next')
            bookmark['bookmark'] = i['url']
            i.update({'cm': [{'title': 32501, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        control.sortmethods('title')
        control.sortmethods()

        directory.add(self.list, content='videos')

    def episodes_list_gr(self, url, title):

        html = client.request(url)

        link = client.parseDOM(html, 'a', ret='data-url')[1]

        html = client.request(link)

        div_season = client.parseDOM(html, 'div', attrs={'class': 'mbSeasonsList'})[0]

        years = client.parseDOM(div_season, 'a')
        show_id = [i for i in client.parseDOM(html, 'script') if 'window.Environment.showId' in i][0]
        show_id = re.search(r'showId = (\d+);', show_id).group(1)

        for y in years:

            h = client.request(self.episodeslist_gr_query.format(year=y, pages='366', show_id=show_id))

            self.data.append(h)

        html = ''.join(self.data)

        items = client.parseDOM(html, 'div', attrs={'class': 'episodeItem flexClm4'})

        try:
            title = title.decode('utf-8')
        except Exception:
            pass

        for item in items:

            descr = client.parseDOM(item, 'a', attrs={'class': 'openVideoPopUp'})[0]
            descr = client.stripTags(descr).strip()
            if descr.endswith((u'Nέο', u'Νεο', u'New')):
                descr = descr[:-3]
            label = u' - '.join([title, descr])
            image = client.parseDOM(item, 'div', attrs={'class': 'epImg'}, ret='style')[0]
            image = re.search(r'\([\'"](.+?)[\'"]\)', image).group(1)
            video = re.search(r'WebTvVideoId&quot;:(\d+).+?Year&quot;:(\d{4})}', item)
            url = self.player_query.format(video_id=video.group(1), show_id=show_id, year=video.group(2))

            self.list.append({'title': label, 'image': image, 'url': url})

        return self.list

    def episodes_list_cy(self, url, title, image):

        try:
            title = title.decode('utf-8')
        except Exception:
            pass

        html = client.request(url)

        try:

            try:
                pages = client.parseDOM(html, 'li', attrs={'class': 'pager__item pager__item--last'})[0]
                pages = int(re.search(r'(\d{1,3})$', client.parseDOM(pages, 'a', ret='href')[0], re.M).group(1))
            except Exception:
                pages = 0

            if pages:

                view_args = view_path = '/'.join(urlparse(url).path.split('/')[1:-1])

                if 'kentrikodeltio' in url:
                    view_args = view_args.replace('shows', 'news')

                threads = []

                for i in list(range(0, pages + 1)):

                    post = self.ajax_post_episodes.format(view_args=view_args, view_path=view_path, page=str(i))

                    threads.append(workers.Thread(self.thread, i, self.views_ajax, post, False))
                    self.data.append('')
                [i.start() for i in threads]
                [i.join() for i in threads]

                htmls = '\n'.join([json.loads(i)[2]['data'] for i in self.data])

                items = client.parseDOM(htmls, 'article')

            else:

                items = client.parseDOM(html, 'article')

            if not items:
                raise Exception

            for item in items:

                itemtitle = client.parseDOM(item, 'div', attrs={'class': 'itemtitle'})[0]
                label = ' - '.join([title, itemtitle])
                url = client.parseDOM(item, 'a', ret='href')[0]
                url = urljoin(self.basecy_link, url)
                image = client.parseDOM(item, 'img', ret='src')[0]

                data = {'title': label, 'image': image, 'url': url}

                self.list.append(data)

        except Exception:

            self.list = [
                {
                    'title': u' - '.join([title, control.lang(32014)]),
                    'action': 'back',
                    'image': image,
                    'isFolder': 'False', 'isPlayable': 'False'
                }
                ,
                {
                    'title': control.lang(32013),
                    'action': 'back',
                    'image': control.icon(),
                    'isFolder': 'False', 'isPlayable': 'False'
                }
            ]

        return self.list

    def episodes(self, url, title=None, image=None):

        if self.basegr_link in url:
            self.list = cache.get(self.episodes_list_gr, 1, url, title)
        else:
            self.list = cache.get(self.episodes_list_cy, 1, url, title, image)

        if self.list is None:
            return

        for c, i in list(enumerate(self.list, 1)):
            if 'action' not in i:
                i.update({'action': 'play', 'isFolder': 'False', 'code': str(c)})

        control.sortmethods('production_code')

        directory.add(self.list, content='videos')

    def news_index(self, url):

        html = client.request(url)

        items = client.parseDOM(html, 'li', attrs={'class': 'dropable.*?'})

        for item in items:

            title = client.parseDOM(item, 'a')[0].strip().capitalize()
            if title.endswith(u'σ'):
                title = title[:-1] + u'ς'
            category = client.parseDOM(item, 'a', ret='data-catid')[0]
            # url = self.newsgr_link_ajax.format(page='1', category=category)

            self.list.append({'title': title, 'query': category})

        return self.list

    def news(self, url):

        self.list = cache.get(self.news_index, 48, url)

        if self.list is None:
            return

        for i in self.list:
            i.update({'action': 'news_episodes', 'icon': 'news.png'})

        directory.add(self.list, content='videos')

    def news_episodes_listing(self, query):

        threads = []

        for i in list(range(1, 101)):

            threads.append(workers.Thread(self.thread, i, self.newsgr_link_ajax.format(page=str(i), category=query)))
            self.data.append('')
        [i.start() for i in threads]
        [i.join() for i in threads]

        html = '\n'.join(self.data)

        items = client.parseDOM(html, 'div', attrs={'class': 'newsItem'})

        for item in items:

            label = client.replaceHTMLCodes(client.parseDOM(item, 'a')[1])
            title = u'[CR]'.join([label, client.parseDOM(item, 'time')[0]])
            image = client.parseDOM(item, 'img', ret='src')[0]
            url = client.parseDOM(item, 'a', ret='href')[1]

            self.list.append({'title': title, 'image': image, 'url': url})

        return self.list

    def news_episodes(self, query):

        self.list = cache.get(self.news_episodes_listing, 1, query)

        if self.list is None:
            return

        for i in self.list:
            i.update({'action': 'play', 'isFolder': 'False'})

        directory.add(self.list, content='videos')

    def play(self, url):

        if url in [self.live_link_cy, self.live_link_gr]:
            title = 'Alpha'
            icon = control.icon()
        else:
            title = None
            icon = None

        directory.resolve(self.resolve(url), meta={'title': title}, icon=icon)

    def resolve(self, url):

        referer = url

        if '.m3u8' in url or '.mp4' in url or url.startswith('plugin'):
            return url

        html = client.request(url)

        if url == self.live_link_gr:

            url = client.parseDOM(html, 'div', attrs={'class': 'livePlayer'}, ret='data-liveurl')[0]

        elif url == self.live_link_cy:

            url = re.search(r'url: [\'"](.+?\.m3u8.+?)[\'"]', html).group(1)

        elif 'cloudskep' in html:

            url = re.search(r'url: [\'"](.+?\.mp4.*?)[\'"]', html).group(1)

        else:

            if 'data-plugin-player' not in html:

                qs = parse_qs(urlparse(url).query)
                video_id = qs['vid'][0]
                year = qs['year'][0]
                show_id = qs['showId'][0]
                html = client.request(self.player_query.format(video_id=video_id, show_id=show_id, year=year))

            try:
                object_ = client.parseDOM(html, 'div', attrs={'id': 'Video-1'}, ret='data-plugin-player')[0]
            except Exception:
                object_ = client.parseDOM(html, 'div', attrs={'id': 'currentvideourl'}, ret='data-plugin-player')[0]

            url = json.loads(client.replaceHTMLCodes(object_))['Url']

        return url + user_agents.spoofer(referer=True, ref_str=referer)

    def thread(self, i, url, post=None, sleep_=True):

        try:

            result = client.request(url, post=post)
            self.data[i] = result
            if sleep_:
                sleep(0.05)

        except:

            return
