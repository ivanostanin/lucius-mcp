# EnvVarValueDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**variable** | [**EnvVarDto**](EnvVarDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.env_var_value_dto import EnvVarValueDto

# TODO update the JSON string below
json = "{}"
# create an instance of EnvVarValueDto from a JSON string
env_var_value_dto_instance = EnvVarValueDto.from_json(json)
# print the JSON string representation of the object
print(EnvVarValueDto.to_json())

# convert the object into a dict
env_var_value_dto_dict = env_var_value_dto_instance.to_dict()
# create an instance of EnvVarValueDto from a dict
env_var_value_dto_from_dict = EnvVarValueDto.from_dict(env_var_value_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


