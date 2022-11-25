import aiohttp
import asyncio
import logging
from libprobe.asset import Asset
from libprobe.exceptions import CheckException
from ..utils import check_config

DEFAULT_TIMEOUT = 10
DEFAULT_VERIFY_SSL = False
DEFAULT_WITH_PAYLOAD = False
DEFAULT_ALLOW_REDIRECTS = False


async def check_http(
        asset: Asset,
        asset_config: dict,
        config: dict) -> dict:

    try:
        uri = config['uri']
        timeout = config.get('timeout', DEFAULT_TIMEOUT)
        verify_ssl = config.get('verifySSL', DEFAULT_VERIFY_SSL)
        with_payload = config.get('withPayload', DEFAULT_WITH_PAYLOAD)
        allow_redirects = config.get('allowRedirects', DEFAULT_ALLOW_REDIRECTS)

        check_config(uri)
    except Exception as e:
        logging.error(f'invalid check configuration: `{e}`')
        return

    try:
        state_data = await get_data(
            uri, verify_ssl, with_payload, timeout, allow_redirects)
    except aiohttp.ClientSSLError as err:
        # Includes:
        # ClientConnectorCertificateError
        # ClientConnectorSSLError
        logging.error(f'HTTP SSL error (uri: {uri}): `{err}`\n')
        pass
    except asyncio.TimeoutError:
        raise CheckException('Check timed out.')
    except Exception as e:
        raise CheckException(f'Check error: {e.__class__.__name__}: {e}')
    else:
        return state_data


async def get_data(uri, verify_ssl, with_payload, timeout, allow_redirects):
    start = asyncio.get_event_loop().time()
    aiohttp_timeout = aiohttp.ClientTimeout(total=timeout)
    if verify_ssl:
        verify_ssl = None  # None for default SSL check
    async with aiohttp.ClientSession(timeout=aiohttp_timeout) as session:
        async with session.get(
            uri,
            allow_redirects=allow_redirects,
            ssl=verify_ssl
        ) as response:
            payload = None
            if with_payload:
                try:
                    payload = await response.text('UTF-8')  # str
                except UnicodeDecodeError:
                    payload = '<BLOB>'

            response_time = asyncio.get_event_loop().time() - start
            status_code = response.status

            item = {
                'name': uri,  # (str)
                'responseTime': response_time,  # (float, seconds)
                'statusCode': status_code,  # (int, for example 200)
            }

            if isinstance(payload, str):
                item['payload'] = payload

            return {'http': [item]}
