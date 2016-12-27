#!/usr/bin/env python

from setuptools import setup

setup(name='django_crate',
      version='0.1.33',
      description='Django database backend for crate.io',
      author='Leeward Bound',
      author_email='l@lwb.co',
      url='https://github.com/linked/django-crate',
      install_requires=[
          'psycopg2==2.6.1',
          'python-dateutil',
      ],
      packages=['django_crate',],
     )
