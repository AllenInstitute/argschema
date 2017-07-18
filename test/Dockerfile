FROM fcollman/argschema
WORKDIR test
RUN pip install -r test_requirements.txt --upgrade
RUN useradd -ms /bin/bash test
RUN chmod -R 777 ..
USER test
WORKDIR ..