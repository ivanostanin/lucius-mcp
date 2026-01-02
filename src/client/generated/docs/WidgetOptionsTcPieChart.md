# WidgetOptionsTcPieChart


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**group_by** | [**GroupBy**](GroupBy.md) |  | [optional] 
**include_in_progress_launches** | **bool** |  | [optional] 
**include_parameters** | **bool** |  | [optional] 
**launch_rql** | **str** |  | [optional] 
**tc_rql** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.widget_options_tc_pie_chart import WidgetOptionsTcPieChart

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetOptionsTcPieChart from a JSON string
widget_options_tc_pie_chart_instance = WidgetOptionsTcPieChart.from_json(json)
# print the JSON string representation of the object
print(WidgetOptionsTcPieChart.to_json())

# convert the object into a dict
widget_options_tc_pie_chart_dict = widget_options_tc_pie_chart_instance.to_dict()
# create an instance of WidgetOptionsTcPieChart from a dict
widget_options_tc_pie_chart_from_dict = WidgetOptionsTcPieChart.from_dict(widget_options_tc_pie_chart_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


