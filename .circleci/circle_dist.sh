#!/usr/bin/env bash

# build package and upload to pypi index
echo "[pypi]" >> ~/.pypirc
echo "username=$PYPI_USERNAME" >> ~/.pypirc
echo "password=$PYPI_PASSWORD" >> ~/.pypirc

python setup.py bdist_wheel --universal
python setup.py sdist
twine upload dist/*