#!/usr/bin/env bash

# build package and upload to private pypi index
echo "[pypi]" >> ~/.pypirc
echo "username=$PYPI_USERNAME" >> ~/.pypirc
echo "password=$PYPI_PASSWORD" >> ~/.pypirc

python setup.py bdist_wheel --universal
twine upload dist/*py2.py3-none-any*