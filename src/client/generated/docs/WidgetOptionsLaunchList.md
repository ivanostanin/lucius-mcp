# WidgetOptionsLaunchList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**date_picker_enabled** | **bool** |  | [optional] 
**launch_rql** | **str** |  | [optional] 
**tc_rql** | [**WidgetOptionsHavingSettableAql**](WidgetOptionsHavingSettableAql.md) |  | [optional] 

## Example

```python
from src.client.generated.models.widget_options_launch_list import WidgetOptionsLaunchList

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetOptionsLaunchList from a JSON string
widget_options_launch_list_instance = WidgetOptionsLaunchList.from_json(json)
# print the JSON string representation of the object
print(WidgetOptionsLaunchList.to_json())

# convert the object into a dict
widget_options_launch_list_dict = widget_options_launch_list_instance.to_dict()
# create an instance of WidgetOptionsLaunchList from a dict
widget_options_launch_list_from_dict = WidgetOptionsLaunchList.from_dict(widget_options_launch_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


