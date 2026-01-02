# WidgetOptionsTopTc


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**days_range** | **int** |  | [optional] 
**launch_rql** | **str** |  | [optional] 
**metric** | [**Metric**](Metric.md) |  | 
**tc_rql** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.widget_options_top_tc import WidgetOptionsTopTc

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetOptionsTopTc from a JSON string
widget_options_top_tc_instance = WidgetOptionsTopTc.from_json(json)
# print the JSON string representation of the object
print(WidgetOptionsTopTc.to_json())

# convert the object into a dict
widget_options_top_tc_dict = widget_options_top_tc_instance.to_dict()
# create an instance of WidgetOptionsTopTc from a dict
widget_options_top_tc_from_dict = WidgetOptionsTopTc.from_dict(widget_options_top_tc_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


