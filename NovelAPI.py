import asyncio
import aiohttp
from bs4 import BeautifulSoup


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
                genres = []
                data = {'title': parse_info.find('h4', class_='seriestitle new').string,
                        'cover': parse_info.find('img').get('src'),
                        'type': parse_info.find('a', class_='genre type').string,
                        'genre': [x.string for x in list(parse_info.find_all('div', id='seriesgenre')[0].children) if len(x.string.strip()) > 0],
                        'tags': [x.string for x in list(parse_info.find_all('div', id='showtags')[0].children) if len(x.string.strip()) > 0],
                        'language': parse_info.find('a', class_='genre lang'),
                        'author': parse_info.find('a', class_='authtag'),
                        'artist': parse_info.find('a', class_='artiststag'),
                        'year': parse_info.find('div', id_='edityear'),
                        'novel_status': parse_info.find('div', id_='editstatus'),
                        'licensed': parse_info.find('div', id_='showlicensed'),
                        'completely_translated': parse_info.find('div', id_='showtranslated'),
                        'publisher': parse_info.find('a', class_='genre', id_='myopub'),
                        'english_publisher': parse_info.find('span', class_='seriesna'),
                        'description': parse_info.find('div', id_='editdescription'),
                        'aliases': parse_info.find('div', id_='editassociated'),
                        'related': parse_info.find('h5', class_='seriesother'),
                        'link': to_parse}
                return data
            else:
                raise aiohttp.ClientResponseError(response.status)
