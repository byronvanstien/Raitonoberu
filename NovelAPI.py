import asyncio
import aiohttp
from bs4 import BeautifulSoup

session = aiohttp.ClientSession()


class NovelUpdatesAPI:
    def __init__(self):
        """The base url that we'll be ripping information from"""
        self.baseurl = 'http://www.novelupdates.com/'

    async def search_novel_updates(self, term: str):
        """This function will get the first link from the search term we do on term and then it will return the link we want to parse from."""
        term = term.replace(' ', '+')
        params = {'s': term, 'post_type': 'seriesplan'}
        async with session.get(self.baseurl, params=params) as response:
            assert isinstance(response, aiohttp.ClientResponse)
            assert response.status == 200
            search = BeautifulSoup(await response.text(), 'lxml')
            parsedsearch = search.find('a', class_='w-blog-entry-link').get('href')
            return parsedsearch

    async def page_info_parser(self, term):
        """This function will parse the information from the link that search_novel_updates returns and then return it as a dictionary"""
        to_parse = await self.search_novel_updates(term)
        async with session.get(to_parse) as response:
            assert isinstance(response, aiohttp.ClientResponse)
            assert response.status == 200
            html = await response.text()
        parse_info = BeautifulSoup(html, 'lxml')
        genres = []
        data = {'title': parse_info.find('h4', class_='seriestitle new').string,
                'cover': parse_info.find('img').get('src'),
                'type': parse_info.find('a', class_='genre type').string,
                'genre': [x.string for x in parse_info.find_all('div', id='seriesgenre')[0].children],
                'tags': [x.string for x in parse_info.find_all('a', class_='genre odd')],
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
        for items in data['genre']:
            genres.append(items)
            if data[items] == ' ' or data[items] == 'newline':
                del data[items]
        for i in genres:
            print(i)
        session.close()
        return data

if __name__ == '__main__':
    n = NovelUpdatesAPI()
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(n.page_info_parser('Sword art online')))

