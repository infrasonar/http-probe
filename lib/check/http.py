import ssl
import aiohttp
import asyncio
from libprobe.asset import Asset
from libprobe.check import Check
from libprobe.exceptions import CheckException, IncompleteResultException
from ..utils import check_config
from ..connector import get_connector
from ..version import __version__

DEFAULT_TIMEOUT = 10.0
DEFAULT_VERIFY_SSL = False
DEFAULT_WITH_PAYLOAD = False
DEFAULT_ALLOW_REDIRECTS = False

MAX_PAYLOAD = 512

USER_AGENT = f'InfraSonarHttpProbe/{__version__}'


class CheckHttp(Check):
    key = 'http'
    unchanged_eol = 0

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        try:
            uri = str(config['uri'])
            timeout = float(config.get('timeout', DEFAULT_TIMEOUT))
            verify_ssl = bool(config.get('verifySSL', DEFAULT_VERIFY_SSL))
            with_payload = \
                bool(config.get('withPayload', DEFAULT_WITH_PAYLOAD))
            allow_redirects = \
                bool(config.get('allowRedirects', DEFAULT_ALLOW_REDIRECTS))

            check_config(uri)
        except Exception as e:
            msg = str(e) or type(e).__name__
            raise CheckException(msg)

        try:
            state_data = await get_data(
                uri, verify_ssl, with_payload, timeout, allow_redirects)
        except aiohttp.ClientSSLError as e:
            # Includes:
            # ClientConnectorCertificateError
            # ClientConnectorSSLError
            msg = str(e) or type(e).__name__
            msg = f'HTTP SSL error (uri: {uri}): `{msg}`'
            raise CheckException(msg)
        except asyncio.TimeoutError:
            raise CheckException(f'HTTP check timed out (uri: {uri})')
        except IncompleteResultException:
            raise
        except Exception as e:
            msg = str(e) or type(e).__name__
            raise CheckException(msg)
        else:
            return state_data


async def get_data(
        uri: str,
        verify_ssl: bool,
        with_payload: bool,
        timeout: float,
        allow_redirects: bool) -> dict:

    loop = asyncio.get_running_loop()
    start = loop.time()
    aiohttp_timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(
            timeout=aiohttp_timeout,
            connector=get_connector(loop=loop),
            headers={'User-Agent': USER_AGENT}) as session:
        async with session.get(
            uri,
            allow_redirects=allow_redirects,
            ssl=verify_ssl
        ) as response:
            payload = None
            incomplete = False
            if with_payload:
                try:
                    payload = await response.text('UTF-8')  # str
                except UnicodeDecodeError:
                    payload = '<BLOB>'

            response_time = loop.time() - start
            status_code = response.status

            item = {
                'name': uri,  # (str)
                'responseTime': response_time,  # (float, seconds)
                'statusCode': status_code,  # (int, for example 200)
            }

            if isinstance(payload, str):
                item['payload'] = payload[:MAX_PAYLOAD]
                incomplete = len(payload) > MAX_PAYLOAD

            result = {'http': [item]}
            if incomplete:
                raise IncompleteResultException(
                    'Payload too large', result)
            return result
