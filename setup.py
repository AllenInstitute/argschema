from setuptools import setup

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

setup(name='json_module',
      version='1.0',
      description=' a wrapper for setting up modules that can have parameters specified by command line arguments,\
       json_files, or dictionary objects. Providing a common wrapper for data processing modules.',
      author='Forrest Collman,David Feng',
      author_email='forrestc@alleninstitute.org',
      py_modules=['json_module'],
      install_requires=required)
