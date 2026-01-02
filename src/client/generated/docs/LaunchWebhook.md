# LaunchWebhook


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**event_settings** | [**List[EventTypeSettings]**](EventTypeSettings.md) |  | 
**filter** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_webhook import LaunchWebhook

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchWebhook from a JSON string
launch_webhook_instance = LaunchWebhook.from_json(json)
# print the JSON string representation of the object
print(LaunchWebhook.to_json())

# convert the object into a dict
launch_webhook_dict = launch_webhook_instance.to_dict()
# create an instance of LaunchWebhook from a dict
launch_webhook_from_dict = LaunchWebhook.from_dict(launch_webhook_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


