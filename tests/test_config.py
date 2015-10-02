import os
import yaml
from nose.tools import raises
from unittest import TestCase

from util import create_fixtures, FIXTURE_PATH

from datamapper.config import Config, ConfigException
from datamapper.generator import Generator, SpecException


class ConfigTestCase(TestCase):

    def setUp(self):
        self.engine = create_fixtures()
        self.config = Config({})
        self.config._engine = self.engine
        with open(os.path.join(FIXTURE_PATH, 'spec.yaml'), 'r') as fh:
            self.spec = yaml.load(fh)
        self.gen = Generator(self.config, self.spec)

    def tearDown(self):
        pass

    def test_load_spec(self):
        assert len(self.gen.tables) == 2
        col = self.gen.get_column('fin.price')
        assert col is not None, col

    def test_make_alias(self):
        alias = self.config.get_alias('http://occrp.org/foo/bar.json#xxx')
        assert alias == 'bar', alias
        again = self.config.get_alias('http://occrp.org/foo/bar.json#xxx')
        assert again == alias, again

    def test_expand_envvars(self):
        config = Config({'foo': '$PATH'})
        assert '$PATH' not in config.get('foo'), config.get('foo')
        assert len(config.get('foo')), config.get('foo')

    @raises(ConfigException)
    def test_invalid_alias(self):
        self.config.get_alias('http://occrp.org/foo/bar.json#xxx')
        self.config.get_alias('http://foo.org/xxx/bar.json')
