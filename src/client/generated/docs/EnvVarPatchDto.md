# EnvVarPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.env_var_patch_dto import EnvVarPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of EnvVarPatchDto from a JSON string
env_var_patch_dto_instance = EnvVarPatchDto.from_json(json)
# print the JSON string representation of the object
print(EnvVarPatchDto.to_json())

# convert the object into a dict
env_var_patch_dto_dict = env_var_patch_dto_instance.to_dict()
# create an instance of EnvVarPatchDto from a dict
env_var_patch_dto_from_dict = EnvVarPatchDto.from_dict(env_var_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


