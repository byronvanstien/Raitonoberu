from pprint import  pformat

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
        """Get search page.

        This function will get the first link from the search term we do on term and then
        it will return the link we want to parse from.

        :param term: Light Novel to Search For
        """
        # Uses the BASEURL and also builds link for the page we want using the term given
        params = {'s': term, 'post_type': 'seriesplan'}
        async with self.session.get(self.BASEURL, params=params) as response:
            # If the response is 200 OK
            if response.status == 200:
                search = BeautifulSoup(await response.text(), 'lxml')
                # Return the link that we need
                return search.find('a', class_='w-blog-entry-link').get('href')
            else:
                # Raise an error with the response status
                raise aiohttp.ClientResponseError(response.status)

    @staticmethod
    def _get_title(parse_info):
        """get title from parse info.

        :param parse_info: Parsed info from html soup.
        """
        return parse_info.select_one('.seriestitlenu').string

    @staticmethod
    def _get_novel_status(parse_info):
        """get title from parse info.

        :param parse_info: Parsed info from html soup.
        """
        return parse_info.select_one('#editstatus').text.strip()

    @staticmethod
    def _get_aliases(parse_info):
        """get aliases from parse info.

        :param parse_info: Parsed info from html soup.
        """
        return [
            x.string.strip()
            for x in parse_info.find('div', id='editassociated')
            if x.string is not None
        ]

    @staticmethod
    def _get_related_series(parse_info):
        """get related_series from parse info.

        :param parse_info: Parsed info from html soup.
        """
        seriesother_tags = [
            x for x in parse_info.select('h5.seriesother')]
        sibling_tag = [x for x in seriesother_tags if x.text == 'Related Series'][0]
        siblings_tag = list(sibling_tag.next_siblings)

        # filter valid tag
        # valid tag is all tag before following tag
        # <h5 class="seriesother">Recommendations</h5>
        valid_tag = []
        keypoint_found = False
        for x in siblings_tag:
            # change keypoint if condition match
            if x.name == 'h5' and x.attrs['class'] == ['seriesother']:
                    keypoint_found = True

            if not keypoint_found and x.strip is not None:
                if x.strip():
                    valid_tag.append(x)
            elif not keypoint_found:
                valid_tag.append(x)

        # only one item found and it is 'N/A
        if len(valid_tag) == 1:
            if valid_tag[0].strip() == 'N/A':
                return None

        # items are combination between bs4 and text
        # merge and return them as list of text
        if len(valid_tag) % 2 == 0:
            zipped_list = zip(valid_tag[::2], valid_tag[1::2])
            result = []
            for x in zipped_list:
                result.append('{} {}'.format(x[0].text, x[1]))
            return result

        raise ValueError("Valid tag isn't recognizeable.\n{}".format(pformat(valid_tag)))


    async def get_first_search_result(self, term: str):
        """Get first search result.

        This function will parse the information from the link that search_novel_updates returns
        and then return it as a dictionary

        :param term: The novel to search for and parse
        """
        # Uses the other method in the class
        # to search the search page for the actual page that we want
        to_parse = await self.get_search_page(term)

        async with self.session.get(to_parse) as response:
            # If the response is OK
            if response.status == 200:
                # The information to parse
                parse_info = BeautifulSoup(await response.text(), 'lxml')
                # Artists,
                # defined up here so we can account for if it is None, e.g. for web novels ect
                artists = parse_info.find('a', class_='genre', id='artiststag')
                # English publisher,
                # defined here so we can account for it if None,
                # e.g. for works unlicensed in English
                english_publisher = parse_info.find('a', class_='genre', id='myepub')
                # Publisher,
                # defined here so we can account for it if it's None, e.g. not published
                publisher = parse_info.find('a', class_='genre', id='myopub')
                # Accounting for if Artists/English Publisher/Publisher is None
                if artists is not None:
                    artists = artists.string
                if english_publisher is not None:
                    english_publisher = english_publisher.children.string
                if publisher is not None:
                    publisher = publisher.string

                # The data to return to the user, in a dictionary
                no_img_found_url = 'http://www.novelupdates.com/img/noimagefound.jpg'
                data = {'title': self._get_title(parse_info=parse_info),
                        'cover': (
                            None
                            if parse_info.find('img').get('src') == no_img_found_url
                            else parse_info.find('img').get('src')
                        ),
                        'type': parse_info.find('a', class_='genre type').string,
                        'genre': (
                            [
                                x.string
                                for x in list(
                                    parse_info.find_all('div', id='seriesgenre')[0].children
                                )
                                if len(x.string.strip()) > 0
                            ]
                        ),
                        'tags': (
                            [
                                x.string
                                for x in list(
                                    parse_info.find_all('div', id='showtags')[0].children
                                )
                                if len(x.string.strip()) > 0
                            ]
                        ),
                        'language': parse_info.find('a', class_='genre lang').string,
                        'authors': list(
                            set([x.string for x in parse_info.find_all('a', id='authtag')])
                        ),
                        'artists': artists,
                        'year': parse_info.find('div', id='edityear').string.strip(),
                        'novel_status': self._get_novel_status(parse_info=parse_info),
                        'licensed': (
                            True
                            if parse_info.find('div', id='showlicensed').string.strip() == 'Yes'
                            else False
                        ),
                        'completely_translated': (
                            True
                            if len(
                                list(parse_info.find('div', id='showtranslated').descendants)
                            ) > 1
                            else False
                        ),
                        'publisher': publisher,
                        'english_publisher': english_publisher,
                        'description': (
                            ' '.join(
                                [
                                    x.string.strip()
                                    for x in list(
                                        parse_info.find('div', id='editdescription').children
                                    )
                                    if x.string.strip()
                                ]
                            )
                        ),
                        'aliases': self._get_aliases(parse_info=parse_info),
                        'link': to_parse,
                        'related_series': self._get_related_series(parse_info=parse_info)}
                # Returning the dictionary with all of the information
                # from novelupdates that we parsed
                return data
            else:
                # Raise an error with the response status
                raise aiohttp.ClientResponseError(response.status)
