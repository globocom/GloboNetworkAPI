FROM globocom/networkapi:1.0.0

RUN mkdir -p /netapi
WORKDIR /netapi

ADD . /netapi/

CMD cd /netapi

EXPOSE 8000

RUN pip install -r requirements.txt
RUN pip install -r requirements_test.txt
RUN pip install virtualenv
RUN pip install gunicorn
