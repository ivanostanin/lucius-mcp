# TestCaseTreeSelectionDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deleted** | **bool** |  | [optional] 
**filter_id** | **int** |  | [optional] 
**groups_exclude** | **List[List[int]]** |  | [optional] 
**groups_include** | **List[List[int]]** |  | [optional] 
**inverted** | **bool** |  | [optional] 
**leafs_exclude** | **List[int]** |  | [optional] 
**leafs_include** | **List[int]** |  | [optional] 
**path** | **List[int]** |  | [optional] 
**project_id** | **int** |  | 
**search** | **str** |  | [optional] 
**tree_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_tree_selection_dto import TestCaseTreeSelectionDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseTreeSelectionDto from a JSON string
test_case_tree_selection_dto_instance = TestCaseTreeSelectionDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseTreeSelectionDto.to_json())

# convert the object into a dict
test_case_tree_selection_dto_dict = test_case_tree_selection_dto_instance.to_dict()
# create an instance of TestCaseTreeSelectionDto from a dict
test_case_tree_selection_dto_from_dict = TestCaseTreeSelectionDto.from_dict(test_case_tree_selection_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


