# JSParser

A python 2.7 script using Tornado and JSBeautifier to parse relative URLs from JavaScript files. Useful for easily discovering AJAX requests when performing security research or bug bounty hunting.

# Dependencies

- safeurl
- tornado
- jsbeautifier

# Installing

```
$ python setup.py install
```

# Running

Run `handler.py` and then visit http://localhost:8008.

```
$ python handler.py
```

# Authors

- https://twitter.com/bbuerhaus/
- https://twitter.com/nahamsec/

# Inspired By

- https://twitter.com/jobertabma/

# References

 - http://buer.haus/2017/03/31/airbnb-web-to-app-phone-notification-idor-to-view-everyones-airbnb-messages/
 - http://buer.haus/2017/03/09/airbnb-chaining-third-party-open-redirect-into-server-side-request-forgery-ssrf-via-liveperson-chat/

# Changelog

1.0 - Release