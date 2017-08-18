FROM globocom/networkapi:1.0.0

RUN mkdir -p /netapi
WORKDIR /netapi

ADD . /netapi/

CMD cd /netapi

EXPOSE 8000

# Needed to ipdb and ipython work together well 
RUN apt-get update
RUN apt-get install -y libncurses5-dev
RUN pip install --upgrade readline

RUN pip install -r requirements.txt
RUN pip install -r requirements_test.txt 
RUN pip install virtualenv
RUN pip install gunicorn
