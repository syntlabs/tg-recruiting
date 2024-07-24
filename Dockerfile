FROM python:3.12

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

ADD requirements.txt requirements.txt

RUN mkdir /var/log/app

RUN apt update -y
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install flake8 pep8-naming flake8-broken-line flake8-return