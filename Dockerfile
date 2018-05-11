FROM ubuntu:xenial-20180123
MAINTAINER Kieran Bacon, Ben Townsend

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get clean; apt-get update; apt-get upgrade; \
apt-get -y install python3 ipython3 python3-pip libopenjpeg-dev python3-grib python3-netcdf4 python3-pandas ;\
pip3 install sklearn pytest pyramid pyramid-jinja2 pydrive

ADD . /root/code

RUN cd /root/code ; \
python3 Server/setup.py install ; \
python3 Learning/setup.py install ;

ENV PYTHONPATH=/root/code/Learning:/root/code/Server
ENV PYTHONUNBUFFERED=Truex
ENV EXPERTLOCATION=/root/code/Server/ExpertWebtool/data/ExpertRep/

WORKDIR /root/code

CMD ["pserve", "Webtool.ini"]