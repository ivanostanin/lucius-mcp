# EnvVarValuePatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.env_var_value_patch_dto import EnvVarValuePatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of EnvVarValuePatchDto from a JSON string
env_var_value_patch_dto_instance = EnvVarValuePatchDto.from_json(json)
# print the JSON string representation of the object
print(EnvVarValuePatchDto.to_json())

# convert the object into a dict
env_var_value_patch_dto_dict = env_var_value_patch_dto_instance.to_dict()
# create an instance of EnvVarValuePatchDto from a dict
env_var_value_patch_dto_from_dict = EnvVarValuePatchDto.from_dict(env_var_value_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


