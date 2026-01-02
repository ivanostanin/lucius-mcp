# PageWidgetDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[WidgetDto]**](WidgetDto.md) |  | [optional] 
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
from src.client.generated.models.page_widget_dto import PageWidgetDto

# TODO update the JSON string below
json = "{}"
# create an instance of PageWidgetDto from a JSON string
page_widget_dto_instance = PageWidgetDto.from_json(json)
# print the JSON string representation of the object
print(PageWidgetDto.to_json())

# convert the object into a dict
page_widget_dto_dict = page_widget_dto_instance.to_dict()
# create an instance of PageWidgetDto from a dict
page_widget_dto_from_dict = PageWidgetDto.from_dict(page_widget_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


