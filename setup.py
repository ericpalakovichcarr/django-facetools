#!/usr/bin/env python

from distutils.core import setup

import facetools

def get_long_description():
    """
    Return the contents of the README file.
    """
    try:
        return open('README.rst').read()
    except:
        pass  # Required to install using pip (won't have README then)

setup(
    name = 'django-facetools',
    version = facetools.__version__,
    description = "Django Facetools provides a set of features to ease development of Facecbook canvas apps in a Django project.",
    long_description = get_long_description(),
    author = "Eric Palakovich Carr",
    author_email = "carreric@gmail.com",
    license = "MIT",
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
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Software Development :: Testing',
    ]
)
