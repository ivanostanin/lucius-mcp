# EnvVarCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 

## Example

```python
from src.client.generated.models.env_var_create_dto import EnvVarCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of EnvVarCreateDto from a JSON string
env_var_create_dto_instance = EnvVarCreateDto.from_json(json)
# print the JSON string representation of the object
print(EnvVarCreateDto.to_json())

# convert the object into a dict
env_var_create_dto_dict = env_var_create_dto_instance.to_dict()
# create an instance of EnvVarCreateDto from a dict
env_var_create_dto_from_dict = EnvVarCreateDto.from_dict(env_var_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


