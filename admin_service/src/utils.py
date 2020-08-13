import urllib.parse as urlparse


def clean_hostname(url):
    hostname = urlparse.urlparse(url).hostname
    hostname = hostname.replace("https://", "")
    hostname = hostname.replace("http://", "")
    hostname = hostname.replace("www.", "")
    return hostname