# TestCaseTreeSelectionDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filter_id** | **int** |  | [optional] 
**groups_exclude** | **List[int]** |  | [optional] 
**groups_include** | **List[int]** |  | [optional] 
**inverted** | **bool** |  | [optional] 
**leaves_exclude** | **List[int]** |  | [optional] 
**leaves_include** | **List[int]** |  | [optional] 
**node_id** | **int** |  | [optional] 
**project_id** | **int** |  | 
**search** | **str** |  | [optional] 
**tree_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_tree_selection_dto_v2 import TestCaseTreeSelectionDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseTreeSelectionDtoV2 from a JSON string
test_case_tree_selection_dto_v2_instance = TestCaseTreeSelectionDtoV2.from_json(json)
# print the JSON string representation of the object
print(TestCaseTreeSelectionDtoV2.to_json())

# convert the object into a dict
test_case_tree_selection_dto_v2_dict = test_case_tree_selection_dto_v2_instance.to_dict()
# create an instance of TestCaseTreeSelectionDtoV2 from a dict
test_case_tree_selection_dto_v2_from_dict = TestCaseTreeSelectionDtoV2.from_dict(test_case_tree_selection_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


