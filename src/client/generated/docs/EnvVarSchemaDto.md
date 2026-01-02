# EnvVarSchemaDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**env_var** | [**EnvVarDto**](EnvVarDto.md) |  | [optional] 
**id** | **int** |  | [optional] 
**key** | **str** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.env_var_schema_dto import EnvVarSchemaDto

# TODO update the JSON string below
json = "{}"
# create an instance of EnvVarSchemaDto from a JSON string
env_var_schema_dto_instance = EnvVarSchemaDto.from_json(json)
# print the JSON string representation of the object
print(EnvVarSchemaDto.to_json())

# convert the object into a dict
env_var_schema_dto_dict = env_var_schema_dto_instance.to_dict()
# create an instance of EnvVarSchemaDto from a dict
env_var_schema_dto_from_dict = EnvVarSchemaDto.from_dict(env_var_schema_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


