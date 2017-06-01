FROM suptel/base_globonetworkapi_netapi:3.4.3

RUN mkdir /netapi
WORKDIR /netapi

ADD . /netapi/

RUN apt-get update && apt-get install -y \
            net-tools \
            dnsutils

CMD cd /netapi

EXPOSE 8000

RUN pip install -r requirements.txt
RUN pip install -r requirements_test.txt
RUN pip install virtualenv
RUN pip install gunicorn
