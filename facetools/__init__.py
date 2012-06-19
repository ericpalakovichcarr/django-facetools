try:
   import json
except ImportError:
   from django.utils import simplejson as json

__version__ = VERSION = '0.2.0'
__version_info__ = tuple(__version__.split('.'))

from common import create_signed_request, parse_signed_request