# PageTestResultTreeNodeDtoContentInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**type** | [**NodeType**](NodeType.md) |  | [optional] 
**custom_field_id** | **int** |  | [optional] 
**statistic** | [**StatisticDto**](StatisticDto.md) |  | [optional] 
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
from src.client.generated.models.page_test_result_tree_node_dto_content_inner import PageTestResultTreeNodeDtoContentInner

# TODO update the JSON string below
json = "{}"
# create an instance of PageTestResultTreeNodeDtoContentInner from a JSON string
page_test_result_tree_node_dto_content_inner_instance = PageTestResultTreeNodeDtoContentInner.from_json(json)
# print the JSON string representation of the object
print(PageTestResultTreeNodeDtoContentInner.to_json())

# convert the object into a dict
page_test_result_tree_node_dto_content_inner_dict = page_test_result_tree_node_dto_content_inner_instance.to_dict()
# create an instance of PageTestResultTreeNodeDtoContentInner from a dict
page_test_result_tree_node_dto_content_inner_from_dict = PageTestResultTreeNodeDtoContentInner.from_dict(page_test_result_tree_node_dto_content_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


