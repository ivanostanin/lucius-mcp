# LaunchProgressDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ready** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_progress_dto import LaunchProgressDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchProgressDto from a JSON string
launch_progress_dto_instance = LaunchProgressDto.from_json(json)
# print the JSON string representation of the object
print(LaunchProgressDto.to_json())

# convert the object into a dict
launch_progress_dto_dict = launch_progress_dto_instance.to_dict()
# create an instance of LaunchProgressDto from a dict
launch_progress_dto_from_dict = LaunchProgressDto.from_dict(launch_progress_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


