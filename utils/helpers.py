
import collections
import ast

def unicode_to_str(data):
  ' Convert python dictionary with key/value from unicode to string '
  if isinstance(data, basestring):
    return str(data)
  elif isinstance(data, collections.Mapping):
    return dict(map(unicode_to_str, data.iteritems()))
  elif isinstance(data, collections.Iterable):
    return type(data)(map(unicode_to_str, data))
  else:
    return data

def dict_key_to_correct_type(req_dict):
  for key, value in req_dict.items():
    try:
      req_dict[key] = ast.literal_eval(value)
    except:
      pass
  return req_dict

