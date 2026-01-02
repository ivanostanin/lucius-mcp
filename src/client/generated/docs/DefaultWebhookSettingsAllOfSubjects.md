# DefaultWebhookSettingsAllOfSubjects


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**event_settings** | [**List[EventTypeSettings]**](EventTypeSettings.md) |  | 
**type** | **str** |  | 
**filter** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.default_webhook_settings_all_of_subjects import DefaultWebhookSettingsAllOfSubjects

# TODO update the JSON string below
json = "{}"
# create an instance of DefaultWebhookSettingsAllOfSubjects from a JSON string
default_webhook_settings_all_of_subjects_instance = DefaultWebhookSettingsAllOfSubjects.from_json(json)
# print the JSON string representation of the object
print(DefaultWebhookSettingsAllOfSubjects.to_json())

# convert the object into a dict
default_webhook_settings_all_of_subjects_dict = default_webhook_settings_all_of_subjects_instance.to_dict()
# create an instance of DefaultWebhookSettingsAllOfSubjects from a dict
default_webhook_settings_all_of_subjects_from_dict = DefaultWebhookSettingsAllOfSubjects.from_dict(default_webhook_settings_all_of_subjects_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


