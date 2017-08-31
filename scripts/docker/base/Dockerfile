#
# Globo Network API base docker image
# Check it at https://hub.docker.com/r/globocom/networkapi/
#

FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install vim -y
RUN apt-get install python-pip -y
RUN apt-get install libmysqlclient-dev -y
RUN apt-get install python-dev -y
RUN apt-get install libldap2-dev libsasl2-dev libssl-dev -y
RUN apt-get install mysql-client -y
RUN apt-get install net-tools -y
RUN apt-get install dnsutils -y

# Needed to ipdb and ipython work together well
RUN apt-get install -y libncurses5-dev
RUN pip install --upgrade readline
