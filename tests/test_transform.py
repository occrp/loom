import os
import yaml
from nose.tools import raises
from unittest import TestCase

from util import create_fixtures, FIXTURE_PATH

from datamapper.transform import Transform, SpecException

class TransformTestCase(TestCase):

    def setUp(self):
        self.engine = create_fixtures()
        with open(os.path.join(FIXTURE_PATH, 'spec.yaml'), 'r') as fh:
            self.spec = yaml.load(fh)
        self.tf = Transform(self.engine, self.spec)

    def tearDown(self):
        pass

    def test_load_spec(self):
        assert len(self.tf.tables) == 2
        col = self.tf.get_column('financials.price')
        assert col is not None, col

    @raises(SpecException)
    def test_invalid_table(self):
        col = self.tf.get_column('financials_xxx.price')

    @raises(SpecException)
    def test_no_table(self):
        col = self.tf.get_column('price')

    @raises(SpecException)
    def test_invalid_column(self):
        col = self.tf.get_column('financials.value')