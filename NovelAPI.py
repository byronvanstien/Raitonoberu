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
            data['title'] = parse_info.find(class_='seriestitle new')
            data['cover'] = parse_info.find('img').get('src')
            data['type'] = parse_info.find('a', class_='genre type').text()
            data['genre'] = parse_info.find_all('a', class_='genre').text()
            data['tags'] = parse_info.find_all('a', class_='genre odd').text()
            data['rating'] = parse_info.find('span', class_='votetext').text()
            data['language'] = parse_info.find('a', class_='genre lang').text()
            data['author'] = parse_info.find('a', class_='authtag').text()
            data['artist'] = parse_info.find('a', class_='artiststag').text()
            data['year'] = parse_info.find('div', id_='edityear').text()
            data['novel_status'] = parse_info.find('div', id_='editstatus').text()
            data['licensed'] = parse_info.find('div', id_='showlicensed').text()
            data['completely_translated'] = parse_info.find('div', id_='showtranslated').text()
            data['publisher'] = parse_info.find('a', class_='genre', id_='myopub').text()
            data['english_publisher'] = parse_info.find('span', class_='seriesna').text()
            data['frequency'] = parse_info.find('h5', class_='seriesother').text()
            data['description'] = parse_info.find('div', id_='editdescription').text().strip()
            data['aliases'] = parse_info.find('div', id_='editassociated').text()
            data['related'] = parse_info.find('h5', class_='seriesother').text()

            return data
