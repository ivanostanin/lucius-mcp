# TestResultLeafNode


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignee** | **str** |  | [optional] 
**duration** | **int** |  | [optional] 
**flaky** | **bool** |  | [optional] 
**hidden** | **bool** |  | [optional] 
**muted** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**parent_uid** | **str** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**tested_by** | **str** |  | [optional] 
**uid** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_leaf_node import TestResultLeafNode

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultLeafNode from a JSON string
test_result_leaf_node_instance = TestResultLeafNode.from_json(json)
# print the JSON string representation of the object
print(TestResultLeafNode.to_json())

# convert the object into a dict
test_result_leaf_node_dict = test_result_leaf_node_instance.to_dict()
# create an instance of TestResultLeafNode from a dict
test_result_leaf_node_from_dict = TestResultLeafNode.from_dict(test_result_leaf_node_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


