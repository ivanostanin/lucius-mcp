# TestResultGroupNode


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context** | [**GroupNodeContext**](GroupNodeContext.md) |  | [optional] 
**leafs** | [**List[TestResultLeafNode]**](TestResultLeafNode.md) |  | [optional] 
**name** | **str** |  | [optional] 
**uid** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_group_node import TestResultGroupNode

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultGroupNode from a JSON string
test_result_group_node_instance = TestResultGroupNode.from_json(json)
# print the JSON string representation of the object
print(TestResultGroupNode.to_json())

# convert the object into a dict
test_result_group_node_dict = test_result_group_node_instance.to_dict()
# create an instance of TestResultGroupNode from a dict
test_result_group_node_from_dict = TestResultGroupNode.from_dict(test_result_group_node_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


