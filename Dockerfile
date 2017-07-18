FROM continuumio/anaconda
MAINTAINER Forrest Collman (forrestc@alleninstitute.org)

RUN mkdir -p /usr/local/argschema
COPY . /usr/local/argschema
WORKDIR /usr/local/argschema
RUN python setup.py install 
