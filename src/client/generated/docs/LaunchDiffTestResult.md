# LaunchDiffTestResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**duration** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**manual** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 

## Example

```python
from src.client.generated.models.launch_diff_test_result import LaunchDiffTestResult

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchDiffTestResult from a JSON string
launch_diff_test_result_instance = LaunchDiffTestResult.from_json(json)
# print the JSON string representation of the object
print(LaunchDiffTestResult.to_json())

# convert the object into a dict
launch_diff_test_result_dict = launch_diff_test_result_instance.to_dict()
# create an instance of LaunchDiffTestResult from a dict
launch_diff_test_result_from_dict = LaunchDiffTestResult.from_dict(launch_diff_test_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


