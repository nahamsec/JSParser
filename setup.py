#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='JSParser',
    version='1.0',
    packages=find_packages(),
    description="",
    long_description=open('README.md').read(),
    author='Ben Sadeghipour',
    url='https://github.com/nahamsec/JSParser',
    install_requires=['safeurl', 'tornado', 'jsbeautifier',
                      'netaddr', 'pycurl', 'BeautifulSoup4'],
)
