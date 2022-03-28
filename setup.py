from setuptools import setup, find_packages
import os, sys

HERE = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(HERE, 'requirements.txt')) as f:
    requirements = [line.strip() for line in f if len(line.strip()) and not line.strip().startswith('#')]

setup(
    name='rickroll',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
)