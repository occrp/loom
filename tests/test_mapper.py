import os
import yaml
from nose.tools import raises
from unittest import TestCase

from util import create_fixtures, FIXTURE_PATH

from loom.config import Config
from loom.spec import Spec
from loom.mapper import Mapper
from loom.util import SpecException, ConfigException


class MapperTestCase(TestCase):

    def setUp(self):
        self.engine = create_fixtures()
        self.config = Config({

        })
        self.config._engine = self.engine
        with open(os.path.join(FIXTURE_PATH, 'spec.yaml'), 'r') as fh:
            spec = yaml.load(fh)
        self.spec = Spec(self.config, spec)
        self.spec._engine = self.engine
        self.mapper = Mapper(self.config, self.spec)
        self.gen = self.mapper.generator

    def tearDown(self):
        pass

    @raises(SpecException)
    def test_invalid_table(self):
        self.gen.get_column('financials_xxx.price')

    @raises(SpecException)
    def test_no_table(self):
        self.gen.get_column('price')

    @raises(SpecException)
    def test_invalid_column(self):
        self.gen.get_column('fin.value')

    @raises(SpecException)
    def test_unaliased_table(self):
        self.gen.get_column('financials.value')

    @raises(ConfigException)
    def test_invalid_output(self):
        for x in self.gen.generate('knuffels'):
            pass

    def test_generate_records(self):
        comps = [e for e in self.gen.generate('companies')]
        assert 'companies.symbol' in comps[0], comps[0]
        assert 'fin' not in comps[0], comps[0]
        assert len(comps) == 496, len(comps)

    def test_mapping(self):
        for stmt in self.mapper.records('companies'):
            assert 'companies.symbol' not in stmt
            (s, p, o, t) = stmt
            assert s is not None
