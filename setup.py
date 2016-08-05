#!/usr/bin/env python

from distutils.core import setup

setup(name='django_crate',
      version='0.1.33',
      description='Django database backend for crate.io',
      author='Leeward Bound',
      author_email='l@lwb.co',
      url='https://github.com/linked/django-crate',
      install_requires=[
          'crate==0.12',
          'crash==0.10.2',
      ],
      packages=['django_crate',],
     )
