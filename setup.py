from setuptools import setup

setup(
    name='Raitonoberu',
    version='1.0.0',
    packages=['Raitonoberu'],
    url='https://github.com/GetRektByMe/Raitonoberu',
    license='MIT',
    author='Recchan',
    author_email='',
    description='Python 3 Aiohttp Novelupdates Scraper',
    long_description=(
        'Raitonoberu is a Python 3 Asyncio NovelUpdates Website scraper '
        'that is capable of getting useful information for use in applications.'
    ),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries'
    ],
    keywords="NovelUpdates asyncio aiohttp scraping",
    install_requires=['aiohttp', 'bs4', 'lxml'],
)
