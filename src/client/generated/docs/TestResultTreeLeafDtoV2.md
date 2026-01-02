# TestResultTreeLeafDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignee** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**duration** | **int** |  | [optional] 
**flaky** | **bool** |  | [optional] 
**hidden** | **bool** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**layer_name** | **str** |  | [optional] 
**manual** | **bool** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**test_case_id** | **int** |  | [optional] 
**tested_by** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_tree_leaf_dto_v2 import TestResultTreeLeafDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultTreeLeafDtoV2 from a JSON string
test_result_tree_leaf_dto_v2_instance = TestResultTreeLeafDtoV2.from_json(json)
# print the JSON string representation of the object
print(TestResultTreeLeafDtoV2.to_json())

# convert the object into a dict
test_result_tree_leaf_dto_v2_dict = test_result_tree_leaf_dto_v2_instance.to_dict()
# create an instance of TestResultTreeLeafDtoV2 from a dict
test_result_tree_leaf_dto_v2_from_dict = TestResultTreeLeafDtoV2.from_dict(test_result_tree_leaf_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


