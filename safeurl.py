# coding: utf8

"""
.. module:: safeurl
    synopsis:: An SSRF protection library
.. moduleauthor:: Nicolas Rodriguez <http://github.com/nicolasrod>
"""

from __future__ import unicode_literals
from __future__ import print_function

from numbers import Number
from socket import gethostbyname_ex

import re
import netaddr
import pycurl
import StringIO

# Python 2.7/3 urlparse
try:
    # Python 2.7
    from urlparse import urlparse
    from urllib import quote
except:
    # Python 3
    from urllib.parse import urlparse
    from urllib.parse import quote


class InvalidOptionException(Exception):
    pass


class InvalidURLException(Exception):
    pass


class InvalidDomainException(Exception):
    pass


class InvalidIPException(Exception):
    pass


class InvalidPortException(Exception):
    pass


class InvalidSchemeException(Exception):
    pass


class Empty(object):
    pass

# TODO: Remove this ugly hack!


def _mutable(obj):
    newobj = Empty()
    for i in dir(obj):
        if not i.startswith("_"):
            setattr(newobj, i, getattr(obj, i))
    return newobj


def _check_allowed_keys(val):
    if val not in ["ip", "port", "domain", "scheme"]:
        raise InvalidOptionException(
            "Provided type 'type' must be 'ip', 'port', 'domain' or 'scheme'")


def _check_allowed_lists(val):
    if val not in ["whitelist", "blacklist"]:
        raise InvalidOptionException(
            "Provided list 'list' must be 'whitelist' or 'blacklist'")


class Options(object):
    """
    This object contains configuration options for safeurl.
    """

    def __init__(self):
        self._follow_location = False
        self._follow_location_limit = 0
        self._send_credentials = False
        self._pin_dns = False
        self._lists = {
            "whitelist": {
                "ip": [],
                "port": ["80", "443", "8080"],
                "domain": [],
                "scheme": ["http", "https"]},
            "blacklist": {
                "ip": ["0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10",
                       "127.0.0.0/8", "169.254.0.0/16",
                       "172.16.0.0/12", "192.0.0.0/29", "192.0.2.0/24",
                       "192.88.99.0/24", "192.168.0.0/16",
                       "198.18.0.0/15", "198.51.100.0/24",
                       "203.0.113.0/24", "224.0.0.0/4", "240.0.0.0/4"],
                "port": [],
                "domain": [],
                "scheme": []}
        }

    def getFollowLocation(self):
        """
        Get followLocation

        :rtype: bool
        """
        return self._follow_location

    def enableFollowLocation(self):
        """
        Enables following redirects

        :rtype: :class:`Options`
        """
        self._follow_location = True
        return self

    def disableFollowLocation(self):
        """
        Disable following redirects

        :rtype: :class:`Options`
        """
        self._follow_location = False
        return self

    def getFollowLocationLimit(self):
        """
        Gets the follow location limit
        0 is no limit (infinite)

        :rtype: int
        """
        return self._follow_location_limit

    def setFollowLocationLimit(self, limit):
        """
        Set follow location limit
        0 is no limit (unlimited)

        :rtype: int
        """
        if not isinstance(limit, Number) or limit < 0:
            raise InvalidOptionException(
                "Provided limit 'limit' must be an integer >= 0")

        self._follow_location_limit = limit
        return self

    def getSendCredentials(self):
        """
        Get send credentials option

        :rtype: bool
        """
        return self._send_credentials

    def enableSendCredentials(self):
        """
        Enable sending of credentials

        :rtype: :class:`Options`
        """
        self._send_credentials = True
        return self

    def disableSendCredentials(self):
        """
        Disable sending of credentials

        :rtype: :class:`Options`
        """
        self._send_credentials = False
        return self

    def getPinDns(self):
        """
        Get pin DNS option

        :rtype: bool
        """
        return self._pin_dns

    def enablePinDns(self):
        """
        Enable pin DNS option

        :rtype: :class:`Options`
        """
        self._pin_dns = True
        return self

    def disablePinDns(self):
        """
        Disable pin DNS option

        :rtype: :class:`Options`
        """
        self._pin_dns = False
        return self

    def isInList(self, lst, type_, value):
        """
        Checks if a specific value is in a list

        :param arg1: Options: "whitelist" or "blacklist"
        :type arg1: string
        :param arg2: Options: "ip", "port", "domain", or "scheme"
        :type arg2: string
        :param arg3: Value to check for
        :type arg3: string

        :rtype: bool
        """
        _check_allowed_lists(lst)
        _check_allowed_keys(type_)

        dst = self._lists[lst][type_]

        if len(dst) == 0:
            if lst == "whitelist":
                return True
            else:
                return False

        # For domains, a regex match is needed
        if type_ == "domain":
            for domain in dst:
                if re.match("(?i)^%s" % domain, value) is not None:
                    return True
            return False
        else:
            return value in dst

    def getList(self, lst, type_=None):
        """"
        Returns a specific list

        :param arg1: Options: "blacklist" or "whitelist"
        :type arg1: string
        :param arg2: Type (Optional) - Options: "ip", "port", "domain", or "scheme"
        :type arg2: string

        :rtype: list
        """
        _check_allowed_lists(lst)

        dst = self._lists[lst]

        if type_ != None:
            _check_allowed_keys(type_)
            return dst[type_]

        return dst

    def setList(self, lst, values, type_=None):
        """
        Sets a list to be passed in as dictionary

        :param arg1: Options: "blacklist" or "whitelist"
        :type arg1: string
        :param arg2: dictionary to be passed in
        :type arg2: dict
        :param arg3: Type (Optional) - Options: "ip", "port", "domain", or "scheme"
        :type arg3: string

        :rtype: :class:`Options`
        """
        _check_allowed_lists(lst)

        if type_ is not None:
            if not isinstance(values, list):
                raise InvalidOptionException("Provided values must be a list")

            _check_allowed_keys(type_)
            self._lists[lst][type_] = values
            return self

        if not isinstance(values, dict):
            raise InvalidOptionException(
                "Provided values must be a dictionary")

        for k, v in values.iteritems():
            _check_allowed_keys(k)
            self._lists[lst][k] = v

        return self

    def clearList(self, lst):
        """
        Clears specified list

        :param arg1: Options: "blacklist" or "whitelist"
        :type arg1: string
        """
        _check_allowed_lists(lst)
        self._lists[lst] = {"ip": [], "domain": [], "port": [], "scheme": []}

    def addToList(self, lst, type_, values):
        """
        Add value(s) to a specific list

        :param arg1: Options: "blacklist" or "whitelist"
        :type arg1: string
        :param arg2: Options: "ip", "domain", "port", or "scheme"
        :type arg2: string
        :param arg3: values to add
        :type arg3: string/list (string)

        :rtype: :class:`Options`
        """
        _check_allowed_lists(lst)
        _check_allowed_keys(type_)

        if len(values) == 0:
            raise InvalidOptionException("Provided values cannot be empty")

        if not isinstance(values, list):
            values = list(values)

        dst = self._lists[lst][type_]

        for v in values:
            if not v in dst:
                dst.append(v)
        return self

    def removeFromList(self, lst, type_, values):
        """
        Remove value(s) from a specific list

        :param arg1: Option: "blacklist" or "whitelist"
        :type arg1: string
        :param arg2: Options: "ip", "domain", "port", or "scheme"
        :type arg2: string
        :param arg3: values to remove
        :type arg3: string/list(string)

        :rtype: :class:`Options`
        """
        _check_allowed_lists(lst)
        _check_allowed_keys(type_)

        if len(values) == 0:
            raise InvalidOptionException("Provided values cannot be empty")

        if not isinstance(values, list):
            values = [values]

        dst = self._lists[lst][type_]
        self._lists[lst][type_] = [x for x in dst if x not in values]
        return self


class Url(object):
    """
    Class for handling URLs
    """
    @staticmethod
    def validateUrl(url, options):
        """
        Validates the whole URL

        :param arg1: The URL
        :type arg1: string
        :param arg2: Options object
        :type arg2: :class:`Options`

        :rtype: dict
        """
        if len(url) == 0:
            raise InvalidURLException("Provided URL 'url' cannot be empty")

        # Split URL into parts first
        parts = _mutable(urlparse(url))

        if parts is None:
            raise InvalidURLException("Error parsing URL 'url'")

        if parts.hostname is None:
            raise InvalidURLException(
                "Provided URL 'url' doesn't contain a hostname")

        # First, validate the scheme
        if len(parts.scheme) != 0:
            parts.scheme = Url.validateScheme(parts.scheme, options)
        else:
            # Default to http
            parts.scheme = "http"

        # Validate the port
        if not parts.port is None:
            parts.port = Url.validatePort(parts.port, options)

        # Reolve host to ip(s)
        parts.ips = Url.resolveHostname(parts.hostname)

        # Validate the host
        parts.hostname = Url.validateHostname(
            parts.hostname, parts.ips, options)

        if options.getPinDns():
            # Since we"re pinning DNS, we replace the host in the URL
            # with an IP, then get cURL to send the Host header
            parts.hostname = parts.ips[0]

        # Rebuild the URL
        cleanUrl = Url.buildUrl(parts)

        return {"originalUrl": str(url),
                "cleanUrl": str(cleanUrl), "parts": parts}

    @staticmethod
    def validateScheme(scheme, options):
        """
        Validates a URL scheme

        :param arg1: scheme
        :type arg1: string
        :param arg2: Options object
        :type arg2: :class:`Object`

        :rtype: string
        """
        # Whitelist always takes precedence over a blacklist
        if not options.isInList("whitelist", "scheme", scheme):
            raise InvalidSchemeException("Provided scheme 'scheme' doesn't \
                match whitelisted values: %s" % (
                ", ".join(options.getList("whitelist", "scheme"))))

        if options.isInList("blacklist", "scheme", scheme):
            raise InvalidSchemeException(
                "Provided scheme 'scheme' matches a blacklisted value")

        # Existing value is fine
        return scheme

    @staticmethod
    def validatePort(port, options):
        """
        Validates a port

        :param arg1: port
        :type arg1: int
        :param arg2: Options object
        :type arg2: :class:`Options`

        :rtype: int
        """
        if not options.isInList("whitelist", "port", port):
            raise InvalidPortException("Provided port 'port' doesn't match \
                whitelisted values: %s" % (
                ", ".join(options.getList("whitelist", "port"))))

        if options.isInList("blacklist", "port", port):
            raise InvalidPortException(
                "Provided port 'port' matches a blacklisted value")

        # Existing value is fine
        return port

    @staticmethod
    def validateHostname(hostname, ips, options):
        """
        Validates a URL hostname

        :param arg1: hostname
        :type arg1: string
        :param arg2: IP addresses to validate
        :type arg2: list (string)
        :param arg3: Options object
        :type arg3: :class:`Options`

        :rtype: string
        """
        # Check the host against the domain lists
        if not options.isInList("whitelist", "domain", hostname):
            raise InvalidDomainException("Provided hostname 'hostname' doesn't match \
            whitelisted values: %s" % (
                ", ".join(options.getList("whitelist", "domain"))))

        if options.isInList("blacklist", "domain", hostname):
            raise InvalidDomainException(
                "Provided hostname 'hostname' matches a blacklisted value")

        whitelistedIps = options.getList("whitelist", "ip")

        if len(whitelistedIps) != 0:
            has_match = any(Url.cidrMatch(ip, wlip)
                            for ip in ips for wlip in whitelistedIps)
            if not has_match:
                raise InvalidIPException("Provided hostname 'hostname' \
                    resolves to '%s', which doesn't match whitelisted values: %s"
                                         % (", ".join(ips),
                                            ", ".join(whitelistedIps)))

        blacklistedIps = options.getList("blacklist", "ip")

        if len(blacklistedIps) != 0:
            has_match = any(Url.cidrMatch(ip, blip)
                            for ip in ips for blip in blacklistedIps)
            if has_match:
                raise InvalidIPException("Provided hostname 'hostname' \
                    resolves to '%s', which matches a blacklisted value: %s" % (
                    ", ".join(ips), blacklistedIps))

        return hostname

    @staticmethod
    def buildUrl(parts):
        """
        Rebuild a URL based on a :func:`_mutable()` object of parts

        :param arg1: object of parts
        :type arg1: :func:`_mutable()` object

        :rtype: string
        """
        url = []

        if len(parts.scheme) != 0:
            url.append("%s://" % parts.scheme)

        if not parts.username is None:
            url.append(quote(parts.username))

        if not parts.password is None:
            url.append(":%s" % quote(parts.password))

        # If we have a user or pass, make sure to add an "@"
        if (not parts.username is None) or (not parts.password is None):
            url.append("@")

        if not parts.hostname is None:
            url.append(parts.hostname)

        if not parts.port is None:
            url.append(":%d" % int(parts.port))

        if len(parts.path) != 0:
            url.append("/%s" % quote(parts.path[1:]))

        # The query string is difficult to encode properly
        # We need to ensure no special characters can be
        # used to mangle the URL, but URL encoding all of it
        # prevents the query string from being parsed properly
        if len(parts.query) != 0:
            query = quote(parts.query)
            # Replace encoded &, =, ;, [ and ] to originals
            query = query.replace("%26", "&").replace("%3D", "=").replace(
                "%3B", ";").replace("%5B", "[").replace("%5D", "]")
            url.append("?")
            url.append(query)

        if len(parts.fragment) != 0:
            url.append("#%s" % quote(parts.fragment))

        return "".join(url)

    @staticmethod
    def resolveHostname(hostname):
        """
        Resolve a hostname to its IP(s)

        :param arg1: hostname
        :type arg1: string

        :rtype: list (string)
        """
        try:
            ips = gethostbyname_ex(hostname)
            return ips[2]
        except:
            raise InvalidDomainException(
                "Provided hostname 'hostname' doesn't \
                to an IP address")

    @staticmethod
    def cidrMatch(ip, cidr):
        """
        Checks a passed in IP against a CIDR

        :param arg1: IP address
        :type arg1: string
        :param arg2: CIDR
        :type arg2: string

        :rtype: bool
        """
        return netaddr.IPAddress(ip) in netaddr.IPNetwork(cidr)


class SafeURL(object):
    """
    Core interface of module
    """

    def __init__(self, handle=None, options=None):
        self.setCurlHandle(handle)

        if options == None:
            options = Options()

        self.setOptions(options)

        # To start with, disable FOLLOWLOCATION since we'll handle it
        self._handle.setopt(pycurl.FOLLOWLOCATION, False)

        # Force IPv4, since this class isn't yet compatible with IPv6
        self._handle.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)

    def getCurlHandle(self):
        """
        Returns cURL Handle

        :rtype: :class:`SafeURL`
        """
        return self._handle

    def setCurlHandle(self, handle):
        """
        Sets cURL handle

        :param arg1: handle
        :type arg1: (Optional) :class:`pycurl.Curl` object

        :rtype: :class:`pycurl.Curl` object
        """
        if handle is None:
            handle = pycurl.Curl()

        # TODO: Fix this hack!
        if repr(handle).find("pycurl.Curl") == -1:
            raise Exception("SafeURL expects a valid cURL object!")

        self._handle = handle

    def getOptions(self):
        """
        Gets Options

        :rtype: :class:`Options`
        """
        return self._options

    def setOptions(self, options):
        """
        Sets options

        :param arg1: Options object
        :type: :class:`Options` object

        :rtype: :class:`Options` object
        """
        self._options = options

    def execute(self, url):
        """
        Executes a cURL request, whilst checking that the URL abides by our whitelists/blacklists

        :param arg1: URL
        :type arg1: string

        :rtype: string
        """
        # Backup the existing URL
        originalUrl = url

        # Execute, catch redirects and validate the URL
        redirected = False
        redirectCount = 0
        redirectLimit = self._options.getFollowLocationLimit()
        followLocation = self._options.getFollowLocation()

        while True:
            # Validate the URL
            url = Url.validateUrl(url, self._options)

            # Are there credentials, but we don"t want to send them?
            if not self._options.getSendCredentials() and \
                    (url["parts"].username is not None or
                        url["parts"].password is not None):
                raise InvalidURLException(
                    "Credentials passed in but 'sendCredentials' \
                    is set to false")

            if self._options.getPinDns():
                # Send a Host header
                self._handle.setopt(pycurl.HTTPHEADER, [
                                    "Host: %s" % url["parts"].hostname])
                # The "fake" URL
                self._handle.setopt(pycurl.URL, url["cleanUrl"])

                # We also have to disable SSL cert verification, which is not great
                # Might be possible to manually check the certificate
                # ourselves?
                self._handle.setopt(pycurl.SSL_VERIFYPEER, False)
            else:
                self._handle.setopt(pycurl.URL, url["cleanUrl"])

            # Execute the cURL request
            response = StringIO.StringIO()
            self._handle.setopt(pycurl.WRITEFUNCTION, response.write)
            self._handle.perform()

            # Check for an HTTP redirect
            if followLocation:
                statuscode = self._handle.getinfo(pycurl.HTTP_CODE)

                if statuscode in [301, 302, 303, 307, 308]:
                    redirectCount += 1
                    if redirectLimit == 0 or redirectCount < redirectLimit:
                        # Redirect received, so rinse and repeat
                        url = self._handle.getinfo(pycurl.REDIRECT_URL)
                        redirected = True
                    else:
                        raise Exception("Redirect limit 'redirectLimit' hit")
                else:
                    redirected = False

            if not redirected:
                break

        return response.getvalue()
