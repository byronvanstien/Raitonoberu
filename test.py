from Raitonoberu import Raitonoberu
import asyncio
import aiohttp


class Why():
    def __init__(self):
        self.session = aiohttp.ClientSession(headers={"User-Agent": "Recchie"})
        self.r = Raitonoberu(session=self.session)

    async def print_some_results(self, novel_name: str):
        rip = await self.r.page_info_parser(novel_name)
        return rip

if __name__ == "__main__":
    why = Why()
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(why.print_some_results("Sword Art Online")))
