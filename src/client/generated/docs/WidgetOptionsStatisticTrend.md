# WidgetOptionsStatisticTrend


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**date_picker_enabled** | **bool** |  | [optional] 
**days_range** | **int** |  | [optional] 
**interval** | [**AnalyticInterval**](AnalyticInterval.md) |  | [optional] 
**launch_rql** | **str** |  | [optional] 
**tc_rql** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.widget_options_statistic_trend import WidgetOptionsStatisticTrend

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetOptionsStatisticTrend from a JSON string
widget_options_statistic_trend_instance = WidgetOptionsStatisticTrend.from_json(json)
# print the JSON string representation of the object
print(WidgetOptionsStatisticTrend.to_json())

# convert the object into a dict
widget_options_statistic_trend_dict = widget_options_statistic_trend_instance.to_dict()
# create an instance of WidgetOptionsStatisticTrend from a dict
widget_options_statistic_trend_from_dict = WidgetOptionsStatisticTrend.from_dict(widget_options_statistic_trend_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


