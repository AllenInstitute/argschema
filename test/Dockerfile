FROM fcollman/json_module
WORKDIR test
RUN pip install -r test_requirements.txt --upgrade
RUN useradd -ms /bin/bash test
USER test
WORKDIR ..