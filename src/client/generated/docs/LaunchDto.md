# LaunchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**autoclose** | **bool** |  | [optional] 
**closed** | **bool** |  | [optional] 
**created_date** | **int** |  | [optional] 
**external** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**tags** | [**List[LaunchTagDto]**](LaunchTagDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.launch_dto import LaunchDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchDto from a JSON string
launch_dto_instance = LaunchDto.from_json(json)
# print the JSON string representation of the object
print(LaunchDto.to_json())

# convert the object into a dict
launch_dto_dict = launch_dto_instance.to_dict()
# create an instance of LaunchDto from a dict
launch_dto_from_dict = LaunchDto.from_dict(launch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


