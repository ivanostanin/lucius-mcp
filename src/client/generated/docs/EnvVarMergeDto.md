# EnvVarMergeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_from** | **int** |  | [optional] 
**to** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.env_var_merge_dto import EnvVarMergeDto

# TODO update the JSON string below
json = "{}"
# create an instance of EnvVarMergeDto from a JSON string
env_var_merge_dto_instance = EnvVarMergeDto.from_json(json)
# print the JSON string representation of the object
print(EnvVarMergeDto.to_json())

# convert the object into a dict
env_var_merge_dto_dict = env_var_merge_dto_instance.to_dict()
# create an instance of EnvVarMergeDto from a dict
env_var_merge_dto_from_dict = EnvVarMergeDto.from_dict(env_var_merge_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


