from setuptools import setup


with open('requirements.txt', 'r') as file:
    REQUIREMENTS = [line.strip() for line in file.readlines()]

setup(
    name='coral',
    packages=['coral'],
    package_data={'coral': ['runtime.so']},
    include_package_data=True,
    install_requires=REQUIREMENTS
)
