FROM globocom/networkapi:1.0.0

RUN mkdir -p /netapi

ADD . /netapi/

EXPOSE 8000

WORKDIR /netapi

RUN pip install -r requirements_debug.txt
