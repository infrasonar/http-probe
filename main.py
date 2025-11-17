from libprobe.probe import Probe
from lib.check.http import CheckHttp
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckHttp,
    )

    probe = Probe("http", version, checks)
    probe.start()
