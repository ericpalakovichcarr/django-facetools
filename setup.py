#!/usr/bin/env python

from distutils.core import setup

import facetools

setup(
    name = 'django-facetools',
    version = facetools.__version__,
    description = "Django Facetools provides a set of features to ease development of Facecbook canvas apps in a Django project.",
    author = "Eric Palakovich Carr",
    author_email = "carreric@gmail.com",
    url = "https://github.com/bigsassy/django-facetools",
    packages = [
        'facetools',
        'facetools.integrations',
        'facetools.management',
        'facetools.management.commands',
        'facetools.migrations',
        'facetools.templatetags',
        'facetools.test',
    ],
)
