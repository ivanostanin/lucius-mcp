# LaunchDiffTestResultDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**message** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**test_case_id** | **int** |  | [optional] 
**trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_diff_test_result_dto import LaunchDiffTestResultDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchDiffTestResultDto from a JSON string
launch_diff_test_result_dto_instance = LaunchDiffTestResultDto.from_json(json)
# print the JSON string representation of the object
print(LaunchDiffTestResultDto.to_json())

# convert the object into a dict
launch_diff_test_result_dto_dict = launch_diff_test_result_dto_instance.to_dict()
# create an instance of LaunchDiffTestResultDto from a dict
launch_diff_test_result_dto_from_dict = LaunchDiffTestResultDto.from_dict(launch_diff_test_result_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


