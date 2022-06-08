from setuptools import setup

with open('README.txt') as file:
    long_description = file.read()

setup(name='modbus',
      version='3.2',
      description='Modbus TCP Server and Client Programs',
      long_description=long_description,
      url='https://github.com/ipal0/modbus',
      author='Pal',
      author_email='ipal0can@gmail.com',
      license='GPL',
      packages=['modbus'],
      install_requires=['numpy'])
