# TestCaseSelectionDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deleted** | **bool** |  | [optional] 
**filter_id** | **int** |  | [optional] 
**groups_exclude** | **List[int]** |  | [optional] 
**groups_include** | **List[int]** |  | [optional] 
**inverted** | **bool** |  | [optional] 
**node_id** | **int** |  | [optional] 
**project_id** | **int** |  | 
**search** | **str** |  | [optional] 
**test_cases_exclude** | **List[int]** |  | [optional] 
**test_cases_include** | **List[int]** |  | [optional] 
**tree_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_selection_dto_v2 import TestCaseSelectionDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseSelectionDtoV2 from a JSON string
test_case_selection_dto_v2_instance = TestCaseSelectionDtoV2.from_json(json)
# print the JSON string representation of the object
print(TestCaseSelectionDtoV2.to_json())

# convert the object into a dict
test_case_selection_dto_v2_dict = test_case_selection_dto_v2_instance.to_dict()
# create an instance of TestCaseSelectionDtoV2 from a dict
test_case_selection_dto_v2_from_dict = TestCaseSelectionDtoV2.from_dict(test_case_selection_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


