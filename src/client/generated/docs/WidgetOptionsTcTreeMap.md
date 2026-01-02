# WidgetOptionsTcTreeMap


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**launch_rql** | [**WidgetOptionsHavingSettableAql**](WidgetOptionsHavingSettableAql.md) |  | [optional] 
**tc_rql** | **str** |  | [optional] 
**tree_id** | **int** |  | [optional] 
**tree_name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.widget_options_tc_tree_map import WidgetOptionsTcTreeMap

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetOptionsTcTreeMap from a JSON string
widget_options_tc_tree_map_instance = WidgetOptionsTcTreeMap.from_json(json)
# print the JSON string representation of the object
print(WidgetOptionsTcTreeMap.to_json())

# convert the object into a dict
widget_options_tc_tree_map_dict = widget_options_tc_tree_map_instance.to_dict()
# create an instance of WidgetOptionsTcTreeMap from a dict
widget_options_tc_tree_map_from_dict = WidgetOptionsTcTreeMap.from_dict(widget_options_tc_tree_map_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


