# TestResultTreeNodeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**type** | [**NodeType**](NodeType.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_tree_node_dto import TestResultTreeNodeDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultTreeNodeDto from a JSON string
test_result_tree_node_dto_instance = TestResultTreeNodeDto.from_json(json)
# print the JSON string representation of the object
print(TestResultTreeNodeDto.to_json())

# convert the object into a dict
test_result_tree_node_dto_dict = test_result_tree_node_dto_instance.to_dict()
# create an instance of TestResultTreeNodeDto from a dict
test_result_tree_node_dto_from_dict = TestResultTreeNodeDto.from_dict(test_result_tree_node_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


