# Third Party Libraries
import aiohttp
from bs4 import BeautifulSoup


class Raitonoberu:

    # Baseurl for novelupdates
    BASEURL = 'http://www.novelupdates.com/'

    def __init__(self, user_agent=None, session=None):
        # Set default user-agent
        self.headers = user_agent or {"User-Agent": "Raitonoberu"}
        # Give the user the option of using their own client session
        self.session = session or aiohttp.ClientSession(headers=self.headers)

    # Closes the session on exit, stopping the unclosed client session error
    def __del__(self):
        self.session.close()

    async def get_search_page(self, term: str):
        """
        This function will get the first link from the search term we do on term and then it will return the link we want to parse from.

        :param term: Light Novel to Search For
        """
        # Uses the BASEURL and also builds link for the page we want using the term given
        async with self.session.get(self.BASEURL, params={'s': term, 'post_type': 'seriesplan'}) as response:
            # If the response is 200 OK
            if response.status == 200:
                search = BeautifulSoup(await response.text(), 'lxml')
                # Return the link that we need
                return search.find('a', class_='w-blog-entry-link').get('href')
            else:
                # Raise an error with the response status
                raise aiohttp.ClientResponseError(response.status)

    async def get_first_search_result(self, term: str):
        """
        This function will parse the information from the link that search_novel_updates returns and then return it as a dictionary

        :param term: The novel to search for and parse
        """
        # Uses the other method in the class to search the search page for the actual page that we want
        to_parse = await self.get_search_page(term)

        async with self.session.get(to_parse) as response:
            # If the response is OK
            if response.status == 200:
                # The information to parse
                parse_info = BeautifulSoup(await response.text(), 'lxml')
                # Artists, defined up here so we can account for if it is None, e.g. for web novels ect
                artists = parse_info.find('a', class_='genre', id='artiststag')
                # English publisher, defined here so we can account for it if None, e.g. for works unlicensed in English
                english_publisher = parse_info.find('a', class_='genre', id='myepub')
                # Publisher, defined here so we can account for it if it's None, e.g. not published
                publisher = parse_info.find('a', class_='genre', id='myopub')
                # Accounting for if Artists/English Publisher/Publisher is None
                if artists is not None:
                    artists = artists.string
                if english_publisher is not None:
                    english_publisher = english_publisher.children.string
                if publisher is not None:
                    publisher = publisher.string

                # The data to return to the user, in a dictionary
                data = {'title': parse_info.find('h4', class_='seriestitle new').string,
                        'cover': None if parse_info.find('img').get('src') == 'http://www.novelupdates.com/img/noimagefound.jpg' else parse_info.find('img').get('src'),
                        'type': parse_info.find('a', class_='genre type').string,
                        'genre': [x.string for x in list(parse_info.find_all('div', id='seriesgenre')[0].children) if len(x.string.strip()) > 0],
                        'tags': [x.string for x in list(parse_info.find_all('div', id='showtags')[0].children) if len(x.string.strip()) > 0],
                        'language': parse_info.find('a', class_='genre lang').string,
                        'authors': list(set([x.string for x in parse_info.find_all('a', id='authtag')])),
                        'artists': artists,
                        'year': parse_info.find('div', id='edityear').string.strip(),
                        'novel_status': parse_info.find('div', id='editstatus').string.strip(),
                        'licensed': True if parse_info.find('div', id='showlicensed').string.strip() == 'Yes' else False,
                        'completely_translated': True if len(list(parse_info.find('div', id='showtranslated').descendants)) > 1 else False,
                        'publisher': publisher,
                        'english_publisher': english_publisher,
                        'description': ' '.join([x.string.strip() for x in list(parse_info.find('div', id='editdescription').children) if x.string.strip()]),
                        'aliases': [x.string for x in parse_info.find('div', id='editassociated') if x.string is not None],
                        'link': to_parse}
                # Returning the dictionary with all of the information from novelupdates that we parsed
                return data
            else:
                # Raise an error with the response status
                raise aiohttp.ClientResponseError(response.status)
