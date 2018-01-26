FROM ubuntu:latest
MAINTAINER Ben Townsend

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update ; \
apt-get -y install python3 ipython3 python3-pip libopenjpeg-dev python3-grib python3-netcdf4 python3-pandas ;\
pip3 install sklearn pytest pyramid pyramid-jinja2

ADD . /root/code

RUN cd /root/code ; \
python3 Server/setup.py install ; \
python3 Learning/setup.py install ;\
cd Server

ENV PYTHONPATH=/root/code/Learning:/root/code/Server
ENV PYTHONUNBUFFERED=Truex
EXPOSE 6543:6543
EXPOSE 22
CMD ["bash /root/code/docker_run_on_start.sh"]