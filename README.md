# JSParser

A python 2.7 script using Tornado and JSBeautifier to parse relative URLs from JavaScript files. Useful for easily discovering AJAX requests when performing security research or bug bounty hunting.

# Dependencies

- safeurl
- tornado
- jsbeautifier

# Installing 
## Ubuntu/Kali

```
sudo apt update --fix-missing
sudo apt update
sudo apt install git
sudo apt install python2
sudo apt install python2-dev
sudo apt install curl
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
sudo python2 get-pip.py
sudo apt install libcurl4-openssl-dev libssl-dev
python2 -m pip install tornado==5.1
python2 -m pip install netaddr
python2 -m pip install pycurl==7.43.0.5
python2 -m pip install jsbeautifier==1.8.0
python2 -m pip install bs4
```

## Windows
```
Python 2.7.18 - https://www.python.org/downloads/release/python-2718/
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
python2 get-pip.py


https://pypi.org/project/pycurl/7.43.0.2/#files
https://files.pythonhosted.org/packages/b3/6c/071e387e40ea3f1d685152f8af41fac32627b4127bb1e050b1cb85a66ca1/pycurl-7.43.0.2.win-amd64-py2.7.exe

python2 -m pip install tornado==5.1
python2 -m pip install netaddr
python2 -m pip install jsbeautifier==1.8.0
python2 -m pip install bs4
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
