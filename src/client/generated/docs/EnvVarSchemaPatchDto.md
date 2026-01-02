# EnvVarSchemaPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**env_var_id** | **int** |  | [optional] 
**key** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.env_var_schema_patch_dto import EnvVarSchemaPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of EnvVarSchemaPatchDto from a JSON string
env_var_schema_patch_dto_instance = EnvVarSchemaPatchDto.from_json(json)
# print the JSON string representation of the object
print(EnvVarSchemaPatchDto.to_json())

# convert the object into a dict
env_var_schema_patch_dto_dict = env_var_schema_patch_dto_instance.to_dict()
# create an instance of EnvVarSchemaPatchDto from a dict
env_var_schema_patch_dto_from_dict = EnvVarSchemaPatchDto.from_dict(env_var_schema_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


