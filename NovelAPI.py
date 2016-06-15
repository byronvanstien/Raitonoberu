import aiohttp
from bs4 import BeautifulSoup

onlysession = aiohttp.ClientSession()


class NovelUpdatesAPI:
    def __init__(self):
        self.baseurl = 'http://www.novelupdates.com/'

    async def search_novel_updates(self, term: str):
        term = term.replace(' ', '+')
        params = {'s': term, 'post_type': 'seriesplan'}
        with onlysession as session:
            async with session.get(self.baseurl, params=params) as response:
                assert isinstance(response, aiohttp.ClientResponse)
                assert response.status == 200
                search = BeautifulSoup(await response.text(), 'lxml')
                parsedsearch = search.find('a', class_='w-blog-entry-link').get('href')
                return parsedsearch

    async def page_info_parser(self, term):
        to_parse = await self.search_novel_updates(term)
        with onlysession as session:
            async with session.get(to_parse) as response:
                assert isinstance(response, aiohttp.ClientResponse)
                assert response.status == 200
            parse_info = BeautifulSoup(await response.text(), 'lxml')
            data = {'title': parse_info.find(class_='seriestitle new'),
                'cover': parse_info.find('img').get('src'),
                'type': parse_info.find('a', class_='genre type').text(),
                'genre': parse_info.find_all('a', class_='genre').text(),
                'tags': parse_info.find_all('a', class_='genre odd').text(),
                'rating': parse_info.find('span', class_='votetext').text(),
                'language': parse_info.find('a', class_='genre lang').text(),
                'author': parse_info.find('a', class_='authtag').text(),
                'artist': parse_info.find('a', class_='artiststag').text(),
                'year': parse_info.find('div', id_='edityear').text(),
                'novel_status': parse_info.find('div', id_='editstatus').text(),
                'licensed': parse_info.find('div', id_='showlicensed').text(),
                'completely_translated': parse_info.find('div', id_='showtranslated').text(),
                'publisher': parse_info.find('a', class_='genre', id_='myopub').text(),
                'english_publisher': parse_info.find('span', class_='seriesna').text(),
                'frequency': parse_info.find('h5', class_='seriesother').text(),
                'description': parse_info.find('div', id_='editdescription').text().strip(),
                'aliases': parse_info.find('div', id_='editassociated').text(),
                'related': parse_info.find('h5', class_='seriesother').text()}

            return data
