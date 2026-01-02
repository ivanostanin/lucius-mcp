# WidgetOptionsLastLaunchPieChart


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**date_picker_enabled** | **bool** |  | [optional] 
**launch_rql** | **str** |  | [optional] 
**tc_rql** | [**WidgetOptionsHavingSettableAql**](WidgetOptionsHavingSettableAql.md) |  | [optional] 

## Example

```python
from src.client.generated.models.widget_options_last_launch_pie_chart import WidgetOptionsLastLaunchPieChart

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetOptionsLastLaunchPieChart from a JSON string
widget_options_last_launch_pie_chart_instance = WidgetOptionsLastLaunchPieChart.from_json(json)
# print the JSON string representation of the object
print(WidgetOptionsLastLaunchPieChart.to_json())

# convert the object into a dict
widget_options_last_launch_pie_chart_dict = widget_options_last_launch_pie_chart_instance.to_dict()
# create an instance of WidgetOptionsLastLaunchPieChart from a dict
widget_options_last_launch_pie_chart_from_dict = WidgetOptionsLastLaunchPieChart.from_dict(widget_options_last_launch_pie_chart_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


