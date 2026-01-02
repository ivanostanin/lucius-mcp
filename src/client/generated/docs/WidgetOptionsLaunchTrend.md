# WidgetOptionsLaunchTrend


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**launch_rql** | **str** |  | [optional] 
**tc_rql** | [**WidgetOptionsHavingSettableAql**](WidgetOptionsHavingSettableAql.md) |  | [optional] 

## Example

```python
from src.client.generated.models.widget_options_launch_trend import WidgetOptionsLaunchTrend

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetOptionsLaunchTrend from a JSON string
widget_options_launch_trend_instance = WidgetOptionsLaunchTrend.from_json(json)
# print the JSON string representation of the object
print(WidgetOptionsLaunchTrend.to_json())

# convert the object into a dict
widget_options_launch_trend_dict = widget_options_launch_trend_instance.to_dict()
# create an instance of WidgetOptionsLaunchTrend from a dict
widget_options_launch_trend_from_dict = WidgetOptionsLaunchTrend.from_dict(widget_options_launch_trend_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


