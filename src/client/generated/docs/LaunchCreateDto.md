# LaunchCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**autoclose** | **bool** |  | [optional] 
**external** | **bool** |  | [optional] 
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**name** | **str** |  | 
**project_id** | **int** |  | 
**tags** | [**List[LaunchTagDto]**](LaunchTagDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.launch_create_dto import LaunchCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchCreateDto from a JSON string
launch_create_dto_instance = LaunchCreateDto.from_json(json)
# print the JSON string representation of the object
print(LaunchCreateDto.to_json())

# convert the object into a dict
launch_create_dto_dict = launch_create_dto_instance.to_dict()
# create an instance of LaunchCreateDto from a dict
launch_create_dto_from_dict = LaunchCreateDto.from_dict(launch_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


