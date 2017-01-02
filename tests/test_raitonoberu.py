from unittest import mock
from itertools import product

import pytest


@pytest.mark.parametrize(
    'user_agent, session',
    product(
        [None, mock.Mock()],
        [None, mock.Mock()]
    )
)
def test_init(user_agent, session):
    with mock.patch('Raitonoberu.raitonoberu.aiohttp') as m_aio:
        from Raitonoberu.raitonoberu import Raitonoberu
        # run
        obj = Raitonoberu(user_agent, session)
        # test
        if user_agent is None:
            obj.headers == {"User-Agent": "Raitonoberu"}
        else:
            obj.headers == user_agent
        if session is None:
            obj.session == m_aio.ClientSession.return_value
            m_aio.ClientSession.assert_called_once_with(headers=obj.headers)
        else:
            obj.session == session


def test_del():
    session = mock.Mock()
    with mock.patch('Raitonoberu.raitonoberu.Raitonoberu.__init__', return_value=None):
        from Raitonoberu.raitonoberu import Raitonoberu
        obj = Raitonoberu()
        obj.session = session
        # run
        del obj
        # test
        session.close.assert_called_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize('term', ['term'])
async def test_get_search_page(term):
    from Raitonoberu.raitonoberu import Raitonoberu
    obj = Raitonoberu()
    # run
    res = await obj.get_search_page(term=term)
    # test
    # the actual result with 'term' as input is
    # 'http://www.novelupdates.com/series/the-last-apostle/'
    assert res.startswith('http://www.novelupdates.com/series/')


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'term, exp_res',
    [
        (
            'smiling proud wanderer',
            {
                'aliases': [
                    'Laughing in the Wind',
                    'State of Divinity',
                    'The Peerless Gallant Errant',
                    'The Proud and Gallant Wanderer',
                    'Xiao Ao Jiang Hu',
                    '笑傲江湖'
                ],
                'artists': None,
                'authors': ['Jin Yong'],
                'completely_translated': True,
                'cover': (
                    'http://www.novelupdates.com/wp-content/uploads/2015/10'
                    '/220px-The_Smiling_Proud_Wanderer_笑傲江湖1.jpg'
                ),
                'description': (
                    'The Smiling, Proud Wanderer is a wuxia novel by Jin Yong (Louis Cha). '
                    'It was first serialised in Hong Kong in the newspaper Ming Pao '
                    'from 20 April 1967 to 12 October 1969. The Chinese title of the novel, '
                    'Xiao Ao Jiang Hu, '
                    'literally means to live a carefree life in a mundane world of strife. '
                    'Alternate English translations of the title include '
                    'Laughing in the Wind, '
                    'The Peerless Gallant Errant, and The Proud and Gallant Wanderer. '
                    'Another alternative title, State of Divinity, '
                    'is used for some of the novel’s adaptations.'
                ),
                'english_publisher': None,
                'genre': ['Action', 'Adventure', 'Martial Arts', 'Wuxia'],
                'language': 'Chinese',
                'licensed': False,
                'link': 'http://www.novelupdates.com/series/smiling-proud-wanderer/',
                'novel_status': '4 Volumes (Completed)\n40 Chapters (Completed)',
                'publisher': 'Ming Pao',
                'tags': [
                    'Adapted To Drama', 'Adapted to Manhua', 'Adapted To Movie', 'Betrayal',
                    'Misunderstandings', 'Politics', 'Revenge', 'Special Abilities'
                ],
                'title': 'Smiling Proud Wanderer',
                'type': 'Chinese Novel',
                'year': '1967'
            }
        )
    ]

)


async def test_get_first_search_result(term, exp_res):
    from Raitonoberu.raitonoberu import Raitonoberu
    obj = Raitonoberu()
    # run
    res = await obj.get_first_search_result(term=term)
    # test
    assert res == exp_res
