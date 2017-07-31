FROM continuumio/anaconda
MAINTAINER Forrest Collman (forrestc@alleninstitute.org)
RUN mkdir -p /usr/local/argschema
COPY . /usr/local/argschema
WORKDIR /usr/local/argschema
RUN python setup.py install 
RUN pip install -r test_requirements.txt --upgrade
RUN pip install --disable-pip-version-check -U setuptools
RUN useradd -ms /bin/bash test
RUN chmod -R 777 ..
USER test
WORKDIR ..