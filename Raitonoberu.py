import urllib

import aiohttp
from bs4 import BeautifulSoup


class NovelUpdatesAPI:
    BASEURL = 'http://www.novelupdates.com/'

    def __init__(self):
        """The base url that we'll be ripping information from"""
        self.session = aiohttp.ClientSession()

    def __del__(self):
        self.session.close()

    async def search_novel_updates(self, term: str):
        """
        This function will get the first link from the search term we do on term and then it will return the link we want to parse from.


        :param term: Light Novel to Search For
        """
        params = urllib.parse.urlencode({'s': term, 'post_type': 'seriesplan'})
        async with self.session.get(self.BASEURL, params=params) as response:
            if response.status == 200:
                search = BeautifulSoup(await response.text(), 'lxml')
                return search.find('a', class_='w-blog-entry-link').get('href')
            else:
                raise aiohttp.ClientResponseError(response.status)

    async def page_info_parser(self, term: str):
        """
        This function will parse the information from the link that search_novel_updates returns and then return it as a dictionary


        :param term: The novel to search for and parse
        """
        to_parse = await self.search_novel_updates(term)
        async with self.session.get(to_parse) as response:
            if response.status == 200:
                parse_info = BeautifulSoup(await response.text(), 'lxml')
                artists = parse_info.find('a', class_='genre', id='artiststag')
                english_publisher = parse_info.find('a', class_='genre', id='myepub')
                if artists is not None:
                    artists = artists.string
                if english_publisher is not None:
                    english_publisher = english_publisher.children.string
                data = {'title': parse_info.find('h4', class_='seriestitle new').string,
                        'cover': None if parse_info.find('img').get(
                            'src') == 'http://www.novelupdates.com/img/noimagefound.jpg' else parse_info.find(
                            'img').get('src'),
                        'type': parse_info.find('a', class_='genre type').string,
                        'genre': [x.string for x in list(parse_info.find_all('div', id='seriesgenre')[0].children) if
                                  len(x.string.strip()) > 0],
                        'tags': [x.string for x in list(parse_info.find_all('div', id='showtags')[0].children) if
                                 len(x.string.strip()) > 0],
                        'language': parse_info.find('a', class_='genre lang').string,
                        'authors': list(set([x.string for x in parse_info.find_all('a', id='authtag')])),
                        'artists': artists,
                        'year': parse_info.find('div', id='edityear').string.strip(),
                        'novel_status': parse_info.find('div', id='editstatus').string.strip(),
                        'licensed': True if parse_info.find('div',
                                                            id='showlicensed').string.strip() == 'Yes' else False,
                        'completely_translated': True if len(
                            list(parse_info.find('div', id='showtranslated').descendants)) > 1 else False,
                        'publisher': parse_info.find('a', class_='genre', id='myopub').string,
                        'english_publisher': english_publisher,
                        'description': ' '.join(
                            [x.string.strip() for x in list(parse_info.find('div', id='editdescription').children) if
                             x.string.strip()]),
                        'aliases': [x.string for x in parse_info.find('div', id='editassociated') if
                                    x.string is not None],
                        'link': to_parse}
                return data
            else:
                raise aiohttp.ClientResponseError(response.status)
