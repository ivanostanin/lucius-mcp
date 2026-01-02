# TestCaseTreeLeafDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**automated** | **bool** |  | [optional] 
**created_date** | **int** |  | [optional] 
**external** | **bool** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**layer_name** | **str** |  | [optional] 
**status** | [**StatusDto**](StatusDto.md) |  | [optional] 
**test_case_id** | **int** |  | [optional] 
**workflow** | [**WorkflowRowDto**](WorkflowRowDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_tree_leaf_dto_v2 import TestCaseTreeLeafDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseTreeLeafDtoV2 from a JSON string
test_case_tree_leaf_dto_v2_instance = TestCaseTreeLeafDtoV2.from_json(json)
# print the JSON string representation of the object
print(TestCaseTreeLeafDtoV2.to_json())

# convert the object into a dict
test_case_tree_leaf_dto_v2_dict = test_case_tree_leaf_dto_v2_instance.to_dict()
# create an instance of TestCaseTreeLeafDtoV2 from a dict
test_case_tree_leaf_dto_v2_from_dict = TestCaseTreeLeafDtoV2.from_dict(test_case_tree_leaf_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


