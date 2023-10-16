from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='PyClust',
    version='0.0.1',
    packages=find_packages(),
    author= 'Jonathan Zhang',
    author_email="jon.zhang@ucsf.edu",
    description='Python package for remote server job management.',
    url='https://github.com/jzhang1198/PyClust',
    classifiers=[
        'Programming Language :: Python :: 3.9.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=requirements,
)