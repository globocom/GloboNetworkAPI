FROM python:2.7

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev \
                       mysql-client

RUN mkdir /netapi
WORKDIR /netapi

ADD . /netapi/

CMD cd /netapi

EXPOSE 8000

RUN pip install -r requirements.txt
RUN pip install virtualenv
RUN pip install virtualenvwrapper
RUN pip install gunicorn
