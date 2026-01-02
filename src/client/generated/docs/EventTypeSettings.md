# EventTypeSettings


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | 
**type** | [**EventType**](EventType.md) |  | 

## Example

```python
from src.client.generated.models.event_type_settings import EventTypeSettings

# TODO update the JSON string below
json = "{}"
# create an instance of EventTypeSettings from a JSON string
event_type_settings_instance = EventTypeSettings.from_json(json)
# print the JSON string representation of the object
print(EventTypeSettings.to_json())

# convert the object into a dict
event_type_settings_dict = event_type_settings_instance.to_dict()
# create an instance of EventTypeSettings from a dict
event_type_settings_from_dict = EventTypeSettings.from_dict(event_type_settings_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


