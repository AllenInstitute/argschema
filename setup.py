from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

with open('test/test_requirements.txt','r') as f:
    test_required = f.read().splitlines()

setup(name='argschema',
      version='1.11',
      description=' a wrapper for setting up modules that can have parameters specified by command line arguments,\
       json_files, or dictionary objects. Providing a common wrapper for data processing modules.',
      author='Forrest Collman,David Feng',
      author_email='forrestc@alleninstitute.org',
      packages=find_packages(),
      url='https://github.com/AllenInstitute/argschema',
      install_requires=required,
      setup_requires=['pytest-runner'],
      tests_require=test_required)
