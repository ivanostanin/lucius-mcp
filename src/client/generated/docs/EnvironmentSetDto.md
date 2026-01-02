# EnvironmentSetDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**values** | [**List[EnvVarValueDto]**](EnvVarValueDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.environment_set_dto import EnvironmentSetDto

# TODO update the JSON string below
json = "{}"
# create an instance of EnvironmentSetDto from a JSON string
environment_set_dto_instance = EnvironmentSetDto.from_json(json)
# print the JSON string representation of the object
print(EnvironmentSetDto.to_json())

# convert the object into a dict
environment_set_dto_dict = environment_set_dto_instance.to_dict()
# create an instance of EnvironmentSetDto from a dict
environment_set_dto_from_dict = EnvironmentSetDto.from_dict(environment_set_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


