import urllib

from model.base.ip_locator_exception import IPLocatorResolvingHostnameException


def get_hostname_of_url(url: str):
    try:
        hostname = urllib.parse.urlsplit(url).hostname
    except Exception as error:
        raise IPLocatorResolvingHostnameException(f'Error resolving hostname: {error}')
    return hostname
