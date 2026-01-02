# DefectWebhook


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**event_settings** | [**List[EventTypeSettings]**](EventTypeSettings.md) |  | 

## Example

```python
from src.client.generated.models.defect_webhook import DefectWebhook

# TODO update the JSON string below
json = "{}"
# create an instance of DefectWebhook from a JSON string
defect_webhook_instance = DefectWebhook.from_json(json)
# print the JSON string representation of the object
print(DefectWebhook.to_json())

# convert the object into a dict
defect_webhook_dict = defect_webhook_instance.to_dict()
# create an instance of DefectWebhook from a dict
defect_webhook_from_dict = DefectWebhook.from_dict(defect_webhook_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


