# EnvVarSchemaCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**env_var_id** | **int** |  | 
**key** | **str** |  | 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.env_var_schema_create_dto import EnvVarSchemaCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of EnvVarSchemaCreateDto from a JSON string
env_var_schema_create_dto_instance = EnvVarSchemaCreateDto.from_json(json)
# print the JSON string representation of the object
print(EnvVarSchemaCreateDto.to_json())

# convert the object into a dict
env_var_schema_create_dto_dict = env_var_schema_create_dto_instance.to_dict()
# create an instance of EnvVarSchemaCreateDto from a dict
env_var_schema_create_dto_from_dict = EnvVarSchemaCreateDto.from_dict(env_var_schema_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


