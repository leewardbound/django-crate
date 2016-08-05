#!/bin/bash
python manage.py migrate example zero --database=crate
#DJANGO_TEST=1 python manage.py migrate --database=crate
python manage.py test
