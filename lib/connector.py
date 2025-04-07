from typing import Optional
import aiohttp
import asyncio


_connector: Optional[aiohttp.TCPConnector] = None


def get_connector(loop: Optional[asyncio.AbstractEventLoop] = None):
    global _connector
    if _connector is None:
        if loop is None:
            loop = asyncio.get_running_loop()

        _connector = aiohttp.TCPConnector(
            limit=100,  # 100 is default
            use_dns_cache=False,
            enable_cleanup_closed=True,
            force_close=True,
            loop=loop,
        )
    return _connector
