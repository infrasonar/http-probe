import asyncio
from libprobe.probe import Probe
from lib.check.http import check_http
from lib.connector import init_connector
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'http': check_http
    }

    loop = asyncio.new_event_loop()
    init_connector(loop)

    probe = Probe("http", version, checks)
    probe.start(loop=loop)
