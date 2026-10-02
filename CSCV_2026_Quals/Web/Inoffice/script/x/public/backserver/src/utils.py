import io
import pickle
from urllib.request import urlopen, Request
from urllib.parse import urlparse
import json

unsafe_builtins = [
  "exec",
  "eval",
  "__import__"
]

invalid_hosts = [
  "127.0.0.1",
  "localhost"
]

def is_valid_address(address):
  try:
    hostname = urlparse(address).hostname
    if hostname in invalid_hosts:
      return False
    return True
  except Exception as e:
    return False

def make_request(method, url, headers):
  if is_valid_address(url):
    request = Request(url=url, headers=json.loads(headers), method=method)
    try:
      with urlopen(request, timeout=3) as response:
        status_code = response.status
      return status_code
    except Exception as e:
      return "error"
  else:
    return "invalid address"
  

def is_safe(module, name):
  if module == "builtins" and name not in unsafe_builtins:
    return True
  return False

class RestrictedUnpickler(pickle.Unpickler):
  def find_class(self, module, name):
    if is_safe(module, name):
      return super().find_class(module, name)
    else:
      raise pickle.UnpicklingError("'%s.%s' is forbidden" % (module, name))


def restricted_loads(s):
  return RestrictedUnpickler(io.BytesIO(s)).load()