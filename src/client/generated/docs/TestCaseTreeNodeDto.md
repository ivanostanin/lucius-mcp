# TestCaseTreeNodeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**type** | [**NodeType**](NodeType.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_tree_node_dto import TestCaseTreeNodeDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseTreeNodeDto from a JSON string
test_case_tree_node_dto_instance = TestCaseTreeNodeDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseTreeNodeDto.to_json())

# convert the object into a dict
test_case_tree_node_dto_dict = test_case_tree_node_dto_instance.to_dict()
# create an instance of TestCaseTreeNodeDto from a dict
test_case_tree_node_dto_from_dict = TestCaseTreeNodeDto.from_dict(test_case_tree_node_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


