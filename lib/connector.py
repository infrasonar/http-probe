from typing import Optional
import aiohttp
import asyncio


connector: Optional[aiohttp.TCPConnector] = None


def init_connector(loop: asyncio.AbstractEventLoop):
    global connector
    connector = aiohttp.TCPConnector(
        limit=100,  # 100 is default
        use_dns_cache=False,
        enable_cleanup_closed=True,
        force_close=True,
        loop=loop,
    )
