# PageStatisticWidgetItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[StatisticWidgetItem]**](StatisticWidgetItem.md) |  | [optional] 
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
from src.client.generated.models.page_statistic_widget_item import PageStatisticWidgetItem

# TODO update the JSON string below
json = "{}"
# create an instance of PageStatisticWidgetItem from a JSON string
page_statistic_widget_item_instance = PageStatisticWidgetItem.from_json(json)
# print the JSON string representation of the object
print(PageStatisticWidgetItem.to_json())

# convert the object into a dict
page_statistic_widget_item_dict = page_statistic_widget_item_instance.to_dict()
# create an instance of PageStatisticWidgetItem from a dict
page_statistic_widget_item_from_dict = PageStatisticWidgetItem.from_dict(page_statistic_widget_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


