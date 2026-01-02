# PageTreeDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[TreeDtoV2]**](TreeDtoV2.md) |  | [optional] 
**empty** | **bool** |  | [optional] 
**first** | **bool** |  | [optional] 
**last** | **bool** |  | [optional] 
**number** | **int** |  | [optional] 
**number_of_elements** | **int** |  | [optional] 
**pageable** | [**Pageable**](Pageable.md) |  | [optional] 
**size** | **int** |  | [optional] 
**sort** | [**PageAccessGroupDtoSort**](PageAccessGroupDtoSort.md) |  | [optional] 
**total_elements** | **int** |  | [optional] 
**total_pages** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.page_tree_dto_v2 import PageTreeDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of PageTreeDtoV2 from a JSON string
page_tree_dto_v2_instance = PageTreeDtoV2.from_json(json)
# print the JSON string representation of the object
print(PageTreeDtoV2.to_json())

# convert the object into a dict
page_tree_dto_v2_dict = page_tree_dto_v2_instance.to_dict()
# create an instance of PageTreeDtoV2 from a dict
page_tree_dto_v2_from_dict = PageTreeDtoV2.from_dict(page_tree_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


