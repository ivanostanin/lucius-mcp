# LaunchTagDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_tag_dto import LaunchTagDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchTagDto from a JSON string
launch_tag_dto_instance = LaunchTagDto.from_json(json)
# print the JSON string representation of the object
print(LaunchTagDto.to_json())

# convert the object into a dict
launch_tag_dto_dict = launch_tag_dto_instance.to_dict()
# create an instance of LaunchTagDto from a dict
launch_tag_dto_from_dict = LaunchTagDto.from_dict(launch_tag_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


