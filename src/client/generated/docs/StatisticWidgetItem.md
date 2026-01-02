# StatisticWidgetItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**statistic** | [**List[TestStatusCount]**](TestStatusCount.md) |  | [optional] 
**uid** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.statistic_widget_item import StatisticWidgetItem

# TODO update the JSON string below
json = "{}"
# create an instance of StatisticWidgetItem from a JSON string
statistic_widget_item_instance = StatisticWidgetItem.from_json(json)
# print the JSON string representation of the object
print(StatisticWidgetItem.to_json())

# convert the object into a dict
statistic_widget_item_dict = statistic_widget_item_instance.to_dict()
# create an instance of StatisticWidgetItem from a dict
statistic_widget_item_from_dict = StatisticWidgetItem.from_dict(statistic_widget_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


