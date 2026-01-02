# LaunchDiffCell


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**launch_id** | **int** |  | [optional] 
**launch_name** | **str** |  | [optional] 
**results** | [**List[LaunchDiffTestResult]**](LaunchDiffTestResult.md) |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 

## Example

```python
from src.client.generated.models.launch_diff_cell import LaunchDiffCell

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchDiffCell from a JSON string
launch_diff_cell_instance = LaunchDiffCell.from_json(json)
# print the JSON string representation of the object
print(LaunchDiffCell.to_json())

# convert the object into a dict
launch_diff_cell_dict = launch_diff_cell_instance.to_dict()
# create an instance of LaunchDiffCell from a dict
launch_diff_cell_from_dict = LaunchDiffCell.from_dict(launch_diff_cell_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


