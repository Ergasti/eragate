import threading
from novaclient.v1_1.client import Client
from novaclient import exceptions

from django.conf import settings

_thread_local = threading.local()

__all__ = ['OS_VM_CREATION_SETTINGS_DEFAULTS', 'nova_api', 'is_nova_exception']

OS_VM_CREATION_SETTINGS_DEFAULTS = {
    'key_name': None,
    'availability_zone': None,
    'nics': [],
    'security_groups': ['default'],
    'floating_ip_pool': None
}

def nova_api():
  global _thread_local
  try:
    return _thread_local.nova_api
  except AttributeError:
    _thread_local.nova_api = \
      Client(settings.OS_USERNAME, settings.OS_PASSWORD,
             settings.OS_TENANT_NAME, settings.OS_AUTH_URL,
             service_type="compute")
  return _thread_local.nova_api

def is_nova_exception(exception):
    return exception.__class__ in exceptions._error_classes

