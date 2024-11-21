from to_json_schema.to_json_schema import SchemaBuilder

data = {
    "PII": ["John Smith", "ACME Corp", "New York"],
    "pseudonym": ["Michael Carter", "TechNova", "Silverlake"] 
}

schema_builder = SchemaBuilder()
json_schema = schema_builder.to_json_schema(data)
print(json_schema)
