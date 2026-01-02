# TestPlanWebhook


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**event_settings** | [**List[EventTypeSettings]**](EventTypeSettings.md) |  | 

## Example

```python
from src.client.generated.models.test_plan_webhook import TestPlanWebhook

# TODO update the JSON string below
json = "{}"
# create an instance of TestPlanWebhook from a JSON string
test_plan_webhook_instance = TestPlanWebhook.from_json(json)
# print the JSON string representation of the object
print(TestPlanWebhook.to_json())

# convert the object into a dict
test_plan_webhook_dict = test_plan_webhook_instance.to_dict()
# create an instance of TestPlanWebhook from a dict
test_plan_webhook_from_dict = TestPlanWebhook.from_dict(test_plan_webhook_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


