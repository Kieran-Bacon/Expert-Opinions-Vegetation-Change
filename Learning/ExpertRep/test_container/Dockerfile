FROM ubuntu:xenial-20180123
MAINTAINER Cerbo IO <support@cerbo.io>

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update ; \
apt-get -y install python3 ipython3 python3-pip libopenjpeg-dev python3-grib python3-netcdf4 python3-pandas openssh-server wget git screen vim-nox emacs-nox;\
pip3 install sklearn pytest pylint;

EXPOSE 22
CMD ["/bin/bash"]