# OCCRP DataMapper

As part of a structured data processing pipeline, this library helps to generate
structured JSON from a set of SQL database tables.

The goal is to map a set of automatically generated SQL queries to JSON objects.
These JSON objects will be instances of various types defined by JSON schema.

## Example configuration

```yaml
source:
    title: "Foo Country Company Registry"
    source_url: http://registry.gov.foo/companies
tables:
    - fo_companies_company
    - fo_companies_director
joins:
    - foo_companies_company.id: fo_companies_director.company_id
outputs:
    - mapping:
        schema:
            $ref: http://data.occrp.org/schema/company.json
        mapping:
            name:
                column: foo_companies_company.name
            company_id:
                column: foo_companies_company.id
            directors:
                mapping:
                    name:
                        column: fo_companies_director.name
```