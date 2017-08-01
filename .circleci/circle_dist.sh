#!/usr/bin/env bash

if [ -z "$CI" ]; then
    echo "Will only continue on CI"
    exit
fi

if [[ $CIRCLE_BRANCH != "auto_deploy" ]]; then
    echo "Will only continue for master builds"
    exit
fi

# build package and upload to private pypi index
echo "[pypi]" >> ~/.pypirc
echo "username=$PYPI_USERNAME" >> ~/.pypirc
echo "password=$PYPI_PASSWORD" >> ~/.pypirc

python setup.py bdist_wheel --universal
twine upload dist/*