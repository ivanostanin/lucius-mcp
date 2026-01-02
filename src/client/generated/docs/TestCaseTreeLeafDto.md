# TestCaseTreeLeafDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**automated** | **bool** |  | [optional] 
**created_date** | **int** |  | [optional] 
**external** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**layer_name** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**status_color** | **str** |  | [optional] 
**status_name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_tree_leaf_dto import TestCaseTreeLeafDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseTreeLeafDto from a JSON string
test_case_tree_leaf_dto_instance = TestCaseTreeLeafDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseTreeLeafDto.to_json())

# convert the object into a dict
test_case_tree_leaf_dto_dict = test_case_tree_leaf_dto_instance.to_dict()
# create an instance of TestCaseTreeLeafDto from a dict
test_case_tree_leaf_dto_from_dict = TestCaseTreeLeafDto.from_dict(test_case_tree_leaf_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


