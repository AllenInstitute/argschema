FROM continuumio/anaconda
MAINTAINER Forrest Collman (forrestc@alleninstitute.org)

RUN mkdir -p /usr/local/json_module
COPY . /usr/local/json_module
WORKDIR /usr/local/json_module
RUN python setup.py install 
