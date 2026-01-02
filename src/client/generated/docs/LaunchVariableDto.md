# LaunchVariableDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** |  | [optional] 
**values** | **List[str]** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_variable_dto import LaunchVariableDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchVariableDto from a JSON string
launch_variable_dto_instance = LaunchVariableDto.from_json(json)
# print the JSON string representation of the object
print(LaunchVariableDto.to_json())

# convert the object into a dict
launch_variable_dto_dict = launch_variable_dto_instance.to_dict()
# create an instance of LaunchVariableDto from a dict
launch_variable_dto_from_dict = LaunchVariableDto.from_dict(launch_variable_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


