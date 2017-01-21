from setuptools import setup, find_packages

from Raitonoberu import (
    __version__ as version,
    __author__ as author,
    __license__ as license,
    __title__ as title
)

setup(
    name=title,
    version=version,
    packages=find_packages(),
    url='https://github.com/GetRektByMe/Raitonoberu',
    license=license,
    author=author,
    author_email='',
    description='Python 3 asynchronous novelupdates scraper',
    long_description="Raitonoberu is a Python 3 Asyncio NovelUpdates Website scraper that is capable of getting useful information for use in applications.",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries'
    ],
    keywords=["NovelUpdates", "asyncio", "aiohttp", "scraping"],
    install_requires=['aiohttp', 'bs4', 'lxml'],
)
