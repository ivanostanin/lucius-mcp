# PageTreeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[TreeDto]**](TreeDto.md) |  | [optional] 
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
from src.client.generated.models.page_tree_dto import PageTreeDto

# TODO update the JSON string below
json = "{}"
# create an instance of PageTreeDto from a JSON string
page_tree_dto_instance = PageTreeDto.from_json(json)
# print the JSON string representation of the object
print(PageTreeDto.to_json())

# convert the object into a dict
page_tree_dto_dict = page_tree_dto_instance.to_dict()
# create an instance of PageTreeDto from a dict
page_tree_dto_from_dict = PageTreeDto.from_dict(page_tree_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


