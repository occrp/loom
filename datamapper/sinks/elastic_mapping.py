from jsonmapping import SchemaVisitor


BASE_MAPPING = {
    "_id": {"path": "id"},
    "_all": {"enabled": True},
    # "_default_": {"type": "string", "store": True, "index": "not_analyzed"},
    "properties": {
        "id": {"type": "string", "index": "not_analyzed"},
        "schema": {"type": "string", "index": "not_analyzed"},
        "indexed_at": {"type": "date", "index": "not_analyzed"},
        "raw": {
            "type": "object",
            "properties": {}
        },
        "source": {"type": "string", "index": "not_analyzed"}
    }
}


def generate_schema_mapping(visitor, path):
    """ Try and recursively iterate a JSON schema and to generate an ES mapping
    that encasulates it. """
    if visitor.is_object:
        mapping = {'type': 'nested', 'properties': {}}
        if not visitor.parent:
            mapping['type'] = 'object'
        if visitor.path in path:
            return mapping
        sub_path = path.union([visitor.path])
        for prop in visitor.properties:
            prop_mapping = generate_schema_mapping(prop, sub_path)
            mapping['properties'][prop.name] = prop_mapping
        return mapping
    elif visitor.is_array:
        for vis in visitor.items:
            return generate_schema_mapping(vis, path)
    else:
        type_name = 'string'
        if 'number' in visitor.types:
            type_name = 'float'
        if 'integer' in visitor.types:
            type_name = 'integer'
        if 'boolean' in visitor.types:
            type_name = 'boolean'
        return {'type': type_name, 'index': 'not_analyzed'}


def generate_mapping(mapping, index, doc_type, record, resolver):
    """ Generate a mapping. """
    mapping = mapping.get(index, {}).get('mappings', {})
    mapping = mapping.get(doc_type, BASE_MAPPING)

    val = {'type': 'string', 'index': 'analyzed', 'store': True}
    for field in record.raw.keys():
        mapping['properties']['raw']['properties'][field] = val

    visitor = SchemaVisitor({'$ref': record.schema}, resolver)
    entity = generate_schema_mapping(visitor, set())
    mapping['properties']['entity'] = entity
    return mapping