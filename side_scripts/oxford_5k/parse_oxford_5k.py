import asyncio
from collections import defaultdict
from urllib.parse import urlparse

import aiohttp
import aiopathlib

DATASET_URL = "https://raw.githubusercontent.com/nalgeon/words/main/data/oxford-5k.csv"
DATASET_FILE = aiopathlib.AsyncPath("oxford_5k.csv")

WORD_IDX, LEVEL_IDX, _, DEFINITION_URL, PRONUNCIATION_URL = range(5)


# https://stackoverflow.com/a/49717630
class Limiter:
    # domain -> req/sec:
    _limits = {
        'api.dictionaryapi.dev': 1,
    }

    # domain -> it's lock:
    _locks = defaultdict(lambda: asyncio.Lock())

    # domain -> it's last request time
    _times = defaultdict(lambda: 0)

    def __init__(self, url):
        self._host = urlparse(url).hostname

    async def __aenter__(self):
        await self._lock

        to_wait = self._to_wait_before_request()
        print(f'Wait {to_wait} sec before next request to {self._host}')
        await asyncio.sleep(to_wait)

    async def __aexit__(self, *args):
        print(f'Request to {self._host} just finished')

        self._update_request_time()
        self._lock.release()

    @property
    def _lock(self):
        """Lock that prevents multiple requests to same host."""
        return self._locks[self._host]

    def _to_wait_before_request(self):
        """What time we need to wait before request to host."""
        request_time = self._times[self._host]
        request_delay = 1 / self._limits[self._host]
        now = asyncio.get_event_loop().time()
        to_wait = request_time + request_delay - now
        to_wait = max(0, to_wait)
        return to_wait

    def _update_request_time(self):
        now = asyncio.get_event_loop().time()
        self._times[self._host] = now


async def download_dataset(session: aiohttp.ClientSession):
    async with session.get(DATASET_URL) as resp:
        resp.raise_for_status()
        await DATASET_FILE.write_bytes(await resp.read())


async def get_definition(session: aiohttp.ClientSession, word_row: str):
    word_data = word_row.split(',')
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_data[WORD_IDX]}"
    async with Limiter(url):
        async with session.get(url) as response:
            return await response.json(), word_data


async def main():
    exists = await DATASET_FILE.exists()
    async with aiohttp.ClientSession() as session:
        if not exists:
            await download_dataset(session)

        dataset = (await DATASET_FILE.read_text()).split('\n')[1:]
        results = await asyncio.gather(*[get_definition(session, entry) for entry in dataset])
        a = 3


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
