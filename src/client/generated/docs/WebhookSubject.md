# WebhookSubject


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**event_settings** | [**List[EventTypeSettings]**](EventTypeSettings.md) |  | [optional] 
**type** | **str** |  | 

## Example

```python
from src.client.generated.models.webhook_subject import WebhookSubject

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookSubject from a JSON string
webhook_subject_instance = WebhookSubject.from_json(json)
# print the JSON string representation of the object
print(WebhookSubject.to_json())

# convert the object into a dict
webhook_subject_dict = webhook_subject_instance.to_dict()
# create an instance of WebhookSubject from a dict
webhook_subject_from_dict = WebhookSubject.from_dict(webhook_subject_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


