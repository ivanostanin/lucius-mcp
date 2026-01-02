# LaunchCopyRqDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignees** | **List[str]** |  | [optional] 
**env_var_value_sets** | [**List[EnvironmentSetDto]**](EnvironmentSetDto.md) |  | [optional] 
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**launch_name** | **str** |  | [optional] 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**tags** | [**List[LaunchTagDto]**](LaunchTagDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.launch_copy_rq_dto import LaunchCopyRqDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchCopyRqDto from a JSON string
launch_copy_rq_dto_instance = LaunchCopyRqDto.from_json(json)
# print the JSON string representation of the object
print(LaunchCopyRqDto.to_json())

# convert the object into a dict
launch_copy_rq_dto_dict = launch_copy_rq_dto_instance.to_dict()
# create an instance of LaunchCopyRqDto from a dict
launch_copy_rq_dto_from_dict = LaunchCopyRqDto.from_dict(launch_copy_rq_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


