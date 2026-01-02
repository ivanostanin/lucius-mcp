# IntegrationWebhookCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id** | **int** |  | 

## Example

```python
from src.client.generated.models.integration_webhook_create_dto import IntegrationWebhookCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of IntegrationWebhookCreateDto from a JSON string
integration_webhook_create_dto_instance = IntegrationWebhookCreateDto.from_json(json)
# print the JSON string representation of the object
print(IntegrationWebhookCreateDto.to_json())

# convert the object into a dict
integration_webhook_create_dto_dict = integration_webhook_create_dto_instance.to_dict()
# create an instance of IntegrationWebhookCreateDto from a dict
integration_webhook_create_dto_from_dict = IntegrationWebhookCreateDto.from_dict(integration_webhook_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


