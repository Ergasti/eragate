import threading
from novaclient.v1_1.client import Client

from django.conf import settings

_thread_local = threading.local()

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
