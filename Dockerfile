FROM continuumio/anaconda
MAINTAINER Forrest Collman (forrest.collman@gmail.com)

#install render python using pip from github
#RUN pip install -e git+https://github.com/fcollman/render-python.git@master#egg=render-python

RUN mkdir -p /usr/local/json_module
COPY . /usr/local/json_module
WORKDIR /usr/local/json_module
RUN python setup.py install 
