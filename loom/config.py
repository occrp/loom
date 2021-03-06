import os
import logging
import urlparse

from normality import slugify
from sqlalchemy import create_engine
from jsonschema import RefResolver
from jsonmapping import SchemaVisitor
from elasticsearch import Elasticsearch

from loom.db import EntityManager, TableManager, Property, Entity
from loom.db import session, Base
from loom.util import ConfigException, EnvMapping

log = logging.getLogger(__name__)


class Config(EnvMapping):
    """ Parsing a configuration file. This specifies the database connection
    and the settings the data sink. """

    def __init__(self, data, path=None):
        self.path = path or os.getcwd()
        data['schemas'] = data.get('schemas', {})
        super(Config, self).__init__(data)

    @property
    def engine(self):
        if not hasattr(self, '_engine'):
            uri = self.get('database')
            if uri is None:
                raise ConfigException("No statement database URI configured!")
            log.debug("Loom database: %r", uri)
            self._engine = create_engine(uri)
        return self._engine

    @property
    def is_postgresql(self):
        return 'postgres' in self.engine.dialect.name

    def setup(self):
        session.configure(bind=self.engine)
        Base.metadata.bind = self.engine
        Base.metadata.create_all()

    @property
    def entities(self):
        if not hasattr(self, '_entities'):
            self._entities = EntityManager(self)
        return self._entities

    @property
    def types(self):
        if not hasattr(self, '_types'):
            self._types = TableManager(self, Entity)
        return self._types

    @property
    def properties(self):
        if not hasattr(self, '_properties'):
            self._properties = TableManager(self, Property)
        return self._properties

    @property
    def base_uri(self):
        uri = 'file://' + os.path.abspath(self.path)
        return self.get('base_uri', uri)

    @property
    def elastic_client(self):
        if not hasattr(self, '_elastic_client'):
            host = self.get('elastic_host')
            if host is None:
                raise ConfigException("No 'elastic_host' is configured.")
            self._elastic_client = Elasticsearch([host])
        return self._elastic_client

    @property
    def elastic_index(self):
        if not hasattr(self, '_elastic_index'):
            self._elastic_index = self.get('elastic_index')
            if self._elastic_index is None:
                raise ConfigException("No 'elastic_index' is configured.")
        return self._elastic_index

    @property
    def schemas(self):
        return self.get('schemas', {})

    @property
    def resolver(self):
        if not hasattr(self, '_resolver'):
            self._resolver = RefResolver(self.base_uri, self.base_uri)
        return self._resolver

    def load_schemas(self):
        for uri in self.schemas.values():
            self.resolver.resolve(uri)

    def _check_match(self, visitor, schema_uri):
        if visitor.id == schema_uri:
            return True
        for parent in visitor.inherited:
            if self._check_match(parent, schema_uri):
                return True
        return False

    def implied_schemas(self, schema_uri):
        """ Given a schema URI, return a list of implied (i.e. child) schema URIs,
        with the original schema included. """
        self.load_schemas()
        schemas = [schema_uri]
        for uri, data in self.resolver.store.items():
            if isinstance(data, dict):
                visitor = SchemaVisitor(data, self.resolver)
                if self._check_match(visitor, schema_uri):
                    schemas.append(data.get('id'))
        return schemas

    def add_schema(self, schema):
        if 'id' in schema and schema['id'] not in self.resolver.store:
            self.resolver.store[schema['id']] = schema

    def get_alias(self, schema):
        """ Slightly hacky way of getting a slug-like name for a schema. This
        is used to determine document types in the Elastic index. """
        for alias, uri in self.schemas.items():
            if uri == schema:
                return alias
        p = urlparse.urlparse(schema)
        name, _ = os.path.splitext(os.path.basename(p.path))
        name = slugify(name, sep='_')
        if not len(name) or name in self.schemas:
            raise ConfigException("Cannot determine alias for: %r" % schema)
        self['schemas'][name] = schema
        return name
