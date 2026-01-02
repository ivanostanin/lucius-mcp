# EnvVarValueCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**variable** | [**IdOnlyDto**](IdOnlyDto.md) |  | 

## Example

```python
from src.client.generated.models.env_var_value_create_dto import EnvVarValueCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of EnvVarValueCreateDto from a JSON string
env_var_value_create_dto_instance = EnvVarValueCreateDto.from_json(json)
# print the JSON string representation of the object
print(EnvVarValueCreateDto.to_json())

# convert the object into a dict
env_var_value_create_dto_dict = env_var_value_create_dto_instance.to_dict()
# create an instance of EnvVarValueCreateDto from a dict
env_var_value_create_dto_from_dict = EnvVarValueCreateDto.from_dict(env_var_value_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


