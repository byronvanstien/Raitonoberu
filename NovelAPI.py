import asyncio
import aiohttp
from bs4 import BeautifulSoup

"""
Currently Broken:
related
"""


class NovelUpdatesAPI:
    def __init__(self):
        """The base url that we'll be ripping information from"""
        self.baseurl = 'http://www.novelupdates.com/'
        self.session = aiohttp.ClientSession()

    async def search_novel_updates(self, term: str):
        """
        This function will get the first link from the search term we do on term and then it will return the link we want to parse from.


        :param term: Light Novel to Search For
        """
        term = term.replace(' ', '+')
        params = {'s': term, 'post_type': 'seriesplan'}
        async with self.session.get(self.baseurl, params=params) as response:
            if response.status == 200:
                search = BeautifulSoup(await response.text(), 'lxml')
                parsedsearch = search.find('a', class_='w-blog-entry-link').get('href')
                return parsedsearch
            else:
                raise aiohttp.ClientResponseError(response.status)

    async def page_info_parser(self, term):
        """
        This function will parse the information from the link that search_novel_updates returns and then return it as a dictionary


        :param term: The novel to search for and parse
        """
        to_parse = await self.search_novel_updates(term)
        async with self.session.get(to_parse) as response:
            if response.status == 200:
                html = await response.text()
                parse_info = BeautifulSoup(html, 'lxml')
                data = {'title': parse_info.find('h4', class_='seriestitle new').string,
                        'cover': parse_info.find('img').get('src'),
                        'type': parse_info.find('a', class_='genre type').string,
                        'genre': list(set([x.string for x in list(parse_info.find_all('div', id='seriesgenre')[0].children) if len(x.string.strip()) > 0])),
                        'tags': list(set([x.string for x in list(parse_info.find_all('div', id='showtags')[0].children) if len(x.string.strip()) > 0])),
                        'language': parse_info.find('a', class_='genre lang').string,
                        'authors': list(set([x.string for x in parse_info.find_all('a', attrs={'id': 'authtag'})])),
                        'artists': list(set([x.string for x in parse_info.find_all('span', attrs={'class': 'seriesna'})])),
                        'year': parse_info.find('div', attrs={'id': 'edityear'}).string.strip(),
                        'novel status': parse_info.find('div', attrs={'id': 'editstatus'}).string.strip(),
                        'licensed': parse_info.find('div', attrs={'id': 'showlicensed'}).string.strip(),
                        'completely translated': parse_info.find('div', attrs={'id': 'showtranslated'}).string.strip(),
                        'publisher': parse_info.find('a', attrs={'class': 'genre', 'id': 'myopub'}).string,
                        'english publisher': parse_info.find('span', class_='seriesna').string,
                        'description': parse_info.find('div', attrs={'id': 'editdescription'}).p.string,
                        'aliases': list(set([x.string for x in parse_info.find('div', attrs={'id': 'editassociated'}) if x.string is not None])),
                        'related': list(set(parse_info.find_all('a', class_='genre'))),  # related novels is in here as well as extras
                        'link': to_parse}
                return data
            else:
                raise aiohttp.ClientResponseError(response.status)
