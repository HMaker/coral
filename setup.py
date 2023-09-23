from setuptools import setup
from mypyc.build import mypycify


with open('requirements.txt', 'r') as file:
    REQUIREMENTS = [line.strip() for line in file.readlines()]

setup(
    name='coral',
    packages=['coral'],
    ext_modules=mypycify([
        'coral/__init__.py',
        'coral/parser.py',
        'coral/ast.py',
    ]),
    install_requires=REQUIREMENTS
)
