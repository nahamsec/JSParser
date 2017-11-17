# docker pull andmyhacks/jsparser

FROM python:2

LABEL "Author"="Keith Hoodlet <keith@attackdriven.io>"

RUN mkdir -p /var/www/jsparser
WORKDIR /var/www/jsparser

COPY . /var/www/jsparser/

RUN apt-get update
RUN apt-get install -y  git python-setuptools
RUN pip install --upgrade pip

RUN python setup.py install

EXPOSE 8008
ENTRYPOINT ["python", "handler.py"]