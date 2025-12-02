from typing import Optional
import ssl
import aiohttp
import asyncio


# Allow unsafe legacy renegotiation when verify SSL is disabled
SSL_OP_NO_UNSAFE_LEGACY_RENEGOTIATION = 0x00040000
SSL_CONTEXT_UNSAFE_NO_CHECK = ssl.create_default_context()
SSL_CONTEXT_UNSAFE_NO_CHECK.options &= ~SSL_OP_NO_UNSAFE_LEGACY_RENEGOTIATION
SSL_CONTEXT_UNSAFE_NO_CHECK.check_hostname = False
SSL_CONTEXT_UNSAFE_NO_CHECK.verify_mode = ssl.CERT_NONE
SSL_CONTEXT_UNSAFE_NO_CHECK.minimum_version = ssl.TLSVersion.TLSv1


def get_connector(
            verify_ssl: bool,
            loop: Optional[asyncio.AbstractEventLoop] = None
        ) -> aiohttp.TCPConnector:
    if loop is None:
        loop = asyncio.get_running_loop()

    ssl_context: None | ssl.SSLContext = None
    if verify_ssl is False:
        ssl_context = SSL_CONTEXT_UNSAFE_NO_CHECK

    return aiohttp.TCPConnector(
        limit=100,  # 100 is default
        use_dns_cache=False,
        enable_cleanup_closed=True,
        force_close=True,
        ssl_context=ssl_context,
        loop=loop,
    )
