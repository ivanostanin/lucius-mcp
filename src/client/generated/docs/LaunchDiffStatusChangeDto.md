# LaunchDiffStatusChangeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**from_id** | **int** |  | [optional] 
**from_message** | **str** |  | [optional] 
**from_name** | **str** |  | [optional] 
**from_status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**from_trace** | **str** |  | [optional] 
**test_case_id** | **int** |  | [optional] 
**to_id** | **int** |  | [optional] 
**to_message** | **str** |  | [optional] 
**to_name** | **str** |  | [optional] 
**to_status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**to_trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_diff_status_change_dto import LaunchDiffStatusChangeDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchDiffStatusChangeDto from a JSON string
launch_diff_status_change_dto_instance = LaunchDiffStatusChangeDto.from_json(json)
# print the JSON string representation of the object
print(LaunchDiffStatusChangeDto.to_json())

# convert the object into a dict
launch_diff_status_change_dto_dict = launch_diff_status_change_dto_instance.to_dict()
# create an instance of LaunchDiffStatusChangeDto from a dict
launch_diff_status_change_dto_from_dict = LaunchDiffStatusChangeDto.from_dict(launch_diff_status_change_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


