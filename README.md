# Loom

``loom`` is a command-line tool that maps data from its source table structure
to a common data model, defined through [JSON Schema](http://json-schema.org/).
Once data has been modeled into such objects, it is stored as a set of
statements in a SQL database and eventually indexed in ElasticSearch.

## Design

The design goal of ``loom`` is to accept data from many different sources and
in many different formats, and to integrate it into a single, coherent data
model that can be used for analysis.

### Data integration

Imagine, for example, trying to investigate a senior politician. You might find
data about that person on WikiData, by scraping a parliament's web site,
extracting data from expense reports and by looking up company ownership
records in a corporate registry.

The purpose of ``loom`` is to read data from all of these sources, and to
translate each source record into a (partially-filled) JSON object representing
a person. This object may have nested items, such as information about party
posts, company directorships etc.

``loom`` will also provide means for de-duplicating entities, so that all the
different records about the politician coming from various sources will be
merged into a single, coherent and complete profile. This is made possible by
splitting the information into atomic statements (often called triples or quads,
[learn more](http://www.w3.org/TR/rdf11-concepts/#section-triples)).

### Indexing

Using statements, the information can also be re-constructed in different ways
than it was originally submitted. For example, after importing a list of people
with nested information about what companies they control, you could very
easily invert that into a list of companies with nested information about the
people who control them.

This aspect is used when indexing the data: ``loom`` will go through all entity
types and try and generate a nested representation of each entity it finds.
This means that if you import a record about a person that controls a company,
you will end up with two indexed objects: the person (with a reference to the
company) and the company (with a reference to the person).

### Design constraints

The statement tables generated by ``loom`` are very similar to an RDF triple
store. It may be tempting to think about using them to perform recursive graph
queries (*Show me all the politicians from Germany that have companies which
have subsidiaries in the Cayman Islands*).

This, however, would quickly lead to an explosion in the join cross-product and
kill any SQL database. It is not a design goal of ``loom`` to support this. We
should, however, provide an export facility to generate RDF data which can be
imported into a triple store and queried there.

## Configuration

All of ``loom`` is controlled via a configuration file which defines the source
and target databases for data mapping, how to query the source data, available
data types, source details and, most importantly, a mapping between source data
structure and the JSON schema-defined model.

```yaml
# Two PostgreSQL databases should be provided. The ODS database is expected to
# contain the source tables referenced below (fo_companies_director,
# fo_companies_company), while the loom database can be empty (statement
# tables will be created automatically). Since loom uses maintenance functions
# (COPY) to load data, you may need to provide superuser access to the target
# database.
ods_database: postgresql://localhost/source_database
loom_database: postgresql://localhost/statements

# ElasticSearch indexing destination. The index does not need to exist prior to
# running loom.
elastic_host: localhost:9200
elastic_index: graph

# This is the schema registry, which will be used to determine short-hand
# aliases for specific types. All schemas listed here will be indexed to
# ElasticSearch.
schemas:
    company: http://schema.occrp.org/generic/company.json#

# Source metadata, limited to three basic fields for the moment.
source:
    slug: foo_companies
    title: "Foo Country Company Registry"
    url: http://registry.gov.foo/companies

# Source data tables, and how to join them. Tables can also be assigned an
# alias to allow for recursive joins (i.e. for parent-child relationships).
tables:
    - fo_companies_company
    - fo_companies_director
joins:
    - foo_companies_company.id: fo_companies_director.company_id

# Outputs define the set of queries to be run, alongside with a mapping that
# is used to translate the resulting records into JSON schema objects:
outputs:
    # Every output has a name, which is used only for internal purposes:
    demo:
        schema:
            $ref: http://schema.occrp.org/generic/company.json#
        mapping:
            # Mapping for a single field in the destination schema:
            name:
                column: foo_companies_company.name
                # Some transformations can be applied:
                transforms:
                    - clean
                    - latinize
            company_id:
                columns: foo_companies_company.id
                format: 'urn:foo:%s'
            directors:
                # Nested object, which uses the same mapping method:
                mapping:
                    name:
                        column: fo_companies_director.name
```

The content of the ``mapping`` section of this specification file is based on
a separate Python library called [jsonmapping](https://github.com/pudo/jsonmapping).
Refer to that package's documentation for information about how to perform more
complex mappings and transformations on the source data.

## Installation

Before installing ``loom``, make sure you have both dependencies - PostgreSQL
and ElasticSearch - installed.

If you wish to use the ``loom`` command line tool, you can install the
application into a Python [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
like this:

```bash
$ pip install git+https://github.com/occrp/loom
```

To do development on the tool, you should instead check out a local copy:

```bash
$ git clone git@github.com:occrp/loom.git
$ cd loom
$ make install
$ make test
```

Instead of executing the ``Makefile`` commands (which create a virtual
environment and install the necessary dependencies), you can also run these
steps manually.

## Usage

A prerequisite for using ``loom`` is that source data needs to be stored in a
PostgreSQL database. The specific layout of the source data tables is not
important, since the JSON object mapping will be applied.

After installing ``loom``, a command-line tool is available. You can use the
``--help`` argument to learn more about it's functioning.

A basic sequence of commands might look like this:

```bash
# first, register the metadata with the loom data store:
$ loom init my_spec.yaml
# translate the source data records into the loom data store as statements:
$ loom map my_spec.yaml
# index the statements into ElasticSearch:
$ loom index my_spec.yaml
# delete statements from the data store:
$ loom flush my_spec.yaml
```

## Similar work and references

``loom`` is heavily inspired by Linked Data and RDF. If you're interested in
similar tools in that ecosystem, check out:

* [Grafter](http://grafter.org/)
* [Silk Framework](http://silk-framework.com/)

## License

``loom`` is free software; it is distributed under the terms of the Affero
General Public License, version 3.
