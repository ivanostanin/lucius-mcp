# LaunchDiffRow


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cells** | [**List[LaunchDiffCell]**](LaunchDiffCell.md) |  | [optional] 
**test_case_id** | **int** |  | [optional] 
**test_case_name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_diff_row import LaunchDiffRow

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchDiffRow from a JSON string
launch_diff_row_instance = LaunchDiffRow.from_json(json)
# print the JSON string representation of the object
print(LaunchDiffRow.to_json())

# convert the object into a dict
launch_diff_row_dict = launch_diff_row_instance.to_dict()
# create an instance of LaunchDiffRow from a dict
launch_diff_row_from_dict = LaunchDiffRow.from_dict(launch_diff_row_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


