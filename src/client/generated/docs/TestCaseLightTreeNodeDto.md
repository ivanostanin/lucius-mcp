# TestCaseLightTreeNodeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] 
**custom_field_id** | **int** |  | [optional] 
**custom_field_value_id** | **int** |  | [optional] 
**parent_node_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_light_tree_node_dto import TestCaseLightTreeNodeDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseLightTreeNodeDto from a JSON string
test_case_light_tree_node_dto_instance = TestCaseLightTreeNodeDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseLightTreeNodeDto.to_json())

# convert the object into a dict
test_case_light_tree_node_dto_dict = test_case_light_tree_node_dto_instance.to_dict()
# create an instance of TestCaseLightTreeNodeDto from a dict
test_case_light_tree_node_dto_from_dict = TestCaseLightTreeNodeDto.from_dict(test_case_light_tree_node_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


