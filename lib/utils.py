from urllib.parse import urlparse


def check_config(uri):
    o = urlparse(uri)
    if o.scheme not in ('http', 'https'):
        raise Exception(f'uri should start with "http" or "https", got: {uri}')
