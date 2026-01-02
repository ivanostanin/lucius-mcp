# WidgetDataDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | **object** |  | [optional] 
**widget_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.widget_data_dto import WidgetDataDto

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetDataDto from a JSON string
widget_data_dto_instance = WidgetDataDto.from_json(json)
# print the JSON string representation of the object
print(WidgetDataDto.to_json())

# convert the object into a dict
widget_data_dto_dict = widget_data_dto_instance.to_dict()
# create an instance of WidgetDataDto from a dict
widget_data_dto_from_dict = WidgetDataDto.from_dict(widget_data_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


