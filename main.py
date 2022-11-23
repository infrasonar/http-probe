from libprobe.probe import Probe
from lib.check.http import check_http
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'http': check_http
    }

    probe = Probe("http", version, checks)

    probe.start()
