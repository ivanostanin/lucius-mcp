# PageTestCaseTreeNodeDtoContentInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**type** | [**NodeType**](NodeType.md) |  | [optional] 
**count** | **int** |  | [optional] 
**custom_field_id** | **int** |  | [optional] 
**custom_field_value_id** | **int** |  | [optional] 
**parent_node_id** | **int** |  | [optional] 
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
from src.client.generated.models.page_test_case_tree_node_dto_content_inner import PageTestCaseTreeNodeDtoContentInner

# TODO update the JSON string below
json = "{}"
# create an instance of PageTestCaseTreeNodeDtoContentInner from a JSON string
page_test_case_tree_node_dto_content_inner_instance = PageTestCaseTreeNodeDtoContentInner.from_json(json)
# print the JSON string representation of the object
print(PageTestCaseTreeNodeDtoContentInner.to_json())

# convert the object into a dict
page_test_case_tree_node_dto_content_inner_dict = page_test_case_tree_node_dto_content_inner_instance.to_dict()
# create an instance of PageTestCaseTreeNodeDtoContentInner from a dict
page_test_case_tree_node_dto_content_inner_from_dict = PageTestCaseTreeNodeDtoContentInner.from_dict(page_test_case_tree_node_dto_content_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


