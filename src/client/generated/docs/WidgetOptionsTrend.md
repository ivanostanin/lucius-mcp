# WidgetOptionsTrend


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**days_range** | **int** |  | [optional] 
**interval** | [**AnalyticInterval**](AnalyticInterval.md) |  | [optional] 
**launch_rql** | **str** |  | [optional] 
**tc_rql** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.widget_options_trend import WidgetOptionsTrend

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetOptionsTrend from a JSON string
widget_options_trend_instance = WidgetOptionsTrend.from_json(json)
# print the JSON string representation of the object
print(WidgetOptionsTrend.to_json())

# convert the object into a dict
widget_options_trend_dict = widget_options_trend_instance.to_dict()
# create an instance of WidgetOptionsTrend from a dict
widget_options_trend_from_dict = WidgetOptionsTrend.from_dict(widget_options_trend_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


