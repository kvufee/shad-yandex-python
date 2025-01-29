import aiohttp
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor


async def async_fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Asyncronously fetch (get-request) single url using provided session
    :param session: aiohttp session object
    :param url: target http url
    :return: fetched text
    """

    async with session.get(url) as response:
        return await response.text()


async def async_requests(urls: list[str]) -> list[str]:
    """
    Concurrently fetch provided urls using aiohttp
    :param urls: list of http urls ot fetch
    :return: list of fetched texts
    """
    async with aiohttp.ClientSession() as session:
        tasks = [async_fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)


def sync_fetch(session: requests.Session, url: str) -> str:
    """
    Syncronously fetch (get-request) single url using provided session
    :param session: requests session object
    :param url: target http url
    :return: fetched text
    """
    response = session.get(url)
    return response.text


def threaded_requests(urls: list[str]) -> list[str]:
    """
    Concurrently fetch provided urls with requests in different threads
    :param urls: list of http urls ot fetch
    :return: list of fetched texts
    """
    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        with requests.Session() as session:
            results = list(executor.map(lambda url: sync_fetch(session, url), urls))

    return results
