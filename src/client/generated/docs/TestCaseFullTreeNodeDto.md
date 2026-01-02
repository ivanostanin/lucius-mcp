# TestCaseFullTreeNodeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**children** | [**PageTestCaseTreeNodeDto**](PageTestCaseTreeNodeDto.md) |  | [optional] 
**custom_field_value_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**parent_node_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_full_tree_node_dto import TestCaseFullTreeNodeDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseFullTreeNodeDto from a JSON string
test_case_full_tree_node_dto_instance = TestCaseFullTreeNodeDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseFullTreeNodeDto.to_json())

# convert the object into a dict
test_case_full_tree_node_dto_dict = test_case_full_tree_node_dto_instance.to_dict()
# create an instance of TestCaseFullTreeNodeDto from a dict
test_case_full_tree_node_dto_from_dict = TestCaseFullTreeNodeDto.from_dict(test_case_full_tree_node_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


