#
# Base stage
#
FROM alpine:3.7 as base

RUN apk update

RUN apk add --update --no-cache py2-pip \
                                libldap \
                                libssl1.0 \
                                mysql-client \
                                mariadb-client-libs \
                                net-tools \
                                iputils \
                                bind-tools \
                                ncurses5-libs \
                                curl \
                                libffi-dev \
                                py-pynacl \
                                libffi-dev \
                                libxslt-dev \
                                gcc \
                                libc-dev \
                                python-dev


RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache virtualenv

RUN mkdir -p /netapi

ADD . /netapi/

EXPOSE 8000

WORKDIR /netapi


#
# Build stage
#
FROM base as build

RUN apk add --update --no-cache python2-dev \
                                openldap-dev \
                                libsass-dev \
                                mariadb-dev \
                                ncurses-dev \
                                linux-headers \
                                gcc \
                                musl-dev \
                                libffi-dev \
                                make

RUN virtualenv /venv && \
    source /venv/bin/activate && \
    pip install --no-cache --no-build-isolation -r requirements_debug.txt


#
# Last stage
#
FROM base as image

COPY --from=build /venv /venv

RUN touch /tmp/networkapi.log

ENV PATH="/venv/bin:${PATH}"

ENV PYTHONPATH="/usr/lib/python2.7:/venv/lib/python2.7"

CMD /netapi/scripts/docker/docker-start-netapi.sh
