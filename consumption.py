#
# eGUIDE.io
#
# License: https://github.com/eGUIDE/eguide-consumption-api/blob/master/LICENSE
# Github:  https://github.com/eGUIDE/consumption-api-python-client
#
# Python client for eGUIDE energy consumption API. For more information see
# https://eguide.io/

"""
# Usage for readme

>>> from consumption import Client
>>> consumption = Client(apikey='USE YOUR API KEY HERE')

# action 1
>>> lat_long_result = consumption.latlong(lat=134324, lon=1231)

# action 2
>>> from consumption import polygon
>>> my_polygon = polygon.from_string("polygon string")
>>> polygon_result = consumption.polygon()

# action 3

for more usage examples check out the tests.
"""

from datetime import datetime
import requests
from urllib.parse import urlencode

_VERSION = "0.1"

_USER_AGENT = "ConsumptionAPiClientPython/%s" % _VERSION
_DEFAULT_BASE_URL = "https://api.eguide.io/v0"


class Client(object):
    """Performs requests to the eGUIDE Consumption API web services."""

    host = 'https://api.eguide.io/'
    base_path = 'v0'
    api_field = 'apikey'
    protocol = 'http'
    api_name = 'Consumption'

    def __init__(self, apikey=None, redirect_uri=None, timeout=None, base_url=_DEFAULT_BASE_URL, requests_kwargs=None):
        """
        :param apikey: consumption API key. Required.
        :type apikey: string

        :param requests_kwargs: Extra keyword arguments for the requests
            library, which among other things allow for proxy auth to be
            implemented. See the official requests docs for more info:
            http://docs.python-requests.org/en/latest/api/#main-interface
        :type requests_kwargs: dict

        :param base_url: The base URL for all requests. Defaults to the consumption API
            server. Should not have a trailing slash.
        :type base_url: string
        """
        if not apikey:
            raise ValueError("Must provide API key when creating client.")

        self.session = requests.Session()
        self.apikey = apikey

        self.requests_kwargs = requests_kwargs or {}
        headers = self.requests_kwargs.pop('headers', {})
        headers.update({"User-Agent": _USER_AGENT})
        headers.update({'x-api-key': self.apikey})

        self.requests_kwargs.update({
            "headers": headers,
            })

        self.base_url = base_url

    def latlong(self, lat, lon):
        """Perform a consumption query on a given lat/long location
        """
        url = "/prediction"

        # construct_aoi_latlong()
        aoi = f"POINT({lat} {lon}"

        # construct params
        params = {"aoi": aoi}

        req = self._request(url, params)

        return req

    def _request(self, url, params, base_url=None, first_request_time=None, verbose=False, requests_kwargs=None):
        """Performs HTTP GET with credentials, returning the body as JSON

        :param url: URL path for the request. Should begin with a slash.
        :type url: string

        :param params: HTTP GET parameters.
        :type params: dict of list of key/value tuples

        :param requests_kwargs: Same extra keywords arg for requests as per
            __init__, but provided here to allow overriding internally on a
            per-request basis.
        :type requests_kwargs: dict

        :raises ApiError: when the API returns an error.
        """

        if not first_request_time:
            first_request_time = datetime.now()

        if base_url is None:
            base_url = self.base_url

        elapsed = datetime.now() - first_request_time
        # TODO: to catch timeouts
        # if elapsed > self.retry_timeout:
        #     raise TimeOutException()

        # create url :: self._generate_query_url(url, params)
        query_url = url

        # url encoding of params
        # TODO: use urlencoding here on params

        requests_kwargs = requests_kwargs or {}
        final_requests_kwargs = dict(self.requests_kwargs, **requests_kwargs)

        # method
        requests_method = self.session.get

        try:
            response = requests_method(
                    base_url + query_url,
                    params=params,
                    **final_requests_kwargs)

            # temporary, for logging
            if verbose:
                pretty_print_POST(response.request)

        except requests.exceptions.Timeout:
            raise TimeOutException()
        except Exception as e:
            raise TransportError(e)

        result = self._get_body(response)

        return result

    def _get_body(self, response):
        """Handle various types of responses here
        """
        # TODO: Not yet implemented
        if response.status_code == 403:
            pass
        if response.status_code == 404:
            # Not Found: outside the geography?
            pass
        if response.status_code != 200:
            raise HTTPError(response.status_code)

        body = response.json()

        api_status = body["status"]

        # Handle different types of 200 OK response types here
        if api_status == "OK":
            return body


def pretty_print_POST(req):
    """
    req is a PreparedRequest object, this function will print it nicely.
    See https://2.python-requests.org/en/master/user/advanced/#id3
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


class TimeOutException(Exception):
    pass


class TransportError(Exception):
    pass


class HTTPError(Exception):
    pass
