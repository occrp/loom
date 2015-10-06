import six
import os
import string
import yaml
from uuid import uuid4
from collections import MutableMapping, Mapping

ALPHABET = string.letters + string.digits


class LoomException(Exception):
    pass


class SpecException(LoomException):
    pass


class ConfigException(LoomException):
    pass


def load_config(config_file):
    """ Loads the configuration file and recursively imports any base
    configurations indicated in the configuration. """
    with open(config_file, 'r') as fh:
        config = yaml.load(fh)
    if 'base' not in config:
        return config
    base_file = os.path.expandvars(config.pop('base'))
    base_config = load_config(base_file)
    base_config.update(config)
    return base_config


class EnvMapping(MutableMapping):

    def __init__(self, data):
        self.data = data

    def __getitem__(self, name):
        return self.get(name)

    def get(self, name, default=None, raw=False):
        value = self.data.get(name)
        if value is None or (isinstance(value, six.string_types)
                             and not len(value.strip())):
            value = default
        if not raw:
            if isinstance(value, Mapping):
                return EnvMapping(value)
            if isinstance(value, six.string_types):
                return os.path.expandvars(value)
        return value

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __contains__(self, name):
        return name in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


def make_id():
    uuid = uuid4().int
    chars = [u'urn:b:']
    while uuid:
        uuid, digit = divmod(uuid, len(ALPHABET))
        chars.append(ALPHABET[digit])
    return u''.join(chars)
