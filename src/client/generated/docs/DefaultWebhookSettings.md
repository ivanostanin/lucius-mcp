# DefaultWebhookSettings


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**headers** | **Dict[str, str]** |  | [optional] 
**subjects** | [**List[DefaultWebhookSettingsAllOfSubjects]**](DefaultWebhookSettingsAllOfSubjects.md) |  | 

## Example

```python
from src.client.generated.models.default_webhook_settings import DefaultWebhookSettings

# TODO update the JSON string below
json = "{}"
# create an instance of DefaultWebhookSettings from a JSON string
default_webhook_settings_instance = DefaultWebhookSettings.from_json(json)
# print the JSON string representation of the object
print(DefaultWebhookSettings.to_json())

# convert the object into a dict
default_webhook_settings_dict = default_webhook_settings_instance.to_dict()
# create an instance of DefaultWebhookSettings from a dict
default_webhook_settings_from_dict = DefaultWebhookSettings.from_dict(default_webhook_settings_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


